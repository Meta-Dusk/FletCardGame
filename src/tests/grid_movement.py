import flet as ft
import asyncio


def before_test(page: ft.Page):
    page.title = "Test 003"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.decoration = ft.BoxDecoration(
        bgcolor=ft.Colors.PRIMARY, border=ft.Border.all(5, ft.Colors.ON_PRIMARY)
    )
    page.theme_mode = ft.ThemeMode.DARK
    page.window.frameless = True


async def test(page: ft.Page):
    await page.window.center()

    # --- Character Movement ---
    async def move(x: float, y: float, duration_in_ms: int = 200):
        nonlocal character
        character.animate_position = ft.Animation(duration_in_ms, ft.AnimationCurve.EASE_IN_OUT)
        character.left += x
        character.top += y
        character.update()
        await asyncio.sleep(duration_in_ms / 1000)

    async def on_keyboard_event(e: ft.KeyboardEvent):
        step = 52
        if e.key == "Escape":
            await page.window.close()
        if e.key == "W":
            await move(0, -step)
        if e.key == "D":
            await move(step, 0)
        if e.key == "S":
            await move(0, step)
        if e.key == "A":
            await move(-step, 0)
        if e.key == " ":
            if page.theme_mode == ft.ThemeMode.DARK:
                page.theme_mode = ft.ThemeMode.LIGHT
            else:
                page.theme_mode = ft.ThemeMode.DARK

    # --- Tile Function ---
    def tile():
        return ft.Container(
            width=50, height=50, border_radius=5,
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            border=ft.Border.all(1, ft.Colors.ON_SECONDARY_CONTAINER),
        )

    # --- Create Grid Background ---
    rows = []
    grid_rows = 10
    grid_cols = 10

    for _ in range(grid_rows):
        row = ft.Row(
            controls=[tile() for _ in range(grid_cols)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=2,
        )
        rows.append(row)

    grid = ft.Column(
        controls=rows, spacing=2,
        alignment=ft.MainAxisAlignment.CENTER,
        height=52*10, width=52*10
    )

    # --- Character Container ---
    character = ft.Container(
        width=50, height=50, border_radius=5,
        border=ft.Border.all(2, ft.Colors.PRIMARY),
        bgcolor=ft.Colors.PRIMARY_CONTAINER,
        left=grid.width / 2,
        top=grid.height / 2,
        animate_position=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
    )

    # --- Stack layers everything ---
    stack = ft.Stack(
        controls=[grid, character],
        alignment=ft.Alignment.CENTER,
    )

    form = ft.WindowDragArea(content=stack, maximizable=False)

    page.on_keyboard_event = on_keyboard_event
    page.add(form)


if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)
