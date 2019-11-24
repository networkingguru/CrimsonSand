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

entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)
weapons = options.weapons
add_weapons(entities, weapons)

entities[0].worn_armor = options.player_armor
apply_armor(entities[0])

aggressor = entities[0]
target = entities[1]
attack = aggressor.fighter.equip_loc[19].attacks[0]



def armor_control(target, location, attack, dam_type, dam_amount) -> (list, list, list):
    locations = [location]
    dam_amt_list = [dam_amount]
    dam_type_list = [dam_type] 
    ao_idx =  1 #Counter. Subtracted from len of loc_armor to determine ao to effect

    if ao_idx == 1:
        idx = len(target.loc_armor[location]) - ao_idx 
        ao = target.loc_armor[location][idx]

        if ao.rigidity == 'rigid':
            locs = []
            #Apply to primary and generate list of secondary locations
            locs, dam_amt_list, dam_type_list = armor_displace(target, location, attack, ao_idx, dam_type, dam_amount)

            if len(locs) > 0:
                for l in locs:
                    if l not in locations:
                        locations.append(l)
            ao_idx += 1
            dam_total = sum(dam_amt_list)



    while dam_total > 0 and ao_idx < len(target.loc_armor[location]):
        
        #Apply to locs

        for loc in locations:
            idx = locations.index(loc)
            dam_amt_list[idx], dam_type_list[idx] = armor_protect(target, loc, attack, ao_idx, dam_type_list[idx], dam_amt_list[idx])

        dam_total = sum(dam_amt_list)
        ao_idx += 1

    return locations, dam_amt_list, dam_type_list


        

        
def armor_displace(target, location, attack, ao_idx, dam_type, dam_amount) -> (list, list, list):
    idx = len(target.loc_armor[location]) - ao_idx 
    ao = target.loc_armor[location][idx]
    locs = [location]
    dam_amt_list = [dam_amount]
    dam_type_list = [dam_type]
    deflect = False
    deflect_max = 0

    #Check deflect
    if dam_type == 'p':
        deflect_max = ao.p_deflect_max
        deflect_chance = ao.p_deflect
    elif dam_type == 's':
        deflect_max = ao.s_deflect_max
        deflect_chance = ao.s_deflect
    elif dam_type == 't':
        deflect_max = ao.t_deflect_max
        deflect_chance = ao.t_deflect
    elif dam_type == 'b':
        deflect_max = ao.b_deflect_max
        deflect_chance = ao.b_deflect

    if dam_amount < deflect_max:
        if roll_dice(1,100) < (deflect_chance * 100):
            deflect = True


    if not deflect:
        #Determine if attack penetrates
        armor_breach_psi = attack.main_area * ao.hits_sq_in
        if dam_amount > armor_breach_psi or ao.hits:
            dam_amount -= min([armor_breach_psi, ao.hits])
            ao.hits -= dam_amount
            dam_amt_list[0] = dam_amount
        #If no penetration, convert damage and apply to next area(s)
        elif dam_type == 'p':
            ao.hits -= dam_amount
            dam_type_list = ['b']
            dam_amt_list = [dam_amount *.3 * ao.b_soak]
        else:
            ao.hits -= dam_amount
            if dam_type == 't': dam_amount *= .1
            if len(ao.covered_locs) < 4:
                locs = ao.covered_locs
            else:
                while len(locs) < 3:
                    i = 1
                    if location - 2 in ao.covered_locs:
                        locs.append(location - 2)
                    if location + 2 in ao.covered_locs:
                        locs.append(location + 2)
                    if location - 1 in ao.covered_locs:
                        locs.append(location - 1)
                    if location + 1 in ao.covered_locs:
                        locs.append(location + 1)
                    while i < len(ao.covered_locs):
                        if ao.covered_locs[i] != location:
                            locs.append(ao.covered_locs[i])
                        i += 1
                    print('Reached end of armor_displace without reaching while loop condition')#Should never be hit
                    break 
        
            for l in locs:
                dam_type_list.append('b')
                if l == locs[0]:
                    dam_amt_list.append(dam_amount *.5 * ao.b_soak)
                else:
                    dam_amt_list.append(dam_amount * .25 * ao.b_soak)        
            
    else: #Deflected
        dam_amount = 0 

    return locs, dam_amt_list, dam_type_list

            

