import math
import time
from statistics import mean
from copy import deepcopy, copy
from components.fighter import Fighter, Attribute, Skill
from components import weapon
from utilities import clamp, inch_conv, itersubclasses


weapon_master_list = list(itersubclasses(weapon.Weapon))

class Entity:

    def __init__(self, x, y, char, color, name, state, player = False, blocks = False, fighter = None, weapons = None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.player = player
        self.blocks = blocks
        self.fighter = fighter
        self.state = state
        self.guard = None
        self.worn_armor = {} #Dict of dicts in the following format: 1:{'component':'Curiass','construction':'Plate','main_material' : 'Hardened Steel','thickness':.05}
        self.loc_armor = [] #List of lists, populated by apply_armor, in order from inner to outer
        while len(self.loc_armor)<29:
            self.loc_armor.append([])

        if self.fighter:
            self.fighter.owner = self

    def mod_attribute(self, attribute, amount) -> None:
        value = int(getattr(self, attribute))
        if value + amount <= 0: setattr(self, attribute, 0)
        else: 
            value += int(amount)
            setattr(self, attribute, value)

    def add_fighter_component(self, fighter_attrs) -> None:
        ai = None
        attributes, skills, facing = fighter_attrs[0], fighter_attrs[1], fighter_attrs[2]
        if len(fighter_attrs) > 3: ai = fighter_attrs[3]
        self.fighter = Fighter(facing, ai)
        self.fighter.attr_dict = self.add_attributes(attributes)
        #Calc and add parent attributes
        parent_list = ['int','str','agi','con','sens','appear']
        parent_name_list = ['Intellect', 'Strength', 'Agility', 'Constitution', 'Senses', 'Appearance']
        for p in parent_list:
            children = []
            idx = parent_list.index(p)
            for key in self.fighter.attr_dict:
                a = self.fighter.attr_dict[key]
                if a.parent_attr == p:
                    children.append(a.val)
            if parent_name_list[idx] == 'Appearance': #Higher fat = lower appearance
                children[-2] = 100 - children[-2]
            p_val = int(round(mean(children)))
            p_attr = Attribute(parent_name_list[idx], p, p_val)
            self.fighter.parent_attr_dict[p] = p_attr

        for key in skills:
            for cls in itersubclasses(Skill):
                c = cls(self)
                if c.abbr == key:
                    xp = skills.get(key)
                    s = cls(self, xp)
            self.fighter.skill_dict[key] = s

        for cls in itersubclasses(Skill):
            c = cls(self)
            if c.abbr not in self.fighter.skill_dict:
                self.fighter.skill_dict[c.abbr] = c


        self.fighter.set_dynamic_attributes()




    def add_weapon_component(self, wpn, loc) -> None:
        '''Assign attacks to fighter component creating instances from base_attacks and then modifying as necessary'''
        scalar = .8 #Adjust this to adjust damage from off hand

        for w in weapon_master_list:
            new_wpn = w()
            if wpn == type(new_wpn).__name__:
                if loc == 0:
                    self.fighter.equip_loc[19] = new_wpn
                elif loc == 1:
                    self.fighter.equip_loc[20] = new_wpn
                elif loc == 2: 
                    self.fighter.equip_loc[27] = new_wpn
                else:
                    self.fighter.equip_loc[28] = new_wpn
                
                for a in new_wpn.base_attacks:

                    atk = a(new_wpn)
 
                    #Set right/l and add

                    if atk.hand:
                        if loc in [0,1]:
                            new_wpn.attacks.append(atk)
                            if atk.hands != 2:
                                if loc == 0:
                                    atk.name += '(R)'
                                else:
                                    atk.name += '(L)'
                                if self.fighter.dom_hand == 'R':
                                    if loc == 0:
                                        continue
                                    else:
                                        atk.force_scalar *= scalar
                                        atk.attack_mod -= 20
                                        atk.parry_mod -= 20
                                elif self.fighter.dom_hand == 'L':
                                    if loc == 0:
                                        atk.force_scalar *= scalar
                                        atk.attack_mod -= 20
                                        atk.parry_mod -= 20
                    else:
                        if loc in [2,3]:
                            new_wpn.attacks.append(atk)
                            if loc == 2:
                                atk.name += '(R)'
                            else:
                                atk.name += '(L)'


                
                for m in new_wpn.base_maneuvers:
                    mnvr = m(self,self,'Scalp')
                    if (loc <=1 and not mnvr.hand) or (loc > 1 and mnvr.hand): #loc variable defines the 'location' the attack originates from. locs = 0:R hand, 1:L Hand, 2:R Foot, 3: L foot
                        continue
                    new_wpn.maneuvers.append(mnvr)
                    

        #Sort the lists of objects alphabetically using the name attribute            
        new_wpn.attacks.sort(key=lambda x: x.name)
        new_wpn.maneuvers.sort(key=lambda x: x.name)

    def validate_attacks(self) -> None:

        for loc in [19,20,27,28]:
            w = self.fighter.equip_loc.get(loc)
            if not w.weapon: continue
            
            remove_list = []
            for a in w.attacks:
                if a.hand:
                    #Remove if it's a foot attack on a hand
                    if loc in [27,28]:
                        remove_list.append(a)
                    #Remove if it's a two-h attack and both hands not free
                    elif a.hands == 2:
                        if loc == 19:
                            if self.fighter.equip_loc.get(20).name not in ['Unarmed', w.name]:
                                remove_list.append(a)
                        else: 
                            if self.fighter.equip_loc.get(19).name not in ['Unarmed', w.name]:
                                remove_list.append(a)
                else:
                    #Remove is hand attack on foot
                    if loc in [19,20]:
                        remove_list.append(a)
            for i in remove_list:
                w.attacks.remove(i)

    def set_guard_def_mods(self) -> None:
        self.fighter.loc_hit_mod = self.guard.loc_hit_mods
        self.fighter.guard_dodge_mod = self.guard.dodge_mod
        self.fighter.guard_parry_mod = self.guard.parry_mod
        self.fighter.auto_block_locs = self.guard.auto_block
        
    def determine_loc_mods(self, location) -> dict:
        to_hit = 0
        dodge_mod = 0
        b_psi = 1
        parry_mod = 0

        if location == 0 or 10 < location < 13:
            to_hit -= 60
            dodge_mod += 10
            #B Soak due to location flexibility
            if 10 < location <13:
                b_psi *= 50/self.fighter.get_attribute('flex')
                dodge_mod += 20
        elif location == 1 or 18 < location < 21 or 22 < location < 25:
            to_hit -= 40
            if location == 1:
                dodge_mod += 20
                parry_mod -= 10
                b_psi *= 100/((self.fighter.get_attribute('flex') + self.fighter.best_combat_skill.rating)/2)
            if 18 < location < 21:
                dodge_mod += 40
                parry_mod += 30
                b_psi *= 25/self.fighter.get_attribute('flex')
        elif location == 2:
            to_hit -= 30
            dodge_mod -= 20
            parry_mod += 10
        elif 4 < location < 7 or 16 < location < 19:
            to_hit += 20
            dodge_mod -= 30
            parry_mod += 20
        elif 6 < location < 9 or 24 < location < 27:
            to_hit -= 10
            if 6 < location < 9:
                dodge_mod -= 10
                parry_mod -= 10
                b_psi *= 100/self.fighter.get_attribute('flex')
            else:
                dodge_mod += 10
                parry_mod -= 20
        elif 8 < location < 11 or 12 < location < 15 or 20 < location < 23:
            to_hit += 10
            if 8 < location < 11 or 12 < location < 15:
                dodge_mod -= 30
                parry_mod += 10
            else:
                dodge_mod -= 10
        elif 14 < location < 17 or 26 < location < 29:
            to_hit -= 20
            if 14 < location < 17:
                dodge_mod += 30
                parry_mod += 20
                b_psi *= 40/self.fighter.get_attribute('flex')
            else:
                dodge_mod += 30
                parry_mod -= 30

        loc_mod_dict = {'to_hit':to_hit, 'dodge_mod':dodge_mod, 'parry_mod': parry_mod, 'b_psi': b_psi}

        return loc_mod_dict

    def determine_combat_stats(self, weapon, attack, location = 30, angle_id = 0) -> dict:
        
        if len(attack.skill) > 1:
            skills = []
            for s in attack.skill:
                skills.append(self.fighter.get_attribute(s))
            max_s = max(skills)
            idx = skills.index(max_s)
            skill = attack.skill[idx]
        else:
            skill = attack.skill[0]
        skill_rating = self.fighter.get_attribute(skill)
        tot_er = self.fighter.er + attack.length
        b_psi = 0
        s_psi = 0
        t_psi = 0
        p_psi = 0
        eff_area = 0
        fist_mass = .0065 * self.fighter.weight 

        if attack.hand:
            if self.fighter.dom_hand == 'R':
                if weapon is self.fighter.equip_loc.get(19):
                    limb_length = self.fighter.reach
                else:
                    limb_length = self.fighter.reach_oh
            else:
                if weapon is self.fighter.equip_loc.get(20):
                    limb_length = self.fighter.reach
                else:
                    limb_length = self.fighter.reach_oh
        else:
            limb_length = self.fighter.reach_leg
            
        wpn_length = attack.length
        reach = limb_length + wpn_length
        if angle_id != 0: #Find distance for semi-circular paths (swings)
            circ = 2 * math.pi * reach #Find circumference
            distance = ((1/8)*circ*math.pi)/12 #Distance traveled for 45 deg angle
        else:
            distance = limb_length
        #Determine max velocity based on pwr stat and mass distribution of attack
        if attack.hands == 2:
            max_vel = math.sqrt(self.fighter.get_attribute('pwr'))*(4.5-(attack.added_mass/2))
        else:
            max_vel = math.sqrt(self.fighter.get_attribute('pwr'))*(3-(attack.added_mass/2))


        #Determine how long attack will take
        if angle_id == 0:
            time = (limb_length/12)/max_vel
        else:
            time = (((1/8)*(2*math.pi*limb_length)*math.pi)/12)/max_vel
        #Find final velocity using full distance travelled by weapon
        velocity = (1/time) * (distance/12)

        force = (fist_mass + attack.added_mass) * velocity

        psi = force*12 #Convert to inches

      
        

        #Damage calc = ((((added_mass + fist mass) * velocity) / main_area) * mech_adv) * sharpness or hardness or pointedness

        if attack.damage_type is 'b':
            eff_area =  attack.main_area * (velocity/40) #scale main area size based on velocity; hack to represent deformation
        else:
            eff_area = attack.main_area 

        ep = ((psi * attack.force_scalar) / eff_area) * attack.mech_adv

        if attack.damage_type == 's':
            modifier = attack.sharpness
            s_psi = ep*modifier
        elif attack.damage_type == 'p':
            modifier = attack.pointedness
            p_psi = ep*modifier
        elif attack.damage_type == 'b':
            modifier = attack.solidness
            b_psi = ep*modifier
        else:
            t_psi = ep

        to_hit = attack.attack_mod + skill_rating + self.fighter.guard_hit_mod - self.fighter.armor_mod - self.fighter.temp_physical_mod
        to_parry = attack.parry_mod + skill_rating - self.fighter.armor_mod - self.fighter.temp_physical_mod
        dodge_mod = self.fighter.stance_dodge - self.fighter.armor_mod - self.fighter.temp_physical_mod
        parry_mod = 0
        dam_mult = 1
        weight_factor = (self.fighter.weight/100)**.4
        
        final_ap = attack.base_ap * (((100/skill_rating)**.2 + weight_factor))
        if final_ap > self.fighter.get_attribute('swift'): final_ap = self.fighter.get_attribute('swift')
        parry_ap = int(weapon.parry_ap * (((100/skill_rating)**.2 + weight_factor)))  

        if self.guard is not None:
            to_hit += self.guard.hit_mod

        #Loc mods
        loc_mod_dict = self.determine_loc_mods(location)
        to_hit += loc_mod_dict.get('to_hit')
        dodge_mod += loc_mod_dict.get('dodge_mod')
        parry_mod += loc_mod_dict.get('parry_mod')
        b_psi *= loc_mod_dict.get('b_psi')

        #Angle mods
        if angle_id == 0:
            dam_mult *= 1.2
            to_hit += 5
            parry_mod += -15
            dodge_mod += 10
        elif angle_id == 1:
            dam_mult *= 1.1
            to_hit += 5
            parry_mod += -10
            dodge_mod += 5
        elif angle_id == 2:
            to_hit += -5
            parry_mod += 5
        elif angle_id == 3:
            to_hit += -5
            parry_mod += 15
            dodge_mod += -15
        elif angle_id == 4:             
            dam_mult *= 1.1
            to_hit -= 10
            parry_mod -= 15
            dodge_mod += 20
        elif angle_id == 5:
            dam_mult *= .9
            to_hit -= 10
            parry_mod -= 20
            dodge_mod -= 20
        elif angle_id == 6:
            to_hit -= 10
            parry_mod += -10
        elif angle_id == 7:
            parry_mod += -15
        elif angle_id == 8:
            dam_mult *= .5
            to_hit += 25
            parry_mod += -25
            dodge_mod += 5

        for x in (b_psi, s_psi, p_psi, t_psi):
            x *= dam_mult

        to_parry += parry_mod

        combat_dict = {'total er': tot_er, 'b psi': b_psi, 's psi': s_psi, 'p psi': p_psi, 't psi': t_psi, 'to hit': to_hit, 
                        'to parry': to_parry, 'dodge mod': dodge_mod, 'final ap': final_ap, 'parry ap': parry_ap, 
                        'parry mod': parry_mod}

        #convert items to int
        for key in combat_dict:
            combat_dict[key] = int(combat_dict[key])


        return combat_dict

    def get_min_ap(self) -> int:
        wpn_ap = []
        min_wpn_ap =[]

        weapons = []
        for loc in [19,20,27,28]:
            w = self.fighter.equip_loc.get(loc)
            if w is not None:
                if w.weapon:
                    weapons.append(w)

        for wpn in weapons:
            for atk in wpn.attacks:
                cs = self.determine_combat_stats(wpn, atk)
                wpn_ap.append(cs.get('final ap'))
            min_wpn_ap.append(min(wpn_ap))
        min_ap = min(min_wpn_ap)
        return min_ap
    
    def set_default_guard(self):
        weapons = []
        for loc in [19,20,27,28]:
            w = self.fighter.equip_loc.get(loc)
            if w.weapon:
                weapons.append(w)

        for wpn in weapons:
            for guard in wpn.guards:
                if self.fighter.dom_hand == 'R' or 'A':
                    if guard.rh_default: self.fighter.change_guard(guard)
                else:
                    if guard.lh_default: self.fighter.change_guard(guard)

    def set_reach(self) -> None:
        weapons = []
        for loc in [19,20,27,28]:
            w = self.fighter.equip_loc.get(loc)
            if w.weapon:
                weapons.append(w)

        r_w = self.fighter.equip_loc.get(19)
        l_w = self.fighter.equip_loc.get(20)

        if self.fighter.dom_hand == 'R':
            self.fighter.reach = clamp(inch_conv(self.fighter.er + r_w.length, 1), 2)
            if len(weapons) > 1: 
                self.fighter.reach_oh = clamp(inch_conv(self.fighter.er + l_w.length, 1), 2)
            else:
                self.fighter.reach_oh = self.fighter.reach
        else:
            self.fighter.reach = clamp(inch_conv(self.fighter.er + l_w.length, 1), 2)
            if len(weapons) > 1: 
                self.fighter.reach_oh = clamp(inch_conv(self.fighter.er + r_w.length, 1), 2)
            else:
                self.fighter.reach_oh = self.fighter.reach
                
        self.fighter.reach_leg = clamp(inch_conv((self.fighter.height*self.fighter.location_ratios[17]) + self.fighter.equip_loc.get(27).length, 1), 2)

    def add_attributes(self, attr_list) -> dict:
        attr_dict = dict()
        name_list = ['Logic', 'Memory', 'Wisdom', 'Comprehension', 'Communication', 'Creativity', 'Mental Celerity', 'Willpower', 'Steady State', 'Power', 'Manual Dexterity', 'Pedal Dexterity', 'Balance', 'Swiftness', 'Flexibility', 'Stamina', 'Dermatology', 'Bone', 'Immune', 'Shock', 'Toxic', 'Sight', 'Hearing', 'Taste/Smell', 'Touch', 'Facial Features', 'Height', 'Body Fat', 'Shapliness']
        abr_list = ['log','mem','wis','comp','comm','cre','men','will','ss','pwr','man','ped','bal','swift','flex','sta','derm','bone','immune','shock','toxic','sit','hear','ts','touch','fac','ht','fat','shape']
        idx = 0
        for a in attr_list:
            atr = Attribute(name_list[idx], abr_list[idx], a)
            attr_dict[abr_list[idx]] = atr
            idx += 1
        return attr_dict




def create_entity_list(entity_list) -> list:
    entities = []
    for item in entity_list:
        entities.append(Entity(*item))

    return entities

def fill_player_list(entities) -> list:
    players = []
    for entity in entities:
        if entity.player:
            players.append(entity)
    return players

def add_fighters(entities, fighter_list) -> None:
    for entity in entities:
        for fighter in fighter_list:
            if fighter[0] == entity.name:
                del fighter[0]
                entity.add_fighter_component(fighter)

def add_weapons(entities, weapon_dict) -> None:
    for entity in entities:
        if hasattr(entity, 'fighter'):
            #look in master weapon dict and find entity
            wpns = weapon_dict.get(entity.name)
            #look in nested entity wpn dict and find weapons for each loc, then assign with AWC method
            entity.add_weapon_component(wpns.get('r_wpn'), 0)
            entity.add_weapon_component(wpns.get('l_wpn'), 1)
            entity.add_weapon_component(wpns.get('rf_wpn'), 2)
            entity.add_weapon_component(wpns.get('lf_wpn'), 3)
            #Remove attacks
            entity.validate_attacks()
            #Set reach for all weapons
            entity.set_reach()


def get_blocking_entities_at_location(entities, destination_x, destination_y) -> object or None:
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity
    return None

