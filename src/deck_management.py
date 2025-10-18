import random
import flet as ft
from datatypes import Card, CardType
from cards import CardComponent, get_card_counterpart, WHITE_CARDS_PATH, BLACK_CARDS_PATH
from utilities import format_card
from typing import Optional
from pathlib import Path


class Player:
    def __init__(
        self, page: ft.Page, deck: list[Card],
        *, is_dealer: bool = False, debug: bool = False,
        name: str = "", id: int = 0, money: float = 0
    ):
        self.page = page
        self.deck: list[Card] = deck
        self.is_dealer: bool = is_dealer
        self.debug: bool = debug
        self.name = name
        self.id = id
        self.money = money
        self.deck_in_hand: list[Card] = []
        self.total_card_value: int = 0
        self.rendered_cards: list[ft.Container] = []
        self.has_bet: bool = False
        self.current_bet: float = 0
        self.finished_turn: bool = False
        self.has_lost: bool = False
    
    def _get_path(self) -> Path:
        match self.page.theme_mode:
            case ft.ThemeMode.LIGHT:
                self._debug_msg("(_get_path) Returning black cards path.\n")
                return BLACK_CARDS_PATH
            case ft.ThemeMode.DARK:
                self._debug_msg("(_get_path) Returning white cards path.\n")
                return WHITE_CARDS_PATH
            case ft.ThemeMode.SYSTEM:
                raise TypeError("Make sure to always set a default ThemeMode for the page: DARK or LIGHT only.")
    
    def _get_card_src(self, card_src: str) -> str:
        return format_card(self._get_path(), card_src)
    
    def _debug_msg(self, msg: str) -> None:
        if self.debug:
            handle = f"{"[DEALER]" if self.is_dealer else "[PLAYER]"}"
            print(f"{handle} {msg}")
    
    def clear_deck(self) -> None:
        """Resets all values (except for `deck`)."""
        self._debug_msg("(clear_deck) Clearing deck and resetting all values.\n")
        self.deck_in_hand.clear()
        self.total_card_value = 0
        self.rendered_cards.clear()
    
    def calculate_hand_value(self, cards: list[Card]) -> int:
        """
        Calculates the best total hand value in Blackjack.
        Handles `FLEXIBLE` (Ace) cards intelligently as 1 or 11.
        """
        total = 0
        flexible_cards = 0
        
        # Step 1: Add the non-flexible cards first
        for card in cards:
            self._debug_msg(f"(calculate_hand_value) Found card in hand: {card}")
            if card.type == CardType.FLEXIBLE:
                self._debug_msg(f"(calculate_hand_value) Found a FLEXIBLE card in hand.")
                flexible_cards += 1
            else:
                total += card.value[0] if isinstance(card.value, list) else card.value
                
        # Step 2: Add Aces — start from 11, downgrade to 1 as needed
        for _ in range(flexible_cards):
            # Try to add 11 if it doesn't bust, otherwise add 1
            if total + 11 <= 21:
                total += 11
            else:
                total += 1
                
        self._debug_msg(f"(calculate_hand_value) Total Card Value is now: {total}\n")
        return total
    
    def draw_card(self) -> None:
        """
        Draw a card from the global deck, with additional steps:
        - Build card into a list of controls.
        - Update total card value.
        """
        drawn_card: Optional[Card] = None
        if len(self.deck) == 0:
            self._debug_msg("(draw_card) Global deck is empty.\n")
            return
        
        # Draw a card from global deck
        drawn_card = random.choice(self.deck)
        self._debug_msg(f"(draw_card) Drawn a card: {drawn_card}")
        
        # Remove drawn card from global deck
        print(f"Global deck size changed: {len(self.deck)} ->", end=" ")
        self.deck.remove(drawn_card)
        print(len(self.deck))
        
        # Build the drawn card
        self.deck_in_hand.append(drawn_card)
        self.build_card(drawn_card)
        self.update_cards()
        
        # Update total card value
        new_total_card_value = self.calculate_hand_value(self.deck_in_hand)
        self._debug_msg(f"(draw_card) Updating total card value: {self.total_card_value} -> {new_total_card_value}\n")
        self.total_card_value = new_total_card_value
    
    def update_cards(self) -> None:
        """Rebuild all rendered cards when theme mode changes."""
        if not self.deck_in_hand:
            return
        
        self._debug_msg("(update_cards) Updating cards for theme switch...")
        
        # Clear rendered UI lists
        self.rendered_cards.clear()
        
        # Rebuild each card from the player's current deck
        for card in self.deck_in_hand:
            # Get the correct card counterpart path (light <-> dark)
            invert: bool = False
            if (
                card.color == "White" and self.page.theme_mode == ft.ThemeMode.LIGHT or
                card.color == "Black" and self.page.theme_mode == ft.ThemeMode.DARK
            ):
                invert = True
            card_counterpart = get_card_counterpart(card.src, invert=invert)
            self._debug_msg(f"(update_cards) Original: {card}\n-> Counterpart: {card_counterpart}")
            
            # Create a new CardComponent for the counterpart card
            self.build_card(card_counterpart)
            
        self._debug_msg(f"(update_cards) Cards rebuilt for theme: {self.page.theme_mode}\n")
    
    def build_card(self, drawn_card: Card) -> None:
        new_card_src = self._get_card_src(drawn_card.src)
        self._debug_msg(f"(build_card) Building a new card with src: {new_card_src}\n")
        new_card = CardComponent(new_card_src)
        self.rendered_cards.append(new_card())


