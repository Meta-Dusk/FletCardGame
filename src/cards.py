import flet as ft
from utilities import assign_values, get_file_names, format_card
from components import WHITE_CARDS_PATH, BLACK_CARDS_PATH
from images import CardImage
from datatypes import Card
from typing import Optional


WHITE_CARDS_LIST = get_file_names(WHITE_CARDS_PATH)
BLACK_CARDS_LIST = get_file_names(BLACK_CARDS_PATH)
WHITE_CARDS_VALUES = assign_values(WHITE_CARDS_LIST)
BLACK_CARDS_VALUES = assign_values(BLACK_CARDS_LIST)


# == HELPERS ==
def find_card(deck: list[Card], src: str) -> Card:
    for card in deck:
        if card.src.lower() == src.lower():
            return card

def get_card_value(card_src: Optional[str]) -> Optional[Card]:
    if card_src is None:
        return
    split_dirs = card_src.split("/")
    card_file = split_dirs[len(split_dirs) - 1]
    card_color = split_dirs[len(split_dirs) - 2]
    
    deck = WHITE_CARDS_VALUES if card_color == "white" else BLACK_CARDS_VALUES
    card_value = find_card(deck, card_file)
    return card_value

def get_card_counterpart(card_src: Optional[str]) -> Optional[str]:
    if card_src is None:
        return None
    split_dirs = card_src.split("/")
    card_file = split_dirs[len(split_dirs) - 1]
    card_color = split_dirs[len(split_dirs) - 2]
    if card_color == "white":
        card_name = format_card(BLACK_CARDS_PATH, card_file)
    else:
        card_name = format_card(WHITE_CARDS_PATH, card_file)
    return card_name

def print_card_names() -> None:
    print("\nPrinting all the names of the white cards list:")
    for i in range(len(WHITE_CARDS_VALUES)):
        print(f"{WHITE_CARDS_VALUES[i].name}")
    print("\nPrinting all the names of the black cards list:")
    for i in range(len(BLACK_CARDS_VALUES)):
        print(f"{BLACK_CARDS_VALUES[i].name}")

def print_card_values() -> None:
    print("\nPrinting all the values of the white cards list:")
    for i in range(len(WHITE_CARDS_VALUES)):
        print(f"{WHITE_CARDS_VALUES[i]}")
    print("\nPrinting all the values of the black cards list:")
    for i in range(len(BLACK_CARDS_VALUES)):
        print(f"{BLACK_CARDS_VALUES[i]}")


# == COMPONENTS ==
class CardComponent:
    """Encapsulates the creation and management of a card image component."""
    def __init__(
        self, card_src: Optional[str],
        *, content: Optional[ft.Control] = None
    ) -> None:
        """`content` will override `card_src` if not `None`."""
        self.src: Optional[str] = card_src
        self.content: ft.Control = None
        self.content = self._build_img(card_src) if content is None else content
        
    def _build_img(self, card_src: str) -> ft.Container:
        """Builds a `CardImage` with `card_src` as the `src`."""
        card_img = CardImage(card_src)
        return ft.Container(
            card_img, col=2, padding=4,
            alignment=ft.Alignment.CENTER
        )
    
    def replace_content(self, content: ft.Control) -> None:
        """Replaces the content with a different control."""
        self.src = None
        self.content.content = content
        if self.content.page:
            self.content.update()
    
    def update_img(self, card_src: str) -> None:
        """Safely update the image inside the wrapper."""
        if self.content is None:
            return
        self.src = card_src
        self.content.src = card_src
        if self.content.page:
            self.content.update()
            
    def control(self):
        """Return the wrapped control for UI placement."""
        return self.content
    
    def __call__(self):
        """Allow the instance to be used directly in Flet controls."""
        return self.content


if __name__ == "__main__":
    print_card_names()
    print_card_values()