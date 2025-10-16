import flet as ft
from datatypes import Card
from deck_management import Player
from enum import Enum


class GameState(Enum):
    WAITING_PHASE = "Waiting Phase"
    BETTING_PHASE = "Betting Phase"
    GAME_PHASE = "Game Phase"
    GAME_OVER = "Game Over"
    
# TODO: Finish the implementation of the BlackJack class here
class BlackJackGame:
    # Handles everything related to the gameplay loop
    def __init__(
        self, page: ft.Page, reference_deck: list[Card], *,
        player_count: int = 1, deck_multiplier: int = 1,
        minimum_bet: float = 1000, win_multiplier: float = 2.0,
        black_jack_multiplier: float = 2.5, debug: bool = True
    ):
        self.page = page
        self.reference_deck = reference_deck
        self.player_count = player_count
        self.deck_multiplier = deck_multiplier
        self.minimum_bet = minimum_bet
        self.win_multiplier = win_multiplier
        self.black_jack_multiplier = black_jack_multiplier
        self.local_deck: list[Card] = []
        self.debug = debug
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
        self._debug_msg("(_copy_deck) Finished.\n")
    
    def local_deck_size(self) -> int:
        return len(self.local_deck)
    
    def _make_players(self) -> None:
        """
        Makes a list of new players to be appended into the `player_list` based
        on `player_count`. Also makes a `dealer`.
        """
        for i in range(self.player_count):
            self._debug_msg(f"(_make_players) Making Player {i+1}.")
            player = Player(self.page, self.local_deck, debug=self.debug, id=i)
            self.player_list.append(player)
            
        self._debug_msg("(_make_players) Making the Dealer.")
        dealer = Player(self.page, self.local_deck, is_dealer=True, debug=self.debug)
        self.dealer = dealer
        
        p_list_size = len(self.player_list)
        _msg_pre = "There is" if p_list_size == 1 else "There are"
        _msg_suf = "player" if p_list_size == 1 else "players"
        self._debug_msg(f"(_make_players) {_msg_pre} now {p_list_size} {_msg_suf} in the game.")
        self._debug_msg("(_make_players) Finished.\n")
    
    def start_game(self):
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
    
    def publish_bets(self):
        self._debug_msg("(publish_bets) Attempting to publishing bets.")
        if self._check_bets():
            self._debug_msg("(publish_bets) Finished publishing bets.\n")
    
    def next_turn(self):
        # Save game state then proceed to next round
        pass
    
    def restart(self):
        self.local_deck.clear()
        self.player_list.clear()
        self.dealer = None
        self.game_start = False
        self.game_round = 0
    
    def bet(self):
        # Handle money for betting
        pass
    
    def all_in(self):
        # Bet all available money
        pass
    
    def hit(self):
        # Draw a card
        pass
    
    def stand(self):
        # Pass turn to Dealer
        pass


from cards import WHITE_CARDS_LIST    

def before_test(page: ft.Page):
    page.title = "Game Manager Test"

async def test(page: ft.Page):
    game = BlackJackGame(
        page, WHITE_CARDS_LIST,
        # player_count=1,
    )
    deck_multiplier = int(input("Enter deck_multiplier: "))
    game.deck_multiplier = deck_multiplier
    print(f"Deck size is currently: {game.local_deck_size()}")
    print(f"Deck size will be: {len(WHITE_CARDS_LIST) * deck_multiplier}")
    
    player_count = int(input("Enter player_count: "))
    game.player_count = player_count
    print(f"There will now be {player_count} players (excluding the dealer) for the game.")
    
    game.start_game()
    game.publish_bets()
    await page.window.close()
    

if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)