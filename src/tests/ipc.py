# ipc.py
import socket
import threading
import time
from typing import Callable, Optional

HOST = "127.0.0.1"
PORT = 50555

class IPCManager:
    def __init__(self, on_message: Optional[Callable[[str], None]] = None, retry_interval=1.0):
        self.on_message = on_message or (lambda msg: None)
        self.sock = None
        self.is_server = False
        self.clients = []
        self.retry_interval = retry_interval
        self.running = True
        self.lock = threading.Lock()

    # === Start the IPC system ===
    def start(self):
        if self.try_start_server():
            self.is_server = True
            print("[IPC] Running as host.")
        else:
            print("[IPC] Connected as client.")
            self.is_server = False
            self.try_connect_client()

        # Start watchdog for automatic host migration
        threading.Thread(target=self._watch_connection, daemon=True).start()

    # === Try to become host ===
    def try_start_server(self) -> bool:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST, PORT))
            s.listen()
            self.sock = s
            threading.Thread(target=self._server_loop, daemon=True).start()
            return True
        except OSError:
            return False

    # === Try connecting as client ===
    def try_connect_client(self, retries=10) -> bool:
        for _ in range(retries):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, PORT))
                self.sock = s
                threading.Thread(target=self._client_loop, daemon=True).start()
                return True
            except ConnectionRefusedError:
                time.sleep(self.retry_interval)
        return False

    # === Send message ===
    def send(self, message: str):
        try:
            if self.is_server:
                with self.lock:
                    for c in self.clients.copy():
                        try:
                            c.sendall(message.encode("utf-8"))
                        except:
                            self.clients.remove(c)
            else:
                self.sock.sendall(message.encode("utf-8"))
        except Exception as e:
            print("[IPC] Send error:", e)

    # === Server loop ===
    def _server_loop(self):
        while self.running:
            try:
                conn, addr = self.sock.accept()
                with self.lock:
                    self.clients.append(conn)
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except OSError:
                break  # Socket closed

    def _handle_client(self, conn):
        while self.running:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode("utf-8")
                self.on_message(msg)
                # Broadcast to all other clients
                with self.lock:
                    for c in self.clients.copy():
                        if c != conn:
                            c.sendall(data)
            except Exception:
                break
        with self.lock:
            if conn in self.clients:
                self.clients.remove(conn)
        conn.close()

    # === Client loop ===
    def _client_loop(self):
        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                msg = data.decode("utf-8")
                self.on_message(msg)
            except Exception:
                break
        print("[IPC] Connection lost.")
        self.sock.close()
        self._handle_disconnect()

    # === Watchdog for host migration ===
    def _watch_connection(self):
        while self.running:
            if not self.is_server and (self.sock is None or self._is_socket_closed()):
                print("[IPC] Lost connection to host, retrying...")
                if not self.try_connect_client(retries=5):
                    print("[IPC] No host found — promoting self to host.")
                    if self.try_start_server():
                        self.is_server = True
                        self.on_message("🟢 New host elected.")
            time.sleep(2)

    def _is_socket_closed(self):
        try:
            self.sock.send(b"")
            return False
        except:
            return True

    # === Handle lost connection gracefully ===
    def _handle_disconnect(self):
        self.sock = None
        time.sleep(1)
        self._watch_connection()

    # === Stop everything ===
    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        print("[IPC] Stopped.")
