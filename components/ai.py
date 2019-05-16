import tcod.path as pathfind
from combat_functions import determine_valid_angles, angle_id, calc_history_modifier, init_combat, determine_valid_locs
from enums import CombatPhase
from components.fighter import Fighter
from fov_aoc import aoc_check
import global_vars

class CombatAI:
    def __init__ (self, host):
        self.host = host
        self.atk_result = []
        self.atk_success = False


    def ai_command(self, entity, entities, combat_phase, game_map, order) -> str:
        command = None
        if combat_phase == CombatPhase.explore:
            command = hunt_target(entity, entities, game_map)
        if combat_phase == CombatPhase.action:
            #Check AOC for targets in case one moved
            entity.fighter.targets = aoc_check(entities, entity)
            #If targets are available but no actions exist, rerun to fill action list
            if len(entity.fighter.targets) != 0 and self.host.action == 0: return command
            elif len(self.host.action) != 0:
                determine_attack(entity)
                if len(self.host.combat_choices) == 0:
                    command = {'End Turn':'End Turn'}
                elif 'Engage' in self.host.action:
                    command = {'Engage':'Engage'}
                else: command = hunt_target(entity, entities, game_map)
            else: command = hunt_target(entity, entities, game_map)
        if combat_phase == CombatPhase.weapon:
            command = {self.host.combat_choices[0].name:self.host.combat_choices[0].name}
        if combat_phase == CombatPhase.option:
            command = {self.host.combat_choices[1].name:self.host.combat_choices[1].name}
        if combat_phase == CombatPhase.location:
            location = self.host.targets[0].fighter.name_location(self.host.combat_choices[2])
            command = {location:location}
        if combat_phase == CombatPhase.option2:
            angle = angle_id(self.host.combat_choices[3])
            command = {angle:angle}
        if combat_phase == CombatPhase.confirm:
            command = {'Accept':'Accept'}
        elif combat_phase == CombatPhase.defend:
            cs = entity.determine_combat_stats(entity.weapons[0], entity.weapons[0].attacks[0])
            command = avoid_attack(self.host.attacker, entity, cs)

        return command



def determine_attack(entity) -> None:
    curr_target = entity.fighter.targets[0]
    min_ap = entity.fighter.ap

    for wpn in entity.weapons:
        for atk in wpn.attacks:
            
            cs = entity.determine_combat_stats(wpn, atk)
            b_psi = cs.get('b psi')
            s_psi = cs.get('s psi')
            p_psi = cs.get('p psi')
            t_psi = cs.get('t psi')
            final_ap = cs.get('final ap')
            if final_ap < min_ap: 
                min_ap = final_ap
                
    
    #Attack logic begins

    best_score = 0
    best_atk = []
    
    #Locations to be scored higher because they kill the foe
    critical_locs = {0,1,2,6}

    for wpn in entity.weapons:
        for atk in wpn.attacks:
            if final_ap <= entity.fighter.ap:
                loc_list = []
                locs = curr_target.fighter.locations
                for i in determine_valid_locs(entity, curr_target, atk):
                    loc_list.append(curr_target.fighter.locations[i])
                for location in loc_list:
                    loc_id = locs.index(location)
                    #Skip if location destroyed
                    if not any(location):
                        continue
                    else:
                        for angle_str in determine_valid_angles(loc_id):
                            #Variable Init
                            angle = angle_id(angle_str)
                            dam_score = 0
                            hit_score = 0
                            overall_score = 0
                            cs = entity.determine_combat_stats(wpn, atk, loc_id, angle)
                            b_psi = cs.get('b psi')
                            s_psi = cs.get('s psi')
                            p_psi = cs.get('p psi')
                            t_psi = cs.get('t psi')
                            to_hit = cs.get('to hit')
                            dodge_mod = cs.get('dodge mod')
                            final_ap = cs.get('final ap')
                            parry_ap = cs.get('parry ap')
                            parry_mod = cs.get('parry mod')
                            dam = (b_psi + s_psi + p_psi + t_psi)
                            #Attks/rd
                            atks_rd = entity.fighter.ap / final_ap
                            #Dam/rd
                            dam_base = dam * atks_rd
                            if len(curr_target.fighter.attacker_history) > 0:
                                    history_mod = calc_history_modifier(curr_target, atk, loc_id, angle)
                                    dodge_mod += history_mod
                                    parry_mod += history_mod
                            #Award points based on dam mult in respect to remaining hits in hit loc
                            for layer in location:
                                if layer > 0:
                                    dam_score += dam_base / layer
                            #Award points based on ability to hit
                            best_avoid = max(dodge_mod+curr_target.fighter.dodge, parry_mod+curr_target.fighter.deflect)
                            if to_hit == best_avoid:
                                hit_score = 1
                            else:    
                                hit_score = (100/(to_hit - best_avoid))
                                overall_score = dam_score * hit_score   
                            for loc in critical_locs:
                                if loc_id == loc: overall_score *= 1.5
                            if overall_score > best_score:
                                best_atk = [wpn, atk, loc_id, angle]
                                best_score = overall_score
    #Clear the list
    entity.fighter.combat_choices.clear()
    #Add new choices to list
    for i in best_atk:
        entity.fighter.combat_choices.append(i)