def armor_protect(target, location, attack, ao_idx, dam_type, dam_amount) -> (int, int):
       
    #Check deflect
    #Damage armor
    #Check soak
    #Return remaining Damage

    idx = len(target.loc_armor[location]) - ao_idx 
    ao = target.loc_armor[location][idx]
    deflect_max = 0
    deflect = False
    penetrate = False

    #Check deflect
    if dam_type == 'p':
        deflect_max = ao.p_deflect_max
        deflect_chance = ao.p_deflect
    elif dam_type == 's':
        deflect_max = ao.s_deflect_max
        deflect_chance = ao.s_deflect
    elif dam_type == 't':
        deflect_max = ao.t_deflect_max
        deflect_chance = ao.t_deflect
    elif dam_type == 'b':
        deflect_max = ao.b_deflect_max
        deflect_chance = ao.b_deflect

    if dam_amount < deflect_max:
        if roll_dice(1,100) < (deflect_chance * 100):
            deflect = True



    if ao.rigidity == 'semi' and not deflect:
        #Determine if attack penetrates
        armor_breach_psi = attack.main_area * ao.hits_sq_in
        if dam_amount > armor_breach_psi or ao.hits:
            dam_amount -= min([armor_breach_psi, ao.hits])
            ao.hits -= dam_amount
        #If no penetration, convert damage and apply to next area(s)
        elif dam_type == 'b':
            ao.hits -= dam_amount * .5
            dam_amount = dam_amount * ao.b_soak
        elif dam_type == 't':
            ao.hits -= dam_amount
            dam_type = 'b'
            dam_amount = dam_amount *.1 * ao.b_soak
        else:
            ao.hits -= dam_amount
            dam_type = 'b'
            dam_amount = dam_amount *.7 * ao.b_soak

    elif not deflect:
        #Determine if attack penetrates
        armor_breach_psi = attack.main_area * ao.hits_sq_in
        if dam_type != 'b':
            if dam_amount > armor_breach_psi or ao.hits:
                dam_amount -= min([armor_breach_psi, ao.hits])
                ao.hits -= dam_amount
                penetrate = True
        #If no penetration, convert damage and apply to next area(s)
        if not penetrate:
            if dam_type == 'b':
                dam_amount = dam_amount * ao.b_soak
            elif dam_type == 't':
                ao.hits -= dam_amount
                dam_type = 'b'
                dam_amount = dam_amount *.2 * ao.b_soak
            else:
                ao.hits -= dam_amount
                dam_type = 'b'
                dam_amount = dam_amount *.8 * ao.b_soak

    else: #Deflected
        dam_amount = 0

    return dam_amount, dam_type




locations, dam_amt_list, dam_type_list = armor_control(aggressor, 5, attack, 's', 3000)

armor_objects = []
total_stam = 0
l_mod = 0
m_mod = 0
h_mod = 0 
phys_mod = 0
la_skill = aggressor.fighter.get_attribute('l_armor')
ma_skill = aggressor.fighter.get_attribute('m_armor')
ha_skill = aggressor.fighter.get_attribute('h_armor')

for loc in aggressor.loc_armor:
    for ao in loc:
        if ao in armor_objects: continue
        else: armor_objects.append(ao)

for ao in armor_objects:
    total_stam += ao.stam_drain
    if ao.density < .1:
        l_mod += ao.physical_mod
    elif ao.density <= .2:
        m_mod += ao.physical_mod
    else:
        h_mod += ao.physical_mod
 
l_mod = clamp(l_mod - la_skill, 0)
m_mod = clamp(m_mod - ma_skill, 0)
h_mod = clamp(h_mod - ha_skill, 0)

l = []

while len(l) < 3:
    l.append(1)
    print(len(l))
    


print('done')