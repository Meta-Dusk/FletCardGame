import flet as ft


def before_test(page: ft.Page):
    page.title = "Test 002"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

async def test(page: ft.Page):
    await page.window.center()
    drag_target_color = ft.Colors.BLUE_GREY_100
    
    def drag_will_accept(e: ft.DragWillAcceptEvent):
        e.control.content.border = ft.Border.all(
            width=2,
            color=e.src.content.bgcolor if e.control.group == "color" else ft.Colors.ERROR
        )
        e.control.content.bgcolor = ft.Colors.with_opacity(0.5, drag_target_color)
        e.control.update()

    def drag_accept(e: ft.DragTargetEvent):
        nonlocal drag_target_color
        drag_target_color = e.src.content.bgcolor
        e.control.content.bgcolor = drag_target_color
        e.control.content.border = None
        # e.src.visible = False
        e.src.update()
        e.control.update()

    def drag_leave(e: ft.DragTargetLeaveEvent):
        e.control.content.bgcolor = drag_target_color
        e.control.content.border = None
        e.control.update()

    page.add(
        ft.Row([
            ft.Column([
                ft.Draggable(
                    group="color",
                    content=ft.Container(
                        width=50, height=50,
                        bgcolor=ft.Colors.CYAN,
                        border_radius=5,
                    ),
                    content_feedback=ft.Container(
                        width=50, height=50,
                        bgcolor=ft.Colors.CYAN,
                        border_radius=3,
                    ),
                    max_simultaneous_drags=1,
                    content_when_dragging=ft.Container()
                ),
                ft.Draggable(
                    group="color",
                    content=ft.Container(
                        width=50, height=50,
                        bgcolor=ft.Colors.YELLOW,
                        border_radius=5,
                    ),
                ),
                ft.Draggable(
                    group="color",
                    content=ft.Container(
                        width=50, height=50,
                        bgcolor=ft.Colors.GREEN,
                        border_radius=5,
                    ),
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(width=100),
            ft.DragTarget(
                group="color",
                content=ft.Container(
                    width=50, height=50,
                    bgcolor=drag_target_color,
                    border_radius=5,
                ),
                on_will_accept=drag_will_accept,
                on_accept=drag_accept,
                on_leave=drag_leave,
            ),
        ], expand=True, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
    )
    

if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)