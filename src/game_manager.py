import flet as ft
from datatypes import Card
from deck_management import Player
from enum import Enum


class GameState(Enum):
    WAITING_PHASE = "Waiting Phase"
    BETTING_PHASE = "Betting Phase"
    GAME_PHASE = "Game Phase"
    DEALER_PHASE = "Dealer Phase"
    GAME_OVER = "Game Over"
    
# TODO: Finish the implementation of the BlackJack class here
class BlackJackGame:
    """Handles everything related to the gameplay loop."""
    def __init__(
        self, page: ft.Page, reference_deck: list[Card], *,
        player_count: int = 1, deck_multiplier: int = 1,
        minimum_bet: float = 1000, win_multiplier: float = 2.0,
        black_jack_multiplier: float = 2.5, debug: bool = True,
        starting_budget: float = 1000
    ):
        self.page = page
        self.reference_deck = reference_deck
        self.player_count = player_count
        self.deck_multiplier = deck_multiplier
        self.minimum_bet = minimum_bet
        self.win_multiplier = win_multiplier
        self.black_jack_multiplier = black_jack_multiplier
        self.debug = debug
        self.starting_budget = starting_budget
        self.local_deck: list[Card] = []
        self.player_list: list[Player] = []
        self.dealer: Player = None
        self.game_round: int = 0
        self.game_start: bool = False
        self.game_state: GameState = GameState.WAITING_PHASE
    
    def _debug_msg(self, msg: str) -> None:
        if self.debug:
            print(f"[BlackJackGame] {msg}")
    
    def _copy_deck(self) -> None:
        """
        Copies the `reference_deck` into the `local_deck` for _n_ times provided
        by the `deck_multiplier`.
        """
        if len(self.local_deck) > 0:
            self._debug_msg("(_copy_deck) Clearing local deck!")
            self.local_deck.clear()
            
        _msg = "deck" if self.deck_multiplier == 1 else "decks"
        self._debug_msg(f"(_copy_deck) Adding {self.deck_multiplier} {_msg} to the local deck.")
        for i in range(self.deck_multiplier):
            self._debug_msg(f"(_copy_deck) Adding the entire reference deck to local deck (Iteration {i+1}).")
            self.local_deck.extend(self.reference_deck)
        self._debug_msg(f"(_copy_deck) Local Deck size is now {self.local_deck_size()}. Operation finished.\n")
    
    def local_deck_size(self) -> int:
        return len(self.local_deck)
    
    def _make_players(self) -> None:
        """
        Makes a list of new players to be appended into the `player_list` based
        on `player_count`. Also makes a `dealer`.
        """
        for i in range(self.player_count):
            self._debug_msg(f"(_make_players) Making Player {i+1}.")
            player = Player(
                self.page, self.local_deck, debug=self.debug,
                id=i+1, name=f"Player {i+1}", money=self.starting_budget
            )
            self.player_list.append(player)
            
        self._debug_msg("(_make_players) Making the Dealer.")
        dealer = Player(self.page, self.local_deck, is_dealer=True, debug=self.debug, id=0, name="Dealer")
        self.dealer = dealer
        
        p_list_size = len(self.player_list)
        _msg_pre = "There is" if p_list_size == 1 else "There are"
        _msg_suf = "player" if p_list_size == 1 else "players"
        self._debug_msg(f"(_make_players) {_msg_pre} now {p_list_size} {_msg_suf} in the game.")
        self._debug_msg("(_make_players) Finished.\n")
    
    def start_game(self) -> None:
        # Should handle drawing two cards for both player and dealer
        self._debug_msg("(start_game) Starting game!")
        self._copy_deck()
        self._make_players()
        self.game_start = True
        self.game_round = 1
        self.game_state = GameState.BETTING_PHASE
        self._debug_msg("(start_game) Make your bets!\n")
    
    def _check_bets(self) -> bool:
        for player in self.player_list:
            if not player.has_bet:
                self._debug_msg(f"(_check_bets) Player \"{player.name}\" (id:{player.id}) hasn't published a bet yet!\n")
                return False
        self._debug_msg("(_check_bets) All players have submitted their bets.\n")
        return True
    
    def publish_bets(self) -> None:
        if self.game_state != GameState.BETTING_PHASE:
            self._debug_msg("(publish_bets) Game State is no longer at Betting Phase!\n")
            return
        self._debug_msg("(publish_bets) Attempting to publish bets.")
        if self._check_bets():
            self._debug_msg("(publish_bets) Finished publishing bets.")
            self._debug_msg("(publish_bets) Setting the Game State to Game Phase!\n")
            self.game_state = GameState.GAME_PHASE
    
    def next_turn(self) -> None:
        # Save game state then proceed to next round
        if self.game_state != GameState.GAME_PHASE:
            self._debug_msg("(next_turn) Game State is no longer at Game Phase!\n")
            return
    
    def restart(self) -> None:
        self.local_deck.clear()
        self.player_list.clear()
        self.dealer = None
        self.game_start = False
        self.game_round = 0
    
    def bet(self, player_id: int, bet_amount: float = None, all_in: bool = False) -> None:
        """Set a player's bet."""
        if self.game_state != GameState.BETTING_PHASE:
            self._debug_msg("(bet) Game State is no longer at Betting Phase!\n")
            return
        player = self.player_list[player_id + 1] # Player ID always starts at 1. The dealer's ID is 0.
        _msg = f"(bet) Player \"{player.name}\" (id:{player.id}),"
        if bet_amount is None and not all_in:
            bet_amount = self.minimum_bet
        elif all_in:
            bet_amount = player.money
            
        if bet_amount < self.minimum_bet:
            self._debug_msg(f"{_msg} minimum bet starts at {self.minimum_bet} only!\n")
        elif player.money < bet_amount:
            self._debug_msg(f"{_msg} you do not have enough money to bet.\n")
        else:
            self._debug_msg(f"{_msg} has bet {bet_amount}!\n")
            player.has_bet = True
            player.current_bet = bet_amount
    
    def cancel_bet(self, player_id: int) -> None:
        if self.game_state != GameState.BETTING_PHASE:
            self._debug_msg("(cancel_bet) Game State is no longer at Betting Phase!\n")
            return
        player = self.player_list[player_id + 1]
        _msg = f"(hit) Player \"{player.name}\" (id:{player.id}),"
        self._debug_msg(f"{_msg} has cancelled their bet.")
        player.has_bet = False
        player.current_bet = 0
    
    def hit(self, player_id: int) -> None:
        """Draw a card for a player."""
        if self.game_state != GameState.GAME_PHASE:
            self._debug_msg("(bet) Game State is no longer at Game Phase!\n")
            return
        player = self.player_list[player_id + 1]
        _msg = f"(hit) Player \"{player.name}\" (id:{player.id}),"
        if player.total_card_value > 21:
            self._debug_msg(f"{_msg} you have lost. Your total card value has exceeded 21!\n")
            return
        self._debug_msg(f"{_msg} has drawn a card!\n")
        player.draw_card()
    
    def stand(self) -> None:
        # Pass turn to Dealer
        if self.game_state != GameState.GAME_PHASE:
            self._debug_msg("(stand) Game State is no longer at Game Phase!\n")
            return
        self.game_start = GameState.DEALER_PHASE


