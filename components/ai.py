import tcod.path as pathfind
from random import randint
from combat_functions import determine_valid_angles, angle_id, calc_history_modifier, init_combat, determine_valid_locs
from enums import CombatPhase, EntityState
from components.fighter import Fighter
from fov_aoc import aoc_check, fov_calc
from entity import get_blocking_entities_at_location
from utilities import entity_angle, prune_list
from entity import Entity
import global_vars

class CombatAI:
    def __init__ (self, host):
        self.host = host
        self.atk_result = []
        self.atk_success = False
        self.target_memory = [] #List of dict entries set by update_enemy_pos to hold last known loc of enemies
        self.command_queue = [] #List of queued commands for random hunting


    def ai_command(self, entity, entities, combat_phase, game_map, order) -> str:
        command = None
        if combat_phase == CombatPhase.explore:
            command = hunt_target(entity, entities, game_map)
        if combat_phase == CombatPhase.action:
            #Check AOC for targets in case one moved
            entity.fighter.targets = aoc_check(entities, entity)
            #If targets are available but no actions exist, run init_combat to fill action list
            if len(entity.fighter.targets) != 0 and len(self.host.action) == 0: 
                _, combat_phase, _, order, _ = init_combat(entity, order, command)
            elif len(self.host.action) != 0:
                determine_attack(entity)
                if len(self.host.combat_choices) == 0:
                    command = {'End Turn':'End Turn'}
                elif 'Engage' in self.host.action:
                    command = {'Engage':'Engage'}
                else: 
                    command = hunt_target(entity, entities, game_map)
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

    def update_enemy_pos(self, entity) -> None:
        if (entity.x, entity.y) in self.host.fov_visible:
            entry = {'target':entity, 'last_loc':(entity.x, entity.y), 'last_seen':global_vars.round_num}
            try:
                if entry in self.target_memory:
                    pass
                else:
                    for item in self.target_memory:
                        target = item.get('target')
                        if target == entity:
                            self.target_memory.remove(item)
                            self.target_memory.append(entry)
                    if entry not in self.target_memory:
                        self.target_memory.append(entry)
            except:
                self.target_memory.append(entry)



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

    best_score = -100
    best_atk = []
    
    #Locations to be scored higher because they kill the foe
    critical_locs = {0,1,2,6}

    for wpn in entity.weapons:
        for atk in wpn.attacks:
            if final_ap <= entity.fighter.ap:
                locs = curr_target.fighter.get_locations()
                #Determine valid locations
                valid_locs = determine_valid_locs(entity, curr_target, atk)
                #Prune list to only valid
                loc_strings = prune_list(curr_target.fighter.get_locations(), valid_locs, True, False)
                for l in loc_strings:
                    loc_id = locs.index(l)
                    location = curr_target.fighter.locations[loc_id]
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
                                if loc_id == loc: overall_score *= 1.2
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

def hunt_target(curr_actor, entities, game_map) -> list or str:
    astar = pathfind.AStar(game_map)
    enemies = []
    closest_coords = []
    closest_dist = None
    path = None
    command = {'End Turn':'End Turn'}

    for entity in entities:
        if entity is not curr_actor:
            if (entity.x, entity.y) in curr_actor.fighter.fov_visible:
                if global_vars.debug: print(entity.name + ' is visible')
                enemies.append(entity)
    if len(enemies) != 0:
        for enemy in enemies:
            dist = sum(((abs(enemy.x - curr_actor.x)),(abs(enemy.y - curr_actor.y))))
            if closest_dist is None or dist < closest_dist:
                closest_dist = dist
                closest_coords = [enemy.x, enemy.y]
    else:
        #See if there's a known loc for an enemy in history
        if len(curr_actor.fighter.ai.target_memory) > 0:
            for entry in curr_actor.fighter.ai.target_memory:
                x,y = entry.get('last_loc')
                dist = sum(((abs(x - curr_actor.x)),(abs(y - curr_actor.y))))
                if closest_dist is None or dist < closest_dist:
                    closest_dist = dist
                    closest_coords = [x, y]
                    closest_enemy = entry.get('target')
        else:
            command = random_hunt(curr_actor, entities, game_map)

    if closest_dist is not None:
        path = astar.get_path(curr_actor.x, curr_actor.y, closest_coords[0], closest_coords[1])
        if len(path) == 0: #What to do if you reached the last known loc?
            if (closest_enemy.x, closest_enemy.y) in curr_actor.fighter.fov_visible:
                path = astar.get_path(curr_actor.x, curr_actor.y, closest_enemy.x, closest_enemy.y)
            else:
                for entry in curr_actor.fighter.ai.target_memory:
                    if entry.get('target') == closest_enemy:
                        curr_actor.fighter.ai.target_memory.remove(entry)
                        command = random_hunt(curr_actor, entities, game_map)
    try:
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

            if len(path) == 1:
                if get_blocking_entities_at_location(entities, closest_coords[0], closest_coords[1]) is not None:
                    #Spin to closest enemy
                    if len(curr_actor.fighter.targets) == 0:
                        command = ['spin']
                        angle = entity_angle(closest_enemy, curr_actor)
                        if angle <= 180: command.append('ccw')
                        else: command.append('cw')
    except:
        pass
            

    return command

def random_hunt(curr_actor, entities, game_map) -> list or str:
    astar = pathfind.AStar(game_map)
    enemies = []
    closest_coords = []
    closest_dist = None
    path = None
    command = {'End Turn':'End Turn'}
    fov_area = fov_calc(int(round(curr_actor.fighter.sit/3)), curr_actor.x, curr_actor.y, 100, 0)
    fov_explored = True
    for (x,y) in fov_area:
        if not (x,y) in curr_actor.fighter.fov_explored: 
            fov_explored = False
            unexplored_pos = (x,y)
            break

    #First see if there is a command queue. If so, pop the first command and return it.
    if len(curr_actor.fighter.ai.command_queue) > 0:
        command = curr_actor.fighter.ai.command_queue.pop(0)
    #Has entire radius has been seen? If not, spin until it has. 
    elif not fov_explored:
        pos = Entity(unexplored_pos[0], unexplored_pos[1], 0x2588, 'dark gray', 'Focus', EntityState.inanimate)
        command = ['spin']
        angle = entity_angle(pos, curr_actor)
        if angle <= 180: command.append('ccw')
        else: command.append('cw')
    else: #Create a path to a radnom location, store the path in the command queue, and return the first comand from the queue
        closest_dist = None
        rand_x = randint(min((curr_actor.x-10),0), min((curr_actor.x+10),game_map.width))
        rand_y = randint(min((curr_actor.y-10),0), min((curr_actor.y+10),game_map.height))
        dist = sum(((abs(rand_x - curr_actor.x)),(abs(rand_y - curr_actor.y))))
        if closest_dist is None or dist < closest_dist:
            closest_dist = dist
            closest_coords = [rand_x, rand_y]
            path = astar.get_path(curr_actor.x, curr_actor.y, closest_coords[0], closest_coords[1])
            for i in reversed(path):
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
                curr_actor.fighter.ai.command_queue.append(command)
            curr_actor.fighter.ai.command_queue.remove(command)
        
    return command
