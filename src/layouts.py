import flet as ft


def preset_win_drag_area(content: ft.Control) -> ft.WindowDragArea:
    """The main window drag area that the main UI uses."""
    return ft.WindowDragArea(
        content=content, maximizable=False, expand=True,
        # opacity=0, offset=ft.Offset(0, -1),
        # animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        # animate_offset=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    )
    
def default_row(
    controls: list[ft.Control], *,
    alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER,
    vertical_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER,
    run_alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER,
    spacing: ft.Number = 8, run_spacing:ft.Number = 8
) -> ft.Row:
    return ft.Row(
        controls, alignment, vertical_alignment, spacing,
        run_alignment=run_alignment, run_spacing=run_spacing
    )

def default_column(
    controls: list[ft.Control], *,
    alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER,
    horizontal_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER,
    run_alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER,
    spacing: ft.Number = 8, run_spacing:ft.Number = 8
) -> ft.Column:
    return ft.Column(
        controls, alignment, horizontal_alignment, spacing,
        run_alignment=run_alignment, run_spacing=run_spacing
    )