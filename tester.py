#import options
from math import sqrt, pi
import time
import global_vars
from utilities import itersubclasses
from components import maneuver, material
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

pwr = 250
arm_length = 41.5
wpn_length = 0
reach = arm_length + wpn_length
hand_weight = .85
wpn_weight = .9
contact_area = 2
circ = 2 * pi * reach #Find circumference
distance = ((1/8)*circ*pi)/12 #Distance traveled for 45 deg angle
max_vel = sqrt(pwr)*(3-(wpn_weight/2))
time = (((1/8)*(2*pi*arm_length)*pi)/12)/max_vel
velocity = (1/time) * distance

force = (hand_weight + wpn_weight) * velocity

psi = (force*12)/contact_area




print(distance)