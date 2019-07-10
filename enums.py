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

class WeaponTypes(Enum):
    thrust_and_slash = auto
    thrust = auto
    slash = auto
    flail = auto

class MenuTypes(Enum):
    combat = auto
    inventory = auto
    options = auto

class CombatPhase(Enum):   
    explore = auto()
    init = auto()
    action = auto()
    weapon = auto()
    option = auto()
    option2 = auto()
    location = auto()
    defend = auto()
    stuck = auto()
    confirm = auto()
    repeat = auto()
    disengage = auto()
    move = auto()
    maneuver = auto()
    feint = auto()