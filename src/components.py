import flet as ft
from pathlib import Path


ASSETS_PATH = Path(__file__).resolve().parent / "assets"
WHITE_CARDS_PATH = ASSETS_PATH / "images" / "cards" / "white"
BLACK_CARDS_PATH = ASSETS_PATH / "images" / "cards" / "black"
CARD_WIDTH = 655
CARD_HEIGHT = 930


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
    