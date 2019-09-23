from statistics import mean
from copy import copy, deepcopy
from utilities import inch_conv, clamp
from enums import FighterStance
from chargen_functions import height_curve

class Fighter:
    def __init__(self, facing, ai = None, l_blocker = None, r_blocker = None):
        #Transitory combat variables
        self.end_turn = False
        if ai is not None:
            self.ai = ai(self)
        self.facing = facing #Facing for FOV
        self.strafe = 'auto'
        self.aoc = [] #List of cells for AOC
        self.aoc_facing = facing
        self.action = [] #List of available commmands for combat menus
        self.atk_result = None #Atk roll for last attack
        self.dam_result = None #Dam multiplier for last attack
        self.new_loc_result = None #Used when attack hits wrong loc
        self.last_atk_ap = 0
        self.targets = [] #This is a list of targets in AOC, set by update_targets
        self.curr_target = None
        self.counter_attack = None #Hold the target against who a counter attack can be executed
        self.loc_hit_diff = [] #A list of dicts in the same order as self.targets in 'location name':mod format displayed to fighter to show perceived hit chances
        self.loc_dodge_diff = [] #A list of dicts in the same order as self.targets in 'location name':mod format displayed to fighter to show perceived dodge chances
        self.loc_parry_diff = [] #A list of dicts in the same order as self.targets in 'location name':mod format displayed to fighter to show perceived parry chances
        self.loc_dodge_mod = dict() #A dict in 'location name':mod format with mods to dodge chance based on location(used in feints)
        self.loc_parry_mod = dict() #A dict in 'location name':mod format with mods to parry chance based on location(used in feints)
        self.loc_hit_mod = dict() #A dict in 'location name':mod format with mods to hit chance based on location(guard mods)
        self.auto_block_locs = [] #A list of locations autoblocked by the guard (ints)
        self.guard = None
        self.guard_dodge_mod = 0
        self.guard_parry_mod = 0
        self.guard_hit_mod = 0
        self.stance = 'Open, Short, Low, Rear'
        self.stance_stability = 0 #A var to hold the modifier to stability from stance
        self.stance_dodge = 0 #Var to adjust dodge chances based on stance
        self.stance_power = 1 # Var to adjust ep based on stanc. Multiplier
        self.atk_instability = 0 #A var to hold the modifier to stability from attacks
        self.paralysis_instability = 0 #Var to hold stability modifications from being unable to use a leg
        self.visible_fighters = [] #This is a list of fighters in FOV, set by detect_enemies
        self.closest_fighter = None #The closest fighter, set by detect_enemies
        self.combat_choices = [] #List of chosen commands for combat menus
        self.attacker = None
        self.attacker_history = []
        self.disengage = False
        self.feint = False
        self.mods = []
        self.wait = False
        self.acted = False
        self.entities_opportunity_attacked = []
        self.disengage_option = None
        #Attributes
        self.male = True
        self.dom_hand = 'R' #'R', 'L', or 'A'
        self.attr_dict = dict()
        self.parent_attr_dict = dict()
        
        #Skills
        self.skill_dict = dict()
        #Derived Attributes
        self.height =0 #Height in inches
        self.er = 0 #Eff reach, 1/2 ht in inches
        #Local var to handle secondary calc for weight
        wt_mod = 0
        self.weight = 0
        self.stamina = 0
        self.max_stamina = 0
        #Local var to handle secondary calc for stamr
        sr_mod = 0
        self.stamr = 0
        self.max_stamr = 0
        self.vitae = 0
        self.max_vitae = 0
        self.vitr = 0
        self.max_mv = 0
        self.mv = self.max_mv
        self.max_ap = 0
        self.ap = self.max_ap
        self.walk_ap = 0
        self.jog_ap = 0
        self.run_ap = 0
        self.init = 0
        self.max_init = 0
        self.clarity = 0 #For dizziness/unconsciousness
        self.clar_recovery = 0
        self.stability_mods = 0
        self.stability = self.stability_mods
        
        #Reach
        self.reach = None #Main hand reach. All reach vars set by entity.set_reach
        self.reach_oh = None #Off hand reach
        self.reach_leg = None #Leg reach
        #Base stamina cost for actions; clamped so all actions require at least some stamina over regin
        self.base_stam_cost = 0

        #Hit Locations
        self.locations = []         
        self.max_locations = []
        
        self.location_ht = []
        self.location_ratios = (1, .9, .87, .82, .82, .8, .8, .7, .7, .72, .72, .63, .63, .6, .6, .55, .55, .53, .53, .49, .49, .4, .4, .29, .29, .2, .2, .04, .04) #Used for location ht calc
               
        #Injury list
        self.injuries = []
        #Static injury effects
        self.temp_physical_mod = 0
        self.paralyzed_locs = set()
        self.severed_locs = set()
        self.diseases = set()
        self.atk_mod_r = 0
        self.atk_mod_l = 0
        self.can_act = True
        self.can_walk = True
        self.can_stand = True
        #Continuous Injury Effects
        self.bleed = [] #Amount, duration
        #rds until dead from suffocation
        self.suffocation = None
        self.stam_drain = 0
        #Temp effects
        self.immobilized_locs = set()
        #Will check modifier due to pain for movement
        self.pain_mod_mov = 0
        self.gen_stance = FighterStance.standing
        #Active Grappling maneuvers
        self.maneuvers = []
        #fov arrays
        self.fov_visible = set()
        self.fov_wall = set()
        self.fov_explored = set()
        #Persistent derived combat attrubites
        self.l_blocker = l_blocker
        self.r_blocker = r_blocker



    def update_aoc_facing(self) -> None:
        #Hack to handle incongruity between aoc facing and fov facing
        if self.facing == 0:
            self.aoc_facing = 7
        else:
            self.aoc_facing = self.facing -1

    def adjust_max_locations(self, location_index, layer_index, value_to_subtract) -> None:
        #Method to reduce max location hits for permanent injuries, also reducing location hits at that time
        self.max_locations[location_index][layer_index] -= value_to_subtract
        if self.locations[location_index][layer_index] > self.max_locations[location_index][layer_index]:
            self.locations[location_index][layer_index] = self.max_locations[location_index][layer_index]

    def mod_attribute(self, attribute, amount, max_val = False) -> None:
        
        #Setter for attributes
        value = self.get_attribute(attribute)
        if value + amount <= 0: value = 0
        else: value += int(amount)
        
        #Normal Data types
        if hasattr(self, attribute):
            setattr(self, attribute, value)

        #Primary attributes (Object in a dict data type)
        else:
            if max_val: prop = 'max_val'
            else: prop = 'val'

            self.set_attribute(attribute, prop, value)
    
    def name_location(self, location) -> int or str:
        #Method to convert loc names to numbers and vice versa
        loc_list = ['Scalp', 'Face', 'Neck', 'R Shoulder', 'L Shoulder', 'R Chest', 'L Chest', 'Up R Arm', 'Up L Arm', 'R Ribs', 'L Ribs', 
                    'R Elbow', 'L Elbow', 'R Abdomen', 'L Abdomen', 'R Forearm', 'L Forearm', 'R Hip', 'L Hip', 'R Hand', 'L Hand', 'R Thigh', 'L Thigh', 
                    'R Knee', 'L Knee', 'R Shin', 'L Shin', 'R Foot', 'L Foot']
        #Key for reference
        # 0 Scalp
        # 1 Face
        # 2 Neck
        # 3 R Shoulder
        # 4 L Shoulder
        # 5 R Chest
        # 6 L Chest
        # 7 Up R Arm
        # 8 Up L Arm
        # 9 R Ribs
        # 10 L Ribs
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
        #Otherwise, return a number
        except:
            title = loc_list.index(location)

        return title

    def get_locations(self) -> list:
        #Creates a list of location names and returns them
        loc_list = []
        i = 0
        for location in self.locations:
            loc_list.append(self.name_location(i))
            i += 1

        return loc_list

    def find_location(self, roll) -> int:
        #Used for random injury location determination (traps, etc)
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

    def adjust_loc_diffs(self, target, location, hit_mod = 0, dodge_mod = 0, parry_mod = 0) -> None:
        i = self.targets.index(target)

        target_hit = self.loc_hit_diff[i]
        target_parry = self.loc_parry_diff[i]
        target_dodge = self.loc_dodge_diff[i]

        target_hit[location] += hit_mod
        target_dodge[location] += dodge_mod
        target_parry[location] += parry_mod

    def change_stance(self, stance) -> None:
        self.stance_stability = 0 #Set back to neutral before applying mods
        self.stance_dodge = 0
        self.stance_power = 1
        
        if 'Open' in stance:
            self.stance_stability += 10
        if 'Long' in stance:
            self.stance_stability += 10
            self.stance_dodge += -10
        elif 'Short' in stance:
            self.stance_stability += -10
            self.stance_dodge += 10
        if 'High' in stance:
            self.stance_dodge += 10
        elif 'Low' in stance:
            self.stance_power += .1
        if 'Front' in stance:
            self.stance_power += .1
        elif 'Rear' in stance:
            self.stance_power += -.1
            self.stance_dodge += 10
        
        self.stance = stance

    def get_defense_modifiers(self, location) -> dict:
        auto_block = False
        loc_idx = self.name_location(location)
        hit_mod = 0

        dodge_mod = self.stance_dodge + self.guard_dodge_mod
        parry_mod = self.guard_parry_mod

        dodge_mod += self.loc_dodge_mod.get(location)
        parry_mod += self.loc_parry_mod.get(location)

        if location in self.loc_hit_mod:
            hit_mod = self.loc_hit_mod.get(location)
        
        if loc_idx in self.auto_block_locs:
            auto_block = True 


        def_mods = {'dodge':dodge_mod, 'parry':parry_mod, 'hit': hit_mod, 'auto-block': auto_block}

        return def_mods

    def change_guard(self, guard) -> None:
        self.guard = guard.name
        self.guard_dodge_mod = guard.dodge_mod
        self.guard_parry_mod = guard.parry_mod
        self.auto_block_locs = guard.auto_block
        self.guard_hit_mod = guard.hit_mod
        self.loc_hit_mod = guard.loc_hit_mods

    def get_attribute(self, attr, value = 'val') -> int:
        dicts = [self.parent_attr_dict, self.attr_dict, self.skill_dict]
        if hasattr(self, attr):
            a = self
            attribute = attr
            result = getattr(a, attribute)
        else:
            for d in dicts:
                for key in d:
                    if key == attr:
                        a = d.get(attr)
                        if d == self.skill_dict:
                            if value == 'val': value = 'rating'
                        result = getattr(a, value)
                        break
        
        return result

    def set_attribute(self, attr, prop = 'val', value = 0) -> None:
        if attr in ['int','str','agi','con','sens','appear']:
            a = self.parent_attr_dict.get(attr)
        else:
            a = self.attr_dict.get(attr)
        setattr(a, prop, value)

    def set_dynamic_attributes(self):
        #Skills
        self.brawling = int(round(self.get_attribute('agi')*0.4 + self.get_attribute('str')*0.4 + ((self.get_attribute('men')+self.get_attribute('wis'))/2)*0.2))
        self.wrestling = int(round(self.get_attribute('agi')*0.5 + self.get_attribute('str')*0.25 + ((self.get_attribute('men')+self.get_attribute('wis'))/2)*0.25))
        self.martial_arts = int(round(self.get_attribute('men')*0.4 + ((self.get_attribute('mem')+self.get_attribute('wis'))/2)*0.4 + self.get_attribute('agi')*0.2))
        self.boxing = int(round(self.get_attribute('agi')*0.5 + ((self.get_attribute('mem')+self.get_attribute('wis'))/2)*0.2 + self.get_attribute('men')*0.3))
        self.long_sword = int(round(self.get_attribute('agi')*0.6 + ((self.get_attribute('men') + self.get_attribute('pwr'))/2)*0.3 + self.get_attribute('wis')*0.1))
        self.dodge = int(round(self.get_attribute('swift')*.6 + ((self.get_attribute('ped') + self.get_attribute('bal'))/2)*.2 + ((self.get_attribute('men') + self.get_attribute('wis'))/2)*.2))
        self.deflect = int(round(((self.get_attribute('men') + self.get_attribute('wis'))/2)*.5 + self.get_attribute('swift')*.3 + self.get_attribute('agi')*.2))
        #Derived Attributes
        self.height = int(round((height_curve(self.get_attribute('ht'))))) #Height in inches
        self.er = self.height/2 #Eff reach, 1/2 ht in inches
        #Local var to handle secondary calc for weight
        wt_mod = ((((self.get_attribute('bone')-100)/20)+((self.get_attribute('fat')-100)/4)+((self.get_attribute('str')-100)/8))/100)+1
        self.weight = int(round((self.get_attribute('ht')*1.6)*wt_mod))
        self.stamina = int(round((self.get_attribute('sta') * 2) + self.get_attribute('shock') + self.get_attribute('ss')))
        self.max_stamina = deepcopy(self.stamina)
        #Local var to handle secondary calc for stamr
        sr_mod = (self.stamina + ((self.get_attribute('immune') / 5) + (self.get_attribute('toxic')/20) + (self.get_attribute('shock')/10)))/100
        self.stamr = int(round((self.stamina/100)*sr_mod))
        self.max_stamr = deepcopy(self.stamr)
        self.vitae = int(round(self.weight/0.03))
        self.max_vitae = deepcopy(self.vitae)
        self.vitr = int((((self.get_attribute('immune')/100)*self.weight)/60))
        self.max_mv = int(round(((self.get_attribute('ht')/2) * 7.5) * (((self.get_attribute('ht') * 2.5) / self.weight) * (self.get_attribute('swift') / 100) * (self.get_attribute('flex') / 100))))
        self.mv = self.max_mv
        self.max_ap = self.get_attribute('swift')
        self.ap = self.max_ap
        self.walk_ap = round(self.ap / inch_conv(self.mv, 1))
        self.jog_ap = round(self.ap / inch_conv(self.mv*1.5, 1))
        self.run_ap = round(self.ap / inch_conv(self.mv*2, 1))
        self.max_init = deepcopy(self.init)
        self.clarity = self.get_attribute('will') #For dizziness/unconsciousness
        self.clar_recovery = self.get_attribute('will')/4
        self.stability_mods = self.stance_stability + self.atk_instability + self.paralysis_instability + (100 - self.clarity)
        self.stability = self.stability_mods

        #Base stamina cost for actions; clamped so all actions require at least some stamina over regin
        self.base_stam_cost = clamp(int(round(((self.get_attribute('fat')/self.get_attribute('str'))*(self.weight/100)*10))),self.max_stamr+1) 

        #Hit Locations
        self.locations = []
        self.locations.append([(self.get_attribute('derm') + self.get_attribute('fat')/2),(self.get_attribute('ss')/6 + self.get_attribute('pwr')/3),(self.get_attribute('bone') * 10)])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/4),(self.get_attribute('ss')/5 + self.get_attribute('pwr')/2),(self.get_attribute('bone') * 8)])
        self.locations.append([(self.get_attribute('derm') + self.get_attribute('fat')/2),(self.get_attribute('ss')/3 + self.get_attribute('pwr')),self.get_attribute('bone')*6])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/4),(self.get_attribute('ss')/2 + self.get_attribute('pwr')*2),self.get_attribute('bone')*6])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/4),(self.get_attribute('ss')/2 + self.get_attribute('pwr')*2),self.get_attribute('bone')*6])
        self.locations.append([(self.get_attribute('derm') + self.get_attribute('fat')/2),(self.get_attribute('ss')/2 + self.get_attribute('pwr')*2),self.get_attribute('bone')*6])
        self.locations.append([(self.get_attribute('derm') + self.get_attribute('fat')/2),(self.get_attribute('ss')/2 + self.get_attribute('pwr')*2),self.get_attribute('bone')*6])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/4),(self.get_attribute('ss')/3 + self.get_attribute('pwr')),(self.get_attribute('bone')*4)])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/4),(self.get_attribute('ss')/3 + self.get_attribute('pwr')),(self.get_attribute('bone')*4)])
        self.locations.append([(self.get_attribute('derm') + self.get_attribute('fat')/2),(self.get_attribute('ss')/5 + self.get_attribute('pwr')/2),(self.get_attribute('bone')*4)])
        self.locations.append([(self.get_attribute('derm') + self.get_attribute('fat')/2),(self.get_attribute('ss')/5 + self.get_attribute('pwr')/2),(self.get_attribute('bone')*4)])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/4),(self.get_attribute('ss')/10 + self.get_attribute('pwr')/4),(self.get_attribute('bone')*4)])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/4),(self.get_attribute('ss')/10 + self.get_attribute('pwr')/4),(self.get_attribute('bone')*4)])
        self.locations.append([(self.get_attribute('derm')/4 + self.get_attribute('fat')*2),(100 + self.get_attribute('ss')/2 + self.get_attribute('pwr')),self.get_attribute('bone')*6])
        self.locations.append([(self.get_attribute('derm')/4 + self.get_attribute('fat')*2),(100 + self.get_attribute('ss')/2 + self.get_attribute('pwr')),self.get_attribute('bone')*6])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/4),(self.get_attribute('ss')/5 + self.get_attribute('pwr')/2),self.get_attribute('bone')*2])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/4),(self.get_attribute('ss')/5 + self.get_attribute('pwr')/2),self.get_attribute('bone')*2])
        self.locations.append([(self.get_attribute('derm')/4 + self.get_attribute('fat')*2),(self.get_attribute('ss')/2 + self.get_attribute('pwr')*2),self.get_attribute('bone')*8])
        self.locations.append([(self.get_attribute('derm')/4 + self.get_attribute('fat')*2),(self.get_attribute('ss')/2 + self.get_attribute('pwr')*2),self.get_attribute('bone')*8])
        self.locations.append([(self.get_attribute('derm')),(self.get_attribute('ss')/10 + self.get_attribute('pwr')/4),self.get_attribute('bone')])
        self.locations.append([(self.get_attribute('derm')),(self.get_attribute('ss')/10 + self.get_attribute('pwr')/4),self.get_attribute('bone')])
        self.locations.append([(self.get_attribute('derm') + self.get_attribute('fat')),(self.get_attribute('ss') + self.get_attribute('pwr')*4),self.get_attribute('bone')*10])
        self.locations.append([(self.get_attribute('derm') + self.get_attribute('fat')),(self.get_attribute('ss') + self.get_attribute('pwr')*4),self.get_attribute('bone')*10])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/2),(self.get_attribute('ss')/5 + self.get_attribute('pwr')/2),self.get_attribute('bone')*6])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/2),(self.get_attribute('ss')/5 + self.get_attribute('pwr')/2),self.get_attribute('bone')*6])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/2),(self.get_attribute('ss')/3 + self.get_attribute('pwr')),self.get_attribute('bone')*8])
        self.locations.append([(self.get_attribute('derm')/2 + self.get_attribute('fat')/2),(self.get_attribute('ss')/3 + self.get_attribute('pwr')),self.get_attribute('bone')*8])
        self.locations.append([(self.get_attribute('derm')*1.5),(self.get_attribute('ss')/6 + self.get_attribute('pwr')/3),(self.get_attribute('bone') * 2)])
        self.locations.append([(self.get_attribute('derm')*1.5),(self.get_attribute('ss')/6 + self.get_attribute('pwr')/3),(self.get_attribute('bone') * 2)])
        #Code to fill locations list
        for location in self.locations:
            i = 0
            for amount in location:
                amount = int(round(amount))
                location[i] = amount
                i += 1
            

        self.max_locations = deepcopy(self.locations)


        for l in self.get_locations():
            #Fill dodge and parry mod dicts with 0's
            self.loc_dodge_mod[l] = 0
            self.loc_parry_mod[l] = 0

        #Fill location heights
        i = 0
        for x in self.locations:
            if not any(x):
                i += 1
                continue
            else:
                self.location_ht.append(self.height * self.location_ratios[i])
                i += 1

        
        #If no blocker defined, use bone in forearms
        if self.l_blocker == None:
            self.l_blocker = self.locations[16][2]
        if self.r_blocker == None:
            self.r_blocker = self.locations[15][2]
        #Best skills
        self.best_combat_skill = None
        self.best_unarmed_skill = None
        self.best_grappling_skill = None

        for key in self.skill_dict:
            skill = self.skill_dict.get(key)
            if skill.offensive:
                if self.best_combat_skill == None or self.best_combat_skill.rating < skill.rating:
                    self.best_combat_skill = skill
        
        for key in self.skill_dict:
            skill = self.skill_dict.get(key)
            if skill.offensive and skill.unarmed:
                if self.best_unarmed_skill == None or self.best_unarmed_skill.rating < skill.rating:
                    self.best_unarmed_skill = skill

        for key in self.skill_dict:
            skill = self.skill_dict.get(key)
            if skill.grappling:
                if self.best_grappling_skill == None or self.best_grappling_skill.rating < skill.rating:
                    self.best_grappling_skill = skill


        self.init = (self.get_attribute('men') + self.get_attribute('swift'))/4 + (self.get_attribute('sens') + self.get_attribute(self.best_combat_skill.abbr))/4


