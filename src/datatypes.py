from enum import Enum
from dataclasses import dataclass


class CardType(Enum):
    NUMBER = "Number"
    FACE = "Face"
    FLEXIBLE = "Flexible"

class CardSuite(Enum):
    SPADES = "Spades/Pikes"
    CLOVERS = "Clovers"
    DIAMONDS = "Diamonds/Tiles"
    HEARTS = "Hearts"

class BlackJack(Enum):
    NORMAL = "Normal"
    NATURAL = "Natural"

@dataclass
class Card:
    src: str
    name: str
    type: CardType
    suite: CardSuite
    value: list[int]
    color: str
    hidden: bool = True
    