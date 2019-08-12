import math
from copy import deepcopy
from components.fighter import Fighter
from components import weapon
from utilities import clamp, inch_conv

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
        self.weapons = weapons
        self.guard = None

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
        attributes, facing = fighter_attrs[0], fighter_attrs[1]
        if len(fighter_attrs) > 2: ai = fighter_attrs[2]
        self.fighter = Fighter(attributes, facing, ai)

    def add_weapon_component(self, wpn, loc) -> None:
        '''Assign attacks to fighter component by copying them from base_attacks and then modifying as necessary'''
        scalar = .8 #Adjust this to reduce damage from off hand
        if self.weapons is None: self.weapons=[]
        for w in weapon.weapon_master_list:
            new_wpn = w()
            if wpn == new_wpn.name:
                #Add a new weapon if it doesn't exist, else, retreive existing weapon
                if len(self.weapons)<1:
                    self.weapons.append(new_wpn)
                    idx = self.weapons.index(new_wpn)
                for wp in self.weapons:
                    if wp.name != new_wpn.name: 
                        self.weapons.append(new_wpn)
                        idx = self.weapons.index(new_wpn)
                    else:
                        idx = self.weapons.index(wp)
                base_wpn = self.weapons[idx]


                for a in base_wpn.base_attacks:
                    if (loc <=1 and not a.hand) or (loc > 1 and a.hand): #loc variable defines the 'location' the attack originates from. locs = 0:R hand, 1:L Hand, 2:R Foot, 3: L foot
                        continue
                    atk = deepcopy(a)
                    base_wpn.attacks.append(atk)
                    if loc == 0 or loc == 2:
                        atk.name += '(R)'
                    else:
                        atk.name += '(L)'
                    if self.fighter.dom_hand == 'R':
                        if loc == 0 or loc == 2:
                            continue
                        else:
                            atk.b_dam *= scalar
                            atk.p_dam *= scalar
                            atk.s_dam *= scalar
                            atk.t_dam *= scalar
                            atk.attack_mod -= 20
                            atk.parry_mod -= 20
                    elif self.fighter.dom_hand == 'L':
                        if loc == 0 or loc == 2:
                            atk.b_dam *= scalar
                            atk.p_dam *= scalar
                            atk.s_dam *= scalar
                            atk.t_dam *= scalar
                            atk.attack_mod -= 20
                            atk.parry_mod -= 20

        #Sort the list of objects alphabetically using the name attribute            
        base_wpn.attacks.sort(key=lambda x: x.name)

    

    def set_guard_def_mods(self) -> None:
        self.fighter.loc_hit_mod = self.guard.loc_hit_mods
        self.fighter.guard_dodge_mod = self.guard.dodge_mod
        self.fighter.guard_parry_mod = self.guard.parry_mod
        self.fighter.auto_block_locs = self.guard.auto_block
        

    def determine_combat_stats(self, weapon, attack, location = 30, angle_id = 10):
        weapon = weapon
        skill = weapon.skill
        skill_rating = getattr(self.fighter, skill)
        tot_er = self.fighter.er + weapon.length
        b_psi = self.fighter.ep * attack.b_dam
        s_psi = self.fighter.ep * attack.s_dam
        t_psi = self.fighter.ep * attack.t_dam
        p_psi = self.fighter.ep * attack.p_dam
        to_hit = attack.attack_mod + skill_rating + self.fighter.guard_hit_mod
        to_parry = attack.parry_mod + skill_rating
        dodge_mod = self.fighter.stance_dodge
        parry_mod = 0
        dam_mult = 1
        weight_factor = (self.fighter.weight/100)**.4
        
        final_ap = int(attack.base_ap * (((100/skill_rating)**.2 + weight_factor)))
        if final_ap > self.fighter.swift: final_ap = self.fighter.swift
        parry_ap = int(weapon.parry_ap * (((100/skill_rating)**.2 + weight_factor)))  

        if self.guard is not None:
            to_hit += self.guard.hit_mod

        #Loc mods
        if location == 0 or 10 < location < 13:
            to_hit -= 60
            dodge_mod += 10
            #B Soak due to location flexibility
            if 10 < location <13:
                b_psi *= 50/self.fighter.flex
                dodge_mod += 20
        elif location == 1 or 18 < location < 21 or 22 < location < 25:
            to_hit -= 40
            if location == 1:
                dodge_mod += 20
                parry_mod -= 10
                b_psi *= 100/((self.fighter.flex + self.fighter.brawling)/2)
            if 18 < location < 21:
                dodge_mod += 40
                parry_mod += 30
                b_psi *= 25/self.fighter.flex
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
                b_psi *= 100/self.fighter.flex
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
                b_psi *= 40/self.fighter.flex
            else:
                dodge_mod += 30
                parry_mod -= 30
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

        for wpn in self.weapons:
            for atk in wpn.attacks:
                cs = self.determine_combat_stats(wpn, atk)
                wpn_ap.append(cs.get('final ap'))
            min_wpn_ap.append(min(wpn_ap))
        min_ap = min(min_wpn_ap)
        return min_ap
    
    def set_default_guard(self):
        for wpn in self.weapons:
            for guard in wpn.guards:
                if self.fighter.dom_hand == 'R' or 'A':
                    if guard.rh_default: self.fighter.change_guard(guard)
                else:
                    if guard.lh_default: self.fighter.change_guard(guard)

    def set_reach(self) -> None:
        if self.fighter.dom_hand == 'R':
            self.fighter.reach = clamp(inch_conv(self.fighter.er + self.weapons[0].length, 1), 2)
            if len(self.weapons) > 1: 
                self.fighter.reach_oh = clamp(inch_conv(self.fighter.er + self.weapons[1].length, 1), 2)
            else:
                self.fighter.reach_oh = self.fighter.reach
        else:
            self.fighter.reach = clamp(inch_conv(self.fighter.er + self.weapons[1].length, 1), 2)
            if len(self.weapons) > 1: 
                self.fighter.reach_oh = clamp(inch_conv(self.fighter.er + self.weapons[0].length, 1), 2)
            else:
                self.fighter.reach_oh = self.fighter.reach
                
        self.fighter.reach_leg = clamp(inch_conv((self.fighter.height*self.fighter.location_ratios[17]) + self.weapons[0].length, 1), 2)


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
            #Set reach for all weapons
            entity.set_reach()


def get_blocking_entities_at_location(entities, destination_x, destination_y) -> object or None:
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity
    return None

