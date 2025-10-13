import flet as ft
from setup import before_main_ui
from cards import test


async def main(page: ft.Page):
    await test(page)
    
def before_main(page: ft.Page):
    before_main_ui(page)


if __name__ == "__main__":
    ft.run(main=main, before_main=before_main)
