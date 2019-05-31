from statistics import mean
from copy import copy, deepcopy
from utilities import inch_conv, clamp
from enums import FighterStance
from chargen_functions import height_curve

class Fighter:
    def __init__(self, attributes, facing, ai = None, l_blocker = None, r_blocker = None):
        #Transitory combat variables
        self.end_turn = False
        if ai is not None:
            self.ai = ai(self)
        self.facing = facing #Facing for FOV
        self.aoc = [] #List of cells for AOC
        self.aoc_facing = facing
        self.action = [] #List of available commmands for combat menus
        self.atk_result = None #Atk roll for last attack
        self.dam_result = None #Dam multiplier for last attack
        self.new_loc_result = None #Used when attack hits wrong loc
        self.last_atk_ap = 0
        self.targets = [] #This is a list of targets in AOC, set by update_targets
        self.curr_target = None
        self.combat_choices = [] #List of chosen commands for combat menus
        self.attacker = None
        self.attacker_history = []
        self.disengage = False
        self.mods = []
        self.wait = False
        self.acted = False
        self.entities_opportunity_attacked = []
        self.disengage_option = None
        #Attributes
        self.male = True
        self.attributes = attributes
        self.max_attributes = attributes.copy()
        #log, mem, wis, comp, comm, cre, men, will, ss, pwr, man, ped, bal, swift, flex, sta, derm, 
        #bone, immune, shock, toxic, sit, hear, ts, touch, fac, ht, fat, shape
        self.log = attributes[0]
        self.mem = attributes[1]
        self.wis = attributes[2]
        self.comp = attributes[3]
        self.comm = attributes[4]
        self.cre = attributes[5]
        self.men = attributes[6]
        self.will = attributes[7]
        self.ss = attributes[8]
        self.pwr = attributes[9]
        self.man = attributes[10]
        self.ped = attributes[11]
        self.bal = attributes[12]
        self.swift = attributes[13]
        self.flex = attributes[14]
        self.sta = attributes[15]
        self.derm = attributes[16]
        self.bone = attributes[17]
        self.immune = attributes[18]
        self.shock = attributes[19]
        self.toxic = attributes[20]
        self.sit = attributes[21]
        self.hear = attributes[22]
        self.ts = attributes[23]
        self.touch = attributes[24]
        self.fac = attributes[25]
        self.ht = attributes[26]
        self.fat = attributes[27]
        self.shape = attributes[28]
        #Meta-Attributes
        self.int = int(round((mean([self.log, self.mem, self.comm, self.comp, self.cre, self.men, self.will, self.wis])),0))
        self.str = int(round((mean([self.ss, self.pwr])),0))
        self.agi = int(round((mean([self.man, self.ped, self.bal, self.swift, self.flex])),0))
        self.con = int(round((mean([self.sta, self.derm, self.bone, self.immune, self.shock, self.toxic])),0))
        self.sens = int(round((mean([self.sit, self.hear, self.ts, self.touch])),0))
        self.appear = int(round((mean([self.fac, self.ht, self.shape, (100-self.fat)])),0))
        #Skills
        self.brawling = int(round(self.agi*0.4 + self.str*0.4 + ((self.men+self.wis)/2)*0.2))
        self.dodge = int(round(self.swift*.6 + ((self.ped + self.bal)/2)*.2 + ((self.men + self.wis)/2)*.2))
        self.deflect = int(round(((self.men + self.wis)/2)*.5 + self.swift*.3 + self.agi*.2))
        #Derived Attributes
        self.height = int(round((height_curve(self.ht)))) #Height in inches
        self.er = self.height/2 #Eff reach, 1/2 ht in inches
        #Local var to handle secondary calc for weight
        wt_mod = ((((self.bone-100)/20)+((self.fat-100)/4)+((self.str-100)/8))/100)+1
        self.weight = int(round((self.ht*1.6)*wt_mod))
        self.stamina = int(round((self.sta * 2) + self.shock + self.ss))
        self.max_stamina = self.stamina
        #Local var to handle secondary calc for stamr
        sr_mod = (self.stamina + ((self.immune / 5) + (self.toxic/20) + (self.shock/10)))/100
        self.stamr = int(round((self.stamina/100)*sr_mod))
        self.max_stamr = self.stamr
        self.vitae = int(round(self.weight/0.03))
        self.max_vitae = self.vitae
        self.vitr = int((((self.immune/100)*self.weight)/60))
        self.max_mv = int(round(((self.ht/2) * 7.5) * (((self.ht * 2.5) / self.weight) * (self.swift / 100) * (self.flex / 100))))
        self.mv = self.max_mv
        self.max_ap = self.swift
        self.ap = self.max_ap
        self.walk_ap = round(self.ap / inch_conv(self.mv, 1))
        self.jog_ap = round(self.ap / inch_conv(self.mv*1.5, 1))
        self.run_ap = round(self.ap / inch_conv(self.mv*2, 1))
        self.init = (self.men + self.swift)/4 + (self.sens + self.brawling)/4
        self.max_init = self.init
        #Effective Power
        self.ep = int(round(((self.pwr * 2) + self.weight + (self.bone * 0.1)) * ((self.brawling + (self.bal/2))/200)))
        #Reach
        self.reach = clamp(inch_conv(self.er, 1), 2)
        #Base stamina cost for actions
        self.base_stam_cost = int(round((self.fat/self.str)*(self.weight/100)))



        #Hit Locations
        self.locations = []
        self.locations.append([(self.derm + self.fat/2),(self.ss/6 + self.pwr/3),(self.bone * 10)])
        self.locations.append([(self.derm/2 + self.fat/4),(self.ss/5 + self.pwr/2),(self.bone * 8)])
        self.locations.append([(self.derm + self.fat/2),(self.ss/3 + self.pwr),self.bone*6])
        self.locations.append([(self.derm/2 + self.fat/4),(self.ss/2 + self.pwr*2),self.bone*6])
        self.locations.append([(self.derm/2 + self.fat/4),(self.ss/2 + self.pwr*2),self.bone*6])
        self.locations.append([(self.derm + self.fat/2),(self.ss/2 + self.pwr*2),self.bone*6])
        self.locations.append([(self.derm + self.fat/2),(self.ss/2 + self.pwr*2),self.bone*6])
        self.locations.append([(self.derm/2 + self.fat/4),(self.ss/3 + self.pwr),(self.bone*4)])
        self.locations.append([(self.derm/2 + self.fat/4),(self.ss/3 + self.pwr),(self.bone*4)])
        self.locations.append([(self.derm + self.fat/2),(self.ss/5 + self.pwr/2),(self.bone*4)])
        self.locations.append([(self.derm + self.fat/2),(self.ss/5 + self.pwr/2),(self.bone*4)])
        self.locations.append([(self.derm/2 + self.fat/4),(self.ss/10 + self.pwr/4),(self.bone*4)])
        self.locations.append([(self.derm/2 + self.fat/4),(self.ss/10 + self.pwr/4),(self.bone*4)])
        self.locations.append([(self.derm/4 + self.fat*2),(100 + self.ss/2 + self.pwr),self.bone*6])
        self.locations.append([(self.derm/4 + self.fat*2),(100 + self.ss/2 + self.pwr),self.bone*6])
        self.locations.append([(self.derm/2 + self.fat/4),(self.ss/5 + self.pwr/2),self.bone*2])
        self.locations.append([(self.derm/2 + self.fat/4),(self.ss/5 + self.pwr/2),self.bone*2])
        self.locations.append([(self.derm/4 + self.fat*2),(self.ss/2 + self.pwr*2),self.bone*8])
        self.locations.append([(self.derm/4 + self.fat*2),(self.ss/2 + self.pwr*2),self.bone*8])
        self.locations.append([(self.derm),(self.ss/10 + self.pwr/4),self.bone])
        self.locations.append([(self.derm),(self.ss/10 + self.pwr/4),self.bone])
        self.locations.append([(self.derm + self.fat),(self.ss + self.pwr*4),self.bone*10])
        self.locations.append([(self.derm + self.fat),(self.ss + self.pwr*4),self.bone*10])
        self.locations.append([(self.derm/2 + self.fat/2),(self.ss/5 + self.pwr/2),self.bone*8])
        self.locations.append([(self.derm/2 + self.fat/2),(self.ss/5 + self.pwr/2),self.bone*8])
        self.locations.append([(self.derm/2 + self.fat/2),(self.ss/3 + self.pwr),self.bone*6])
        self.locations.append([(self.derm/2 + self.fat/2),(self.ss/3 + self.pwr),self.bone*6])
        self.locations.append([(self.derm*1.5),(self.ss/6 + self.pwr/3),(self.bone * 2)])
        self.locations.append([(self.derm*1.5),(self.ss/6 + self.pwr/3),(self.bone * 2)])
        #Code to fill locations list
        for location in self.locations:
            i = 0
            for amount in location:
                amount = int(round(amount))
                location[i] = amount
                i += 1

        self.max_locations = deepcopy(self.locations)

        self.location_ht = []
        self.location_ratios = (1, .9, .87, .82, .82, .8, .8, .7, .7, .72, .72, .63, .63, .6, .6, .55, .55, .53, .53, .49, .49, .4, .4, .29, .29, .2, .2, .04, .04)
        #Fill location heights
        i = 0
        for x in self.locations:
            if not any(x):
                i += 1
                continue
            else:
                self.location_ht.append(self.height * self.location_ratios[i])
                i += 1

        
        #Injury list
        self.injuries = []
        #Static injury effects
        self.temp_physical_mod = 0
        self.paralyzed_locs = []
        self.diseases = []
        self.atk_mod_r = 0
        self.atk_mod_l = 0
        #Continuous Injury Effects
        self.bleed = [] #Amount, duration
        #rds until dead from suffocation
        self.suffocation = None
        self.stam_drain = 0
        #Will check modifier due to pain for movement
        self.pain_mod_mov = 0
        self.stance = FighterStance.standing
        #fov arrays
        self.fov_visible = set()
        self.fov_wall = set()
        self.fov_explored = set()
        #Persistent derived combat attrubites
        self.l_blocker = l_blocker
        self.r_blocker = r_blocker
        #If no blocker defined, use bone in forearms
        if self.l_blocker == None:
            self.l_blocker = self.locations[16][2]
        if self.r_blocker == None:
            self.r_blocker = self.locations[15][2]
        self.best_combat_skill = self.brawling

    def update_aoc_facing(self) -> None:
        #Hack to handle incongruity between aoc facing and fov facing
        if self.facing == 0:
            self.aoc_facing = 7
        else:
            self.aoc_facing = self.facing -1

    def adjust_max_locations(self, location_index, layer_index, value_to_subtract) -> None:
        self.max_locations[location_index][layer_index] -= value_to_subtract
        if self.locations[location_index][layer_index] > self.max_locations[location_index][layer_index]:
            self.locations[location_index][layer_index] = self.max_locations[location_index][layer_index]

    def mod_attribute(self, attribute, amount) -> None:
        value = int(getattr(self, attribute))
        if value + amount <= 0: setattr(self, attribute, 0)
        else: 
            value += int(amount)
            setattr(self, attribute, value)

    
    def name_location(self, location):
        loc_list = ['Scalp', 'Face', 'Neck', 'R Shoulder', 'L Shoulder', 'Up R Chest', 'Up L Chest', 'Up R Arm', 'Up L Arm', 'Low R Chest', 'Low L Chest', 
                    'R Elbow', 'L Elbow', 'R Abdomen', 'L Abdomen', 'R Forearm', 'L Forearm', 'R Hip', 'L Hip', 'R Hand', 'L Hand', 'R Thigh', 'L Thigh', 
                    'R Knee', 'L Knee', 'R Shin', 'L Shin', 'R Foot', 'L Foot']
        #Key for reference
        # 0 Scalp
        # 1 Face
        # 2 Neck
        # 3 R Shoulder
        # 4 L Shoulder
        # 5 Up R Chest
        # 6 Up L Chest
        # 7 Up R Arm
        # 8 Up L Arm
        # 9 Low R Chest
        # 10 Low L Chest
        # 11 R Elbow
        # 12 L Elbow
        # 13 R Abdomen
        # 14 L Abdomen
        # 15 R Forearm
        # 16 L Forearm
        # 17 R Hip
        # 18 L Hip
        # 19 R Hand
        # 20 L Hand
        # 21 R Thigh
        # 22 L Thigh
        # 23 R Knee
        # 24 L Knee
        # 25 R Shin
        # 26 L Shin
        # 27 R Foot
        # 28 L Foot


        #If given a number, return a name
        try:
            val = int(location)
            title = loc_list[location]
        except:
            title = loc_list.index(location)

        return title

    def get_locations(self):
        loc_list = []
        i = 0
        for location in self.locations:
            loc_list.append(self.name_location(i))
            i += 1

        return loc_list

    def find_location(self, roll):
        location = 0
        if roll == 0:
            return 28
        else: 
            location += 1
            if roll > 3:
                location += 1
            if roll > 8:
                location += 1
            if roll > 10:
                location += 1
            if roll > 13:
                location += 1
            if roll > 16:
                location += 1
            if roll > 25:
                location += 1
            if roll > 34:
                location += 1
            if roll > 39:
                location += 1
            if roll > 44:
                location += 1
            if roll > 49:
                location += 1
            if roll > 54:
                location += 1
            if roll > 55:
                location += 1
            if roll > 56:
                location += 1
            if roll > 59:
                location += 1
            if roll > 62:
                location += 1
            if roll > 66:
                location += 1
            if roll > 70:
                location += 1
            if roll > 72:
                location += 1
            if roll > 74:
                location += 1
            if roll > 76:
                location += 1
            if roll > 78:
                location += 1
            if roll > 83:
                location += 1
            if roll > 88:
                location += 1
            if roll > 89:
                location += 1
            if roll > 90:
                location += 1
            if roll > 94:
                location += 1
            if roll > 98:
                location += 1
            return location

    