class Attribute():
    def __init__(self, name, abr, max_val, **kwargs):
        self.name = name
        self.abr = abr
        self.max_val = max_val
        self.val = self.max_val
        self.parent_attr = None
        
        self.__dict__.update(kwargs)
        self.set_parent()
    def set_parent(self):
        if self.abr in ['log', 'mem', 'wis', 'comp', 'comm', 'cre', 'men', 'will']:
            self.parent_attr = 'int'
        elif self.abr in ['ss','pwr']:
            self.parent_attr = 'str'
        elif self.abr in ['man','ped','bal','swift','flex']:
            self.parent_attr = 'agi'
        elif self.abr in ['sta','derm','bone','immune','shock','toxic']:
            self.parent_attr = 'con'
        elif self.abr in ['sit','hear','ts','touch']:
            self.parent_attr = 'sens'
        else:
            self.parent_attr = 'appear'


class Skill():
    def __init__(self, entity, experience = 0, **kwargs):
        self.name = ''
        self.abbr = ''
        self.category = ''
        self.entity = entity
        self.level = 0
        self.prim_base = [] #Primary base attribute(s). If multiple, are averaged
        self.prim_amount = 0 #Percentage the PB contributes to total score
        self.sec_base = []
        self.sec_amount = 0
        self.ter_base = []
        self.ter_amount = 0
        self.experience = experience #The experience aquired in the skill
        self.autodidact = True #Defines if skill can be used untrained
        self.cost = 0 #Determines difficulty in improving skill
        self.rating = 0
        self.offensive = True
        self.unarmed = False
        self.grappling = False

        self.__dict__.update(kwargs)


    def set_level(self) -> int:
        xp = self.experience
        level = 0
        while xp > 0:
            if xp > self.cost * level:
                xp -= self.cost * level
                level += 1
            else:
                xp = 0
        
        return level

    def set_rating(self) -> int:
        prim_list = []
        sec_list = []
        ter_list = []
        prim_avg = 0
        sec_avg = 0
        ter_avg = 0
        base_rating = 0
        rating = 0

        for attr in self.prim_base:
            prim_list.append(self.entity.fighter.get_attribute(attr))

        for attr in self.sec_base:
            sec_list.append(self.entity.fighter.get_attribute(attr))
        
        for attr in self.ter_base:
            ter_list.append(self.entity.fighter.get_attribute(attr))

        prim_avg = mean(prim_list)
        sec_avg = mean(sec_list)
        ter_avg = mean(ter_list)

        base_rating = (prim_avg*self.prim_amount) + (sec_avg*self.sec_amount) + (ter_avg*self.ter_amount)

        if self.level == 0:
            rating = base_rating/2
        elif self.level == 1:
            rating = base_rating
        else:
            rating = (base_rating*2)/(self.level+1)*self.level

        return int(round(rating))

