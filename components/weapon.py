import global_vars
from math import sqrt
from enums import WeaponTypes, FighterStance, EntityState
from utilities import itersubclasses, clamp, roll_dice
from components.maneuver import (Headbutt, Tackle, Push, Trip, Bearhug, Reap, Wind_Choke, Blood_Choke, Collar_Tie, Compression_Lock, Joint_Lock, Limb_Capture, Sacrifice_Throw, 
    Shoulder_Throw, Strangle_Hold, Hip_Throw, Double_Leg_Takedown, Single_Leg_Takedown, Neck_Crank, Weapon_Push, Weapon_Trip, Disarm, Deshield, Hook_Neck)
from components.material import (m_steel, m_leather, m_wood, m_tissue, m_bone, m_adam, m_bleather, m_bronze, m_canvas, m_cloth, m_copper, m_gold, m_granite, m_hgold,
    m_hsteel, m_ssteel, m_hssteel, m_iron, m_hiron, m_mithril, m_silver, m_hide, m_xthide)

quality_dict = {'Junk': .5, 'Very Poor': .7, 'Poor': .8, 'Below Average': .9, 'Average': 1, 'Above Average': 1.15, 'Fine': 1.3, 'Exceptional': 1.4, 'Masterwork': 1.5}
craft_diff_dict = {'de blade':1.5, 'blade':1, 'curved blade':1.2, 'point':.8, 'wedge':.6, 'round':.4, 'flat':.2, 'hook':2}


class Weapon:
    def __init__(self, **kwargs):
        self.name = ''
        self.weapon = True
        self.shafted = False #Used to determine if wpn has a shaft
        self.allowed_main_materials = [] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = 0
        self.parry_mod = 0 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Weapon'
        self.bname_variants = [] #A list of variant names for the weapon
        self.skill = None #This is the default skill used for the weapon. String
        self.length = 1
        self.shaft_length = 0 #Also used as tethers for flail and whip like weapons
        self.shaft_diameter = 0
        self.shaft_num = 0
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1 #1.25 average longsword
        self.main_width = 1 #Absolute width at widest point
        self.avg_main_depth = .1 #.14 is average for a sword blade
        self.main_depth = .2 #Absolute depth at deepest point
        self.main_shape = 'de blade' #Acceptable values: de blade, blade, curved blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 1 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .5 #Center of mass for the main weapon component
        self.main_loc = .1 #Location along the total length for the main weapon component
        self.accent_loc = .05 #Location along the total length for the accent component
        self.grip_loc = .03 #location along the total length for the grip
        self.main_weight = 0
        self.shaft_weight = 0
        self.accent_weight = 0
        self.grip_weight = 0
        self.weight = 1
        self.main_length = 0
        self.added_mass = 0
        self.craft_diff = 1

        self.damage_type = 'b'
        self.stamina = 0

        self.parry_ap = 0
        

        #Maximums; used to procedurally gen weapons
        self.main_len_range = (0,0) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0,0)
        self.main_avg_depth_range = (0,0)
        self.main_width_range = (0,0)
        self.main_avg_width_range = (0,0)
        self.length_range = (0,0)
        self.shaft_length_range = (0,0) 
        self.shaft_diameter_range = (0,0)
        self.max_main_num = 1
        self.max_shaft_num = 1
        
        
        self.main_only_com = 0
        self.shaft_only_com = 0
        self.accent_only_com = 0
        self.com = 0 #Center of mass for the whole weapon
        self.com_perc = 0 #com as a percentage
        self.axis_vs_com = 0 #Shows COM relative to grip location (axis for swings). Used to determine AP/stamina costs.

        self.main_hits = 0
        self.staff_hits = 0
        self.accent_hits = 0        

        self.min_pwr_1h = 0 #1 pwr = 1 ft/lb; accelleration = 40 f/s2; weight of average hand = .86 lb
        self.min_pwr_2h = 0 #1 pwr = 1.5 ft/lb; accelleration = 40 f/s2; weight of average hand = .86 lb

        self.solidness = 1 #Used in damage calc
        self.sharpness = 1 
        self.pointedness = 1

        #Lists of attacks, mnvrs, guards
        self.base_attacks = []
        self.attacks = []
        self.base_maneuvers = []
        self.guards = []

        #Cost and rarity
        self.cost = 0
        self.normality = 1

        self.__dict__.update(kwargs)

        #self.set_dynamic_attributes()
        
    def set_dynamic_attributes(self):
        #Determine which variant name to use
        if len(self.bname_variants) > 1:
            n_idx = roll_dice(1, len(self.bname_variants))
            n_idx -= 1

            self.base_name = self.bname_variants[n_idx]

        #Name weapon using quality and material, if applicable
        if self.main_material not in [m_tissue, m_bone]:
            if self.quality != 'Average':
                self.name = self.quality + ' ' + self.main_material.name + ' ' + self.base_name
            else:
                self.name = self.main_material.name + ' ' + self.base_name
        else:
            self.name = self.base_name

        self.attack_mod += 20 * quality_dict.get(self.quality)
        self.parry_mod += 20 * quality_dict.get(self.quality)

        self.length = self.main_length + self.shaft_length

        sword_like = ['sword','dagger']
        if self.skill is not None:
            for s in sword_like:
                if s in self.skill:
                    self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
                    self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
                    self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
                    break
        

        self.main_weight = ((self.main_length * self.avg_main_depth * self.avg_main_width)*self.main_num) * (self.main_material.density * .03)
        self.shaft_weight = (self.shaft_length * self.shaft_diameter * (self.shaft_material.density * .03)) * self.shaft_num
        self.accent_weight = self.accent_cuin * (self.accent_material.density * .03)
        self.grip_weight = self.grip_material.density * (.3 * max(self.hands))
        self.weight = self.main_weight + self.shaft_weight + self.accent_weight
        self.main_only_com = ((self.main_length*self.main_com)+(self.main_loc*self.length))*self.main_weight
        self.shaft_only_com = (self.shaft_length*.5)*self.shaft_weight
        self.accent_only_com = (self.accent_loc*self.length)*self.accent_weight
        self.com = (self.main_only_com + self.shaft_only_com + self.accent_only_com)/self.weight #Effective added weight on strike for the whole weapon
        self.com_perc = self.com / self.length #com as a percentage
        self.axis_vs_com = self.com_perc - self.grip_loc #Shows COM relative to grip location (axis for swings). Used to determine AP/stamina costs.

        self.main_hits = (self.main_material.elasticity * 1450000) * (self.main_weight/(self.main_material.density*.03)) * self.main_material.toughness * sqrt(self.main_material.hardness)

        self.parry_ap += (self.weight * 100)*self.axis_vs_com

        self.min_pwr_1h = ((self.added_mass + .86) * 40)/1 #1 pwr = 1 ft/lb/s; accelleration = 40 f/s2; weight of average hand = .86 lb
        self.min_pwr_2h = ((self.added_mass + 1.72) * 40)/1.5 #1 pwr = 1.5 ft/lb/s; accelleration = 40 f/s2; weight of average hand = .86 lb

        self.solidness = sqrt(self.main_material.elasticity * self.main_material.hardness)
        if self.main_material.hardness < 1: 
            self.sharpness = self.main_material.hardness
            self.pointedness = self.main_material.hardness
        else:
            self.sharpness = sqrt((self.main_material.hardness/m_iron.hardness)*quality_dict.get(self.quality))
            self.pointedness = sqrt(self.main_material.hardness/m_iron.hardness)
        if self.main_shape == 'curved blade': self.sharpness *= 1.1
        
        

        self.craft_diff = craft_diff_dict.get(self.main_shape)
        main_materials_cost = self.main_material.cost * self.main_weight
        shaft_materials_cost = self.shaft_material.cost * self.shaft_weight
        grip_materials_cost = self.grip_material.cost * self.grip_weight
        accent_materials_cost = self.accent_material.cost * self.accent_weight

        #Crafting costs. 1 day skilled labor = ~5 material cost
        main_crafting_cost = self.main_material.craft_diff * self.main_weight * self.craft_diff
        shaft_crafting_cost = self.shaft_material.craft_diff * self.shaft_weight
        grip_crafting_cost = self.grip_material.craft_diff * self.grip_weight
        accent_crafting_cost = self.accent_material.craft_diff * self.accent_weight


        self.cost = main_crafting_cost + main_materials_cost + shaft_crafting_cost + shaft_materials_cost + grip_crafting_cost + grip_materials_cost + accent_crafting_cost + accent_materials_cost
        
        self.normality = self.main_material.normality * self.shaft_material.normality * self.grip_material.normality * self.accent_material.normality
        
