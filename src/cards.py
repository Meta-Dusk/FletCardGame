import flet as ft
from utilities import assign_values, get_file_names
from components import WHITE_CARDS_PATH, BLACK_CARDS_PATH
from images import CardImage
from datatypes import Card
from typing import Optional


WHITE_CARDS_SRC_LIST = get_file_names(WHITE_CARDS_PATH)
BLACK_CARDS_SRC_LIST = get_file_names(BLACK_CARDS_PATH)
WHITE_CARDS_LIST = assign_values(WHITE_CARDS_SRC_LIST)
BLACK_CARDS_LIST = assign_values(BLACK_CARDS_SRC_LIST)
DEBUG = False


# == HELPERS ==
def _debug_print(msg: str) -> None:
    if DEBUG:
        print(f"[DEBUG] {msg}")

def extract_card_file(card_src: str) -> str:
    split_dirs = card_src.split("/")
    card_file = split_dirs[len(split_dirs) - 1]
    return card_file

def find_card(deck: list[Card], card_src: str) -> Card:
    for card in deck:
        src = extract_card_file(card_src)
        _debug_print(f"Comparing {card.src} with {src}.")
        if card.src == src:
            _debug_print("Found match!")
            return card

def get_card_value(card_src: str) -> Card:
    split_dirs = card_src.split("/")
    card_file = split_dirs[len(split_dirs) - 1]
    card_color = split_dirs[len(split_dirs) - 2]
    
    deck = WHITE_CARDS_LIST if card_color == "white" else BLACK_CARDS_LIST
    card_value = find_card(deck, card_file)
    return card_value

def get_card_counterpart(card_src: str, *, invert: bool = False) -> Card:
    card_file = extract_card_file(card_src)
    card_segments = card_file.split("_")
    card_color = card_segments[len(card_segments) - 1].removesuffix(".png")
    if invert:
        _debug_print("Getting inverted card counterpart!")
        card_src = card_src.replace(
            card_color,
            "white" if card_color == "black" else "black"
        )
        _debug_print(f"Card color is now {card_color}")
        card = find_card(
            BLACK_CARDS_LIST if card_color == "white" else WHITE_CARDS_LIST,
            card_src
        )
        return card
    else:
        _debug_print(f"Getting card counterpart for card of color: {card_color}")
        card = find_card(
            BLACK_CARDS_LIST if card_color == "black" else WHITE_CARDS_LIST,
            card_src
        )
        return card

def print_card_list(list: list[Card]) -> None:
    for i in range(len(list)):
        print(f"{list[i]}")


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
        container: ft.Container = self.content
        container.content = content
        if container.page:
            container.update()
    
    def update_img(self, card_src: Optional[str]) -> None:
        """Safely update the image inside the wrapper."""
        if self.content is None or self.src is None:
            return
        container: ft.Container = self.content
        image: CardImage = container.content
        if card_src:
            image.change_src(card_src)
            self.src = card_src
        else:
            image.change_src(self.src)
    
    def hide_card(self) -> None:
        """Hides the card's face."""
        if self.content is None or self.src is None:
            return
        container: ft.Container = self.content
        image: CardImage = container.content
        image.change_src(None)
        self.src = None
    
    def control(self):
        """Return the wrapped control for UI placement."""
        return self.content
    
    def __call__(self):
        """Allow the instance to be used directly in Flet controls."""
        return self.content


if __name__ == "__main__":
    print("Printing all the possible white cards: ")
    print_card_list(WHITE_CARDS_LIST)
    print("\nPrinting all the possible black cards: ")
    print_card_list(BLACK_CARDS_LIST)