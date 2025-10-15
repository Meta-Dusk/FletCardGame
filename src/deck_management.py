import random
import flet as ft
from datatypes import Card, CardType
from cards import CardComponent, get_card_counterpart, WHITE_CARDS_VALUES, WHITE_CARDS_PATH, BLACK_CARDS_PATH
from utilities import format_card
from components import preset_appbar, theme_button, exit_button
from layouts import preset_win_drag_area
from typing import Optional
from pathlib import Path


class Player:
    def __init__(
        self, page: ft.Page, global_deck: list[Card],
        *, is_dealer: bool = False, debug: bool = False
    ):
        self.page = page
        self.is_dealer: bool = is_dealer
        self.debug: bool = debug
        self.global_deck: list[Card] = global_deck
        self.deck_in_hand: list[Card] = []
        self.total_card_value: int = 0
        self.rendered_cards: list[ft.Container] = []
        self.card_list_data: list[CardComponent] = []
    
    def _get_path(self) -> Path:
        match self.page.theme_mode:
            case ft.ThemeMode.LIGHT:
                return BLACK_CARDS_PATH
            case ft.ThemeMode.DARK:
                return WHITE_CARDS_PATH
    
    def _get_card_src(self, card_src: str) -> str:
        return format_card(self._get_path(), card_src)
    
    def _debug_msg(self, msg: str) -> None:
        if self.debug:
            handle = f"{"[DEALER]" if self.is_dealer else "[PLAYER]"}"
            print(f"{handle} {msg}")
    
    def calculate_hand_value(self, cards: list[Card]) -> int:
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
    
    def draw_card(self) -> None:
        """
        Draw a card from the global deck, with additional steps:
        - Build card into a list of controls.
        - Update total card value.
        """
        drawn_card: Optional[Card] = None
        if len(self.global_deck) == 0:
            self._debug_msg("Global deck is empty.")
            return
        
        # Draw a card from global deck
        drawn_card = random.choice(self.global_deck)
        self._debug_msg(f"Drawn a card: {drawn_card}")
        
        # Remove drawn card from global deck
        print(f"Global deck size changed: {len(self.global_deck)} ->", end=" ")
        self.global_deck.remove(drawn_card)
        print(len(self.global_deck))
        
        # Build the drawn card
        self.deck_in_hand.append(drawn_card)
        self.build_card(drawn_card)
        
        # Update total card value
        new_total_card_value = self.calculate_hand_value(self.deck_in_hand)
        self._debug_msg(f"Updating total card value: {self.total_card_value} -> {new_total_card_value}")
        self.total_card_value = new_total_card_value
    
    def update_card(self) -> None:
        """Rebuild cards when theme mode changes (light <-> dark)."""
        if not self.card_list_data:
            return
        
        self._debug_msg(f"Card List Data: {self.card_list_data}")
        for card in self.card_list_data:
            card_counterpart = get_card_counterpart(card.src, invert=True)
            self._debug_msg(f"src: {card.src}")
            self._debug_msg(f"Card Counterpart (inv): {card_counterpart}")
        
        self.rendered_cards.clear()
        total_cards = self.card_list_data.copy()
        self.card_list_data.clear()
        for _ in range(len(total_cards)):
            self.build_card(card_counterpart)
        
        self._debug_msg(f"Cards updated for theme: {self.page.theme_mode}")
    
    def build_card(self, drawn_card: Card) -> None:
        new_card_src = self._get_card_src(drawn_card.src)
        self._debug_msg(f"Building a new card with src: {new_card_src}")
        new_card = CardComponent(new_card_src)
        self.rendered_cards.append(new_card())
        self.card_list_data.append(new_card)


def before_test(page: ft.Page):
    page.title = "Deck Management Test"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.title_bar_hidden = True

async def test(page: ft.Page):
    # Event Handlers
    def fab_on_click(_):
        player.draw_card()
        card_row.update()
    
    def theme_btn_on_click(_):
        player.update_card()
        card_row.update()
    
    # Setup
    white_cards_list = WHITE_CARDS_VALUES.copy()
    player = Player(page, white_cards_list)
    dealer = Player(page, white_cards_list, is_dealer=True)
    
    # Buttons
    theme_btn = theme_button(page, on_click=theme_btn_on_click)
    exit_btn = exit_button(page)
    
    # App Bar
    appbar_actions = [theme_btn, exit_btn]
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
    await page.window.center()
    
if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)