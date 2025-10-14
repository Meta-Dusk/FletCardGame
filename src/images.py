import flet as ft
from components import error_container, CARD_WIDTH, CARD_HEIGHT
from typing import Optional


class CardImage(ft.Image):
    """Custom Image widget with predefined size and error display."""
    def __init__(
        self, src: str, *,
        width: int | float = CARD_WIDTH / 4,
        height: int | float = CARD_HEIGHT / 4,
        error_content: Optional[ft.Control] = None,
        fit: ft.BoxFit = ft.BoxFit.CONTAIN,
        gapless_playback: bool = True
    ):
        super().__init__(
            src=src, width=width, height=height,
            error_content=error_content or error_container("SOURCE ERROR"),
            fit=fit, gapless_playback=gapless_playback
        )