class Deflect(Skill):
    def __init__(self, entity, experience = 0, **kwargs):
        self.entity = entity
        self.experience = experience #The experience aquired in the skill
        self.name = 'Deflect'
        self.abbr = 'deflect'
        self.category = 'Unarmed'
        self.level = 0
        self.prim_base = ['men','wis'] #Primary base attribute(s). If multiple, are averaged
        self.prim_amount = .5 #Percentage the PB contributes to total score
        self.sec_base = ['swift']
        self.sec_amount = .3
        self.ter_base = ['agi']
        self.ter_amount = .2
        
        self.autodidact = True #Defines if skill can be used untrained
        self.cost = 8 #Determines difficulty in improving skill
        self.rating = 0
        self.offensive = False
        self.unarmed = True
        self.grappling = False

        self.__dict__.update(kwargs)
        self.level = self.set_level()
        self.rating = self.set_rating()

class Dodge(Skill):
    def __init__(self, entity, experience = 0, **kwargs):
        self.entity = entity
        self.experience = experience #The experience aquired in the skill
        self.name = 'Dodge'
        self.abbr = 'dodge'
        self.category = 'Unarmed'
        self.level = 0
        self.prim_base = ['swift'] #Primary base attribute(s). If multiple, are averaged
        self.prim_amount = .6 #Percentage the PB contributes to total score
        self.sec_base = ['ped','bal']
        self.sec_amount = .2
        self.ter_base = ['men','wis']
        self.ter_amount = .2
        
        self.autodidact = True #Defines if skill can be used untrained
        self.cost = 6 #Determines difficulty in improving skill
        self.rating = 0
        self.offensive = False
        self.unarmed = True
        self.grappling = False

        self.__dict__.update(kwargs)
        self.level = self.set_level()
        self.rating = self.set_rating()