from cards import WHITE_CARDS_LIST    
from layouts import DefaultRow, preset_win_drag_area

def before_test(page: ft.Page):
    page.title = "Game Manager Test"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

async def test(page: ft.Page):
    game = BlackJackGame(page, WHITE_CARDS_LIST)
    game.deck_multiplier = int(input("Enter deck_multiplier: "))
    print(f"Deck size is currently: {game.local_deck_size()}")
    print(f"Deck size will be: {len(WHITE_CARDS_LIST) * game.deck_multiplier}")
    
    game.player_count = int(input("Enter player_count: "))
    _pc_msg = "players" if game.player_count > 1 else "player"
    print(f"There will now be {game.player_count} {_pc_msg} (excluding the dealer) for the game.")
    
    game.start_game()
    game.publish_bets()
    
    player_containers: list[ft.Control] = []
    for i in range(game.player_count):
        _p = game.player_list[i]
        _p_text = ft.Text(f"{_p.name} (id:{_p.id})", text_align=ft.TextAlign.CENTER)
        _p_cont = ft.Container(
            content=_p_text, padding=8,
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            alignment=ft.Alignment.CENTER,
            border_radius=8
        )
        print(f"Made a container for player \"{_p.name}\" (id:{_p.id})")
        player_containers.append(_p_cont)
    
    player_row = DefaultRow(player_containers, vertical_alignment=ft.CrossAxisAlignment.END)
    form = preset_win_drag_area(ft.Container(player_row, expand=False))
    page.add(form)
    

if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)