from pathlib import Path
from datatypes import Card, CardSuite, CardType


def get_file_names(path: Path) -> list[str]:
    """Returns a list of names of the files found in the `path`."""
    return [f.name for f in path.iterdir() if f.is_file()]

def format_card(path: Path, src: str) -> str:
    """Returns the string of a path with file destination."""
    return Path(path / Path(src)).as_posix()

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
            type = CardType.NUMBER
        elif mid_split.isalpha() and not mid_split == "A": # Face Cards
            card_value = [10]
            type = CardType.FACE
        else: # Ace Cards, etc.
            card_value = [1, 11]
            type = CardType.FLEXIBLE
            
        suite: str = split[0]
        for card_suite in CardSuite:
            if suite in card_suite.value:
                suite = card_suite
                break
            
        entry = Card(
            src=card, name=mid_split if mid_split != "A" else "Ace",
            type=type, suite=suite, value=card_value, color=color
        )
        new_card_list.append(entry)
    return new_card_list