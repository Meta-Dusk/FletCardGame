import asyncio
import flet as ft
from pathlib import Path
from typing import Optional


ASSETS_PATH = Path(__file__).resolve().parent / "assets"
WHITE_CARDS_PATH = ASSETS_PATH / "images" / "cards" / "white"
BLACK_CARDS_PATH = ASSETS_PATH / "images" / "cards" / "black"
CARD_WIDTH = 655
CARD_HEIGHT = 930


# === COMPONENT PRESETS ===
def simple_icon_button(
    icon: ft.IconDataOrControl,
    icon_color: ft.ColorValue = ft.Colors.PRIMARY,
    on_click: Optional[ft.ControlEventHandler[ft.IconButton]] = None
) -> ft.IconButton:
    """Literally just an `IconButton` with a default `icon_color`."""
    return ft.IconButton(
        icon=icon, icon_color=icon_color, on_click=on_click
    )

def simple_button(
    text: str, icon: Optional[ft.IconDataOrControl] = None,
    color: ft.ColorValue = ft.Colors.PRIMARY,
    on_click: Optional[ft.ControlEventHandler[ft.Button]] = None
) -> ft.Button:
    """Just a simple button with color applied to both text and icon."""
    return ft.Button(
        content=ft.Text(text, color=color, text_align=ft.TextAlign.CENTER),
        icon=icon, icon_color=color, on_click=on_click
    )

# === PRE-ASSEMBLED COMPONENTS ===
# | Buttons |
def fullscreen_button(page: ft.Page) -> ft.IconButton:
    """Handles the window maximizing functionality."""
    def update_icon():
        nonlocal btn
        btn.icon = set_icon()
        btn.update()
        
    def set_icon() -> ft.IconData:
        if page.window.full_screen:
            icon = ft.Icons.FULLSCREEN
        else:
            icon = ft.Icons.FULLSCREEN_EXIT
        return icon
    
    def on_click(_):
        page.window.full_screen = not page.window.full_screen
        
    page.on_resize = lambda _: update_icon()
    btn = simple_icon_button(
        icon=set_icon(), on_click=on_click
    )
    return btn

def minimize_button(page: ft.Page) -> ft.IconButton:
    """Handles the window minimizing functionality."""
    def on_click(_):
        page.window.minimized = True
    return simple_icon_button(
        icon=ft.Icons.MINIMIZE, on_click=on_click
    )

def theme_button(
    page: ft.Page, *,
    on_click: Optional[ft.ControlEventHandler[ft.IconButton]] = None
) -> ft.AnimatedSwitcher:
    """
    An animated theme-swapping button.
    Provide a function to `on_click` for it to be called after
    the theme swap event.
    """
    def swap_theme(_):
        icon_btn: ft.IconButton = btn.content
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            icon_btn.icon = ft.Icons.LIGHT_MODE
        else:
            page.theme_mode = ft.ThemeMode.DARK
            icon_btn.icon = ft.Icons.DARK_MODE
        icon_btn.update()
        if on_click:
            on_click(_)
            
    if page.theme_mode == ft.ThemeMode.DARK:
        icon = ft.Icons.DARK_MODE
    else:
        icon = ft.Icons.LIGHT_MODE
    btn = ft.AnimatedSwitcher(
        content=ft.IconButton(
            icon=icon, icon_color=ft.Colors.PRIMARY,
            on_click=swap_theme
        ),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
        switch_out_curve=ft.AnimationCurve.BOUNCE_IN,
        duration=500, reverse_duration=200
    )
    return btn

def exit_button(
    page: ft.Page,
    on_click: Optional[ft.ControlEventHandler[ft.IconButton]] = None
) -> ft.IconButton:
    """
    A simple exit button. If `on_click` is `None`, then it will be set
    to a function that calls the `close()` method from the `page`'s
    `window`.
    """
    if on_click is None:
        on_click = lambda _: asyncio.create_task(
            coro=page.window.close(),
            name="Exit Button -> Closing Window"
        )
    return simple_icon_button(
        icon=ft.Icons.CLOSE,
        on_click=on_click
    )

def error_container(
    text: str,
    width: ft.Number = CARD_WIDTH / 4,
    height: ft.Number = CARD_HEIGHT / 4
) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, color=ft.Colors.ERROR),
        bgcolor=ft.Colors.ERROR_CONTAINER,
        border=ft.Border.all(2, ft.Colors.ON_ERROR_CONTAINER),
        padding=5, border_radius=15,
        width=width, height=height,
        alignment=ft.Alignment.CENTER
    )

def empty_card_container() -> ft.Container:
    return ft.Container(
        bgcolor=ft.Colors.SECONDARY,
        border=ft.Border.all(2, ft.Colors.ON_SECONDARY),
        border_radius=15,
        width=CARD_WIDTH / 4, height=CARD_HEIGHT / 4,
        alignment=ft.Alignment.CENTER
    )

def simple_anim_con(content: ft.Control) -> ft.AnimatedSwitcher:
    return ft.AnimatedSwitcher(
        content=content, duration=500, reverse_duration=250,
        transition=ft.AnimatedSwitcherTransition.SCALE,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN
    )

# | App Bar |
def preset_appbar(title: str, actions: list[ft.Control]) -> ft.AppBar:
    """
    An `AppBar` that has its `title` component wrapped in a `WindowDragArea`.
    """
    return ft.AppBar(
        title=ft.WindowDragArea(
            content=ft.Text(value=title, color=ft.Colors.PRIMARY),
            maximizable=False
        ),
        actions=actions,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions_padding=4, title_spacing=4,
        # shape=ft.RoundedRectangleBorder(radius=5),
        leading_width=8, leading=ft.Container()
    )
    
# | Loading Screen |
def loading_indicator() -> ft.ProgressRing:
    return ft.ProgressRing(
        color=ft.Colors.PRIMARY,
        stroke_width=4, width=100, height=100
    )

def loading_screen_container(
    loading_text: ft.Text, progress_ring: ft.ProgressRing
) -> ft.WindowDragArea:
    loading_controls = ft.WindowDragArea(
        content=ft.Container(
            content=ft.Column(
                controls=[loading_text, progress_ring],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16, run_alignment=16
            ),
            expand=True, alignment=ft.Alignment.CENTER,
            padding=8
        ),
        maximizable=False, expand=True
    )
    return loading_controls