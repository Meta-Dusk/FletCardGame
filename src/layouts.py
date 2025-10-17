import flet as ft


def preset_win_drag_area(content: ft.Control) -> ft.WindowDragArea:
    """The main window drag area that the main UI uses."""
    return ft.WindowDragArea(
        content=content, maximizable=False, expand=True,
        # opacity=0, offset=ft.Offset(0, -1),
        # animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        # animate_offset=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    )
    
class DefaultRow(ft.Row):
    def __init__(
        self, controls: list[ft.Control], *,
        alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER,
        vertical_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER,
        run_alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER,
        spacing: ft.Number = 8, run_spacing:ft.Number = 8
    ):
        super().__init__(
            controls=controls, alignment=alignment, vertical_alignment=vertical_alignment,
            run_alignment=run_alignment, spacing=spacing, run_spacing=run_spacing
        )