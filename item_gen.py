from random import choice, randrange, uniform
from numpy.random import normal
from math import sqrt, pi
from components.weapon import Weapon, quality_dict
from components.armor import Armor_Component, armor_classifier, gen_armor
from utilities import roll_dice, itersubclasses, inch_conv, clamp
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

    if attack.damage_type == 'b':
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


def armor_component_filter(rigidity,classification,main_t=False,first_layer=False) -> list:
    #Helper function for armor store. Generates armors that meet a rigidity and classification (torso, head, legs, etc) filter
    valid_comps = {}

    components = itersubclasses(Armor_Component)
    for component in components:
        c = component()
        for cn in c.allowed_constructions:
            const = cn()
            if classification is 'h': #Allow rigid helms in flex and semi suits
                if first_layer and cn.__name__ != 'Padded':
                    continue
                valid_comps[component]=cn
            elif const.rigidity == rigidity and classification == armor_classifier(c):
                if main_t and not set([3,4,5,6,9,10]).issubset(set(c.covered_locs)): #If main_t set, filter out t armors that only cover small areas
                   continue 
                if first_layer and cn.__name__ != 'Padded':
                    continue
                valid_comps[component]=cn

    return valid_comps

def gen_filtered_armor(entity,rigidity,classification,cost,main_t=False,first_layer=False) -> list:
    valid_comps = armor_component_filter(rigidity,classification,main_t,first_layer)
    armors = []
    components = []
    constructions = []
    for key, value in valid_comps.items():
        components.append(key)
        constructions.append(value)

    i=0
    while len(armors)<20 and len(components) > 0: 
        if i>100: break
        roll = roll_dice(1,len(components))
        c = components[roll-1]
        construction = constructions[roll-1]
        armor = gen_armor(c,construction=construction,entity=entity,cost=cost)[0]
        if armor is not None: armors.append(armor)
        i += 1

    return armors

def rank_armors(entity,armors,cost,favor_coverage=False) -> object:
    a_dict = {}
    la_skill = entity.fighter.get_attribute('l_armor')
    ma_skill = entity.fighter.get_attribute('m_armor')
    ha_skill = entity.fighter.get_attribute('h_armor')
    mod = 0
    
    if len(armors) == 0:
        return None

    for a in armors:
        points = 0
        if a.density < .5:
            mod += a.physical_mod - la_skill
        elif a.density <= 1:
            a.physical_mod - ma_skill
        else:
            a.physical_mod - ha_skill


        points += (a.b_deflect_max * a.b_deflect) + (a.p_deflect_max * a.p_deflect) + (a.s_deflect_max * a.s_deflect)
        points += a.b_soak * 100000
        points -= mod*30
        if favor_coverage and points > 0: points *= len(a.covered_locs)/8

        a_dict[a] = points

    sorted_armor = dict(sorted(a_dict.items(), key = lambda kv:kv[1],reverse=True))
    armor_list = list(sorted_armor.keys())
    best_armor = armor_list[0]    

    return best_armor

def build_armor_set(entity,rigidity) -> list:
    #Purchase the best armor possible until money is expended
    #Money distribution across body parts: T - 50%, H - 25%, A - 10%, L - 10%, O - 5%
    #Money distribution across layers: L1: 25%, L2+: 75%
    #For clarity, Layer 1 is padded for blunt absorption, L2 is the main armor

    armor_list = []

    money = entity.fighter.money
    t_l2_money = money*.375
    t_l1_money = t_l2_money/4
    h_l2_money = money*.25*.75
    h_l1_money = h_l2_money/4
    a_l2_money = money*.1*.75
    a_l1_money = a_l2_money/4
    l_l2_money = money*.1*.75
    l_l1_money = l_l2_money/4
    o_l2_money = money*.05

    #Begin by buying L2 armor. If L2 is unaffordable, skip L1 in that loc and save player $
    
    #Select primary torso armor
    armors = gen_filtered_armor(entity,rigidity,'t',t_l2_money,True,False)
    armor = rank_armors(entity,armors,t_l2_money,True)
    if armor is not None: armor_list.append(armor)

    #Select L1 torso armor
    if armor is not None:
        armors = gen_filtered_armor(entity,'flexible','t',t_l1_money,True,True)
        armor = rank_armors(entity,armors,t_l1_money,True)
        armor_list.append(armor)

    #Select primary head armor
    armors = gen_filtered_armor(entity,rigidity,'h',h_l2_money,False,False)
    armor = rank_armors(entity,armors,h_l2_money,True)
    if armor is not None: armor_list.append(armor)

    #Select L1 head armor
    if armor is not None:
        armors = gen_filtered_armor(entity,'flexible','h',h_l1_money,False,True)
        armor = rank_armors(entity,armors,h_l1_money,True)
        armor_list.append(armor)

    #Select primary arm armor
    armors = gen_filtered_armor(entity,rigidity,'a',a_l2_money,False,False)
    armor = rank_armors(entity,armors,a_l2_money,True)
    if armor is not None: armor_list.append(armor)

    #Select L1 arm armor
    if armor is not None:
        armors = gen_filtered_armor(entity,'flexible','a',a_l1_money,False,True)
        armor = rank_armors(entity,armors,a_l1_money,True)
        armor_list.append(armor)

    #Select primary leg armor
    armors = gen_filtered_armor(entity,rigidity,'l',l_l2_money,False,False)
    armor = rank_armors(entity,armors,l_l2_money,True)
    if armor is not None: armor_list.append(armor)

    #Select L1 leg armor
    if armor is not None:
        armors = gen_filtered_armor(entity,'flexible','l',l_l1_money,False,True)
        armor = rank_armors(entity,armors,l_l1_money,True)
        armor_list.append(armor)

    #Select primary other armor
    armors = gen_filtered_armor(entity,rigidity,'o',o_l2_money,False,False)
    armor = rank_armors(entity,armors,o_l2_money,True)
    if armor is not None: armor_list.append(armor)

    return armor_list