def avoid_attack(attacker, defender, cs) -> str:
    
    parry = False
    dodge = False
    parry_best = False
    can_dodge = False
    can_parry = False
    attack = attacker.fighter.combat_choices[1]
    atk_name = attack.name 

    dodge_mod = cs.get('dodge mod')
    parry_mod = cs.get('parry mod')
    final_to_hit = cs.get('to hit')                       
    cs_d = defender.determine_combat_stats(defender.weapons[0],defender.weapons[0].attacks[0])
    parry_ap = cs_d.get('parry ap')
    if defender.fighter.ap >= defender.fighter.walk_ap: can_dodge = True
    if defender.fighter.ap >= parry_ap: can_parry = True
    if len(defender.fighter.attacker_history) > 0:
        history_mod = calc_history_modifier(defender, atk_name, attacker.fighter.combat_choices[2], attacker.fighter.combat_choices[3])
        dodge_mod += history_mod
        parry_mod += history_mod
    parry_chance = defender.fighter.deflect + parry_mod
    dodge_chance = defender.fighter.dodge + dodge_mod
    
    #Determine best method. Negative numbers = dodge, positive = parry
    #Divide chance by AP on each side, then subtract dodge from parry
    parry_score = parry_chance / parry_ap
    dodge_score = dodge_chance / defender.fighter.walk_ap
    final = parry_score - dodge_score

    if final > 0: parry_best

    #Use best if possible
    if parry_best:
        if can_parry: parry = True
        elif can_dodge: dodge =  True
    else:
        if can_dodge: dodge = True
        elif can_parry: parry = True

    if parry: command = {'Parry':'Parry'}
    elif dodge: command = {'Dodge':'Dodge'}
    else: command = {'Take the hit':'Take the hit'}
    
    return command

def hunt_target(curr_actor, entities, game_map) -> list:
    astar = pathfind.AStar(game_map)
    enemies = []
    closest_coords = []
    closest_dist = 100
    path = None
    command = {'End Turn':'End Turn'}

    for entity in entities:
        if entity is not curr_actor:
            if (entity.x, entity.y) in curr_actor.fighter.fov_visible:
                if global_vars.debug: print(entity.name + ' is visible')
                enemies.append(entity)
    for enemy in enemies:
        dist = sum(((abs(enemy.x - curr_actor.x)),(abs(enemy.y - curr_actor.y))))
        if dist < closest_dist:
            closest_dist = dist
            closest_coords = [enemy.x, enemy.y]
    if closest_dist is not None:
        path = astar.get_path(curr_actor.x, curr_actor.y, closest_coords[0], closest_coords[1])

    if len(path) != 0:
        command = ['move']
        y_dir = None
        x_dir = None
        x,y = path[0]
        x_mod = x - curr_actor.x
        y_mod = y - curr_actor.y
        if y_mod == -1: y_dir = 'n'
        if y_mod == 1: y_dir = 's'
        if x_mod == -1: x_dir = 'w'
        if x_mod == 1: x_dir = 'e'
        if x_dir is not None and y_dir is not None:
            mv_dir = str(y_dir + x_dir)
        elif y_dir is not None:
            mv_dir = y_dir
        else:
            mv_dir = x_dir
        command.append(mv_dir)

    return command