class Attack():
    def __init__(self, weapon, **kwargs):
        self.name = ''
        self.weapon = weapon
        self.skill = []
        self.attack_mod = 0
        self.parry_mod = 0 #Modifier to OPPONENT'S parry chance
        self.stamina = 0
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 0
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = True #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [] #Angles that are allowed as a clockwise index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. S->N with an uppercut)
        self.allowed_angles_l = [] #Angles that are allowed as a clockwise index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. S->N with an uppercut)
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.added_mass = 0 #Dynamicly assigned
        self.main_area = 0 #Dynamicly assigned
        self.mech_adv = 1 #Dynamicly assigned
        self.shape = '' #Dynamicly assigned
        self.main_shape = self.weapon.main_shape
        self.main_length = self.weapon.main_length
        self.avg_main_width = self.weapon.avg_main_width
        self.main_depth = self.weapon.main_depth
        self.avg_main_depth = self.weapon.avg_main_depth
        self.main_width = self.weapon.main_width
        self.main_material = self.weapon.main_material
        self.shaft_material = self.weapon.shaft_material
        self.shaft_length = self.weapon.shaft_length
        self.accent_material = self.weapon.accent_material
        self.weight = self.weapon.weight
        self.axis_vs_com = self.weapon.axis_vs_com
        self.com_perc = self.weapon.com_perc #Center of Mass as a percentage
        self.main_num = self.weapon.main_num
        self.solidness = self.weapon.solidness #Used in damage calc
        self.sharpness = self.weapon.sharpness 
        self.pointedness = self.weapon.pointedness

        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

    def set_dynamic_attributes(self):
        #Set length
        if self.striker == 'main':
            self.length = self.main_length
        elif self.striker == 'shaft':
            self.length = self.shaft_length
        else:
            self.length = 0


        for t in self.damage_type:
            if t == 'b':
                if self.weapon.base_name == 'Halbard':
                    shape = 'flat'
                elif self.striker == 'main':
                    shape = self.main_shape
                    if shape in ['de blade', 'blade', 'curved blade']:
                        shape = 'flat'
                    elif shape == 'wedge':
                        if 'axe' in self.weapon.skill or self.weapon.base_name == 'Pole Axe':
                            shape = 'flat'
                else:
                    shape = 'round'

                if shape == 'wedge':
                    self.main_area = self.main_length * self.avg_main_depth
                    self.mech_adv =  self.main_width / self.main_depth
                elif shape == 'round':
                    #Basic hack, treating cylinders and spheres the same and basically making them truncated rectangles
                    #Tried to use Hertz's formula, but got wacky results
                    if self.striker == 'main':
                        material = self.main_material
                        width = self.main_width
                        length = self.main_length
                    elif self.striker == 'shaft':
                        material == self.shaft_material
                        width = 1
                        length = self.shaft_length
                    else:
                        material = self.accent_material
                        width = length = 2
                    self.solidness = (material.elasticity / 2) ** (1. / 3)
                    self.main_area = (min(length,8)*width)/8
                elif shape == 'flat':
                    self.main_area = min(self.main_depth,8) * min(self.main_width,8)

            elif t == 's':
                if self.main_shape in ['blade','curved blade']:
                    self.main_area = min(self.main_length, 12) * self.avg_main_depth
                    self.mech_adv =  self.main_width / self.main_depth
                elif self.main_shape == 'de blade':
                    self.main_area = min(self.main_length, 12) * self.avg_main_depth
                    self.mech_adv =  (self.main_width/2) / self.main_depth
            elif t == 'p':
                if self.striker == 'main' and self.weapon.base_name != 'Halbard':
                    shape = self.main_shape
                    length = self.main_length
                    depth = self.main_depth
                    width = self.main_width
                elif self.striker == 'shaft':
                    shape = 'point'
                    length = min(self.shaft_length, 12)
                    depth = width = self.weapon.shaft_diameter
                elif self.weapon.base_name == 'Halbard':
                    shape = 'point'
                    length = self.main_length / 2
                    depth = width = self.weapon.shaft_diameter
                else:
                    shape = 'point'
                    length = depth = width = self.weapon.shaft_diameter
                if shape in ['point', 'blade', 'de blade']:
                    wedge1 = length / width
                    wedge2 = width / depth
                    if shape in ['point', 'de blade']:
                        #Double each (since there are two wedges per side) and multiply for full MA of tip
                        self.mech_adv = (wedge1*2)*(wedge2*2)
                    else:
                        self.mech_adv = (wedge1)*(wedge2)
                    self.main_area = depth * length * width * self.main_num
            else:
                if self.main_shape == 'hook':
                    wedge1 = self.main_length / self.main_width
                    wedge2 = self.main_width / self.main_depth
                    #Double each (since there are two wedges per side) and multiply for full MA of tip
                    self.mech_adv = (wedge1*2)*(wedge2*2)
                    self.main_area = self.main_depth * self.main_width * self.main_num



        if self.damage_type in ['s','b']:
            self.stamina += int((self.weight*self.axis_vs_com)/2)
            self.base_ap += min(self.weight*10, (self.weight * 10)*self.axis_vs_com)
            self.added_mass = self.weight * self.com_perc
            self.attack_mod += (20 - ((self.weight*10) * self.com_perc))    
            self.parry_mod -= ((self.weight*10) * self.com_perc) 

            if self.main_num > 1:
                self.attack_mod += self.main_num * 5
                self.parry_mod -= self.main_num * 20
        else:
            self.stamina += self.weight/5
            self.base_ap += self.weight * 5
            self.added_mass = self.weight/10

            if self.damage_type == 'p':
                self.attack_mod -= self.weight/10
                self.parry_mod -= self.weight * 5

            self.attack_mod += -5 + (self.main_num * 5)
            self.parry_mod -= self.main_num * 20

class Guard():
    def __init__(self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = [], rh_default = False, lh_default = False, desc = ''):
        self.name = name
        self.desc = desc
        self.loc_hit_mods = loc_hit_mods #A dict in 'location name':mod format with mods to hit chance based on location
        self.hit_mod = hit_mod
        self.dodge_mod = dodge_mod
        self.parry_mod = parry_mod
        self.req_locs = req_locs #A list of locs required to be functional to use the guard
        self.auto_block = auto_block #A list of locations autoblocked
        self.rh_default = rh_default
        self.lh_default = lh_default  

