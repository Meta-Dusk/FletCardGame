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
        name: str = "", id: int = 0
    ):
        self.page = page
        self.is_dealer: bool = is_dealer
        self.debug: bool = debug
        self.deck: list[Card] = deck
        self.deck_in_hand: list[Card] = []
        self.total_card_value: int = 0
        self.rendered_cards: list[ft.Container] = []
        self.has_bet: bool = False
        self.money: float = 0
        self.name = name
        self.id = id
    
    def _get_path(self) -> Path:
        match self.page.theme_mode:
            case ft.ThemeMode.LIGHT:
                self._debug_msg("(_get_path) Returning black cards path.\n")
                return BLACK_CARDS_PATH
            case ft.ThemeMode.DARK:
                self._debug_msg("(_get_path) Returning white cards path.\n")
                return WHITE_CARDS_PATH
    
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
            self._debug_msg("\n(draw_card) Global deck is empty.")
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

def before_test(page: ft.Page):
    page.title = "Deck Management Test"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.title_bar_hidden = True

async def test(page: ft.Page):
    # Events
    def update_text_displays():
        deck_counter_text.spans[1].text = len(white_cards_list)
        deck_counter_text.update()
        if player.total_card_value > 21:
            container: ft.Container = card_val_total.content
            container.bgcolor = ft.Colors.ERROR_CONTAINER
            text: ft.Text = container.content
            text.color = ft.Colors.ERROR
            card_val_total.update()
        elif player.total_card_value == 21:
            container: ft.Container = card_val_total.content
            container.bgcolor = ft.Colors.INVERSE_SURFACE
            text: ft.Text = container.content
            text.color = ft.Colors.INVERSE_PRIMARY
            card_val_total.update()
        else:
            container: ft.Container = card_val_total.content
            container.bgcolor = ft.Colors.PRIMARY_CONTAINER
            text: ft.Text = container.content
            text.color = ft.Colors.PRIMARY
            card_val_total.update()
        card_val_total_text.spans[1].text = player.total_card_value
        card_val_total_text.update()
    
    # Event Handlers
    def fab_on_click(_):
        player.draw_card()
        card_row.update()
        update_text_displays()
    
    def theme_btn_on_click(_):
        player.update_cards()
        card_row.update()
    
    def cd_btn_on_click(_):
        player.clear_deck()
        card_row.update()
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
        ], color=ft.Colors.TERTIARY
    )
    deck_counter = ft.Container(
        ft.Container(
            deck_counter_text, padding=8, alignment=ft.Alignment.CENTER,
            border_radius=8, bgcolor=ft.Colors.TERTIARY_CONTAINER
        ), padding=8
    )
    
    # Buttons
    theme_btn = theme_button(page, on_click=theme_btn_on_click)
    exit_btn = exit_button(page)
    clear_deck_btn = simple_button(
        "Clear Hand", ft.Icons.CREDIT_CARD_OFF, on_click=cd_btn_on_click
    )
    
    # App Bar
    appbar_actions = [
        card_val_total, deck_counter,
        clear_deck_btn, theme_btn, exit_btn
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
    await page.window.center()
    
if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)