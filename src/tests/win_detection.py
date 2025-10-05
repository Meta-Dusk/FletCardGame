import flet as ft
import psutil, asyncio
import uiautomation as auto

from enum import Enum
from typing import Optional

# === CONFIG ===
PRODUCTIVE_APPS = [
    "code.exe", "pycharm64.exe", "anki.exe", "obsidian.exe",
    "notepad.exe", "pdfreader.exe", "mspowerpoint.exe"
]
DISTRACTING_KEYWORDS = [
    "youtube", "facebook", "reddit", "twitter", "tiktok", "discord", "netflix"
]
class AppType(Enum):
    DISTRACTING = "distracting"
    NEUTRAL = "neutral"
    PRODUCTIVE = "productive"

class WindowInfo(Enum):
    NAME = "name"
    CLASS_NAME = "class_name"
    PROCESS_ID = "process_id"

# === BACKGROUND MONITOR FUNCTION ===
def get_active_window_info() -> dict[WindowInfo, Optional[str | int]]:
    """Returns dict with info about the currently focused window."""
    # Proper COM init for this thread
    with auto.UIAutomationInitializerInThread():
        ctrl = auto.GetForegroundControl()
        return {
            WindowInfo.NAME: ctrl.Name or None,
            WindowInfo.CLASS_NAME: ctrl.ClassName or None,
            WindowInfo.PROCESS_ID: ctrl.ProcessId or 0
        }


def get_process_name(pid: int) -> str:
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "unknown"


def classify_window(win_info) -> AppType:
    title = win_info["name"].lower()
    process = get_process_name(win_info["process_id"]).lower()

    if any(app in process for app in PRODUCTIVE_APPS):
        return AppType.PRODUCTIVE
    elif any(word in title for word in DISTRACTING_KEYWORDS):
        return AppType.DISTRACTING
    else:
        return AppType.NEUTRAL


# === MAIN FLET APP ===
def before_main(page: ft.Page):
    page.title = "Anti-Slacking Monitor"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.maximizable = False
    page.window.resizable = False
    page.window.minimizable = False
    page.window.width = 500
    page.window.height = 300
    page.window.always_on_top = False

async def main(page: ft.Page):
    await page.window.center()
    
    REFRESH_RATE = 0.1
    
    current_app = ft.Column(
        controls=[ft.Text("Detecting active window...", size=18, weight=ft.FontWeight.BOLD, data="editable_text")],
        scroll=ft.ScrollMode.ALWAYS, expand=True
    )
    category_text = ft.Text("Unknown", size=28, weight=ft.FontWeight.BOLD)

    container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Current Window:", size=14),
                current_app,
                ft.Divider(height=20),
                ft.Text("Status:", size=14),
                category_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=20, border_radius=16, expand=True,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        alignment=ft.Alignment.CENTER,
    )
    
    page.add(container)
    
    stop_event = asyncio.Event()

    async def monitor_focus_async():
        prev_title = ""
        while not stop_event.is_set():
            # Run blocking call in a background thread with COM initialized
            info = await asyncio.to_thread(get_active_window_info)
            category = classify_window(info)
            title = info.get(WindowInfo.NAME) if not None else "Unknown Window"
            
            if category == AppType.DISTRACTING:
                await page.window.to_front()
            
            if title != prev_title:
                prev_title = title
                current_app_column: ft.Column = current_app.controls
                for ctrl in current_app_column:
                    if isinstance(ctrl, ft.Text) and ctrl.data == "editable_text":
                        current_app_text: ft.Text = ctrl
                        current_app_text.value = title
                category_text.value = category.value.title()
                category_text.color = (
                    ft.Colors.GREEN if category == AppType.PRODUCTIVE
                    else ft.Colors.RED if category == AppType.DISTRACTING
                    else ft.Colors.AMBER
                )
                page.update()
            
            if category != AppType.DISTRACTING:
                await asyncio.sleep(REFRESH_RATE)
            else:
                print("Detected distraction!")
                await asyncio.sleep(2)
        print("Monitor task stopped.")
    
    # Start monitoring task
    page.run_task(monitor_focus_async)
    
    # Stop it cleanly when window closes
    async def on_close(_):
        print("App is closing... Waiting for monitor to stop.")
        if not stop_event.is_set():
            stop_event.set()
    
    page.on_close = on_close


if __name__ == "__main__":
    ft.run(main=main, before_main=before_main)
