from enum import Enum, auto

class GameStates(Enum):
    default = auto()
    menu = auto()

class EntityState(Enum):
    conscious = auto()
    unconscious = auto()
    stunned = auto()
    dead = auto()
    inanimate = auto()
    shock = auto()

class FighterStance(Enum):
    standing = auto()
    prone = auto()
    kneeling = auto()
    sitting = auto()

class Colors(Enum):
    white = auto()