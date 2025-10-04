import flet as ft


def before_test(page: ft.Page):
    page.title = "Test 001"

async def test(page: ft.Page):
    await page.window.center()
    
    def get_padding(ctrl: ft.Container):
        """Return (left, right, top, bottom) padding values for a container."""
        p = ctrl.padding
        if p is None:
            return 0, 0, 0, 0
        if isinstance(p, (int, float)):
            return p, p, p, p
        # p is ft.Padding
        return p.left, p.right, p.top, p.bottom

    def get_container_width(ctrl: ft.Container) -> float:
        left, right, _, _ = get_padding(ctrl)
        return ctrl.width + left + right

    def get_container_height(ctrl: ft.Container) -> float:
        _, _, top, bottom = get_padding(ctrl)
        return ctrl.height + top + bottom
    
    def limit_between(
        min_val: float | int,
        max_val: float | int,
        value: float | int
    ) -> float:
        return float(min(max_val, max(min_val, value)))
    
    def bring_to_front(ctrl: ft.Control):
        if ctrl in form.controls:
            form.controls.remove(ctrl)
            form.controls.append(ctrl)
            form.update()
    
    def on_tap(e: ft.DragStartEvent):
        bring_to_front(e.control)
    
    def on_pan_update(e: ft.DragUpdateEvent):
        gd: ft.GestureDetector = e.control
        gd_ctrl: ft.Container = gd.content
        gd.left = limit_between(
            min_val=0,
            max_val=page.window.width - get_container_width(gd_ctrl) + page.padding.left,
            value=gd.left + e.local_delta.x,
        )
        gd.top = limit_between(
            min_val=0,
            max_val=page.window.height - get_container_height(gd_ctrl) - page.padding.bottom,
            value=gd.top + e.local_delta.y,
        )
        gd_ctrl.data = {"left": gd.left, "top": gd.top}
        gd.update()

    def on_resize(e: ft.PageResizeEvent):
        # Clamp every draggable container in the Stack
        for ctrl in form.controls:
            if not isinstance(ctrl, ft.GestureDetector):
                return
            gd_ctrl: ft.Container = ctrl.content
            left = limit_between(
                min_val=0,
                max_val=e.width - get_container_width(gd_ctrl) + page.padding.right,
                value=gd_ctrl.data.get("left", ctrl.left or 0) if gd_ctrl.data else 0,
            )
            top = limit_between(
                min_val=0,
                max_val=e.height - get_container_height(gd_ctrl) - page.padding.bottom,
                value=gd_ctrl.data.get("top", ctrl.top or 0) if gd_ctrl.data else 0,
            )
            if (left, top) != (ctrl.left, ctrl.top):
                ctrl.left, ctrl.top = left, top
                gd_ctrl.data = {"left": left, "top": top}
                ctrl.update()

    # Add multiple draggable containers
    draggable1 = ft.GestureDetector(
        content=ft.Container(
            content=ft.Text("Drag Me 1!", color=ft.Colors.ON_PRIMARY_CONTAINER, text_align=ft.TextAlign.CENTER),
            bgcolor=ft.Colors.PRIMARY_CONTAINER, padding=20, border_radius=20,
            width=100, height=70, alignment=ft.Alignment.CENTER,
            data={"left": 0, "right": 0}, border=ft.Border.all(2, ft.Colors.PRIMARY)
        ),
        left=0, top=0, drag_interval=10,
        on_pan_update=on_pan_update,
        on_tap=on_tap,
        mouse_cursor=ft.MouseCursor.MOVE,
    )
    
    draggable2 = ft.GestureDetector(
        content=ft.Container(
            content=ft.Text("Drag Me 2!", color=ft.Colors.ON_SECONDARY_CONTAINER, text_align=ft.TextAlign.CENTER),
            bgcolor=ft.Colors.SECONDARY_CONTAINER, padding=20, border_radius=20,
            width=120, height=80, alignment=ft.Alignment.CENTER,
            data={"left": 200, "right": 100}, border=ft.Border.all(2, ft.Colors.SECONDARY)
        ),
        left=200, top=100, drag_interval=10,
        on_pan_update=on_pan_update,
        on_tap=on_tap,
        mouse_cursor=ft.MouseCursor.MOVE,
    )

    form = ft.Stack(controls=[draggable1, draggable2])

    page.on_resize = on_resize
    page.add(form)


if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)
