#import options
from math import sqrt, pi
import time
import global_vars
from utilities import itersubclasses, roll_dice, name_location, clamp, armor_log
from components.material import Material, material_dict
from components.armor import Armor_Component, Armor_Construction, gen_armor, apply_armor, component_sort
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
#from combat_functions import armor_control
import options
from components.professions import DeathKnight
from components.circumstances import Circumstance
from components.upbringing import get_valid_upbringings
from item_gen import weapon_generator, calc_weapon_stats, armor_component_filter, gen_filtered_armor

entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)

#components = component_sort(entities[0])
#armor_log(entities, components)

armors = gen_filtered_armor(entities[0],'flexible','t',500,True,True)





print('done')