import flet as ft
from setup import before_main_ui
from main_ui import main_ui
from deck_management import test, before_test


async def main(page: ft.Page):
    await test(page)
    
def before_main(page: ft.Page):
    before_test(page)


if __name__ == "__main__":
    ft.run(main=main, before_main=before_main)
