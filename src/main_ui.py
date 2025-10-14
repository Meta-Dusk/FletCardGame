import flet as ft
from utilities import pick_then_del
from components import error_container, WHITE_CARDS_PATH
from cards import WHITE_CARDS_LIST, BLACK_CARDS_LIST, get_card_counterpart, CardComponent, get_card_value
from datatypes import CardType
from typing import Optional


async def main_ui(page: ft.Page) -> None:
    # == EVENTS ==
    def choose_random_card():
        nonlocal rnd_white_card, rnd_black_card
        rnd_white_card = pick_then_del(WHITE_CARDS_PATH, white_cards_list, black_cards_list)
        rnd_black_card = get_card_counterpart(rnd_white_card)
        
        
    # == SETUP ==
    white_cards_list = WHITE_CARDS_LIST
    black_cards_list = BLACK_CARDS_LIST
    rnd_white_card: Optional[str] = None
    rnd_black_card: Optional[str] = None
    choose_random_card()
    initial_card_value = get_card_value(
        rnd_white_card if page.theme_mode == ft.ThemeMode.DARK
        else rnd_black_card
    )
    print(f"Card Value: {initial_card_value}")
    initial_total_card_value: int = 0
    # if initial_card_value:
    #     if initial_card_value.type == CardType.FLEXIBLE:
    #         for val in initial_card_value.value:
    #             initial_total_card_value += val
    #     else:
    #         initial_total_card_value = initial_card_value.value[0]
    
    
    # == EVENT HANDLERS ==
    async def on_keyboard_event(e: ft.KeyboardEvent):
        if e.key == "Escape":
            print("Exiting app!")
            await page.window.close()
        if e.key == "`":
            nonlocal white_cards_list
            print("Clearing deck")
            white_cards_list = []
    
    def randomize_card(_):
        choose_random_card()
        if rnd_white_card is None:
            initial_card.replace_content(error_container("DECK EXHAUSTED"))
            test_btn.disabled = True
        else:
            initial_card.update_img(rnd_white_card)
        
    def hit_btn_on_click(_):
        print("[FletJack] Player chose to Hit.")
        choose_random_card()
        new_card = CardComponent(rnd_white_card)
        card_row.controls.append(new_card())
        card_row.update()
    
    def stand_btn_on_click(_):
        print("[FletJack] Player chose to Stand.")
    
    
    # == CONTROLS ==
    # Components
    initial_card = CardComponent(rnd_white_card)
    total_card_value = ft.Text(
        spans=[
            ft.TextSpan("Total Card Value: "),
            ft.TextSpan(initial_total_card_value)
        ], text_align=ft.TextAlign.CENTER,
        size=16, weight=ft.FontWeight.BOLD
    )
    
    # Buttons
    test_btn = ft.Button("Randomize Card", on_click=randomize_card)
    hit_btn = ft.Button("Hit", on_click=hit_btn_on_click)
    stand_btn = ft.Button("Stand", on_click=stand_btn_on_click)
    
    # Layout
    card_row = ft.Row(
        controls=[initial_card()],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.END,
        run_alignment=ft.MainAxisAlignment.CENTER,
        spacing=4, run_spacing=4
    )
    button_column = ft.Column(
        controls=[test_btn, hit_btn, stand_btn],
        alignment=ft.MainAxisAlignment.END,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        run_alignment=ft.MainAxisAlignment.CENTER,
        spacing=4, run_spacing=4
    )
    main_row = ft.Row(
        controls=[card_row, button_column, total_card_value],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.END,
        run_alignment=ft.MainAxisAlignment.CENTER,
        spacing=4, run_spacing=4
    )
    draggable_win = ft.WindowDragArea(
        content=main_row, expand=True, maximizable=False
    )
    
    # Page Stuff
    page.add(draggable_win)
    page.on_keyboard_event = on_keyboard_event
    await page.window.center()
    