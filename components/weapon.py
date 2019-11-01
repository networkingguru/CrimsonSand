import global_vars
from math import sqrt
from enums import WeaponTypes, FighterStance, EntityState
from utilities import itersubclasses, clamp, roll_dice
from components.maneuver import (Headbutt, Tackle, Push, Trip, Bearhug, Reap, Wind_Choke, Blood_Choke, Collar_Tie, Compression_Lock, Joint_Lock, Limb_Capture, Sacrifice_Throw, 
    Shoulder_Throw, Strangle_Hold, Hip_Throw, Double_Leg_Takedown, Single_Leg_Takedown, Neck_Crank)
from components.material import (m_steel, m_leather, m_wood, m_tissue, m_bone, m_adam, m_bleather, m_bronze, m_canvas, m_cloth, m_copper, m_gold, m_granite, m_hgold,
    m_hsteel, m_ssteel, m_hssteel, m_iron, m_hiron, m_mithril, m_silver, m_hide, m_xthide)

quality_dict = {'Junk': -.5, 'Very Poor': -.3, 'Poor': -.2, 'Below Average': -.1, 'Average': 1, 'Above Average': 1.15, 'Fine': 1.3, 'Exceptional': 1.4, 'Masterwork': 1.5}



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
        self.main_shape = 'de blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
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

        self.base_attacks = []
        self.attacks = []
        self.base_maneuvers = []
        self.maneuvers = []
        self.guards = []

        self.cost = 0
        self.normality = 1

        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()
        
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

        

        self.main_weight = ((self.main_length * self.avg_main_depth * self.avg_main_width)*self.main_num) * (self.main_material.density * .03)
        self.shaft_weight = (self.shaft_length * self.shaft_diameter * (self.shaft_material.density * .03)) * self.shaft_num
        self.accent_weight = self.accent_cuin * (self.accent_material.density * .03)
        self.grip_weight = self.grip_material.density * (.3 * max(self.hands))
        self.weight = self.main_weight + self.shaft_weight + self.accent_weight
        self.main_only_com = ((self.main_length*self.main_com)+(self.main_loc*self.length))*self.main_weight
        self.shaft_only_com = (self.shaft_length*.5)*self.shaft_weight
        self.accent_only_com = (self.accent_loc*self.length)*self.accent_weight
        self.com = (self.main_only_com + self.shaft_only_com + self.accent_only_com)/self.weight #Center of mass for the whole weapon
        self.com_perc = self.com / self.length #com as a percentage
        self.axis_vs_com = self.com_perc - self.grip_loc #Shows COM relative to grip location (axis for swings). Used to determine AP/stamina costs.

        self.main_hits = (self.main_material.elasticity * 1450000) * (self.main_weight/(self.main_material.density*.03)) * self.main_material.toughness * sqrt(self.main_material.hardness)

        self.parry_ap += (self.weight * 10)/self.axis_vs_com

        self.min_pwr_1h = ((self.added_mass + .86) * 40)/1 #1 pwr = 1 ft/lb/s; accelleration = 40 f/s2; weight of average hand = .86 lb
        self.min_pwr_2h = ((self.added_mass + 1.72) * 40)/1.5 #1 pwr = 1.5 ft/lb/s; accelleration = 40 f/s2; weight of average hand = .86 lb

        self.solidness = sqrt(self.main_material.elasticity * self.main_material.hardness)
        if self.main_material.hardness < 1: 
            self.sharpness = self.main_material.hardness
            self.pointedness = self.main_material.hardness
        else:
            self.sharpness = sqrt((self.main_material.hardness/m_iron.hardness)*quality_dict.get(self.quality))
            self.pointedness = sqrt(self.main_material.hardness/m_iron.hardness)

  
        main_materials_cost = self.main_material.cost * self.main_weight
        shaft_materials_cost = self.shaft_material.cost * self.shaft_weight
        grip_materials_cost = self.grip_material.cost * self.grip_weight
        accent_materials_cost = self.accent_material.cost * self.accent_weight

        #Crafting costs. 1 day skilled labor = ~5 material cost
        main_crafting_cost = self.main_material.craft_diff * self.main_weight
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
        self.allowed_angles_r = [] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.added_mass = 0 #Dynamicly assigned
        self.main_area = 0 #Dynamicly assigned
        self.mech_adv = 1 #Dynamicly assigned
        self.shape = '' #Dynamicly assigned
        self.main_shape = self.weapon.main_shape
        self.main_length = self.weapon.main_length
        self.avg_main_width = self.weapon.avg_main_width
        self.main_depth = self.weapon.main_depth
        self.avg_main_width = self.weapon.avg_main_width
        self.main_width = self.weapon.main_width
        self.main_material = self.weapon.main_material
        self.shaft_material = self.weapon.shaft_material
        self.shaft_length = self.weapon.shaft_length
        self.accent_material = self.weapon.accent_material
        self.weight = self.weapon.weight
        self.axis_vs_com = self.weapon.axis_vs_com
        self.com_perc = self.weapon.com_perc
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
                if self.striker == 'main':
                    shape = self.main_shape
                else:
                    shape = 'round'
                    
                if shape == 'wedge':
                    self.main_area = self.main_length * self.avg_main_width
                    self.mech_adv =  self.main_depth / self.main_width
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
                elif self.main_shape == 'flat':
                    self.main_area = min(self.main_length,8) * min(self.main_width,8)

            elif t == 's':
                if self.main_shape == 'blade':
                    self.main_area = min(self.main_length, 12) * self.avg_main_width
                    self.mech_adv =  self.main_depth / self.main_width
                elif self.main_shape == 'de blade':
                    self.main_area = min(self.main_length, 12) * self.avg_main_width
                    self.mech_adv =  (self.main_depth/2) / self.main_width
            
            elif t == 'p':
                if self.striker == 'main':
                    shape = self.main_shape
                    length = self.main_length
                    depth = self.main_depth
                    width = self.main_width
                else:
                    shape = 'point'
                    if self.striker == 'shaft':
                        length = min(self.shaft_length, 12)
                        depth = width = 1
                    else:
                        length = depth = width = 1
                if shape in ['point', 'blade', 'de blade']:
                    wedge1 = length / width
                    wedge2 = width / depth
                    if shape in ['point', 'de blade']:
                        #Double each (since there are two wedges per side) and multiply for full MA of tip
                        self.mech_adv = (wedge1*2)*(wedge2*2)
                        self.main_area = depth * length * width
                    else:
                        self.mech_adv = (wedge1)*(wedge2)
                        self.main_area = depth * length * width
                        
            else:
                if self.main_shape == 'hook':
                    wedge1 = self.main_length / self.main_width
                    wedge2 = self.main_width / self.main_depth
                    #Double each (since there are two wedges per side) and multiply for full MA of tip
                    self.mech_adv = (wedge1*2)*(wedge2*2)
                    self.main_area = self.main_depth * self.main_width



        if self.damage_type in ['s','b']:
            self.stamina += self.weight + int(self.weight*self.axis_vs_com)
            self.base_ap += min(self.weight*10, (self.weight * 10)*self.axis_vs_com)
            self.added_mass = self.weight * self.com_perc
            self.attack_mod += (20 - ((self.weight*10) * self.com_perc))    
            self.parry_mod -= ((self.weight*10) * self.com_perc) 
            
            if self.main_num > 1:
                self.attack_mod += self.main_num * 5
                self.parry_mod -= self.main_num * 20
        else:
            self.stamina += self.weight/2
            self.base_ap += self.weight * 5
            self.added_mass = self.weight/10
            
            if self.damage_type == 'p':
                self.attack_mod -= self.weight/10
                self.parry_mod -= self.weight * 5
            else:
                self.attack_mod += -5 + (self.main_num * 5)
                self.parry_mod -= self.main_num * 20

