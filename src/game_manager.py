import flet as ft
from datatypes import Card, BlackJack
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
            _id = i + 1
            _temp_p_name = f"Player {_id}"
            self._debug_msg(f"(_make_players) Making {_temp_p_name}.")
            player = Player(
                self.page, self.local_deck, debug=self.debug,
                id=_id, name=_temp_p_name, money=self.starting_budget
            )
            self.player_list.append(player)
        if self.player_count == 1:
            self._debug_msg("(_make_players) Singleplayer Mode | Making the Dealer.")
            dealer = Player(self.page, self.local_deck, is_dealer=True, debug=self.debug, id=0, name="Dealer")
            self.dealer = dealer
        else:
            self._debug_msg("(_make_players) Multiplayer Mode | No Dealer will be made.")
        
        _msg_pre = "There is" if self.player_count == 1 else "There are"
        _msg_suf = "player" if self.player_count == 1 else "players"
        self._debug_msg(f"(_make_players) {_msg_pre} now {self.player_count} {_msg_suf} in the game.")
        self._debug_msg("(_make_players) Finished player setup.\n")
    
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
        _not_all_ready: bool = True
        for player in self.player_list:
            if not player.has_bet:
                self._debug_msg(f"(_check_bets) \"{player.name}\" (id:{player.id}) hasn't published a bet yet!")
                _not_all_ready = False
        if not _not_all_ready:
            self._debug_msg("(_check_bets) There are players that haven't submitted a bet yet!\n")
            return False
        self._debug_msg("(_check_bets) All players have submitted their bets.\n")
        return True
    
    def publish_bets(self) -> None:
        if self.game_state != GameState.BETTING_PHASE:
            self._debug_msg("(publish_bets) Game State is not at Betting Phase!\n")
            return
        self._debug_msg("(publish_bets) Attempting to publish bets.")
        if self._check_bets():
            self._debug_msg("(publish_bets) Finished publishing bets.")
            self._debug_msg("(publish_bets) Setting the Game State to Game Phase!\n")
            self.game_state = GameState.GAME_PHASE
    
    def next_turn(self) -> None:
        # Save game state then proceed to next round
        if self.game_state != GameState.GAME_PHASE:
            self._debug_msg("(next_turn) Game State is not at Game Phase!\n")
            return
        for player in self.player_list:
            if not player.finished_turn:
                self._debug_msg(f"(next_turn) Not all players have finished their turn!\n")
                return
        self._debug_msg(f"(next_turn) Moving on to the Dealer Phase.\n")
        self.game_start = GameState.DEALER_PHASE
    
    def dealer_phase(self) -> bool | None:
        """The dealer's turn."""
        if self.game_state != GameState.DEALER_PHASE:
            self._debug_msg("(dealer_phase) Game State is not at Dealer Phase!\n")
            return
        dealer_tcv = self.dealer.total_card_value
        dealer_bj = self.dealer.hand_is_blackjack()
        if self.player_count == 1:
            player = self.player_list[0]
            player_tcv = player.total_card_value
            player_bj = player.hand_is_blackjack()
            if dealer_tcv > 21 or (dealer_bj == BlackJack.NORMAL and player_bj == BlackJack.NATURAL):
                self._debug_msg(f"(dealer_phase) {player.name} Wins!")
                return True
            elif dealer_bj == BlackJack.NATURAL and player_bj == BlackJack.NORMAL:
                self._debug_msg("(dealer_phase) Dealer Wins!")
                return True
            elif dealer_bj == BlackJack.NATURAL and player_bj == BlackJack.NATURAL:
                self._debug_msg("(dealer_phase) It's a Draw!")
                return True
            if dealer_tcv <= player_tcv:
                self.dealer.draw_card()
                return False
        elif self.player_count > 1:
            winning_players: list[Player] = [self.player_list[0]]
            for player in self.player_list:
                if player.has_lost:
                    return
                if player.hand_is_blackjack() == BlackJack.NATURAL:
                    if winning_players[0].hand_is_blackjack() == BlackJack.NATURAL:
                        winning_players.append(player)
                        return
                    winning_players = [player]
                    return
                if player.total_card_value > winning_players[0].total_card_value:
                    winning_players = [player]
            self._debug_msg(f"(dealer_phase) Winners: {[p.name for p in winning_players]}")
            return True
        return None
    
    def restart(self) -> None:
        """Restart values back to their defaults."""
        self.local_deck.clear()
        self.player_list.clear()
        self.dealer = None
        self.game_start = False
        self.game_round = 0
        self.game_state = GameState.WAITING_PHASE
    
    def bet(self, player_id: int, bet_amount: float = None, all_in: bool = False) -> None:
        """Set a player's bet."""
        if self.game_state != GameState.BETTING_PHASE:
            self._debug_msg("(bet) Game State is not at Betting Phase!\n")
            return
        player = self.player_list[player_id - 1] # Player ID always starts at 1. The dealer's ID is 0.
        _msg = f"(bet) \"{player.name}\" (id:{player.id}),"
        if player.has_lost:
            self._debug_msg(f"{_msg} you have already lost!\n")
            return
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
            self._debug_msg("(cancel_bet) Game State is not at Betting Phase!\n")
            return
        player = self.player_list[player_id - 1]
        _msg = f"(hit) \"{player.name}\" (id:{player.id}),"
        if player.has_lost:
            self._debug_msg(f"{_msg} you have already lost!\n")
            return
        self._debug_msg(f"{_msg} has cancelled their bet.")
        player.has_bet = False
        player.current_bet = 0
    
    def hit(self, player_id: int) -> None:
        """Draw a card for a player."""
        if self.game_state != GameState.GAME_PHASE:
            self._debug_msg("(bet) Game State is not at Game Phase!\n")
            return
        player = self.player_list[player_id - 1]
        _msg = f"(hit) \"{player.name}\" (id:{player.id}),"
        if player.has_lost:
            self._debug_msg(f"{_msg} you have already lost!\n")
            return
        self._debug_msg(f"{_msg} has drawn a card!\n")
        player.draw_card()
        if player.total_card_value > 21:
            self._debug_msg(f"{_msg} you have lost. Your total card value has exceeded 21!\n")
            player.finished_turn = True
            player.has_lost = True
            return
    
    def stand(self, player_id: int) -> None:
        # Pass turn to Dealer
        if self.game_state != GameState.GAME_PHASE:
            self._debug_msg("(stand) Game State is not at Game Phase!\n")
            return
        player = self.player_list[player_id - 1]
        _msg = f"(stand) Player \"{player.name}\" (id:{player.id}),"
        if player.has_lost:
            self._debug_msg(f"{_msg} you have already lost!\n")
            return
        self._debug_msg(f"{_msg} has chose to stand.\n")
        player.finished_turn = True


