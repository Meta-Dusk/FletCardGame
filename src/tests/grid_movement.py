import flet as ft
import asyncio


def swap_theme(page: ft.Page):
    if page.theme_mode == ft.ThemeMode.DARK:
        page.theme_mode = ft.ThemeMode.LIGHT
    else:
        page.theme_mode = ft.ThemeMode.DARK
        

def before_test(page: ft.Page):
    page.title = "Test 003"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.decoration = ft.BoxDecoration(
        bgcolor=ft.Colors.PRIMARY, border=ft.Border.all(5, ft.Colors.ON_PRIMARY)
    )
    page.theme_mode = ft.ThemeMode.DARK
    page.window.title_bar_hidden = True
    
async def test(page: ft.Page):
    await page.window.center()
    
    # --- Character Movement ---
    async def move(x: float, y: float, duration_in_ms: int = 200):
        nonlocal character
        character.animate_position = ft.Animation(duration_in_ms, ft.AnimationCurve.EASE_IN_OUT)
        if (character.left != 0 or x > 0) and ((character.left + x) != grid.width or x < 0):
            character.left += x
        if (character.top != 0 or y > 0) and ((character.top + y) != grid.height or y < 0):
            character.top += y
        character.update()
        print(f"Player Position: ({character.left}, {character.top}).")
        await asyncio.sleep(duration_in_ms / 1000)
        
    async def on_keyboard_event(e: ft.KeyboardEvent):
        step = character.width + character.border.left.width
        print(f"Step size: {step};", end=" ")
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
            swap_theme(page)
            
    # --- Tile Function ---
    def tile():
        return ft.Container(
            width=50, height=50, border_radius=5,
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            border=ft.Border.all(2, ft.Colors.with_opacity(0.5, ft.Colors.ON_SECONDARY_CONTAINER)),
        )
        
    # --- Create Grid Background ---
    rows = []
    grid_rows = 10
    grid_cols = 10
    
    for _ in range(grid_rows):
        row = ft.Row(
            controls=[tile() for _ in range(grid_cols)],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=temp_tile.border.left.width,
        )
        rows.append(row)
    
    temp_tile = tile()
    tile_size = temp_tile.width + temp_tile.border.left.width
    grid = ft.Column(
        controls=rows, spacing=temp_tile.border.left.width,
        alignment=ft.MainAxisAlignment.CENTER,
        width=tile_size * grid_rows,
        height=tile_size * grid_cols
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
    print(f"Map Size: ({grid.width}, {grid.height}), Player Size: ({character.width}, {character.height})")
    
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
    