class Martial_Arts(Skill):
    def __init__(self, entity, experience = 0, **kwargs):
        self.entity = entity
        self.experience = experience #The experience aquired in the skill
        self.name = 'Martial Arts'
        self.abbr = 'martial_arts'
        self.category = 'Unarmed'
        self.level = 0
        self.prim_base = ['men'] #Primary base attribute(s). If multiple, are averaged
        self.prim_amount = .4 #Percentage the PB contributes to total score
        self.sec_base = ['mem','wis']
        self.sec_amount = .4
        self.ter_base = ['agi']
        self.ter_amount = .2
        
        self.autodidact = False #Defines if skill can be used untrained
        self.cost = 16 #Determines difficulty in improving skill
        self.rating = 0
        self.offensive = True
        self.unarmed = True
        self.grappling = True

        self.__dict__.update(kwargs)
        self.level = self.set_level()
        self.rating = self.set_rating()

class Boxing(Skill):
    def __init__(self, entity, experience = 0, **kwargs):
        self.entity = entity
        self.experience = experience #The experience aquired in the skill
        self.name = 'Boxing'
        self.abbr = 'boxing'
        self.category = 'Unarmed'
        self.level = 0
        self.prim_base = ['agi'] #Primary base attribute(s). If multiple, are averaged
        self.prim_amount = .5 #Percentage the PB contributes to total score
        self.sec_base = ['men']
        self.sec_amount = .3
        self.ter_base = ['mem','wis']
        self.ter_amount = .2
        
        self.autodidact = False #Defines if skill can be used untrained
        self.cost = 10 #Determines difficulty in improving skill
        self.rating = 0
        self.offensive = True
        self.unarmed = True
        self.grappling = False

        self.__dict__.update(kwargs)
        self.level = self.set_level()
        self.rating = self.set_rating()