from cards import WHITE_CARDS_LIST    
from layouts import default_row, preset_win_drag_area, default_column

def before_test(page: ft.Page):
    page.title = "Game Manager Test"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

async def test(page: ft.Page):
    game = BlackJackGame(page, WHITE_CARDS_LIST)
    game.deck_multiplier = int(input("Enter deck_multiplier: "))
    print(f"Deck size is currently: {game.local_deck_size()}")
    print(f"Deck size will be: {len(WHITE_CARDS_LIST) * game.deck_multiplier}")
    
    game.player_count = int(input("Enter player_count: "))
    _pc_msg = "players" if game.player_count > 1 else "player"
    print(f"There will now be {game.player_count} {_pc_msg} (excluding the dealer) for the game.\n")
    
    game.start_game()
    game.publish_bets()
    
    current_player_id: int = 1
    
    player_containers: list[ft.Container] = []
    for i in range(game.player_count):
        _p = game.player_list[i]
        _p_text = ft.Text(
            spans=[
                ft.TextSpan(f"{_p.name} (id:{_p.id}) | "),
                ft.TextSpan(_p.total_card_value)
            ],
            text_align=ft.TextAlign.CENTER, size=16,
            color=ft.Colors.SECONDARY if (i + 1) != current_player_id else ft.Colors.PRIMARY
        )
        _p_cont = ft.Container(
            content=_p_text, padding=8,
            bgcolor=ft.Colors.ON_SECONDARY if (i + 1) != current_player_id else ft.Colors.ON_PRIMARY,
            alignment=ft.Alignment.CENTER,
            border_radius=8, data=i + 1
        )
        print(f"Made a container for player \"{_p.name}\" (id:{_p.id})")
        player_containers.append(_p_cont)
    player_row = default_row(player_containers)
    
    def update_buttons():
        player = game.player_list[current_player_id - 1]
        for btn in button_row.controls:
            if btn not in [next_round_btn, next_player_btn] and player.has_lost:
                btn.disabled = True
            else:
                btn.disabled = False
        button_row.update()
    
    def npb_on_click(_):
        nonlocal current_player_id
        if current_player_id < game.player_count:
            current_player_id += 1
        else:
            current_player_id = 1
        print(f"Current Player ID: {current_player_id}")
        for container in player_containers:
            container: ft.Container
            text: ft.Text = container.content
            if container.data == current_player_id:
                container.bgcolor = ft.Colors.ON_PRIMARY
                text.color = ft.Colors.PRIMARY
            else:
                container.bgcolor = ft.Colors.ON_SECONDARY
                text.color = ft.Colors.SECONDARY
        player_row.update()
        update_buttons()
    
    def hb_on_click(_):
        game.hit(current_player_id)
        _p_index = current_player_id - 1
        _p = game.player_list[_p_index]
        _p_cont = player_containers[_p_index]
        _p_text: ft.Text = _p_cont.content
        _p_text.spans[1].text = _p.total_card_value
        if _p.has_lost:
            _p_cont.bgcolor = ft.Colors.ERROR_CONTAINER
            _p_text.color = ft.Colors.ERROR
        _p_cont.update()
        update_buttons()
    
    def bb_on_click(_):
        game.bet(current_player_id)
        publish_bets_btn.disabled = False
        cancel_bet_btn_btn.disabled = False
        publish_bets_btn.update()
    
    def pbb_on_click(_):
        game.publish_bets()
        for btn in [hit_btn, stand_btn, next_round_btn]:
            btn.disabled = False
        button_row.update()
    
    next_player_btn = ft.Button(
        "Next Player", on_click=npb_on_click,
        disabled=False if game.player_count > 1 else True
    )
    bet_btn = ft.Button("Bet", on_click=bb_on_click)
    cancel_bet_btn_btn = ft.Button("Cancel Bet", on_click=lambda _: game.cancel_bet(current_player_id), disabled=True)
    all_in_btn = ft.Button("All In", on_click=lambda _: game.bet(current_player_id, all_in=True), disabled=True)
    hit_btn = ft.Button("Hit", on_click=hb_on_click, disabled=True)
    stand_btn = ft.Button("Stand", on_click=lambda _: game.stand(current_player_id), disabled=True)
    next_round_btn = ft.Button("Next Round", on_click=lambda _: game.next_turn(), disabled=True)
    publish_bets_btn = ft.Button("Publish Bets", on_click=pbb_on_click, disabled=True)
    dealer_btn = ft.Button("Dealer's Turn", on_click=lambda _: game.dealer_phase)
    button_row = default_row([
        next_player_btn, bet_btn, cancel_bet_btn_btn, all_in_btn, hit_btn, stand_btn, next_round_btn,
        publish_bets_btn, dealer_btn
    ])
    
    main_column = default_column([player_row, button_row])
    form = preset_win_drag_area(ft.Container(main_column))
    
    page.add(form)
    await page.window.to_front()
    await page.window.center()
    

if __name__ == "__main__":
    ft.run(main=test, before_main=before_test)