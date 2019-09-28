import global_vars
from math import sqrt
from utilities import itersubclasses, clamp, roll_dice
from components.material import (m_steel, m_leather, m_wood, m_tissue, m_bone, m_adam, m_bleather, m_bronze, m_canvas, m_cloth, m_copper, m_gold, m_granite, m_hgold,
    m_hsteel, m_ssteel, m_hssteel, m_iron, m_hiron, m_mithril, m_silver, m_hide, m_xthide)

quality_dict = {'Junk': -.5, 'Very Poor': -.3, 'Poor': -.2, 'Below Average': -.1, 'Average': 1, 'Above Average': 1.15, 'Fine': 1.3, 'Exceptional': 1.4, 'Masterwork': 1.5}

class Armor_Construction:
    def __init__(self, **kwargs):
        self.name = ''
        self.allowed_main_materials = [] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_steel #Primary material
        self.rigidity = 'rigid' #rigid, semi, or flexible
        self.density = 1 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.balance = 1 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1
        self.t_resist = 1
        self.construction_diff = 1 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)

class Armor_Component:
    def __init__(self, **kwargs):
        self.base_name = ''
        self.ht_range = () #Tuple containing min and max ht supported by the armor
        self.str_fat_range = () #Tuple containing min and max str/fat combination supported by the armor
        self.allowed_constructions = [] #List of Armor_Constructions that may be used
        self.construction = None
        self.thickness = .1 #Thickness in inches
        self.allowed_binder_materials = [] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 1 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.assembly_diff = 1 #Scalar for base construction time
        self.covered_locs = [] #List of locations protected
        self.shape = '' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        #Dynamic attributes below
        self.name = ''
        self.main_area = 0
        self.weight = 0
        self.cost = 0
        self.rigidity = '' #Set from construction
        self.b_deflect_max = 0 #PSI at which damage is no longer deflected
        self.s_deflect_max = 0 #PSI at which damage is no longer deflected
        self.p_deflect_max = 0 #PSI at which damage is no longer deflected
        self.t_deflect_max = 0 #PSI at which damage is no longer deflected
        self.b_deflect = 0 #% to deflect
        self.s_deflect = 0 #% to deflect
        self.p_deflect = 0 #% to deflect
        self.t_deflect = 0 #% to deflect
        self.hits = 0 #Overall structural hits
        self.breach_hits = 0 #Hits required to breach armor
        self.b_soak = 0 #Amount of force absorbed by padding. Percentage/Scalar
        self.physical_mod = 0 #Modifier to all physical actions due to armor. Reducable with armor skill

    def set_dynamic_attributes(self):
        #Location circ calcs
        avg_ht = (self.ht_range[0] + self.ht_range[1] / 2)
        waist = avg_ht * (.3 + (self.str_fat_range/1000)) 
        shoulder = waist * 1.6
        arm = waist * .45
        leg = waist * .7
        head = avg_ht * .3

        #Find surface area
        location_ratios = (1, .9, .87, .82, .82, .8, .8, .7, .7, .72, .72, .63, .63, .6, .6, .55, .55, .53, .53, .49, .49, .4, .4, .29, .29, .2, .2, .04, .04)
        min_ht = avg_ht
        max_ht = 0
        #Determine widest hit location
        if any(elem in [3,4,5,6,9,10] for elem in self.covered_locs):
            circ = shoulder
        elif any(elem in [13,14,17,18] for elem in self.covered_locs):
            circ = waist
        elif any(elem in [2,7,8,11,12,15,16,19,20] for elem in self.covered_locs):
            circ = arm
        elif any(elem in range(21,29) for elem in self.covered_locs):
            circ = leg
        else:
            circ = head

        if self.shape == 'h_cyl':
                circ /= 2

        #Find height 
        for loc in self.covered_locs:
            loc_ht = location_ratios[loc]*avg_ht
            if loc_ht > max_ht: max_ht = loc_ht
            if loc_ht < min_ht: min_ht = loc_ht

        height = max_ht - min_ht

        #Handle armor with single hit loc and therefore no height
        if height == 0:
            #Handle helmets
            if self.covered_locs[0] == 0:
                height = location_ratios[0]*avg_ht - location_ratios[1]*avg_ht
            else:
                min_ht = location_ratios[self.covered_locs[0]]*avg_ht
                max_ht = location_ratios[(self.covered_locs[0] - 1)]*avg_ht
            
            height = max_ht - min_ht

        self.main_area = circ * height

        construction_vol = self.thickness * self.main_area
        construction_wt = construction_vol * (self.construction.density * (self.construction.main_material.density * .03))
        binder_wt = (self.binder_amount * construction_vol) * (self.binder_material.density * .03)
        accent_wt = (self.accent_amount * construction_vol) * (self.accent_material.density * .03)

        self.weight = construction_wt + binder_wt + accent_wt

        construction_cost = construction_vol * self.construction.material.cost * self.construction.construction_diff 
        binder_cost = construction_vol * self.binder_amount * self.binder_material.cost
        accent_cost = construction_vol * self.accent_amount * self.accent_material.cost

        self.cost = (construction_cost + binder_cost + accent_cost) * self.assembly_diff * self.quality

        self.rigidity = self.construction.rigidity

        if self.rigidity == 'rigid':
            self.b_deflect = .2
            self.s_deflect = .5
            self.p_deflect = .8
            self.t_deflect = 1
        elif self.rigidity == 'semi':
            self.b_deflect = .1
            self.s_deflect = .35
            self.p_deflect = .5
            self.t_deflect = .5
        else:
            self.b_deflect = .05
            self.s_deflect = .1
            self.p_deflect = .1
            self.t_deflect = .3

        for i in [self.b_deflect, self.s_deflect, self.p_deflect, self.t_deflect]:
            i *= self.quality
        
        self.hits = (self.construction.main_material.elasticity * 1450000) * (construction_wt/(self.construction.main_material.density*.03)) * self.construction.main_material.toughness * sqrt(self.construction.main_material.hardness)
        self.breach_hits = self.hits/10 * self.thickness * self.construction.main_material.toughness

        deflect_max = (sqrt(self.construction.main_material.hardness))/8 * self.breach_hits

        self.b_deflect_max = deflect_max * 5
        self.s_deflect_max = deflect_max
        self.p_deflect_max = deflect_max
        self.t_deflect_max = deflect_max * 25

        self.b_soak = .045/self.construction.main_material.hardness * self.thickness


        




        


