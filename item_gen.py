from random import choice, randrange, uniform
from numpy.random import normal
from components.weapon import Weapon, quality_dict
from utilities import roll_dice, itersubclasses
from components.material import (m_steel, m_leather, m_wood, m_tissue, m_bone, m_adam, m_bleather, m_bronze, m_canvas, m_cloth, m_copper, m_gold, m_granite, m_hgold,
    m_hsteel, m_ssteel, m_hssteel, m_iron, m_hiron, m_mithril, m_silver, m_hide, m_xthide)

weapon_master_list = itersubclasses(Weapon)


def weapon_generator(weapon,quantity,min_cost=0,max_cost=100000) -> list:
    weapon_classes = []
    weapons = []

    #Fill weapon classes with weapon objects from each class of the chosen weapon
    for w in weapon_master_list:
        wpn = w()
        if weapon in wpn.skill:
            weapon_classes.append(wpn)

    #Generate
    while len(weapons) < quantity:
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

wpns = weapon_generator('sword',15,0,50)

print('done')