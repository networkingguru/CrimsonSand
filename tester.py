#import options
from math import sqrt, pi
import time
import global_vars
from utilities import itersubclasses, roll_dice
from components.material import Material, material_dict
from components.armor import Armor_Component, Armor_Construction, gen_armor, apply_armor
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from utilities import itersubclasses, clamp
#from combat_functions import armor_control
import options
from components.professions import DeathKnight
from components.circumstances import Circumstance
from components.upbringing import get_valid_upbringings


entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)
weapons = options.weapons
add_weapons(entities, weapons)
entities[0].creation_choices['sex'] = 'Male'
entities[0].creation_choices['circumstance'] = 'Contracted Gladiator'
entities[0].creation_choices['ethnicity'] = 'Eastern'



entities[0].worn_armor = options.player_armor
apply_armor(entities[0])

u_list = get_valid_upbringings(entities[0],50)






print('done')