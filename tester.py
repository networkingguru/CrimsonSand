#import options
from math import sqrt, pi
import time
import global_vars
from utilities import itersubclasses
from components import armor
from components.material import Material, material_dict
from components.armor import Armor_Component, Armor_Construction, gen_armor
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from utilities import itersubclasses
import options

entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)
weapons = options.weapons
add_weapons(entities, weapons)


aggressor = entities[0]
target = entities[1]
aggressor.worn_armor = options.player_armor

armor.apply_armor(aggressor)