class Jab(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Jab/Cross"
        self.weapon = weapon
        self.skill = ['brawling', 'martial_arts', 'boxing']
        self.attack_mod = 0
        self.parry_mod = 0 #Modifier to OPPONENT'S parry chance
        self.stamina = 1
        self.force_scalar = .8 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 3
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [0] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Haymaker(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Haymaker"
        self.weapon = weapon
        self.skill = ['brawling', 'boxing']
        self.attack_mod = -20
        self.parry_mod = 20 #Modifier to OPPONENT'S parry chance
        self.stamina = 3
        self.force_scalar = 1.5 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 12
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = True #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [27,28] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [2,3,4] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()
        
class Hook(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Hook"
        self.weapon = weapon
        self.skill = ['martial_arts', 'boxing']
        self.attack_mod = -10
        self.parry_mod = 10 #Modifier to OPPONENT'S parry chance
        self.stamina = 2
        self.force_scalar = 1.3 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 10
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = True #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [27,28] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [2,3,4] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Uppercut(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Uppercut"
        self.weapon = weapon
        self.skill = ['brawling', 'martial_arts', 'boxing']
        self.attack_mod = -20
        self.parry_mod = 0 #Modifier to OPPONENT'S parry chance
        self.stamina = 2
        self.force_scalar = 1.2 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 10
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [0,2,3,4,7,8,11,12,15,16,19,20,21,22,23,24,25,26,27,28] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [3,4] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [5,4] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)

        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Hammerfist(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Hammer Fist"
        self.weapon = weapon
        self.skill = ['brawling', 'martial_arts', 'boxing']
        self.attack_mod = 0
        self.parry_mod = -20 #Modifier to OPPONENT'S parry chance
        self.stamina = 1
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 5
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [2,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [7,0,1] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [7,0,1] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Elbow_Strike(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Elbow Strike"
        self.weapon = weapon
        self.skill = ['brawling', 'martial_arts']
        self.attack_mod = -20
        self.parry_mod = -20 #Modifier to OPPONENT'S parry chance
        self.stamina = 1
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'accent'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 5
        self.hand = True
        self.length = -10 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = True #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [27,28] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,7,6,5] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Front_Kick(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Front Kick"
        self.weapon = weapon
        self.skill = ['brawling', 'martial_arts']
        self.attack_mod = -10
        self.parry_mod = 10 #Modifier to OPPONENT'S parry chance
        self.stamina = 2
        self.force_scalar = 1.2 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 0
        self.damage_type = 'b'
        self.base_ap = 13
        self.hand = False
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [0,27,28] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [3,4,5,8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [3,4,5,8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Roundhouse_Kick(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Roundhouse Kick"
        self.weapon = weapon
        self.skill = ['brawling', 'martial_arts']
        self.attack_mod = 10
        self.parry_mod = 20 #Modifier to OPPONENT'S parry chance
        self.stamina = 5
        self.force_scalar = 1.8 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 0
        self.damage_type = 'b'
        self.base_ap = 15
        self.hand = False
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [0,27,28] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [2,3] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [5,6] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Side_Kick(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Side Kick"
        self.weapon = weapon
        self.skill = ['brawling', 'martial_arts']
        self.attack_mod = -20
        self.parry_mod = 10 #Modifier to OPPONENT'S parry chance
        self.stamina = 3
        self.force_scalar = 1.6 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 0
        self.damage_type = 'b'
        self.base_ap = 10
        self.hand = False
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [0,27,28] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [8,4] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [8,4] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Stomp(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Stomp"
        self.weapon = weapon
        self.skill = ['brawling', 'martial_arts']
        self.attack_mod = 20
        self.parry_mod = 0 #Modifier to OPPONENT'S parry chance
        self.stamina = 1
        self.force_scalar = 1.5 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 0
        self.damage_type = 'b'
        self.base_ap = 5
        self.hand = False
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [7,1,2] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [7,1,2] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Knee_Strike(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Knee Strike"
        self.weapon = weapon
        self.skill = ['brawling', 'martial_arts']
        self.attack_mod = -30
        self.parry_mod = -10 #Modifier to OPPONENT'S parry chance
        self.stamina = 1
        self.force_scalar = 1.2 #Used to adjust force/damage for the attack
        self.striker = 'accent'
        self.hands = 0
        self.damage_type = 'b'
        self.base_ap = 8
        self.hand = False
        self.length = -15 #Used to add or subtract from base weapon length for added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [0,2,27,28] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [3,4] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [4,5] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Slash(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Slash"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = -20
        self.parry_mod = 20 #Modifier to OPPONENT'S parry chance
        self.stamina = 6
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 's'
        self.base_ap = 15
        self.hand = True
        self.length = weapon.main_length #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Slash_2H(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Two-Handed Slash"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = -10
        self.parry_mod = 10 #Modifier to OPPONENT'S parry chance
        self.stamina = 8
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 2
        self.damage_type = 's'
        self.base_ap = 20
        self.hand = True
        self.length = weapon.main_length #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Stab(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Stab"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = -10
        self.parry_mod = -10 #Modifier to OPPONENT'S parry chance
        self.stamina = 3
        self.force_scalar = .3 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'p'
        self.base_ap = 7
        self.hand = True
        self.length = weapon.main_length #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [0] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Pommel_Strike(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Pommel Strike"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = 0
        self.parry_mod = -10 #Modifier to OPPONENT'S parry chance
        self.stamina = 3
        self.force_scalar = .5 #Used to adjust force/damage for the attack
        self.striker = 'accent'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 5
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)

        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Tip_Strike(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Tip Strike"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = 0
        self.parry_mod = 0 #Modifier to OPPONENT'S parry chance
        self.stamina = 5
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 2
        self.damage_type = weapon.damage_type
        self.base_ap = 15
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)

        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Shaft_Strike(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Shaft Strike"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = 0
        self.parry_mod = -10 #Modifier to OPPONENT'S parry chance
        self.stamina = 5
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'shaft'
        self.hands = 2
        self.damage_type = 'b'
        self.base_ap = 15
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)

        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Thrust(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Thrust"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = -20
        self.parry_mod = -10 #Modifier to OPPONENT'S parry chance
        self.stamina = 3
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 2
        self.damage_type = weapon.damage_type
        self.base_ap = 8
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)

        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Axe_Hammer(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Axe Hammer"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = -20
        self.parry_mod = 20 #Modifier to OPPONENT'S parry chance
        self.stamina = 6
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 15
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)

        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Horn_Thrust(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Horn Thrust"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = -30
        self.parry_mod = -20 #Modifier to OPPONENT'S parry chance
        self.stamina = 3
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'p'
        self.base_ap = 7
        self.hand = True
        self.length = weapon.main_length #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [0] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Swing(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Swing"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = 0
        self.parry_mod = -20 #Modifier to OPPONENT'S parry chance
        self.stamina = 6
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'b'
        self.base_ap = 15
        self.hand = True
        self.length = weapon.main_length #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Swing_2H(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Two-Handed Swing"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = -10
        self.parry_mod = 0 #Modifier to OPPONENT'S parry chance
        self.stamina = 8
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 2
        self.damage_type = 'b'
        self.base_ap = 20
        self.hand = True
        self.length = weapon.main_length #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Impale(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Impale"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = 0
        self.parry_mod = -40 #Modifier to OPPONENT'S parry chance
        self.stamina = 8
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'p'
        self.base_ap = 20
        self.hand = True
        self.length = weapon.main_length #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Impale_2H(Attack):
    def __init__(self, weapon, **kwargs):
        Attack.__init__(self, weapon)

        self.name = "Two-Handed Impale"
        self.weapon = weapon
        self.skill = [weapon.skill]
        self.attack_mod = 0
        self.parry_mod = -60 #Modifier to OPPONENT'S parry chance
        self.stamina = 12
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 2
        self.damage_type = 'p'
        self.base_ap = 25
        self.hand = True
        self.length = weapon.main_length #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,1,2,3,4,5,6,7] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Unarmed(Weapon):

    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'unarmed'
        self.shafted = False #Used to determine if wpn has a shaft
        self.allowed_main_materials = [m_tissue] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_bone #Damage component (blade, head, etc) material
        self.shaft_material = m_bone
        self.grip_material = m_bone
        self.accent_material = m_bone
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Unarmed'
        self.skill = 'brawling' #This is the default skill used for the weapon. String
        self.length = 3
        self.avg_main_width = 2 #1.25 average longsword
        self.main_width = 2 #Absolute width at widest point
        self.avg_main_depth = 2 #.14 is average for a sword blade
        self.main_depth = 2 #Absolute depth at deepest point
        self.main_shape = 'flat' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.accent_cuin = 4 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .5 #Center of mass for the main weapon component
        self.main_loc = 0 #Location along the total length for the main weapon component
        self.grip_loc = 0 #location along the total length for the grip
        self.main_length = 3
        
        self.damage_type = 'b'

        self.main_length = 3      

        for key in self.__dict__:
            for k in kwargs:
                if k == key:
                    self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below
        
        self.base_attacks = [Jab,Hammerfist,Haymaker,Hook,Uppercut,Elbow_Strike,Front_Kick,Roundhouse_Kick,Side_Kick,Knee_Strike,Stomp]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.conventional = Guard('Conventional', {'Face': -10, 'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20}, 0, 0, 0, [7,8,11,12,15,16], [9,10], 
                                True, desc = 'Minor face protection, good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, to-hit and parry chances. \n\nAuto-blocks ribs.')
        self.southpaw = Guard('Southpaw', {'Face': -10, 'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20}, 0, 0, 0, [7,8,11,12,15,16],[9,10], 
                                False, True, desc = 'Minor face protection, good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, to-hit and parry chances. \n\nAuto-blocks ribs.')
        self.high = Guard('High', {'Scalp': -20, 'Face': -30, 'Neck': -60, 'R Chest': -40, 'L Chest': -40, 'R Ribs': -20, 'L Ribs': -20, 'R Elbow': 20, 'L Elbow': 20, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20}, -10, -20, 20, [7,8,11,12,15,16], [0,1,2,5,6], 
                                desc = 'Good head protection, very good neck protection, good upper body protection, exposes arms. \n\n-20 to dodge, -10 to-hit and +20 parry chances. \n\nAuto-blocks head, neck, and chest.')
        self.low = Guard('Low', {'Scalp': 20, 'Face': -10, 'Neck': -80, 'R Chest': -80, 'L Chest': -80, 'R Ribs': -80, 'L Ribs': -80, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20, 'R Abdomen': -60, 'L Abdomen': -60}, -20, -10, 20, [7,8,11,12,15,16], [2,5,6,9,10,13,14], 
                                desc = 'Minor face protection, excellent neck protection, excellent core protection, exposes scalp and arms. \n\n-10 to dodge, -20 to-hit and +20 to parry chances. \n\nAuto-blocks neck and center torso.')
        self.half_l = Guard('Half, L lead', {'Neck': -10, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'R Ribs': -60, 
                                'R Elbow': -60, 'R Forearm': -60, 'R Hand': -60}, 20, 20, 0, [7,11,15], [9, 10],
                                desc = 'Minor neck protection, good right-side protection, exposes left shoulder. \n\n+20 to dodge, +20 to-hit and neutral parry chances. \n\nAuto-blocks ribs.')
        self.half_r = Guard('Half, R lead', {'Neck': -10, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'L Ribs': -60, 
                                'L Elbow': -60, 'L Forearm': -60, 'L Hand': -60}, 20, 20, 0, [7,11,15], [9, 10],
                                desc = 'Minor neck protection, good left-side protection, exposes right shoulder. \n\n+20 to dodge, +20 to-hit and neutral parry chances. \n\nAuto-blocks ribs.')
        self.guards = [self.conventional, self.southpaw, self.high, self.low, self.half_l, self.half_r]
        self.base_maneuvers = [Headbutt,Tackle,Push,Trip,Bearhug,Collar_Tie,Limb_Capture,Wind_Choke,Strangle_Hold,Compression_Lock,Blood_Choke,Joint_Lock,Neck_Crank,Reap,Sacrifice_Throw,Hip_Throw,Shoulder_Throw,Single_Leg_Takedown,Double_Leg_Takedown]

class De_Medium_Sword(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'de_medium_sword'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (30,47) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.15,0.3)
        self.main_avg_depth_range = (0.07,0.2)
        self.main_width_range = (0.7,5)
        self.main_avg_width_range = (0.5,4)
        self.length_range = (35,51)
        self.shaft_length_range = (4,9) 
        self.shaft_diameter_range = (0.5,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = -20
        self.parry_mod = 30 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1,2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Hand and a Half Sword'
        self.bname_variants = ['Longsword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'long_sword' #This is the default skill used for the weapon. String
        self.main_length = 39
        self.shaft_length = 6 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1.25 #1.25 average longsword
        self.main_width = 1.5 #Absolute width at widest point
        self.avg_main_depth = .14 #.14 is average for a sword blade
        self.main_depth =  .2 #Absolute depth at deepest point
        self.main_shape = 'de blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 7 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .33 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash, Slash_2H, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ox_r = Guard('Hanging, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ox_l = Guard('Hanging, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.plow_r = Guard('Middle, Right-handed', {'Neck': -20, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': -40, 'R Abdomen': -80, 'R Hip': -80, 'L Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, very good right side protection, exposes left side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks left upper body and hands.')
        self.plow_l = Guard('Middle, Left-handed', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -80, 'L Hip': -80, 'R Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, very good left side protection, exposes right side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks right upper body and hands.')
        self.low = Guard('Low', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'L Elbow': -40, 'R Elbow': 20, 'L Forearm': -20, 'R Forearm': 20, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -20, 'L Hip': -80, 'R Hip': -40}, 0, 30, -10, [7,8,11,12,15,16,19,20], 
                                [23,24,25,26,27,28], desc = 'Minor neck protection, very good left side protection, exposes right side. \n\nNeutral to hit, +30 to dodge, -10 to parry chances. \n\nAuto-blocks lower legs.')
        self.high = Guard('High', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -20, 'L Chest': 20, 'Up R Arm': -20, 'Up L Arm': 40, 'R Ribs': -20, 
                                'L Ribs': 20, 'L Elbow': 40, 'R Forearm': -20, 'L Forearm': 20, 'R Hand': -20, 'L Hand': -20, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': 20, 'R Abdomen': -20, 'R Hip': -80, 'L Hip': -20}, 20, 10, 10, [7,8,11,12,15,16,19,20], 
                                [19,20], desc = 'Good neck protection, very good right side protection, exposes left side. \n\n+20 to hit, +10 to dodge, +10 to parry chances. \n\nAuto-blocks head.')
        self.guards = [self.ox_l, self.ox_r, self.plow_l, self.plow_r, self.low, self.high]
        self.base_maneuvers = []
        self.maneuvers = [] 

class Se_Medium_Sword(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'se_medium_sword'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (30,47) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.15,0.3)
        self.main_avg_depth_range = (0.07,0.2)
        self.main_width_range = (0.7,4)
        self.main_avg_width_range = (0.5,3.5)
        self.length_range = (35,51)
        self.shaft_length_range = (4,9) 
        self.shaft_diameter_range = (0.5,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = -20
        self.parry_mod = 30 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1,2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Falchion'
        self.bname_variants = ['Katana', 'Falchion', 'Badelaire', 'Kamplain'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'long_sword' #This is the default skill used for the weapon. String
        self.main_length = 39
        self.shaft_length = 6 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1.5  #1.25 average longsword
        self.main_width = 2 #Absolute width at widest point
        self.avg_main_depth = .14 #.14 is average for a sword blade
        self.main_depth = .2 #Absolute depth at deepest point
        self.main_shape = 'blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 7 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .35 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash, Slash_2H, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ox_r = Guard('Hanging, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ox_l = Guard('Hanging, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.plow_r = Guard('Middle, Right-handed', {'Neck': -20, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': -40, 'R Abdomen': -80, 'R Hip': -80, 'L Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, very good right side protection, exposes left side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks left upper body and hands.')
        self.plow_l = Guard('Middle, Left-handed', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -80, 'L Hip': -80, 'R Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, very good left side protection, exposes right side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks right upper body and hands.')
        self.low = Guard('Low', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'L Elbow': -40, 'R Elbow': 20, 'L Forearm': -20, 'R Forearm': 20, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -20, 'L Hip': -80, 'R Hip': -40}, 0, 30, -10, [7,8,11,12,15,16,19,20], 
                                [23,24,25,26,27,28], desc = 'Minor neck protection, very good left side protection, exposes right side. \n\nNeutral to hit, +30 to dodge, -10 to parry chances. \n\nAuto-blocks lower legs.')
        self.high = Guard('High', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -20, 'L Chest': 20, 'Up R Arm': -20, 'Up L Arm': 40, 'R Ribs': -20, 
                                'L Ribs': 20, 'L Elbow': 40, 'R Forearm': -20, 'L Forearm': 20, 'R Hand': -20, 'L Hand': -20, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': 20, 'R Abdomen': -20, 'R Hip': -80, 'L Hip': -20}, 20, 10, 10, [7,8,11,12,15,16,19,20], 
                                [19,20], desc = 'Good neck protection, very good right side protection, exposes left side. \n\n+20 to hit, +10 to dodge, +10 to parry chances. \n\nAuto-blocks head.')
        self.guards = [self.ox_l, self.ox_r, self.plow_l, self.plow_r, self.low, self.high]
        self.base_maneuvers = []
        self.maneuvers = []

class Sec_Medium_Sword(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'sec_medium_sword'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (20,40) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.15,0.3)
        self.main_avg_depth_range = (0.07,0.2)
        self.main_width_range = (1.2,4)
        self.main_avg_width_range = (0.5,3.5)
        self.length_range = (24,49)
        self.shaft_length_range = (4,9) 
        self.shaft_diameter_range = (0.5,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = -40
        self.parry_mod = 0 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1,2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Scimitar'
        self.bname_variants = ['Scimitar', 'Sabre', 'Khopesh', 'Talwar', 'Scythe Sword'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'long_sword' #This is the default skill used for the weapon. String
        self.main_length = 26
        self.shaft_length = 6 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1.5  #1.25 average longsword
        self.main_width = 2 #Absolute width at widest point
        self.avg_main_depth = .14 #.14 is average for a sword blade
        self.main_depth =  .2 #Absolute depth at deepest point
        self.main_shape = 'curved blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 7 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .49 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash, Slash_2H, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ox_r = Guard('Hanging, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ox_l = Guard('Hanging, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.plow_r = Guard('Middle, Right-handed', {'Neck': -20, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': -40, 'R Abdomen': -80, 'R Hip': -80, 'L Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, very good right side protection, exposes left side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks left upper body and hands.')
        self.plow_l = Guard('Middle, Left-handed', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -80, 'L Hip': -80, 'R Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, very good left side protection, exposes right side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks right upper body and hands.')
        self.low = Guard('Low', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'L Elbow': -40, 'R Elbow': 20, 'L Forearm': -20, 'R Forearm': 20, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -20, 'L Hip': -80, 'R Hip': -40}, 0, 30, -10, [7,8,11,12,15,16,19,20], 
                                [23,24,25,26,27,28], desc = 'Minor neck protection, very good left side protection, exposes right side. \n\nNeutral to hit, +30 to dodge, -10 to parry chances. \n\nAuto-blocks lower legs.')
        self.high = Guard('High', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -20, 'L Chest': 20, 'Up R Arm': -20, 'Up L Arm': 40, 'R Ribs': -20, 
                                'L Ribs': 20, 'L Elbow': 40, 'R Forearm': -20, 'L Forearm': 20, 'R Hand': -20, 'L Hand': -20, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': 20, 'R Abdomen': -20, 'R Hip': -80, 'L Hip': -20}, 20, 10, 10, [7,8,11,12,15,16,19,20], 
                                [19,20], desc = 'Good neck protection, very good right side protection, exposes left side. \n\n+20 to hit, +10 to dodge, +10 to parry chances. \n\nAuto-blocks head.')
        self.guards = [self.ox_l, self.ox_r, self.plow_l, self.plow_r, self.low, self.high]
        self.base_maneuvers = []
        self.maneuvers = []

class De_Short_Sword(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'de_short_sword'

        self.allowed_main_materials = [m_copper,m_bronze,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (12,28) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.2,0.5)
        self.main_avg_depth_range = (0.1,0.3)
        self.main_width_range = (2,4)
        self.main_avg_width_range = (1,2)
        self.length_range = (16,34)
        self.shaft_length_range = (4,6) 
        self.shaft_diameter_range = (0.5,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = 0
        self.parry_mod = 20 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Short Sword'
        self.bname_variants = ['Short Sword', 'Gladius', 'Xiphos', 'Jian', 'Spatha', 'Tsurugi', 'Cinquedea', 'Katzbalger'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'short_sword' #This is the default skill used for the weapon. String
        self.main_length = 28
        self.shaft_length = 6 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2 #1.25 average longsword
        self.main_width = 2.5 #Absolute width at widest point
        self.avg_main_depth = .2 #.14 is average for a sword blade 
        self.main_depth =  .3 #Absolute depth at deepest point 
        self.main_shape = 'de blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 5 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .19 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ox_r = Guard('Hanging, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ox_l = Guard('Hanging, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.plow_r = Guard('Middle, Right-handed', {'Neck': -20, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': -40, 'R Abdomen': -80, 'R Hip': -80, 'L Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, very good right side protection, exposes left side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks left upper body and hands.')
        self.plow_l = Guard('Middle, Left-handed', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -80, 'L Hip': -80, 'R Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, very good left side protection, exposes right side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks right upper body and hands.')
        self.low = Guard('Low', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'L Elbow': -40, 'R Elbow': 20, 'L Forearm': -20, 'R Forearm': 20, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -20, 'L Hip': -80, 'R Hip': -40}, 0, 30, -10, [7,8,11,12,15,16,19,20], 
                                [23,24,25,26,27,28], desc = 'Minor neck protection, very good left side protection, exposes right side. \n\nNeutral to hit, +30 to dodge, -10 to parry chances. \n\nAuto-blocks lower legs.')
        self.high = Guard('High', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -20, 'L Chest': 20, 'Up R Arm': -20, 'Up L Arm': 40, 'R Ribs': -20, 
                                'L Ribs': 20, 'L Elbow': 40, 'R Forearm': -20, 'L Forearm': 20, 'R Hand': -20, 'L Hand': -20, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': 20, 'R Abdomen': -20, 'R Hip': -80, 'L Hip': -20}, 20, 10, 10, [7,8,11,12,15,16,19,20], 
                                [19,20], desc = 'Good neck protection, very good right side protection, exposes left side. \n\n+20 to hit, +10 to dodge, +10 to parry chances. \n\nAuto-blocks head.')
        self.guards = [self.ox_l, self.ox_r, self.plow_l, self.plow_r, self.low, self.high]
        self.base_maneuvers = []
        self.maneuvers = [] 

class Se_Short_Sword(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'se_short_sword'

        self.allowed_main_materials = [m_copper,m_bronze,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (12,28) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.2,0.5)
        self.main_avg_depth_range = (0.07,0.25)
        self.main_width_range = (1,3)
        self.main_avg_width_range = (1,2)
        self.length_range = (16,34)
        self.shaft_length_range = (4,6) 
        self.shaft_diameter_range = (0.5,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = 10
        self.parry_mod = 10 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Cutlass'
        self.bname_variants = ['Machete', 'Seax', 'Makhaira', 'Kodachi', 'Wakizashi', 'Ninjato', 'Messer', 'Dha', 'Cutlass', 'Yatagan'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'short_sword' #This is the default skill used for the weapon. String
        self.main_length = 28
        self.shaft_length = 6 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1.25 #1.25 average longsword
        self.main_width = 1.5 #Absolute width at widest point
        self.avg_main_depth = .14 #.14 is average for a sword blade 
        self.main_depth =  .2 #Absolute depth at deepest point 
        self.main_shape = 'blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 5 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .27 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ox_r = Guard('Hanging, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ox_l = Guard('Hanging, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.plow_r = Guard('Middle, Right-handed', {'Neck': -20, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': -40, 'R Abdomen': -80, 'R Hip': -80, 'L Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, very good right side protection, exposes left side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks left upper body and hands.')
        self.plow_l = Guard('Middle, Left-handed', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -80, 'L Hip': -80, 'R Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, very good left side protection, exposes right side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks right upper body and hands.')
        self.low = Guard('Low', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'L Elbow': -40, 'R Elbow': 20, 'L Forearm': -20, 'R Forearm': 20, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -20, 'L Hip': -80, 'R Hip': -40}, 0, 30, -10, [7,8,11,12,15,16,19,20], 
                                [23,24,25,26,27,28], desc = 'Minor neck protection, very good left side protection, exposes right side. \n\nNeutral to hit, +30 to dodge, -10 to parry chances. \n\nAuto-blocks lower legs.')
        self.high = Guard('High', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -20, 'L Chest': 20, 'Up R Arm': -20, 'Up L Arm': 40, 'R Ribs': -20, 
                                'L Ribs': 20, 'L Elbow': 40, 'R Forearm': -20, 'L Forearm': 20, 'R Hand': -20, 'L Hand': -20, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': 20, 'R Abdomen': -20, 'R Hip': -80, 'L Hip': -20}, 20, 10, 10, [7,8,11,12,15,16,19,20], 
                                [19,20], desc = 'Good neck protection, very good right side protection, exposes left side. \n\n+20 to hit, +10 to dodge, +10 to parry chances. \n\nAuto-blocks head.')
        self.guards = [self.ox_l, self.ox_r, self.plow_l, self.plow_r, self.low, self.high]
        self.base_maneuvers = []
        self.maneuvers = [] 

class Sec_Short_Sword(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'sec_short_sword'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (12,28) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.1,0.5)
        self.main_avg_depth_range = (0.07,0.25)
        self.main_width_range = (2,4)
        self.main_avg_width_range = (1,3)
        self.length_range = (16,34)
        self.shaft_length_range = (4,6) 
        self.shaft_diameter_range = (0.5,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = 0
        self.parry_mod = -10 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Falcata'
        self.bname_variants = ['Kukri', 'Falcata', 'Kopis', 'Kora', 'Kilij'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'short_sword' #This is the default skill used for the weapon. String
        self.main_length = 20
        self.shaft_length = 4 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2.25 #1.25 average longsword
        self.main_width = 3 #Absolute width at widest point
        self.avg_main_depth = .14 #.14 is average for a sword blade 
        self.main_depth =  .2 #Absolute depth at deepest point 
        self.main_shape = 'curved blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 3 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .22 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ox_r = Guard('Hanging, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ox_l = Guard('Hanging, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.plow_r = Guard('Middle, Right-handed', {'Neck': -20, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': -40, 'R Abdomen': -80, 'R Hip': -80, 'L Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, very good right side protection, exposes left side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks left upper body and hands.')
        self.plow_l = Guard('Middle, Left-handed', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -80, 'L Hip': -80, 'R Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, very good left side protection, exposes right side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks right upper body and hands.')
        self.low = Guard('Low', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'L Elbow': -40, 'R Elbow': 20, 'L Forearm': -20, 'R Forearm': 20, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -20, 'L Hip': -80, 'R Hip': -40}, 0, 30, -10, [7,8,11,12,15,16,19,20], 
                                [23,24,25,26,27,28], desc = 'Minor neck protection, very good left side protection, exposes right side. \n\nNeutral to hit, +30 to dodge, -10 to parry chances. \n\nAuto-blocks lower legs.')
        self.high = Guard('High', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -20, 'L Chest': 20, 'Up R Arm': -20, 'Up L Arm': 40, 'R Ribs': -20, 
                                'L Ribs': 20, 'L Elbow': 40, 'R Forearm': -20, 'L Forearm': 20, 'R Hand': -20, 'L Hand': -20, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': 20, 'R Abdomen': -20, 'R Hip': -80, 'L Hip': -20}, 20, 10, 10, [7,8,11,12,15,16,19,20], 
                                [19,20], desc = 'Good neck protection, very good right side protection, exposes left side. \n\n+20 to hit, +10 to dodge, +10 to parry chances. \n\nAuto-blocks head.')
        self.guards = [self.ox_l, self.ox_r, self.plow_l, self.plow_r, self.low, self.high]
        self.base_maneuvers = []
        self.maneuvers = [] 

class De_Great_Sword(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'de_great_sword'

        self.allowed_main_materials = [m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (41,70) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.15,0.3)
        self.main_avg_depth_range = (0.1,0.2)
        self.main_width_range = (2,3)
        self.main_avg_width_range = (1.5,2.5)
        self.length_range = (51,88)
        self.shaft_length_range = (10,18) 
        self.shaft_diameter_range = (1,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = -30
        self.parry_mod = -20 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Greatsword'
        self.bname_variants = ['Greatsword', 'Two-handed Sword', 'Claymore', 'Estoc', 'Flamberge'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'great_sword' #This is the default skill used for the weapon. String
        self.main_length = 54
        self.shaft_length = 11 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1.5 #1.25 average longsword
        self.main_width = 2 #Absolute width at widest point
        self.avg_main_depth = .15 #.14 is average for a sword blade 
        self.main_depth =  .18 #Absolute depth at deepest point 
        self.main_shape = 'de blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 9 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .54 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash_2H, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ox_r = Guard('Hanging, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [17,8,11,12,15,16,19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ox_l = Guard('Hanging, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [7,8,11,12,15,16,19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.plow_r = Guard('Middle, Right-handed', {'Neck': -20, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': -40, 'R Abdomen': -80, 'R Hip': -80, 'L Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [7,8,11,12,15,16,19,20], True, desc = 'Minor neck protection, very good right side protection, exposes left side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks left upper body and hands.')
        self.plow_l = Guard('Middle, Left-handed', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -80, 'L Hip': -80, 'R Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [7,8,11,12,15,16,19,20], False, True, desc = 'Minor neck protection, very good left side protection, exposes right side. \n\n+10 to hit, +20 to dodge, neutral parry chances. \n\nAuto-blocks right upper body and hands.')
        self.low = Guard('Low', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'L Elbow': -40, 'R Elbow': 20, 'L Forearm': -20, 'R Forearm': 20, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -20, 'L Hip': -80, 'R Hip': -40}, 0, 30, -10, [7,8,11,12,15,16,19,20], 
                                [7,8,11,12,15,16,19,20], desc = 'Minor neck protection, very good left side protection, exposes right side. \n\nNeutral to hit, +30 to dodge, -10 to parry chances. \n\nAuto-blocks lower legs.')
        self.high = Guard('High', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -20, 'L Chest': 20, 'Up R Arm': -20, 'Up L Arm': 40, 'R Ribs': -20, 
                                'L Ribs': 20, 'L Elbow': 40, 'R Forearm': -20, 'L Forearm': 20, 'R Hand': -20, 'L Hand': -20, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': 20, 'R Abdomen': -20, 'R Hip': -80, 'L Hip': -20}, 20, 10, 10, [7,8,11,12,15,16,19,20], 
                                [7,8,11,12,15,16,19,20], desc = 'Good neck protection, very good right side protection, exposes left side. \n\n+20 to hit, +10 to dodge, +10 to parry chances. \n\nAuto-blocks head.')
        self.guards = [self.ox_l, self.ox_r, self.plow_l, self.plow_r, self.low, self.high]
        self.base_maneuvers = []
        self.maneuvers = [] 

class De_Dagger(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'de_dagger'

        self.allowed_main_materials = [m_copper,m_bronze,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (8,15) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.1,0.2)
        self.main_avg_depth_range = (0.07,0.15)
        self.main_width_range = (.5,2)
        self.main_avg_width_range = (.3,1.5)
        self.length_range = (12,20)
        self.shaft_length_range = (4,5) 
        self.shaft_diameter_range = (.5,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = +20
        self.parry_mod = -20 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Dagger'
        self.bname_variants = ['Dirk', 'Dagger', 'Stiletto', 'Baselard', 'Kris'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'dagger' #This is the default skill used for the weapon. String
        self.main_length = 12
        self.shaft_length = 4 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = .7 #1.25 average longsword
        self.main_width = 1 #Absolute width at widest point
        self.avg_main_depth = .12 #.14 is average for a sword blade 
        self.main_depth =  .18 #Absolute depth at deepest point 
        self.main_shape = 'de blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 1 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .4 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'

       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.conventional = Guard('Conventional', {'Face': -10, 'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20}, 0, 0, 0, [7,8,11,12,15,16], [9,10], 
                                True, desc = 'Minor face protection, good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, to-hit and parry chances. \n\nAuto-blocks ribs.')
        self.southpaw = Guard('Southpaw', {'Face': -10, 'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20}, 0, 0, 0, [7,8,11,12,15,16],[9,10], 
                                False, True, desc = 'Minor face protection, good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, to-hit and parry chances. \n\nAuto-blocks ribs.')
        self.high = Guard('High', {'Scalp': -20, 'Face': -30, 'Neck': -60, 'R Chest': -40, 'L Chest': -40, 'R Ribs': -20, 'L Ribs': -20, 'R Elbow': 20, 'L Elbow': 20, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20}, -10, -20, 20, [7,8,11,12,15,16], [0,1,2,5,6], 
                                desc = 'Good head protection, very good neck protection, good upper body protection, exposes arms. \n\n-20 to dodge, -10 to-hit and +20 parry chances. \n\nAuto-blocks head, neck, and chest.')
        self.low = Guard('Low', {'Scalp': 20, 'Face': -10, 'Neck': -80, 'R Chest': -80, 'L Chest': -80, 'R Ribs': -80, 'L Ribs': -80, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20, 'R Abdomen': -60, 'L Abdomen': -60}, -20, -10, 20, [7,8,11,12,15,16], [2,5,6,9,10,13,14], 
                                desc = 'Minor face protection, excellent neck protection, excellent core protection, exposes scalp and arms. \n\n-10 to dodge, -20 to-hit and +20 to parry chances. \n\nAuto-blocks neck and center torso.')
        self.half_l = Guard('Half, L lead', {'Neck': -10, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'R Ribs': -60, 
                                'R Elbow': -60, 'R Forearm': -60, 'R Hand': -60}, 20, 20, 0, [7,11,15], [9, 10],
                                desc = 'Minor neck protection, good right-side protection, exposes left shoulder. \n\n+20 to dodge, +20 to-hit and neutral parry chances. \n\nAuto-blocks ribs.')
        self.half_r = Guard('Half, R lead', {'Neck': -10, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'L Ribs': -60, 
                                'L Elbow': -60, 'L Forearm': -60, 'L Hand': -60}, 20, 20, 0, [7,11,15], [9, 10],
                                desc = 'Minor neck protection, good left-side protection, exposes right shoulder. \n\n+20 to dodge, +20 to-hit and neutral parry chances. \n\nAuto-blocks ribs.')
        self.guards = [self.conventional, self.southpaw, self.high, self.low, self.half_l, self.half_r]
        self.base_maneuvers = [Headbutt,Tackle,Push,Trip,Collar_Tie,Wind_Choke,Strangle_Hold,Blood_Choke,Neck_Crank,Reap,Sacrifice_Throw,Hip_Throw,Shoulder_Throw,Single_Leg_Takedown,Double_Leg_Takedown]

class Se_Knife(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'se_knife'

        self.allowed_main_materials = [m_copper,m_bronze,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (6,12) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.1,0.4)
        self.main_avg_depth_range = (0.08,0.3)
        self.main_width_range = (1,2)
        self.main_avg_width_range = (.8,1.6)
        self.length_range = (11,19)
        self.shaft_length_range = (5,7) 
        self.shaft_diameter_range = (.5,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_leather
        self.accent_material = m_steel
        self.attack_mod = +20
        self.parry_mod = -20 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'accent' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Knife'
        self.bname_variants = ['Knife', 'Tanto'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'dagger' #This is the default skill used for the weapon. String
        self.main_length = 11
        self.shaft_length = 5 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1 #1.25 average longsword
        self.main_width = 1.25 #Absolute width at widest point
        self.avg_main_depth = .16 #.14 is average for a sword blade 
        self.main_depth =  .2 #Absolute depth at deepest point 
        self.main_shape = 'blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .4 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = (self.shaft_length/(self.length/100))/100 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'

       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.conventional = Guard('Conventional', {'Face': -10, 'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20}, 0, 0, 0, [7,8,11,12,15,16], [9,10], 
                                True, desc = 'Minor face protection, good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, to-hit and parry chances. \n\nAuto-blocks ribs.')
        self.southpaw = Guard('Southpaw', {'Face': -10, 'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20}, 0, 0, 0, [7,8,11,12,15,16],[9,10], 
                                False, True, desc = 'Minor face protection, good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, to-hit and parry chances. \n\nAuto-blocks ribs.')
        self.high = Guard('High', {'Scalp': -20, 'Face': -30, 'Neck': -60, 'R Chest': -40, 'L Chest': -40, 'R Ribs': -20, 'L Ribs': -20, 'R Elbow': 20, 'L Elbow': 20, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20}, -10, -20, 20, [7,8,11,12,15,16], [0,1,2,5,6], 
                                desc = 'Good head protection, very good neck protection, good upper body protection, exposes arms. \n\n-20 to dodge, -10 to-hit and +20 parry chances. \n\nAuto-blocks head, neck, and chest.')
        self.low = Guard('Low', {'Scalp': 20, 'Face': -10, 'Neck': -80, 'R Chest': -80, 'L Chest': -80, 'R Ribs': -80, 'L Ribs': -80, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20, 'R Abdomen': -60, 'L Abdomen': -60}, -20, -10, 20, [7,8,11,12,15,16], [2,5,6,9,10,13,14], 
                                desc = 'Minor face protection, excellent neck protection, excellent core protection, exposes scalp and arms. \n\n-10 to dodge, -20 to-hit and +20 to parry chances. \n\nAuto-blocks neck and center torso.')
        self.half_l = Guard('Half, L lead', {'Neck': -10, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'R Ribs': -60, 
                                'R Elbow': -60, 'R Forearm': -60, 'R Hand': -60}, 20, 20, 0, [7,11,15], [9, 10],
                                desc = 'Minor neck protection, good right-side protection, exposes left shoulder. \n\n+20 to dodge, +20 to-hit and neutral parry chances. \n\nAuto-blocks ribs.')
        self.half_r = Guard('Half, R lead', {'Neck': -10, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'L Ribs': -60, 
                                'L Elbow': -60, 'L Forearm': -60, 'L Hand': -60}, 20, 20, 0, [7,11,15], [9, 10],
                                desc = 'Minor neck protection, good left-side protection, exposes right shoulder. \n\n+20 to dodge, +20 to-hit and neutral parry chances. \n\nAuto-blocks ribs.')
        self.guards = [self.conventional, self.southpaw, self.high, self.low, self.half_l, self.half_r]
        self.base_maneuvers = [Headbutt,Tackle,Push,Trip,Collar_Tie,Wind_Choke,Strangle_Hold,Blood_Choke,Neck_Crank,Reap,Sacrifice_Throw,Hip_Throw,Shoulder_Throw,Single_Leg_Takedown,Double_Leg_Takedown]

class Staff(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'staff'

        self.allowed_main_materials = [m_wood,m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (1,3) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.15,0.3)
        self.main_avg_depth_range = (0.15,0.3)
        self.main_width_range = (1,1.8)
        self.main_avg_width_range = (1,1.8)
        self.length_range = (72,144)
        self.shaft_length_range = (66,138) 
        self.shaft_diameter_range = (1,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_wood #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = 20
        self.parry_mod = 40 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Staff'
        self.bname_variants = ['Staff'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'staff' #This is the default skill used for the weapon. String
        self.main_length = 2
        self.shaft_length = 66 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.5
        self.shaft_num = 1
        self.pre_load = True #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2 #1.25 average longsword
        self.main_width = 2 #Absolute width at widest point
        self.avg_main_depth = .15 #.14 is average for a sword blade
        self.main_depth =  .15 #Absolute depth at deepest point
        self.main_shape = 'round' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .5 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = (self.length/100)/2 #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Tip_Strike,Shaft_Strike,Thrust]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Push,Weapon_Trip]
        self.maneuvers = [] 

class Spear(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'spear'

        self.allowed_main_materials = [m_wood,m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (6,20) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.1,0.5)
        self.main_avg_depth_range = (0.15,0.25)
        self.main_width_range = (1,4)
        self.main_avg_width_range = (.2,2)
        self.length_range = (60,120)
        self.shaft_length_range = (54,100) 
        self.shaft_diameter_range = (1,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = 20
        self.parry_mod = 40 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'shaft' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1,2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Spear'
        self.bname_variants = ['Spear','Hasta','Spetum','Boar Spear','Dory'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'spear' #This is the default skill used for the weapon. String
        self.main_length = 12
        self.shaft_length = 60 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = True #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = .16 #1.25 average longsword
        self.main_width = 2 #Absolute width at widest point
        self.avg_main_depth = .1 #.14 is average for a sword blade
        self.main_depth =  .2 #Absolute depth at deepest point
        self.main_shape = 'point' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .6 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = (self.length/100)/2 #location along the total length for the grip
        
        self.damage_type = 'p'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Stab,Shaft_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Push,Weapon_Trip]
        self.maneuvers = []

class Pike(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'pike'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (6,20) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.1,0.5)
        self.main_avg_depth_range = (0.15,0.25)
        self.main_width_range = (1,4)
        self.main_avg_width_range = (.2,2)
        self.length_range = (120,300)
        self.shaft_length_range = (114,280) 
        self.shaft_diameter_range = (1.3,2)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -20
        self.parry_mod = -80 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'none' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Pike'
        self.bname_variants = ['Pike','Sarissa','Partizan','Awl Pike'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'spear' #This is the default skill used for the weapon. String
        self.main_length = 12
        self.shaft_length = 168 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.5
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = .16 #1.25 average longsword
        self.main_width = 2 #Absolute width at widest point
        self.avg_main_depth = .1 #.14 is average for a sword blade
        self.main_depth =  .2 #Absolute depth at deepest point
        self.main_shape = 'point' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .52 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = (self.length/100)/2 #location along the total length for the grip
        
        self.damage_type = 'p'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Stab]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                      
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = []
        self.maneuvers = []

class Trident(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'trident'

        self.allowed_main_materials = [m_wood,m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (6,20) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.2,0.5)
        self.main_avg_depth_range = (0.15,0.4)
        self.main_width_range = (.2,.5)
        self.main_avg_width_range = (.15,.4)
        self.length_range = (60,120)
        self.shaft_length_range = (54,100) 
        self.shaft_diameter_range = (1,1.5)
        self.max_main_num = 3
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -20
        self.parry_mod = 0 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'shaft' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [1,2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Trident'
        self.bname_variants = ['Trident','Trishula','Fuscina'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'spear' #This is the default skill used for the weapon. String
        self.main_length = 12
        self.shaft_length = 60 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = True #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = .25 #1.25 average longsword
        self.main_width = .4 #Absolute width at widest point
        self.avg_main_depth = .25 #.14 is average for a sword blade
        self.main_depth =  .4 #Absolute depth at deepest point
        self.main_shape = 'point' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 3 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .7 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = (self.length/100)/2 #location along the total length for the grip
        
        self.damage_type = 'p'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Stab,Shaft_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Push,Weapon_Trip]
        self.maneuvers = []

class Small_Axe(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'small_axe'

        self.allowed_main_materials = [m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (2,4) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.5,2)
        self.main_avg_depth_range = (0.15,1)
        self.main_width_range = (2,6)
        self.main_avg_width_range = (2,6)
        self.length_range = (12,24)
        self.shaft_length_range = (10,20) 
        self.shaft_diameter_range = (.6,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -30
        self.parry_mod = -30 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Hand Axe'
        self.bname_variants = ['Hand Axe','Hatchet'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'small_axe' #This is the default skill used for the weapon. String
        self.main_length = 4
        self.shaft_length = 20 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = .8
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 4 #1.25 average longsword
        self.main_width = 4 #Absolute width at widest point
        self.avg_main_depth = .5 #.14 is average for a sword blade
        self.main_depth =  1 #Absolute depth at deepest point
        self.main_shape = 'wedge' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .7 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Axe_Hammer,Horn_Thrust,Slash]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = [Disarm,Deshield]
        self.maneuvers = []

class Large_Axe(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'large_axe'

        self.allowed_main_materials = [m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (6,12) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.5,2)
        self.main_avg_depth_range = (0.15,1)
        self.main_width_range = (6,10)
        self.main_avg_width_range = (1,8)
        self.length_range = (24,48)
        self.shaft_length_range = (18,36) 
        self.shaft_diameter_range = (.7,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -30
        self.parry_mod = -30 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Battle Axe'
        self.bname_variants = ['Battle Axe','Bearded Axe','Broad Axe'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'large_axe' #This is the default skill used for the weapon. String
        self.main_length = 6
        self.shaft_length = 36 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = .8
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1 #1.25 average longsword
        self.main_width = 8 #Absolute width at widest point
        self.avg_main_depth = .5 #.14 is average for a sword blade
        self.main_depth =  1 #Absolute depth at deepest point
        self.main_shape = 'wedge' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .77 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-12)/self.length) #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Axe_Hammer,Horn_Thrust,Slash_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = [Weapon_Trip,Hook_Neck,Disarm,Deshield]
        self.maneuvers = []

class Club(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'club'

        self.allowed_main_materials = [m_wood,m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (6,8) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.1,0.2)
        self.main_avg_depth_range = (0.1,0.2)
        self.main_width_range = (1,1.5)
        self.main_avg_width_range = (1,1.5)
        self.length_range = (12,24)
        self.shaft_length_range = (5,16) 
        self.shaft_diameter_range = (.6,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_wood #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = 0
        self.parry_mod = -10 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Club'
        self.bname_variants = ['Club', 'Cudgel', 'Baton', 'Bludgeon', 'Truncheon', 'Cosh'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'mace' #This is the default skill used for the weapon. String
        self.main_length = 6
        self.shaft_length = 16 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1 #1.25 average longsword
        self.main_width = 1 #Absolute width at widest point
        self.avg_main_depth = .1 #.14 is average for a sword blade
        self.main_depth =  .1 #Absolute depth at deepest point
        self.main_shape = 'round' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .5 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Swing]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Small_Mace(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'small_mace'

        self.allowed_main_materials = [m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (3,6) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (2,6)
        self.main_avg_depth_range = (1.5,3)
        self.main_width_range = (2,6)
        self.main_avg_width_range = (1.5,3)
        self.length_range = (24,36)
        self.shaft_length_range = (21,30) 
        self.shaft_diameter_range = (.8,1.8)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -10
        self.parry_mod = -20 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Footman\'s Mace'
        self.bname_variants = ['Footman\'s Mace'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'mace' #This is the default skill used for the weapon. String
        self.main_length = 5
        self.shaft_length = 19 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2.75 #1.25 average longsword
        self.main_width = 2.75 #Absolute width at widest point
        self.avg_main_depth = 2.75 #.14 is average for a sword blade
        self.main_depth =  2.75 #Absolute depth at deepest point
        self.main_shape = 'round' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .8 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Swing]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Fluted_Small_Mace(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'fluted_small_mace'

        self.allowed_main_materials = [m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (3,6) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (.2,.5)
        self.main_avg_depth_range = (.2,.5)
        self.main_width_range = (2,6)
        self.main_avg_width_range = (1,3)
        self.length_range = (24,36)
        self.shaft_length_range = (21,30) 
        self.shaft_diameter_range = (.8,1.8)
        self.max_main_num = 3
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -10
        self.parry_mod = -20 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Fluted Footman\'s Mace'
        self.bname_variants = ['Fluted Footman\'s Mace'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'mace' #This is the default skill used for the weapon. String
        self.main_length = 5
        self.shaft_length = 19 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2.75 #1.25 average longsword
        self.main_width = 2.75 #Absolute width at widest point
        self.avg_main_depth = 2.75 #.14 is average for a sword blade
        self.main_depth =  2.75 #Absolute depth at deepest point
        self.main_shape = 'wedge' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 2 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .8 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Swing]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Medium_Mace(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'medium_mace'

        self.allowed_main_materials = [m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (3,6) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (2,6)
        self.main_avg_depth_range = (1.5,3)
        self.main_width_range = (2,6)
        self.main_avg_width_range = (1.5,3)
        self.length_range = (36,48)
        self.shaft_length_range = (33,42) 
        self.shaft_diameter_range = (.8,1.8)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -30
        self.parry_mod = -50 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [1,2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Horseman\'s Mace'
        self.bname_variants = ['Horseman\'s Mace'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'mace' #This is the default skill used for the weapon. String
        self.main_length = 5
        self.shaft_length = 40 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2.75 #1.25 average longsword
        self.main_width = 2.75 #Absolute width at widest point
        self.avg_main_depth = 2.75 #.14 is average for a sword blade
        self.main_depth =  2.75 #Absolute depth at deepest point
        self.main_shape = 'round' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .7 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Swing,Swing_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Fluted_Medium_Mace(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'fluted_medium_mace'

        self.allowed_main_materials = [m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (3,6) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (.2,.5)
        self.main_avg_depth_range = (.2,.5)
        self.main_width_range = (2,6)
        self.main_avg_width_range = (1.5,3)
        self.length_range = (36,48)
        self.shaft_length_range = (33,42) 
        self.shaft_diameter_range = (.8,1.8)
        self.max_main_num = 3
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -30
        self.parry_mod = -50 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [1,2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Fluted Horseman\'s Mace'
        self.bname_variants = ['Fluted Horseman\'s Mace'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'mace' #This is the default skill used for the weapon. String
        self.main_length = 5
        self.shaft_length = 40 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2.75 #1.25 average longsword
        self.main_width = 2.75 #Absolute width at widest point
        self.avg_main_depth = .3 #.14 is average for a sword blade
        self.main_depth =  .3 #Absolute depth at deepest point
        self.main_shape = 'wedge' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 2 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .7 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Swing,Swing_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Large_Mace(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'large_mace'

        self.allowed_main_materials = [m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (3,6) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (2,6)
        self.main_avg_depth_range = (1.5,3)
        self.main_width_range = (2,6)
        self.main_avg_width_range = (1.5,3)
        self.length_range = (48,60)
        self.shaft_length_range = (45,54) 
        self.shaft_diameter_range = (1,1.8)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -40
        self.parry_mod = -80 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Two-Handed Mace'
        self.bname_variants = ['Two-Handed Mace'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'mace' #This is the default skill used for the weapon. String
        self.main_length = 5
        self.shaft_length = 50 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2.75 #1.25 average longsword
        self.main_width = 2.75 #Absolute width at widest point
        self.avg_main_depth = 2.75 #.14 is average for a sword blade
        self.main_depth =  2.75 #Absolute depth at deepest point
        self.main_shape = 'round' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .65 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Swing_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Fluted_Large_Mace(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'fluted_large_mace'

        self.allowed_main_materials = [m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (3,6) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (.2,.5)
        self.main_avg_depth_range = (.2,.5)
        self.main_width_range = (2,6)
        self.main_avg_width_range = (1.5,3)
        self.length_range = (48,60)
        self.shaft_length_range = (45,54) 
        self.shaft_diameter_range = (1,1.8)
        self.max_main_num = 3
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -40
        self.parry_mod = -80 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Two-Handed Mace'
        self.bname_variants = ['Two-Handed Mace'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'mace' #This is the default skill used for the weapon. String
        self.main_length = 5
        self.shaft_length = 50 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2.75 #1.25 average longsword
        self.main_width = 2.75 #Absolute width at widest point
        self.avg_main_depth = .3 #.14 is average for a sword blade
        self.main_depth =  .3 #Absolute depth at deepest point
        self.main_shape = 'wedge' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 2 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .65 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Swing_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Hammer(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'hammer'

        self.allowed_main_materials = [m_wood,m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (1,3) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (1,3)
        self.main_avg_depth_range = (1,3)
        self.main_width_range = (4,7)
        self.main_avg_width_range = (4,7)
        self.length_range = (24,36)
        self.shaft_length_range = (23,34) 
        self.shaft_diameter_range = (.8,1.8)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_steel
        self.attack_mod = -10
        self.parry_mod = -30 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [1] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Warhammer'
        self.bname_variants = ['Warhammer'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 's_hammer' #This is the default skill used for the weapon. String
        self.main_length = 2
        self.shaft_length = 22 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 5 #1.25 average longsword
        self.main_width = 5 #Absolute width at widest point
        self.avg_main_depth = 2 #.14 is average for a sword blade
        self.main_depth =  2 #Absolute depth at deepest point
        self.main_shape = 'flat' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = .2 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .85 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Swing]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Maul(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'maul'

        self.allowed_main_materials = [m_wood,m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (2,4) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (2,3)
        self.main_avg_depth_range = (2,3)
        self.main_width_range = (6,9)
        self.main_avg_width_range = (6,9)
        self.length_range = (48,60)
        self.shaft_length_range = (46,56) 
        self.shaft_diameter_range = (1,1.8)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_steel
        self.attack_mod = -40
        self.parry_mod = -100 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'War Maul'
        self.bname_variants = ['War Maul'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'l_hammer' #This is the default skill used for the weapon. String
        self.main_length = 2
        self.shaft_length = 56 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1.25
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 6 #1.25 average longsword
        self.main_width = 6 #Absolute width at widest point
        self.avg_main_depth = 2 #.14 is average for a sword blade
        self.main_depth =  2 #Absolute depth at deepest point
        self.main_shape = 'flat' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = .2 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .9 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'b'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Swing]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Pick(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'pick'

        self.allowed_main_materials = [m_wood,m_copper,m_bronze,m_granite,m_bone,m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (2,4) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (2,3)
        self.main_avg_depth_range = (.7,1.3)
        self.main_width_range = (4,7)
        self.main_avg_width_range = (4,7)
        self.length_range = (36,48)
        self.shaft_length_range = (32,44) 
        self.shaft_diameter_range = (.8,1.8)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_steel
        self.attack_mod = -60
        self.parry_mod = -100 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'none'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [1,2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Horseman\'s Pick'
        self.bname_variants = ['Horseman\'s Pick'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'pick' #This is the default skill used for the weapon. String
        self.main_length = 2
        self.shaft_length = 36 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 6 #1.25 average longsword
        self.main_width = 6 #Absolute width at widest point
        self.avg_main_depth = .7 #.14 is average for a sword blade
        self.main_depth =  2 #Absolute depth at deepest point
        self.main_shape = 'point' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .85 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length-6)/self.length) #location along the total length for the grip
        
        self.damage_type = 'p'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Impale,Impale_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.default_r = Guard('Default, Right handed', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -40, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 0, [7,11,15,19], [], 
                                desc = 'Good neck protection, good right-side protection, exposes left side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')
        self.default_l = Guard('Default, Left handed', {'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -40, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 0, [8,12,16,20], [], 
                                desc = 'Good neck protection, good left-side protection, exposes right side. \n\nNeutral dodge, parry and to-hit modifiers. \n\nAuto-blocks nothing.')                       
        self.guards = [self.default_l,self.default_r]
        self.base_maneuvers = []
        self.maneuvers = []

class Falx(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'falx'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (24,36) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.2,0.4)
        self.main_avg_depth_range = (0.1,0.2)
        self.main_width_range = (2,4)
        self.main_avg_width_range = (1,3)
        self.length_range = (60,84)
        self.shaft_length_range = (36,48) 
        self.shaft_diameter_range = (.8,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -20
        self.parry_mod = -30 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'none' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Falx'
        self.bname_variants = ['Falx'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'polearm' #This is the default skill used for the weapon. String
        self.main_length = 24
        self.shaft_length = 36 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1.5 #1.25 average longsword
        self.main_width = 2.5 #Absolute width at widest point
        self.avg_main_depth = .15 #.14 is average for a sword blade
        self.main_depth =  .3 #Absolute depth at deepest point
        self.main_shape = 'curved blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .7 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = (self.length/100)/2 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Trip]
        self.maneuvers = []

class Fauchard(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'fauchard'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (24,36) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.2,0.4)
        self.main_avg_depth_range = (0.1,0.2)
        self.main_width_range = (3,6)
        self.main_avg_width_range = (1.5,4)
        self.length_range = (84,108)
        self.shaft_length_range = (60,72) 
        self.shaft_diameter_range = (.8,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -20
        self.parry_mod = -30 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'shaft' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Fauchard'
        self.bname_variants = ['Fauchard','Naginata','Guan Dao'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'polearm' #This is the default skill used for the weapon. String
        self.main_length = 24
        self.shaft_length = 72 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1.5 #1.25 average longsword
        self.main_width = 3 #Absolute width at widest point
        self.avg_main_depth = .15 #.14 is average for a sword blade
        self.main_depth =  .3 #Absolute depth at deepest point
        self.main_shape = 'curved blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .7 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = (self.length/100)/2 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash_2H,Shaft_Strike,Stab]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Trip]
        self.maneuvers = []

class Bardiche(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'bardiche'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (20,48) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.3,0.6)
        self.main_avg_depth_range = (0.15,0.3)
        self.main_width_range = (3,6)
        self.main_avg_width_range = (2,4)
        self.length_range = (64,80)
        self.shaft_length_range = (54,56) 
        self.shaft_diameter_range = (.8,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -10
        self.parry_mod = -30 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'shaft' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Bardiche'
        self.bname_variants = ['Bardiche','Lochaber Axe'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'polearm' #This is the default skill used for the weapon. String
        self.main_length = 36
        self.shaft_length = 54 #Also used as tethers for flail and whip like weapons
        self.length = (self.main_length/2) + (self.shaft_length-(self.main_length/2))
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2 #1.25 average longsword
        self.main_width = 3 #Absolute width at widest point
        self.avg_main_depth = .15 #.14 is average for a sword blade
        self.main_depth =  .3 #Absolute depth at deepest point
        self.main_shape = 'curved blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .6 #Center of mass for the main weapon component
        self.main_loc = ((self.length-(self.main_length))/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = ((self.shaft_length/2)/(self.length/100))/100 #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash_2H,Stab]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Trip]
        self.maneuvers = []

class Pole_Axe(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'pole_axe'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (6,12) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.5,2)
        self.main_avg_depth_range = (0.15,1)
        self.main_width_range = (6,10)
        self.main_avg_width_range = (1,8)
        self.length_range = (54,102)
        self.shaft_length_range = (48,96) 
        self.shaft_diameter_range = (1,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -20
        self.parry_mod = -10 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Pole Axe'
        self.bname_variants = ['Pole Axe'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'polearm' #This is the default skill used for the weapon. String
        self.main_length = 8
        self.shaft_length = 72 #Also used as tethers for flail and whip like weapons
        self.length = (self.main_length/2) + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = True #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 1 #1.25 average longsword
        self.main_width = 8 #Absolute width at widest point
        self.avg_main_depth = .5 #.14 is average for a sword blade
        self.main_depth =  1 #Absolute depth at deepest point
        self.main_shape = 'wedge' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .6 #Center of mass for the main weapon component
        self.main_loc = ((self.length-(self.main_length/2))/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length/2)/self.length) #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Axe_Hammer,Horn_Thrust,Slash_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Trip,Hook_Neck,Disarm,Deshield]
        self.maneuvers = []

class Bill(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'bill'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (12,18) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.15,.5)
        self.main_avg_depth_range = (0.1,.3)
        self.main_width_range = (2.5,5)
        self.main_avg_width_range = (2,4)
        self.length_range = (60,108)
        self.shaft_length_range = (48,90) 
        self.shaft_diameter_range = (1,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -10
        self.parry_mod = -10 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'none' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Bill'
        self.bname_variants = ['Bill','Bill Hook'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'polearm' #This is the default skill used for the weapon. String
        self.main_length = 12
        self.shaft_length = 72 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = True #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 3 #1.25 average longsword
        self.main_width = 4 #Absolute width at widest point
        self.avg_main_depth = .15 #.14 is average for a sword blade
        self.main_depth =  .25 #Absolute depth at deepest point
        self.main_shape = 'curved blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .55 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length/2)/self.length) #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Trip,Hook_Neck,Disarm,Deshield]
        self.maneuvers = []

class Guisarme(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'guisarme'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (24,36) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.15,.5)
        self.main_avg_depth_range = (0.1,.3)
        self.main_width_range = (1.5,3)
        self.main_avg_width_range = (.5,2)
        self.length_range = (72,120)
        self.shaft_length_range = (48,84) 
        self.shaft_diameter_range = (1,1.5)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -10
        self.parry_mod = -10 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'none' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'none'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Guisarme'
        self.bname_variants = ['Guisarme'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'polearm' #This is the default skill used for the weapon. String
        self.main_length = 30
        self.shaft_length = 85 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = True #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2 #1.25 average longsword
        self.main_width = 3 #Absolute width at widest point
        self.avg_main_depth = .15 #.14 is average for a sword blade
        self.main_depth =  .25 #Absolute depth at deepest point
        self.main_shape = 'curved blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .55 #Center of mass for the main weapon component
        self.main_loc = (self.shaft_length/((self.length-self.main_length)/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length/2)/self.length) #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash_2H]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Trip,Hook_Neck,Disarm,Deshield]
        self.maneuvers = []

class Halbard(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'halbard'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (12,24) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (1,1.5)
        self.main_avg_depth_range = (0.2,.5)
        self.main_width_range = (3,6)
        self.main_avg_width_range = (2,4)
        self.length_range = (60,96)
        self.shaft_length_range = (48,72) 
        self.shaft_diameter_range = (1,1.75)
        self.max_main_num = 1
        self.max_shaft_num = 1

        self.main_material = m_steel #Damage component (blade, head, etc) material
        self.shaft_material = m_wood
        self.grip_material = m_wood
        self.accent_material = m_wood
        self.attack_mod = -20
        self.parry_mod = -10 #Mod to weilder's ability to parry with weapon
        self.b_striker = 'main' #Striking surface for damage type. Can be main, shaft, accent, or none
        self.s_striker = 'main'
        self.p_striker = 'main'
        self.t_striker = 'none'
        self.hands = [2] #List can include 0,1,2
        self.quality = 'Average'
        self.base_name = 'Halbard'
        self.bname_variants = ['Halbard'] #A list of variant names for the weapon 'Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'
        self.skill = 'polearm' #This is the default skill used for the weapon. String
        self.main_length = 19
        self.shaft_length = 67 #Also used as tethers for flail and whip like weapons
        self.length = self.main_length + self.shaft_length
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = True #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = 2.5 #1.25 average longsword
        self.main_width = 3.75 #Absolute width at widest point
        self.avg_main_depth = .4 #.14 is average for a sword blade
        self.main_depth =  1 #Absolute depth at deepest point
        self.main_shape = 'wedge' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 0 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .55 #Center of mass for the main weapon component
        self.main_loc = ((self.length-(self.main_length/2))/(self.length/100))/100 #Location along the total length for the main weapon component
        self.accent_loc = 0 #Location along the total length for the accent component
        self.grip_loc = 1-((self.length/2)/self.length) #location along the total length for the grip
        
        self.damage_type = 's'


        
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash_2H,Stab,Axe_Hammer]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ht_r = Guard('High Thrust, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good right-side protection, exposes left side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.ht_l = Guard('High Thrust, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20], 
                                desc = 'Excellent neck protection, good left-side protection, exposes right side. \n\nNeutral dodge and to-hit modifiers, +20 to parry chances. \n\nAuto-blocks hands.')
        self.hs_l = Guard('High Striking, Left-handed', {'Neck': -20, 'R Shoulder': -20, 'L Shoulder': 20, 'R Chest': -10, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -20, 
                                'L Ribs': -20, 'R Elbow': -40, 'L Elbow': 30, 'R Forearm': -60, 'L Forearm': 40, 'R Hand': -60, 'L Hand': 40, 'R Thigh': 60, 'R Knee': 80, 
                                'R Shin': 60, 'R Foot': 40, 'L Knee': -30, 'L Shin': -40, 'L Thigh': -20, 'L Foot': -60, 'L Abdomen': -40, 'R Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True, desc = 'Minor neck protection, good right upper body protection, exposes left upper and right lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks right upper body.')
        self.hs_r = Guard('High Striking, Right-handed', {'Neck': -20, 'L Shoulder': 20, 'R Shoulder': -20, 'L Chest': -10, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -20, 
                                'R Ribs': -20, 'L Elbow': -40, 'R Elbow': 30, 'L Forearm': -60, 'R Forearm': 40, 'L Hand': -60, 'R Hand': 40, 'L Thigh': 60, 'L Knee': 80, 
                                'L Shin': 60, 'L Foot': 40, 'R Knee': -30, 'R Shin': -40, 'R Thigh': -20, 'R Foot': -60, 'R Abdomen': -40, 'L Abdomen': -30, 'L Hip': -10}, 30, 10, -10, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True, desc = 'Minor neck protection, good left upper body protection, exposes right upper and left lower body. \n\n+30 to hit, +10 to dodge, -10 parry chances. \n\nAuto-blocks left upper body.')
        self.rudder = Guard('Rudder', {'L Shoulder': -20, 'R Shoulder': -60, 'Up L Arm': -20, 'Up R Arm': -60, 'L Ribs': -20, 
                                'L Elbow': -20, 'R Elbow': -40, 'L Forearm': -60, 'R Forearm': -60, 'L Thigh': -60, 'L Knee': -60, 'R Chest':-20,
                                'L Shin': -60, 'L Foot': -80, 'R Thigh':-60, 'R Knee': -80, 'R Shin': -100,'R Foot': -120, 'R Abdomen': -40, 'R Ribs': -20, 'L Hip': -80, 'R Hip': -40}, -60, -30, 40, [7,8,11,12,15,16,19,20], [0,1,2,3,4,5,6,7,8,9,11,12,15,16,17,21], 
                                desc = 'Excellent overall protection. \n\n -60 to hit, -30 to dodge, +40 to parry chances. \n\nAuto-blocks head, neck, shoulders, chest, arms, right hip and right thigh.')
        self.mid_r = Guard('Middle, Right-handed', {'Neck': -80, 'L Hand': 20, 'L Forearm': 10, 'Up L Arm': -10, 'L Shoulder': -20, 'Scalp': -40, 'Face':-30, 'R Shoulder':-40, 
                                'Up R Arm':-60, 'R Elbow': -80, 'R Forearm': -40, 'R Hand': -30, 'L Chest': -30, 'R Chest': -40, 'L Ribs': -40, 'R Ribs': -80, 'L Abdomen': -50, 
                                'R Abdomen': -100, 'L Hip': -30, 'L Thigh': -30, 'L Knee': -40, 'L Shin': -60, 'L Foot': -80, 'R Hip': -140, 'R Thigh': -50, 'R Knee': -60,
                                'R Shin': -80, 'R Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')
        self.mid_l = Guard('Middle, Left-handed', {'Neck': -80, 'R Hand': 20, 'R Forearm': 10, 'Up R Arm': -10, 'R Shoulder': -20, 'Scalp': -40, 'Face':-30, 'L Shoulder':-40, 
                                'Up L Arm':-60, 'L Elbow': -80, 'L Forearm': -40, 'L Hand': -30, 'R Chest': -30, 'L Chest': -40, 'R Ribs': -40, 'L Ribs': -80, 'R Abdomen': -50, 
                                'L Abdomen': -100, 'R Hip': -30, 'R Thigh': -30, 'R Knee': -40, 'R Shin': -60, 'R Foot': -80, 'L Hip': -140, 'L Thigh': -50, 'L Knee': -60,
                                'L Shin': -80, 'L Foot': -100}, 40, 30, 10, [7,8,11,12,15,16,19,20], [], 
                                 desc = 'Good overall protection, slightly exposes left hand and forearm. \n\n+40 to hit, +30 to dodge, +10 to parry chances. \n\nNo locations auto-blocked.')                        
        self.guards = [self.ht_l, self.ht_r, self.hs_l, self.hs_r, self.rudder, self.mid_r, self.mid_l]
        self.base_maneuvers = [Weapon_Trip,Hook_Neck,Disarm,Deshield]
        self.maneuvers = []
