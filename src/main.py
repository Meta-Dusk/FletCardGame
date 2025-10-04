import flet as ft


def before_main(page: ft.Page):
    page.title = "Flet Tests"

async def main(page: ft.Page):
    await page.window.center()
    
    counter = ft.Text("0", size=50, data=0)
    
    def increment_click(_):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()
        
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )
    
    page.add(ft.SafeArea(ft.Container(content=counter, alignment=ft.Alignment.CENTER), expand=True))


if __name__ == "__main__":
    ft.run(main=main, before_main=before_main)
