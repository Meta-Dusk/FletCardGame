import flet as ft
import asyncio


def before_test(page: ft.Page):
    page.title = "Test 005"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.decoration = ft.BoxDecoration(
        bgcolor=ft.Colors.PRIMARY, border=ft.Border.all(5, ft.Colors.ON_PRIMARY)
    )
    
    page.window.frameless = True
    
async def test(page: ft.Page):
    await page.window.center()
    
    async def on_keyboard_event(e: ft.KeyboardEvent):
        if e.key == "Escape":
            await page.window.close()
    
    async def on_click(_):
        await loop()
        
    async def loop():
        duration: float = 1
        while True:
            text: ft.Text = test_gen.content
            text.scale = ft.Scale(0.95)
            text.opacity = 0.7
            text.update()
            await asyncio.sleep(duration)
            text.scale = ft.Scale(1)
            text.opacity = 1
            text.update()
            await asyncio.sleep(duration)
            number_display.value += 1
            number_display.update()
            
    
    test_gen = ft.Container(
        content=ft.Text(
            value="🌲🪚", size=100,
            animate_scale=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
            animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
            scale=ft.Scale(1), opacity=1,
            text_align=ft.TextAlign.CENTER,
        ),
        alignment=ft.Alignment.BOTTOM_CENTER,
        on_click=on_click
    )
    number_display = ft.Text(value=0, size=100, text_align=ft.TextAlign.CENTER)
    form_row = ft.Row(
        controls=[test_gen, number_display],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.END
    )
    form = ft.WindowDragArea(content=form_row, maximizable=False, expand=True)
    
    page.add(form)
    page.on_keyboard_event = on_keyboard_event

if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)