#import options
from math import sqrt, pi
import time
import global_vars
from utilities import itersubclasses
from components import maneuver, material, armor
#from components import fighter, injuries, weapon
""" from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from utilities import itersubclasses
import combat_functions

entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)
weapons = options.weapons
add_weapons(entities, weapons)

aggressor = entities[0]
target = entities[1] """
amount = 10

armors = armor.gen_armor(armor.Jerkin, random = False, comparison = True, thickness = 1)

if len(armors) >= amount:
    for a in armors:
        print(a.name)
        print(a.weight)
        print(a.hits_sq_in)

print('Done')