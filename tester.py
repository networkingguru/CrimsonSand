#import options
from math import sqrt, pi
import time
import global_vars
from utilities import itersubclasses, roll_dice
from components.material import Material, material_dict
from components.armor import Armor_Component, Armor_Construction, gen_armor, apply_armor, component_sort
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from utilities import itersubclasses, clamp
#from combat_functions import armor_control
import options
from components.professions import DeathKnight
from components.circumstances import Circumstance
from components.upbringing import get_valid_upbringings
from item_gen import weapon_generator, calc_weapon_stats


components = component_sort()


print('done')