class Brawling(Skill):
    def __init__(self, entity, experience = 0, **kwargs):
        self.entity = entity
        self.experience = experience #The experience aquired in the skill
        self.name = 'Brawling'
        self.abbr = 'brawling'
        self.category = 'Unarmed'
        self.level = 0
        self.prim_base = ['agi'] #Primary base attribute(s). If multiple, are averaged
        self.prim_amount = .4 #Percentage the PB contributes to total score
        self.sec_base = ['str']
        self.sec_amount = .4
        self.ter_base = ['men','wis']
        self.ter_amount = .2
        
        self.autodidact = True #Defines if skill can be used untrained
        self.cost = 8 #Determines difficulty in improving skill
        self.rating = 0
        self.offensive = True
        self.unarmed = True
        self.grappling = False

        self.__dict__.update(kwargs)
        self.level = self.set_level()
        self.rating = self.set_rating()

class Wrestling(Skill):
    def __init__(self, entity, experience = 0, **kwargs):
        self.entity = entity
        self.experience = experience #The experience aquired in the skill
        self.name = 'Wrestling'
        self.abbr = 'wrestling'
        self.category = 'Unarmed'
        self.level = 0
        self.prim_base = ['agi'] #Primary base attribute(s). If multiple, are averaged
        self.prim_amount = .5 #Percentage the PB contributes to total score
        self.sec_base = ['str']
        self.sec_amount = .25
        self.ter_base = ['men','wis']
        self.ter_amount = .25
        
        self.autodidact = True #Defines if skill can be used untrained
        self.cost = 12 #Determines difficulty in improving skill
        self.rating = 0
        self.offensive = True
        self.unarmed = True
        self.grappling = True

        self.__dict__.update(kwargs)
        self.level = self.set_level()
        self.rating = self.set_rating()

class Long_Sword(Skill):
    def __init__(self, entity, experience = 0, **kwargs):
        self.entity = entity
        self.experience = experience #The experience aquired in the skill
        self.name = 'Long Sword'
        self.abbr = 'long_sword'
        self.category = 'Bladed'
        self.level = 0
        self.prim_base = ['agi'] #Primary base attribute(s). If multiple, are averaged
        self.prim_amount = .6 #Percentage the PB contributes to total score
        self.sec_base = ['men','pwr']
        self.sec_amount = .3
        self.ter_base = ['wis']
        self.ter_amount = .1
        
        self.autodidact = True #Defines if skill can be used untrained
        self.cost = 10 #Determines difficulty in improving skill
        self.rating = 0
        self.offensive = True
        self.unarmed = False
        self.grappling = False

        self.__dict__.update(kwargs)
        self.level = self.set_level()
        self.rating = self.set_rating()