# === CLASS PREVIEW ===
from cards import WHITE_CARDS_LIST
from components import preset_appbar, theme_button, exit_button, simple_button
from layouts import preset_win_drag_area
from notifications import simple_notification, error_notif

def before_test(page: ft.Page):
    page.title = "Deck Management Test"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.title_bar_hidden = True
    page.window.min_width = 940
    page.window.min_height = 140

async def test(page: ft.Page):
    # Events
    def update_text_displays() -> None:
        deck_counter_text.spans[1].text = len(white_cards_list)
        deck_counter_text.update()
        if player.total_card_value > 21:
            container: ft.Container = card_val_total.content
            container.bgcolor = ft.Colors.ERROR_CONTAINER
            text: ft.Text = container.content
            text.color = ft.Colors.ERROR
            card_val_total.update()
            error_notif(page, "Your total card value has went over 21!")
        elif player.total_card_value == 21:
            container: ft.Container = card_val_total.content
            container.bgcolor = ft.Colors.INVERSE_SURFACE
            text: ft.Text = container.content
            text.color = ft.Colors.INVERSE_PRIMARY
            card_val_total.update()
            simple_notification(page, "You got a Black Jack!", duration=2000)
        else:
            container: ft.Container = card_val_total.content
            container.bgcolor = ft.Colors.PRIMARY_CONTAINER
            text: ft.Text = container.content
            text.color = ft.Colors.PRIMARY
            card_val_total.update()
        card_val_total_text.spans[1].text = player.total_card_value
        card_val_total_text.update()
    
    # Event Handlers
    def fab_on_click(_) -> None:
        player.draw_card()
        card_row.update()
        update_text_displays()
    
    def tb_on_click(_) -> None:
        player.update_cards()
        card_row.update()
    
    def cdb_on_click(_) -> None:
        player.clear_deck()
        card_row.update()
        update_text_displays()
    
    def rdb_on_click(_) -> None:
        nonlocal white_cards_list
        white_cards_list = WHITE_CARDS_LIST.copy()
        update_text_displays()
    
    # Setup
    white_cards_list = WHITE_CARDS_LIST.copy()
    player = Player(page, white_cards_list, debug=True)
    
    # Displays
    card_val_total_text = ft.Text(
        spans=[
            ft.TextSpan("Total Card Value: "),
            ft.TextSpan(player.total_card_value)
        ], color=ft.Colors.PRIMARY
    )
    card_val_total = ft.Container(
        ft.Container(
            card_val_total_text, padding=8, alignment=ft.Alignment.CENTER,
            border_radius=8, bgcolor=ft.Colors.PRIMARY_CONTAINER
        ), padding=8
    )
    
    deck_counter_text = ft.Text(
        spans=[
            ft.TextSpan("Cards in Deck: "),
            ft.TextSpan(len(white_cards_list))
        ], color=ft.Colors.SECONDARY
    )
    deck_counter = ft.Container(
        ft.Container(
            deck_counter_text, padding=8, alignment=ft.Alignment.CENTER,
            border_radius=8, bgcolor=ft.Colors.SECONDARY_CONTAINER
        ), padding=8
    )
    
    # Buttons
    theme_btn = theme_button(page, on_click=tb_on_click)
    exit_btn = exit_button(page)
    clear_deck_btn = simple_button(
        "Clear Hand", ft.Icons.CREDIT_CARD_OFF, on_click=cdb_on_click
    )
    reset_deck_btn = ft.Container(simple_button(
        "Reset Deck", ft.Icons.CREDIT_CARD, on_click=rdb_on_click
    ), padding=8)
    
    # App Bar
    appbar_actions = [
        card_val_total, deck_counter,
        clear_deck_btn, reset_deck_btn,
        theme_btn, exit_btn
    ]
    appbar = preset_appbar("Deck Management Test", appbar_actions)
    
    # Layouts
    card_row = ft.ResponsiveRow(
        player.rendered_cards, spacing=4, run_spacing=4,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )
    form = preset_win_drag_area(card_row)
    
    # Page Stuff
    page.appbar = appbar
    page.floating_action_button = ft.FloatingActionButton(
        "Draw Card", ft.Icons.ADD_CARD,
        on_click=fab_on_click
    )
    page.add(form)
    # page.on_resize = lambda e: print(e)
    await page.window.center()
    
if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)