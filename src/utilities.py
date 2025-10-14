import random
from pathlib import Path
from typing import Optional
from datatypes import Card, CardSuite, CardType


def get_file_names(path: Path) -> list[str]:
    """Returns a list of names of the files found in the `path`."""
    return [f.name for f in path.iterdir() if f.is_file()]

def format_card(path: Path, src: str) -> str:
    """Returns the string of a path with file destination."""
    return Path(path / Path(src)).as_posix()

def pick_random_src(path: Path, list: list) -> str:
    """Returns a random src from a list. Use with images."""
    rnd_card: str = random.choice(list)
    print(f"Picked {rnd_card} from deck.")
    return format_card(path, rnd_card)

def pick_then_del(path: Path, *lists: list[str]) -> Optional[str]:
    """
    Handles card picking by deleting it from one or more decks (lists).
    
    If multiple lists are provided, the picked card will be removed
    from all lists that contain it.
    """
    # Pick from the first list
    if not lists or len(lists[0]) == 0:
        print("No deck provided or deck is empty.")
        return None
    
    main_deck = lists[0]
    deck_size = len(main_deck)
    rnd_card = random.choice(main_deck)
    
    print(f"Picked {rnd_card} from deck of size {deck_size}.", end=" ")
    
    # Remove the picked card from *all* provided lists
    for deck in lists:
        if rnd_card in deck:
            deck.remove(rnd_card)
            
    print(f"Deck(s) now updated after removal.")
    return format_card(path, rnd_card)

def assign_values(card_list: list[str]) -> list[Card]:
    """Assigns the correct values each card should have."""
    new_card_list = []
    for card in card_list:
        split: list[str] = card.split("_")
        mid_split: str = split[1]
        card_value: list[int] = [0]
        type: str = mid_split
        color: str = split[2]
        color = color.removesuffix(".png").title()
        
        if mid_split.isdigit(): # Number Cards
            card_value = [int(mid_split)]
            type = CardType.NUMBER.name
        elif mid_split.isalpha() and not mid_split == "A": # Face Cards
            card_value = [10]
            type = CardType.FACE.name
        else: # Ace Cards, etc.
            card_value = [1, 11]
            type = CardType.FLEXIBLE.name
            
        suite: str = split[0]
        for card_suite in CardSuite:
            if suite in card_suite.value:
                suite = card_suite.name
                break
            
        entry = Card(
            src=card, name=mid_split if mid_split != "A" else "Ace",
            type=type, suite=suite, value=card_value, color=color
        )
        new_card_list.append(entry)
    return new_card_list