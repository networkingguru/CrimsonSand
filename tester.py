import options
import time
from components import fighter, injuries, weapon
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from utilities import itersubclasses
from combat_functions import filter_injuries, apply_injuries

entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)
weapons = options.weapons
add_weapons(entities, weapons)

set1 = {1,2,3,4,5,6,7}
set2 = {2,7}
set3 = {5,9}

for s in [set2, set3]:
    if s.issubset(set1):
        print('True')
    else:
        print('False')