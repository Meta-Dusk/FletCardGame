import flet as ft
from utilities import pick_then_del
from components import WHITE_CARDS_PATH, CARD_WIDTH, CARD_HEIGHT
from cards import WHITE_CARDS_VALUES, BLACK_CARDS_VALUES, get_card_counterpart, CardComponent, get_card_value
from datatypes import CardType, Card
from typing import Optional


async def main_ui(page: ft.Page) -> None:
    # == EVENTS ==
    def choose_random_card():
        nonlocal current_white_card, current_black_card, w_cards_in_hand, b_cards_in_hand
        current_white_card = pick_then_del(WHITE_CARDS_PATH, white_cards_list, black_cards_list)
        current_black_card = get_card_counterpart(current_white_card)
        w_cards_in_hand.append(get_card_value(current_white_card))
        b_cards_in_hand.append(get_card_value(current_black_card))
    
    def dealer_pick_card():
        nonlocal w_dealer_cards, b_dealer_cards
        c_w_dealer_card = pick_then_del(WHITE_CARDS_PATH, white_cards_list, black_cards_list)
        c_b_dealer_card = get_card_counterpart(c_w_dealer_card)
        w_dealer_cards.append(get_card_value(c_w_dealer_card))
        b_dealer_cards.append(get_card_value(c_b_dealer_card))
        print(f"Dealer's hand: {w_dealer_cards}")
        
    
    def calculate_hand_value(cards: list[Card]) -> int:
        """
        Calculates the best total hand value in Blackjack.
        - Adds card values from each card's `.value` list.
        - Treats `FLEXIBLE` (Ace) cards intelligently as 11 or 1.
        """
        total = 0
        flexible_cards = 0
        
        # Step 1: Add base values (use the *highest* by default for flexible cards)
        for card in cards:
            if card.type == CardType.FLEXIBLE:
                flexible_cards += 1
                total += max(card.value)  # Usually 11
            else:
                total += card.value[0] if isinstance(card.value, list) else card.value

        # Step 2: Adjust Aces/FLEXIBLEs if total > 21
        while total > 21 and flexible_cards > 0:
            total -= 10  # Convert an Ace from 11 to 1
            flexible_cards -= 1

        return total
    
    def update_total_card_value():
        total_card_value = calculate_hand_value(w_cards_in_hand)
        total_card_value_text.spans[1].text = total_card_value
        total_card_value_text.update()
    
    # == SETUP ==
    # TODO: Improve setup by making these classes instead.
    white_cards_list = WHITE_CARDS_VALUES.copy()
    black_cards_list = BLACK_CARDS_VALUES.copy()
    w_cards_in_hand: list[Card] = []
    b_cards_in_hand: list[Card] = []
    current_white_card: Optional[str] = None
    current_black_card: Optional[str] = None
    choose_random_card()
    total_card_value = calculate_hand_value(w_cards_in_hand)
    
    # TODO: Starting hand should be 2 for both dealer and player.
    w_dealer_cards: list[Card] = []
    b_dealer_cards: list[Card] = []
    c_w_dealer_card: Optional[str] = None
    c_b_dealer_card: Optional[str] = None
    dealer_pick_card()
    
    
    # == EVENT HANDLERS ==
    async def on_keyboard_event(e: ft.KeyboardEvent):
        match e.key:
            case "Escape":
                print("Exiting app!")
                await page.window.close()
            case "`":
                nonlocal w_cards_in_hand, b_cards_in_hand, total_card_value
                print("Clearing current deck")
                card_row.controls.clear()
                card_row.update()
                w_cards_in_hand.clear()
                b_cards_in_hand.clear()
                update_total_card_value()
        
    def hit_btn_on_click(_):
        nonlocal total_card_value
        print("[FletJack] Player chose to Hit.")
        choose_random_card()
        update_total_card_value()
        new_card = CardComponent(current_white_card)
        card_row.controls.append(new_card())
        card_row.update()
    
    def stand_btn_on_click(_):
        print("[FletJack] Player chose to Stand.")
    
    
    # == CONTROLS ==
    # Components
    initial_card = CardComponent(current_white_card)
    total_card_value_text = ft.Text(
        spans=[
            ft.TextSpan("Total Card Value: "),
            ft.TextSpan(total_card_value)
        ], text_align=ft.TextAlign.CENTER,
        size=16, weight=ft.FontWeight.BOLD
    )
    
    # Buttons
    hit_btn = ft.Button("Hit", on_click=hit_btn_on_click)
    stand_btn = ft.Button("Stand", on_click=stand_btn_on_click)
    
    # Layout
    card_row = ft.Row(
        controls=[initial_card()],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.END,
        run_alignment=ft.MainAxisAlignment.CENTER,
        spacing=4, run_spacing=4, scroll=ft.ScrollMode.ALWAYS,
        width=CARD_WIDTH, height=CARD_HEIGHT
    )
    button_column = ft.Column(
        controls=[hit_btn, stand_btn, total_card_value_text],
        alignment=ft.MainAxisAlignment.END,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        run_alignment=ft.MainAxisAlignment.CENTER,
        spacing=4, run_spacing=4
    )
    main_row = ft.Row(
        controls=[card_row, button_column],
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
    