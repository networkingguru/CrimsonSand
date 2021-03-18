from random import choice, randrange, uniform
from numpy.random import normal
from math import sqrt, pi
from components.weapon import Weapon, quality_dict
from components.armor import Armor_Component, armor_classifier
from utilities import roll_dice, itersubclasses, inch_conv
from components.material import (m_steel, m_leather, m_wood, m_tissue, m_bone, m_adam, m_bleather, m_bronze, m_canvas, m_cloth, m_copper, m_gold, m_granite, m_hgold,
    m_hsteel, m_ssteel, m_hssteel, m_iron, m_hiron, m_mithril, m_silver, m_hide, m_xthide)




def weapon_generator(weapon,quantity,min_cost=0,max_cost=100000) -> list:
    weapon_classes = []
    weapons = []
    weapon_master_list = itersubclasses(Weapon)
    #Fill weapon classes with weapon objects from each class of the chosen weapon
    for w in weapon_master_list:
        wpn = w()
        if weapon in wpn.skill:
            weapon_classes.append(wpn)

    #Generate
    while len(weapons) < quantity and len(weapon_classes) > 0:
        wpn = choice(weapon_classes)
        wcls = wpn.__class__
        #Range setup
        allowed_main_materials = wpn.allowed_main_materials
        main_len_range = wpn.main_len_range
        main_depth_range = wpn.main_depth_range
        md_mu = main_depth_range[0] + ((main_depth_range[1]-main_depth_range[0])/2)
        md_sigma = (main_depth_range[1]-main_depth_range[0])/10
        main_avg_depth_range = wpn.main_avg_depth_range
        mad_mu = main_avg_depth_range[0] + ((main_avg_depth_range[1]-main_avg_depth_range[0])/2)
        mad_sigma = (main_avg_depth_range[1]-main_avg_depth_range[0])/10
        main_width_range = wpn.main_width_range
        main_avg_width_range = wpn.main_avg_width_range
        shaft_length_range = wpn.shaft_length_range 
        shaft_diameter_range = wpn.shaft_diameter_range
        qualities = list(quality_dict.keys())
        #Begin randomization
        rand_quality = normal(len(qualities)/2,1)
        quality = qualities[int(rand_quality)-1]
        material = allowed_main_materials[(roll_dice(1,len(allowed_main_materials))-1)]
        main_length = randrange(main_len_range[0],main_len_range[1])
        main_depth = normal(md_mu,md_sigma)
        rand_avg_depth = normal(mad_mu,mad_sigma)
        main_avg_depth = rand_avg_depth if rand_avg_depth < main_depth else main_depth
        main_width = uniform(main_avg_width_range[0],main_avg_width_range[1])
        rand_avg_width = uniform(main_avg_width_range[0],main_avg_width_range[1])
        main_avg_width = rand_avg_width if rand_avg_width < main_width else main_width
        shaft_length = randrange(shaft_length_range[0],shaft_length_range[1])
        shaft_diameter = uniform(shaft_diameter_range[0],shaft_diameter_range[1])
        #Gen weapon
        w = wcls(main_material=material,shaft_length=shaft_length,shaft_diameter=shaft_diameter,avg_main_width=main_avg_width,
                main_width=main_width,avg_main_depth=main_avg_depth,quality=quality,main_length=main_length,main_depth=main_depth)
        if min_cost <= w.cost <= max_cost: 
            weapons.append(w)

    return weapons



def calc_weapon_stats(entity, weapon) -> dict:
    attack = weapon.base_attacks[0](weapon)
        
    if len(attack.skill) > 1:
        skills = []
        for s in attack.skill:
            skills.append(entity.fighter.get_attribute(s))
        max_s = max(skills)
        idx = skills.index(max_s)
        skill = attack.skill[idx]
    else:
        skill = attack.skill[0]
    skill_rating = entity.fighter.get_attribute(skill)
    tot_er = entity.fighter.er + attack.length + (weapon.length*weapon.grip_loc)
    b_psi = 0
    s_psi = 0
    t_psi = 0
    p_psi = 0
    eff_area = 0
    fist_mass = .0065 * entity.fighter.weight 


    if attack.hand:
        limb_length = entity.fighter.er
    else:
        limb_length = inch_conv(entity.fighter.height*entity.fighter.location_ratios[17])

    distance = limb_length + attack.length


    #Determine max velocity based on pwr stat and mass distribution of attack
    if attack.hands == 2:
        max_vel = sqrt(entity.fighter.get_attribute('pwr'))*(4.5-(attack.added_mass/2))
    else:
        max_vel = sqrt(entity.fighter.get_attribute('pwr'))*(3-(attack.added_mass/2))


    #Determine how long attack will take
    time = (((1/8)*(2*pi*limb_length)*pi)/12)/max_vel
    #Find final velocity using full distance travelled by weapon
    velocity = (1/time) * (distance/12)

    force = (fist_mass + attack.added_mass) * velocity

    psi = force*12 #Convert to inches

    
    

    #Damage calc = ((((added_mass + fist mass) * velocity) / main_area) * mech_adv) * sharpness or hardness or pointedness

    if attack.damage_type is 'b':
        eff_area =  attack.main_area * (velocity/40) #scale main area size based on velocity; hack to represent deformation
    else:
        eff_area = attack.main_area 

    ep = (((psi * attack.force_scalar) / eff_area) * attack.mech_adv) * attack.main_num

    if attack.damage_type == 's':
        modifier = attack.sharpness
        s_psi = ep*modifier
    elif attack.damage_type == 'p':
        modifier = attack.pointedness
        p_psi = ep*modifier/3
    elif attack.damage_type == 'b':
        modifier = attack.solidness*.01
        b_psi = ep*modifier*2.5
    else:
        t_psi = ep

    psi = max([s_psi,b_psi,t_psi,p_psi])

    to_hit = attack.attack_mod + skill_rating
    to_parry = weapon.parry_mod + skill_rating

    dam_mult = 1
    weight_factor = (entity.fighter.weight/100)**.4
    
    final_ap = attack.base_ap * (((100/skill_rating)**.2 + weight_factor))
    if final_ap > entity.fighter.get_attribute('swift'): final_ap = entity.fighter.get_attribute('swift')
    parry_ap = int(weapon.parry_ap * (((100/skill_rating)**.2 + weight_factor)))  


    combat_dict = {'total er': tot_er, 'psi': psi,'to hit': to_hit, 
                    'to parry': to_parry, 'final ap': final_ap, 'parry ap': parry_ap}

    #convert items to int
    for key in combat_dict:
        combat_dict[key] = int(combat_dict[key])



    return combat_dict


def armor_component_filter(rigidity,classification) -> set:
    #Helper function for armor store. Generates armors that meet a rigidity and classification (torso, head, legs, etc) filter
    valid_comps = set()

    components = itersubclasses(Armor_Component)
    for component in components:
        c = component()
        if c.rigidity == rigidity:
            if classification == armor_classifier(c):
                valid_comps.add(component)

    return valid_comps