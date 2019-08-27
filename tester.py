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

list1 = [0,1,2]
set1 = set([3,5,3,8,9])
set2 = set([1])
list2 = [12]
combo = set1 | set2 | set(list2)
lset = set(list1)

locs_allowed = set(range(23,29)) #Locs maneuver can target
restricted_locs = list(set(range(29)).difference(locs_allowed)) #Added because reachable_locs needs it 



for i in restricted_locs:
    print(i)
