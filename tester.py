import options
import time
import global_vars
from components import fighter, injuries, weapon
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from utilities import itersubclasses
import combat_functions

entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)
weapons = options.weapons
add_weapons(entities, weapons)

aggressor = entities[0]
target = entities[1]

fall, locs = combat_functions.calc_falling_damage(aggressor, 240)

print(str(fall) + ' psi to ' + str(locs) + ' locations')

