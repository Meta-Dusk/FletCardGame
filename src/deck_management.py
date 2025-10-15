import random
import flet as ft
from datatypes import Card, CardType
from cards import CardComponent, get_card_counterpart, WHITE_CARDS_VALUES, WHITE_CARDS_PATH, BLACK_CARDS_PATH
from utilities import format_card
from typing import Optional
from pathlib import Path


class Player:
    def __init__(
        self, page: ft.Page, global_deck: list[Card],
        *, is_dealer: bool = False
    ):
        self.page = page
        self.is_dealer: bool = is_dealer
        self.global_deck: list[Card] = global_deck
        self.deck_in_hand: list[Card] = []
        self.total_card_value: int = 0
        self.rendered_cards: list[ft.Container] = []
        self.card_list_data: list[CardComponent] = []
    
    def _get_path(self) -> Path:
        match self.page.theme_mode:
            case ft.ThemeMode.LIGHT:
                return BLACK_CARDS_PATH
            case ft.ThemeMode.DARK | _:
                return WHITE_CARDS_PATH
    
    def _get_card_src(self, card_src: str) -> str:
        return format_card(self._get_path(), card_src)
    
    def _debug_msg(self, msg: str) -> None:
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
        new_card_src = format_card(self._get_path(), drawn_card.src)
        new_card = CardComponent(new_card_src)
        self.rendered_cards.append(new_card())
        
        # Update total card value
        new_total_card_value = self.calculate_hand_value(self.deck_in_hand)
        self._debug_msg(f"Updating total card value: {self.total_card_value} -> {new_total_card_value}")
        self.total_card_value = new_total_card_value
    
    def update_card(self) -> None:
        # Update card color depending on page.theme_mode
        raise NotImplementedError("Update Card method hasn't been implemented yet.")
    
    def build_cards(self, rebuild: bool = False) -> None:
        if len(self.card_list_data) == 0:
            return
        
        if rebuild:
            self.rendered_cards.clear()
            for card in self.card_list_data:
                self.rendered_cards.append(card())
            return
        
        for card in self.card_list_data:
            built_card = card()
            if built_card not in self.rendered_cards:
                self.rendered_cards.append(built_card)


def test(page: ft.Page):
    page.title = "Deck Management Test"
    
    def fab_on_click(_):
        player1.draw_card()
        card_row.update()
    
    white_cards_list = WHITE_CARDS_VALUES.copy()
    player1 = Player(page, white_cards_list)
    
    card_row = ft.ResponsiveRow(
        player1.rendered_cards, spacing=4, run_spacing=4,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )
    
    page.add(card_row)
    page.floating_action_button = ft.FloatingActionButton(
        "Draw Card", ft.Icons.ADD_CARD,
        on_click=fab_on_click
    )
    
if __name__ == "__main__":
    ft.run(test)