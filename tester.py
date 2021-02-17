#import options
from math import sqrt, pi
import time
import global_vars
from utilities import itersubclasses, roll_dice, name_location
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

with open('armor_gen.txt','w') as armor_log:
    for cat in components:
        armor_log.write('Category: ' + cat + '\n')
        armor_log.write('\n')
        for a in components.get(cat):
            locs = ''
            for i, l in enumerate(a.covered_locs):
                if i: 
                    locs += ', '
                locs += name_location(l)

            armor_log.write('Name: ' + a.name + '\n')
            armor_log.write('Cost: ' + str(round(a.cost)) + '\n') 
            armor_log.write('Thickness: ' + str(round(a.thickness,2)) + ' inches'+ '\n')
            armor_log.write('Rigidity: ' + a.rigidity + '\n')
            armor_log.write('Covered Locations: ' + locs + '\n')
            armor_log.write('Area Covered: ' + str(round(a.main_area,1)) + ' square inches\n')
            armor_log.write('Weight: ' + str(round(a.weight)) + ' pounds \n')
            armor_log.write('Density: ' + str(round(a.density)) + '\n')
            armor_log.write('Quality: ' + a.quality + '\n')
            armor_log.write('B/S/P Deflect Maximums: ' + str(round(a.b_deflect_max)) + '/' + str(round(a.s_deflect_max)) + '/' + str(round(a.p_deflect_max)) + ' PSI' + '\n')
            armor_log.write('B/S/P Deflect Percentage: ' + str(round(a.b_deflect*100,2)) + '%/' + str(round(a.s_deflect*100,2)) + '%/' + str(round(a.p_deflect*100,2)) + '%' + '\n')
            armor_log.write('Hits: ' + str(round(a.hits)) + '\n')
            armor_log.write('Hits per Square Inch: ' + str(round(a.hits_sq_in)) + '\n')
            armor_log.write('B Soak: ' + str(round(a.b_soak*100)) + '%' + '\n')
            armor_log.write('Physical Modifier (base): ' + str(round(a.physical_mod)) + '\n')
            armor_log.write('Stamina Drain: ' + str(round(a.stam_drain)) + ' per round' + '\n')
            armor_log.write('\n')

print('done')