class Guard():
    def __init__(self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = [], rh_default = False, lh_default = False):
        self.name = name
        self.loc_hit_mods = loc_hit_mods #A dict in 'location name':mod format with mods to hit chance based on location
        self.hit_mod = hit_mod
        self.dodge_mod = dodge_mod
        self.parry_mod = parry_mod
        self.req_locs = req_locs #A list of locs required to be funtional to use the guard
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
        self.base_ap = 10
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
        self.base_ap = 25
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
        self.base_ap = 20
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
        self.base_ap = 20
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
        self.base_ap = 10
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
        self.base_ap = 10
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
        self.base_ap = 15
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
        self.base_ap = 30
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
        self.base_ap = 20
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
        self.base_ap = 10
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
        self.base_ap = 15
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
        self.base_ap = 10
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
        self.base_ap = 15
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
        self.force_scalar = 1 #Used to adjust force/damage for the attack
        self.striker = 'main'
        self.hands = 1
        self.damage_type = 'p'
        self.base_ap = 5
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
        self.base_ap = 0
        self.hand = True
        self.length = 0 #Used to add or subtract from base weapon length got added/reduced reach
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = [] #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = [0,8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = [0,8] #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)

        
        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

class Unarmed(Weapon):

    def __init__(self, **kwargs):
        Weapon.__init__(self)
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
                                True)
        self.southpaw = Guard('Southpaw', {'Face': -10, 'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20}, 0, 0, 0, [7,8,11,12,15,16],[9,10], 
                                False, True)
        self.high = Guard('High', {'Scalp': -20, 'Face': -30, 'Neck': -60, 'R Chest': -40, 'L Chest': -40, 'R Ribs': -20, 'L Ribs': -20, 'R Elbow': 20, 'L Elbow': 20, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20}, -10, -20, 20, [7,8,11,12,15,16], [0,1,2,5,6])
        self.low = Guard('Low', {'Scalp': 20, 'Face': -10, 'Neck': -80, 'R Chest': -80, 'L Chest': -80, 'R Ribs': -80, 'L Ribs': -80, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20, 'R Abdomen': -60, 'L Abdomen': -60}, -20, -10, 20, [7,8,11,12,15,16], [2,5,6,9,10,13,14])
        self.half = Guard('Half', {'Neck': -10, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'R Ribs': -60, 
                                'R Elbow': -60, 'R Forearm': -60, 'R Hand': -60}, 20, 20, 0, [7,11,15], [9])
        self.guards = [self.conventional, self.southpaw, self.high, self.low, self.half]
        self.base_maneuvers = [Headbutt,Tackle,Push,Trip,Bearhug,Collar_Tie,Limb_Capture,Wind_Choke,Strangle_Hold,Compression_Lock,Blood_Choke,Joint_Lock,Neck_Crank,Reap,Sacrifice_Throw,Hip_Throw,Shoulder_Throw,Single_Leg_Takedown,Double_Leg_Takedown]

class De_Medium_Sword(Weapon):
    def __init__(self, **kwargs):
        Weapon.__init__(self)
        self.name = 'de_medium_sword'

        self.allowed_main_materials = [m_iron,m_hiron,m_steel,m_hsteel,m_ssteel,m_hssteel,m_mithril,m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        #Maximums; used to procedurally gen weapons
        self.main_len_range = (30,47) #Tuple containing min and max range for acceptable lengths
        self.main_depth_range = (0.15,0.5)
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
        self.base_name = 'Long Sword'
        self.bname_variants = ['Long Sword', 'Bastard Sword', 'Hand and a Half Sword', 'Arming Sword', 'Broadsword', 'Knight’s Sword', 'Kaskara', 'Rapier', 'Schiavona'] #A list of variant names for the weapon
        self.skill = 'long_sword' #This is the default skill used for the weapon. String
        self.length = 45
        self.shaft_length = 6 #Also used as tethers for flail and whip like weapons
        self.shaft_diameter = 1
        self.shaft_num = 1
        self.pre_load = False #Used to account for weapons that can be preloaded with velocity, like flails or staves
        self.avg_main_width = .14 #.14 is average for a sword blade 
        self.main_width = .2 #Absolute depth at deepest point
        self.avg_main_depth = 1.25 #1.25 average longsword
        self.main_depth =  1.5 #Absolute width at widest point
        self.main_shape = 'de blade' #Acceptable values: de blade, blade, point, wedge, round, flat, hook
        self.main_num = 1 #Number of main attack surfaces, mostly used for flails/flogs
        self.accent_cuin = 7 #Cubic inches of accent material, such as the crossguard and pommel on a sword
        self.main_com = .3 #Center of mass for the main weapon component
        self.main_loc = .13 #Location along the total length for the main weapon component
        self.accent_loc = .1 #Location along the total length for the accent component
        self.grip_loc = .1 #location along the total length for the grip
        
        self.damage_type = 's'


        self.main_length = 39
       


        self.__dict__.update(kwargs)

        self.set_dynamic_attributes()

        #Attacks below

        self.base_attacks = [Slash, Slash_2H, Stab, Pommel_Strike]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ox_r = Guard('Hanging, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20])
        self.ox_l = Guard('Hanging, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20])
        self.plow_r = Guard('Middle, Right-handed', {'Neck': -20, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': -40, 'R Abdomen': -80, 'R Hip': -80, 'L Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True)
        self.plow_l = Guard('Middle, Left-handed', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -80, 'L Hip': -80, 'R Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True)
        self.low = Guard('Low', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'L Elbow': -40, 'R Elbow': 20, 'L Forearm': -20, 'R Forearm': 20, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -20, 'L Hip': -80, 'R Hip': -40}, 0, 30, -10, [7,8,11,12,15,16,19,20], 
                                [23,24,25,26,27,28])
        self.high = Guard('High', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -20, 'L Chest': 20, 'Up R Arm': -20, 'Up L Arm': 40, 'R Ribs': -20, 
                                'L Ribs': 20, 'L Elbow': 40, 'R Forearm': -20, 'L Forearm': 20, 'R Hand': -20, 'L Hand': -20, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': 20, 'R Abdomen': -20, 'R Hip': -80, 'L Hip': -20}, 20, 10, 10, [7,8,11,12,15,16,19,20], 
                                [0,1])
        self.guards = [self.ox_l, self.ox_r, self.plow_l, self.plow_r, self.low, self.high]
        self.base_maneuvers = []
        self.maneuvers = [] 






