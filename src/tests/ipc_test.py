import asyncio
import flet as ft
from ipc import IPCManager


def before_test(page: ft.Page):
    page.title = "Test 005 - IPC"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.width = 500
    page.window.height = 300


async def test(page: ft.Page):
    # --- UI setup ---
    messages = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, auto_scroll=True)
    input_box = ft.TextField(label="Message", autofocus=True, expand=True)
    toggle_btn = ft.Button("Toggle Me", icon=ft.Icons.CHECK_BOX_OUTLINE_BLANK)
    toggle: bool = False
    loop_task: asyncio.Task = None
    loop_stop_event: asyncio.Event = asyncio.Event()

    # Helper function for consistent message appending
    def add_message(text: str):
        messages.controls.append(ft.Text(text))
        page.update()

    # --- Initialize IPC ---
    ipc = IPCManager(on_message=lambda msg: add_message(f"📩 {msg}"))
    ipc.start()  # auto host/client + host migration (to be implemented in IPCManager)
    
    # Loop
    async def loop():
        """Continuously sends window coordinates every 0.2s until stop_event is set."""
        nonlocal messages
        try:
            while not loop_stop_event.is_set():
                await asyncio.sleep(0.2)
                data = {"x": page.window.left, "y": page.window.top}
                ipc.send(f"Window position: {data}")
                if len(messages.controls) > 10:
                    messages.controls.pop(0)
                    messages.update()
        except asyncio.CancelledError:
            print("[Loop] Cancelled safely.")
        finally:
            print("[Loop] Exited loop.")
    
    # Display the current role
    add_message("🔷 Running as host" if ipc.is_server else "🟢 Connected to host")

    # --- Send message manually ---
    def on_submit(_):
        msg = input_box.value.strip()
        if msg:
            ipc.send(msg)
            add_message(f"🧑‍💻 You: {msg}")
            input_box.value = ""
            page.update()

    # --- Toggle button callback ---
    def on_click(_):
        nonlocal toggle, loop_task, loop_stop_event

        toggle = not toggle
        toggle_btn.icon = ft.Icons.CHECK_BOX if toggle else ft.Icons.CHECK_BOX_OUTLINE_BLANK
        toggle_btn.update()

        if toggle:
            # Start loop
            loop_stop_event.clear()
            loop_task = asyncio.create_task(loop())
            add_message("🌀 Started sending window data...")
        else:
            # Stop loop
            loop_stop_event.set()
            if loop_task:
                loop_task.cancel()
                loop_task = None
            add_message("⏹️ Stopped sending window data.")

    input_box.on_submit = on_submit
    toggle_btn.on_click = on_click

    # --- UI layout ---
    layout = ft.Column(
        controls=[
            messages,
            ft.Row([input_box, toggle_btn]),
        ],
        expand=True,
        spacing=8,
    )

    page.add(layout)
    await page.window.center()

    # --- Handle graceful shutdown ---
    def on_close(_):
        loop_stop_event.set()
        if loop_task:
            loop_task.cancel()
        ipc.stop()
        print("[IPC] Closed cleanly.")

    page.on_close = on_close


if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)
    