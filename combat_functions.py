import tcod as libtcodpy
import time
import global_vars
from math import sqrt
import options
from enums import CombatPhase, MenuTypes, EntityState, GameStates, FighterStance
from entity import get_blocking_entities_at_location
from fov_aoc import modify_fov, change_face, aoc_check
from game_messages import Message
from utilities import inch_conv, roll_dice, prune_list, entity_angle, save_roll_con, save_roll_un, find_defense_probability, itersubclasses
from game_map import cells_to_keys, get_adjacent_cells, command_to_offset
from components.injuries import Injury

def detect_enemies(entities) -> int:
    '''Goal is to see if enemies exist in each entity's FOV, and if so, change the combat phase. 
        Secondary goal is to populate/update visible fighters and closest enemy lists. '''
    combat_phase = CombatPhase.explore
    for entity in entities:
        #For each fighter, create a list of opponents. Then see if any of them are in FOV. If so, start combat by changing phase
        if entity.fighter is not None:
            opponents = entities.copy()
            opponents.remove(entity)
            for opponent in opponents:
                if opponent.fighter is None:
                    opponents.remove(opponent)
                elif (opponent.x, opponent.y) in entity.fighter.fov_visible:
                    combat_phase = CombatPhase.init
                    entity.fighter.visible_fighters.append(opponent)
                elif len(entity.fighter.visible_fighters) > 0:
                    if opponent in entity.fighter.visible_fighters:
                        entity.fighter.visible_fighters.remove(opponent)
    
            find_closest_enemy(entity)

    return combat_phase

def find_closest_enemy(entity):
    closest_dist = None
    if len(entity.fighter.visible_fighters) > 0:
        for enemy in entity.fighter.visible_fighters:
            x,y = enemy.x, enemy.y
            dist = sum(((abs(x - entity.x)),(abs(y - entity.y))))
            if closest_dist is None or dist < closest_dist:
                closest_dist = dist
                entity.fighter.closest_fighter = enemy

def move_actor(game_map, entity, entities, command, logs) -> bool:

    fov_recompute = False
    #Dict containing facing direction based on x,y offset
    facing_dict = {(-1,0):6,(-1,1):5,(-1,-1):7,(1,-1):1,(1,1):3,(1,0):2,(0,1):4,(0,-1):0}
    #Dict containing facing direction based on angle
    angle_dict = {0:2,45:1,90:0,135:7,180:6,225:5,270:4,315:3}
    
    #Name message logs
    message_log = logs[2]

    #Set ap cost based on stance
    if entity.fighter.gen_stance == FighterStance.standing:
        ap_cost = entity.fighter.walk_ap
    elif entity.fighter.gen_stance == FighterStance.kneeling:
        ap_cost = entity.fighter.walk_ap*2
    else:
        ap_cost = entity.fighter.walk_ap*4
    
    if not entity.fighter.can_act:
        message = Message('You can\'t move while unconscious!', 'black')

    if command[0] == 'move' and entity.fighter.can_act and entity.fighter.can_walk:
        #Mark last known pos of entity for AI
        for e in entities:
            if e is not entity and hasattr(e.fighter, 'ai'):
                e.fighter.ai.update_enemy_pos(entity)

        x_mod, y_mod = command_to_offset(command)

        fx, fy =entity.x + x_mod, entity.y + y_mod
        #Boundary and blocker checking
        blocker = get_blocking_entities_at_location(entities, fx, fy)
        if (game_map.width -1 >= fx and game_map.height -1 >= fy):
            if (game_map.walkable[fx, fy] and not (fx < 0  or fy < 0) 
                and blocker is None):
                entity.mod_attribute('x', x_mod)
                entity.mod_attribute('y', y_mod)
                if global_vars.debug: print(entity.name + ' ' + str(entity.x) + ' ' + str(entity.y))
                fov_recompute = True
                if entity.fighter.strafe == 'auto': entity.fighter.facing = facing_dict.get((x_mod,y_mod))
                elif entity.fighter.strafe == 'enemy' and entity.fighter.closest_fighter is not None: 
                    e_angle = entity_angle(entity.fighter.closest_fighter, entity, False)
                    e_angle = (e_angle // 45) * 45
                    entity.fighter.facing = angle_dict.get(e_angle)
                if not hasattr(entity.fighter, 'ai'): 
                    message = Message('You move ' + command[1], 'black')
                    message_log.add_message(message)
            if blocker and not hasattr(entity.fighter, 'ai'):
                message = Message('You can\'t walk over '+blocker.name+'!', 'black')
                message_log.add_message(message)

        
    if command[0] == 'spin': 
        direction = command[1]
        if direction == 'ccw': entity.fighter.facing -= 1
        else: entity.fighter.facing += 1
        fov_recompute = True
        #Setting boundaries
        if entity.fighter.facing == 8: entity.fighter.facing = 0
        elif entity.fighter.facing == -1: entity.fighter.facing = 7
        #Change facing
        
    if command[0] == 'spin' or 'move':
        entity.fighter.update_aoc_facing()
        entity.fighter.aoc = change_face(entity.fighter.aoc_facing, entity.x, entity.y, entity.fighter.reach)

    if command[0] == 'prone':
        message = Message('You drop prone', 'black')
        entity.fighter.gen_stance = FighterStance.prone
        fov_recompute = True
    
    if command[0] == 'kneel':
        message = Message('You kneel', 'black')
        entity.fighter.gen_stance = FighterStance.kneeling
        fov_recompute = True

    if command[0] == 'stand' and entity.fighter.can_stand:
        message = Message('You stand up', 'black')
        entity.fighter.gen_stance = FighterStance.standing
        fov_recompute = True

    if fov_recompute == True:
        entity.fighter.mod_attribute('ap', -ap_cost)

    if hasattr(entity, 'fighter') and fov_recompute == True:
        if global_vars.debug_time: t0 = time.time()
        for e in entities:
            if e.fighter is not None:
                fov_radius = int(round(e.fighter.sit/5))
                game_map.compute_fov(e.x, e.y, fov_radius, True, libtcodpy.FOV_SHADOW)
                modify_fov(e, game_map)
        #Added to handle prone stance changes        
        handle_mobility_change(entity)

        if global_vars.debug_time: t1 = time.time()
        if global_vars.debug_time: total_time = t1 - t0
        if global_vars.debug_time: print('FOV recompute time: ' + str(total_time))



    targets = aoc_check(entities, entity)

    if targets is not None:
        update_targets(entity, targets)
        for target in targets:
            e_targets = aoc_check(entities, target)
            update_targets(target, e_targets)

    return fov_recompute #Used to id that entity moved for ap reduction in combat

def relo_actor(game_map, target, aggressor, entities, direction, distance) -> bool:
    '''Used to relocate an actor, suich as when they are pushed or thrown by something else'''
    #Dict containing x,y offset based on facing direction  
    offset_dict = {6:(-1,0),5:(-1,1),7:(-1,-1),1:(1,-1),3:(1,1),2:(1,0),4:(0,1),0:(0,-1)}
    #Dict containing facing direction based on angle
    angle_dict = {0:2,45:1,90:0,135:7,180:6,225:5,270:4,315:3}
    mobility_changed = False #Used to signal not to run handle mobility change in calling function

    for x_mod,y_mod in offset_dict.get(direction):
        x = x_mod * distance
        y = y_mod * distance

    fx, fy = target.x + x, target.y + y
    #Boundary and blocker checking
    blocker = get_blocking_entities_at_location(entities, fx, fy)
    if (game_map.width -1 >= fx and game_map.height -1 >= fy) and (game_map.walkable[fx, fy] and not (fx < 0  or fy < 0) and blocker is None):
            target.mod_attribute('x', x_mod)
            target.mod_attribute('y', y_mod)
    else:
        #Find first free square within 1 square of original target
        for x in range(fx-1,fx+1):
            for y in range(fy-1,fy+1):
                blocker = get_blocking_entities_at_location(entities, x, y)
                if (game_map.width -1 >= x and game_map.height -1 >= y) and (game_map.walkable[x, y] and not (x < 0  or y < 0) and blocker is None):
                    target.mod_attribute('x', x)
                    target.mod_attribute('y', y)


    #Mark last known pos of entity for AI
    for e in entities:
        if e is not target and hasattr(e.fighter, 'ai'):
            e.fighter.ai.update_enemy_pos(target)

    
    if hasattr(target, 'fighter'):
        if global_vars.debug_time: t0 = time.time()
        for e in entities:
            if e.fighter is not None:
                fov_radius = int(round(e.fighter.sit/5))
                game_map.compute_fov(e.x, e.y, fov_radius, True, libtcodpy.FOV_SHADOW)
                modify_fov(e, game_map)

        #Added to handle prone stance changes        
        handle_mobility_change(target)
        mobility_changed = True

    targets = aoc_check(entities, target)

    if targets is not None:
        update_targets(target, targets)
        for t in targets:
            e_targets = aoc_check(entities, t)
            update_targets(t, e_targets)

    #Update aggressor facing to face target
    if aggressor is not None:
        angle = entity_angle(target, aggressor, False)
        aggressor.fighter.facing = angle_dict.get(angle)
        aggressor.fighter.update_aoc_facing()
        aggressor.fighter.aoc = change_face(aggressor.fighter.aoc_facing, aggressor.x, aggressor.y, aggressor.fighter.reach)
    
    return mobility_changed

def strafe_control(entity):
    #Cycle through the strafe modes
    if entity.fighter.strafe == 'auto': 
        entity.fighter.strafe = 'enemy'
        message = Message('Strafe mode changed to Follow Enemy')
    elif entity.fighter.strafe == 'enemy': 
        entity.fighter.strafe = 'manual'
        message = Message('Strafe mode changed to Manual')
    else: 
        entity.fighter.strafe = 'auto'
        message = Message('Strafe mode changed to Auto')
    return message

def turn_order(entities) -> list:
    #Sort entities by highest init and make list of sorted entities
    order = sorted(entities, key=lambda entities: (entities.fighter.init + roll_dice(1,100)), reverse = True)

    return(order)

def update_targets(entity, targets) -> None:
    """Purpose is to remove or change target list when aoc changes"""
    #See if any targets are not in the list and add them. Also update sister diff dicts
    for target in targets:
        hit_diff_dict = dict()
        dodge_diff_dict = dict()
        parry_diff_dict = dict()
        if target not in entity.fighter.targets:
            entity.fighter.targets.append(target)
            #Add hit/dodge/parry loc_diffs
            loc_list = target.fighter.get_locations()
            #Fill dicts with locations and set value to 0's
            for loc in loc_list:
                hit_diff_dict[loc] = 0
                dodge_diff_dict[loc] = 0
                parry_diff_dict[loc] = 0

            entity.fighter.loc_hit_diff.append(hit_diff_dict)
            entity.fighter.loc_dodge_diff.append(dodge_diff_dict)
            entity.fighter.loc_parry_diff.append(parry_diff_dict)
    
    #See if any targets need to be removed and do so
    if set(entity.fighter.targets) != set(targets):
        for t in entity.fighter.targets:
            if not t in targets:
                i = entity.fighter.targets.index(t)
                entity.fighter.targets.remove(t)
                entity.fighter.loc_hit_diff.pop(i)
                entity.fighter.loc_dodge_diff.pop(i)
                entity.fighter.loc_parry_diff.pop(i)

        if entity.fighter.curr_target not in set(entity.fighter.targets):
            entity.fighter.curr_target = None

    #Set current target if not set; hack, remove when target selection implemented
    if entity.fighter.curr_target == None and len(entity.fighter.targets) > 0: 
        entity.fighter.curr_target = entity.fighter.targets[0] 

def get_percieved_mods(attacker, defender, location) -> dict:
    idx = attacker.fighter.targets.index(defender)
    p_hit = attacker.fighter.loc_hit_diff[idx].get(location)
    p_dodge = attacker.fighter.loc_dodge_diff[idx].get(location)
    p_parry = attacker.fighter.loc_parry_diff[idx].get(location)

    p_mods = {'p_hit':p_hit, 'p_dodge':p_dodge, 'p_parry': p_parry}

    return p_mods

def determine_valid_locs(attacker, defender, attack) -> list:
    #Factors and counters:
    #Effective Reach: Distance and Height
    #Specific Limb
    #Relative positions
    
    er = attacker.fighter.er * 1.3 #1.3 multiplier to account for the stretch from twisting
    er += attack.length

    #Init location pool
    locations = []
    i = 0
    for location in defender.fighter.locations:
        #Skip if no psi left
        if not any(location):
            i += 1
            continue
        locations.append(i)
        i += 1
        
    #Determine relative positioning
    #Start by determining defender facing relative to attacker
    defender_angle = entity_angle(attacker, defender)

    #Now determine attacker angle to defender    
    attacker_angle = entity_angle(defender, attacker)

    #Lists for holding locations to prune
    loc_list = []
    loc_list2 = []

    #Remove locations based on defender angle
    if 45 < defender_angle < 135:
        #Locations to remove
        loc_list = [3,5,7,9,11,13,15,17,19,21,23,25,27]
    elif 225 < defender_angle < 315:
        #Locations to remove
        loc_list = [4,6,8,10,12,14,16,18,20,22,24,26,28]

    #Remove locations based on attack hand/foot(if applicable)
    if attack.side_restrict:
        if "(R)" in attack.name:
            #Locations to remove
            loc_list2 = [3,5,7,9,11,13,15,17,19,21,23,25,27]
        elif "(L)" in attack.name:
            #Locations to remove
            loc_list2 = [4,6,8,10,12,14,16,18,20,22,24,26,28] 
    #Combine lists if necessary
    loc_list += list(set(loc_list2)-set(loc_list))

    #Remove locations based on specific attack restrictions
    for l in attack.restricted_locs:
        if not l in loc_list:
            loc_list.append(l)

    #modify er based on attacker angle
    if 45 < attacker_angle < 90:
        er -= attacker.fighter.er/2
    elif 270 < attacker_angle < 315:
        er += attacker.fighter.er/2
    #Remove all locations if defender flanks attacker
    elif 90 < attacker_angle < 270:
        locations = []
        return locations

    #Find distance between attacker and defender. 
    distance = sqrt((defender.x - attacker.x)**2 + (defender.y - attacker.y)**2)
    #Convert squares into inches and round it off. 36" subtracted due to each combatant being in the middle of a square
    distance = int(round(distance*36))-36
    
    #Remove locations that are unreachable due to angle
    for location in locations:
        can_reach = location_angle(attacker, defender, er, distance, attack, location)
        if not can_reach:
            if not location in loc_list:
                loc_list.append(location)
    locations = prune_list(locations, loc_list)


    return locations

def location_angle(attacker, defender, er, distance, attack, location) -> bool:
    can_reach = False
    #Determine defender height based on stance
    if defender.fighter.gen_stance == FighterStance.prone:
        location_ht = defender.fighter.location_ht[25]
    elif defender.fighter.gen_stance == FighterStance.kneeling or FighterStance.sitting:
        location_ht = defender.fighter.location_ht[location] - defender.fighter.location_ht[23]
    else:
        location_ht = defender.fighter.location_ht[location]

    #Determine pivot point based on attacker stance
    if attacker.fighter.gen_stance == FighterStance.prone:
        pivot = attacker.fighter.location_ht[25]
        if not attack.hand: er *= 1.2 #Legs average 1.2x longer than arms
    else:
        if attack.hand:
            pivot = attacker.fighter.location_ht[3]
        else:
            pivot = attacker.fighter.location_ht[17]
            er *= 1.2 #Legs average 1.2x longer than arms
        if attacker.fighter.gen_stance == FighterStance.kneeling or FighterStance.sitting:
            pivot -= attacker.fighter.location_ht[23]

    #Find length of hypotenuse(len of reach to hit location)
    reach_req = sqrt(distance**2 + abs(location_ht-pivot)**2)
    if reach_req <= er: can_reach = True
    
    return can_reach

def determine_valid_angles(location, attack) -> list:
    result = []
    # Full Spectrum, clockwise: 'N -> S', 'NE -> SW', 'E -> W', 'SE -> NW', 'S -> N', 'SW -> NE', 'W -> E', 
    # 'NW -> SE', 'Straight (jab)'
    if location == 0:
        result = ['N -> S', 'NE -> SW', 'E -> W', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location == 1:
        result = ['N -> S', 'NE -> SW', 'E -> W', 'SE -> NW', 'S -> N', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location == 2:
        result = ['NE -> SW', 'E -> W', 'SE -> NW', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location < 7:
        result = ['N -> S', 'NE -> SW', 'E -> W', 'SE -> NW', 'S -> N', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location < 9:
        result = ['NE -> SW', 'E -> W', 'SE -> NW', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location < 11:
        result = ['NE -> SW', 'E -> W', 'SE -> NW', 'S -> N', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location < 13:
        result = ['NE -> SW', 'E -> W', 'SE -> NW', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location < 15:
        result = ['NE -> SW', 'E -> W', 'SE -> NW', 'S -> N', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location < 17:
        result = ['NE -> SW', 'E -> W', 'SE -> NW', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location == 17:
        result = ['S -> N', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location == 18:
        result = ['NE -> SW', 'E -> W', 'SE -> NW', 'S -> N', 'Straight (jab)']
    elif location < 23:
        result = ['N -> S', 'NE -> SW', 'E -> W', 'SE -> NW', 'S -> N', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location < 25:
        result = ['N -> S', 'NE -> SW', 'E -> W', 'SE -> NW', 'S -> N', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location < 27:
        result = ['NE -> SW', 'E -> W', 'W -> E', 'NW -> SE', 'Straight (jab)']
    elif location < 29:
        result = ['N -> S']

    allowed_angles = []

    if "(L)" in attack.name:
        atk_allowed_angles = attack.allowed_angles_l
    else:
        atk_allowed_angles = attack.allowed_angles_r

    for a in atk_allowed_angles:
        angle = angle_id(a)
        allowed_angles.append(angle)

    final = []

    for r in result:
        if r in allowed_angles:
            final.append(r)

    return final

def angle_id(angle) -> list or int:
    angle_list = ['N -> S', 'NE -> SW', 'E -> W', 'SE -> NW', 'S -> N', 'SW -> NE', 'W -> E', 'NW -> SE', 'Straight (jab)']
    try:
        int(angle)
        return angle_list[angle]
    except:
        return angle_list.index(angle)

def calc_history_modifier(entity, attack, loc, angle) -> int:
    history = entity.fighter.attacker_history
    curr_attack = (attack, loc, angle)
    mod = 0
    repeats = 0
    element_repeat = 0
    for i in history:
        #Add up completely duplicated attacks
        if i == curr_attack:
            repeats = history.count(curr_attack)
        #Add up how many times the elements repeat
        else:
            for n in curr_attack:
                for x in i:
                    if n == x:
                        element_repeat += 1
    mod += ((repeats-1) * 15) + ((element_repeat) * 3)
    return mod

def calc_final_mods(attacker, defender) -> dict:
    '''Goal is to bring together all the various hidden and percieved mods for both sides and create a single dict with all of them taken into account'''
    weapon = attacker.fighter.combat_choices[0]
    attack = attacker.fighter.combat_choices[1]
    location = attacker.fighter.combat_choices[2]
    angle = attacker.fighter.combat_choices[3]
    loc_name = attacker.fighter.targets[0].fighter.name_location(location)
    
    def_mods = defender.fighter.get_defense_modifiers(loc_name)
    cs = attacker.determine_combat_stats(weapon, attack, location, angle)
    p_mods = get_percieved_mods(attacker, defender, loc_name)
    final_to_hit = cs.get('to hit') + def_mods.get('hit')
    p_hit = p_mods.get('p_hit') + final_to_hit
    dodge_mod = cs.get('dodge mod') + def_mods.get('dodge')
    p_dodge_mod = p_mods.get('p_dodge') + cs.get('dodge mod')
    parry_mod = cs.get('parry mod') + def_mods.get('parry')
    p_parry_mod = p_mods.get('p_parry') + cs.get('parry mod')
    

    total_ep = sum([cs.get('b psi'), cs.get('s psi'), cs.get('p psi'), cs.get('t psi')])

    if len(defender.fighter.attacker_history) > 0:
        history_mod = calc_history_modifier(defender, attack.name, location, angle)
        dodge_mod += history_mod
        parry_mod += history_mod
        p_dodge_mod += history_mod
        p_parry_mod += history_mod
    

    #Adjust cs based on mods. 
    cs['dodge mod'] = dodge_mod
    cs['parry mod'] = parry_mod

    final_mods = cs
    final_mods['p_dodge'] = p_dodge_mod
    final_mods['p_parry'] = p_parry_mod
    final_mods['p_hit'] = p_hit
    final_mods['auto-block'] = def_mods.get('auto-block')
    final_mods['total ep'] = total_ep

    return final_mods

def perform_attack(entity, entities, final_to_hit, curr_target, cs, combat_phase) -> (list, int):
    effects = []
    messages = []
    attack = entity.fighter.combat_choices[1]  
    final_ap = cs.get('final ap')
    active_entity = entity
    curr_actor = entity
    enemy = curr_target
    missed =  False
    location = entity.fighter.combat_choices[2]
    dam_type = curr_actor.fighter.combat_choices[1].damage_type[0]
    

    #Clear history if attacker changed
    if curr_target.fighter.attacker is not entity:
        curr_target.fighter.attacker = entity
        curr_target.fighter.attacker_history.clear
        add_history(curr_target)
    else:
        add_history(curr_target)
    
    atk_result = make_attack_roll(final_to_hit, 1, location)
    entity.fighter.atk_result, entity.fighter.dam_result, entity.fighter.new_loc_result = atk_result[0], atk_result[1], atk_result[2]
    dam_mult = curr_actor.fighter.dam_result
    
    
    #Subtract attack AP and stamina
    #Subtract AP from enemy if this is a disengagement attack or an attack due to a wait

    if curr_target in entity.fighter.entities_opportunity_attacked:
        curr_target.fighter.mod_attribute('ap', -final_ap)
    elif curr_target.fighter.wait or curr_target.fighter.feint:
        curr_target.fighter.mod_attribute('ap', -final_ap)
    else:
        entity.fighter.mod_attribute('ap', -final_ap)

    entity.fighter.mod_attribute('stamina', -(attack.stamina*entity.fighter.base_stam_cost))
    

    #No damage
    if atk_result[1] == 0:
        missed = True
        if not hasattr(entity.fighter, 'ai'):
            messages.append('You missed. ')
            #Show rolls
            if options.show_rolls: 
                rolls = 'You rolled a ' + str(entity.fighter.atk_result) + ', missing. '
                messages.insert(0, rolls)
        else:
            messages.append(entity.name + ' missed you. ')
        
        if enemy.fighter.disengage:       
            combat_phase = CombatPhase.disengage
            active_entity = enemy
            game_state = GameStates.default
            menu_dict = dict()
        else:
            if curr_actor.player:
                #See if curr_actor has AP for repeat
                if curr_actor.fighter.ap >= curr_actor.fighter.last_atk_ap:           
                    combat_phase = CombatPhase.repeat
                    game_state = GameStates.menu
        
    else:
        #First, see if this is an attack from behind
        if entity in curr_target.fighter.targets:
            combat_phase = CombatPhase.defend
        else:
            effects = damage_controller(curr_target, curr_actor, location, dam_type, dam_mult, entity.fighter.atk_result, cs, entities)
    
            if effects:
                combat_phase = CombatPhase.action
                curr_actor.fighter.action.clear()
                for effect in effects:
                    messages.append(effect)
                if enemy.fighter is not None:
                    if enemy.fighter.disengage:       
                        combat_phase = CombatPhase.disengage
                        active_entity = enemy
                        game_state = GameStates.default
                        menu_dict = dict()
                else:
                    if curr_actor.player and len(curr_actor.fighter.targets) > 0:
                        #See if curr_actor has AP for repeat
                        if curr_actor.fighter.ap >= curr_actor.fighter.last_atk_ap:           
                            combat_phase = CombatPhase.repeat
                            game_state = GameStates.menu

            if hasattr(curr_actor.fighter, 'ai'):
                menu_dict = dict()
                game_state = GameStates.default

    

    entity.fighter.mods = cs

    if combat_phase == CombatPhase.defend:
        active_entity = curr_target

    return messages, combat_phase, active_entity, missed

def apply_stability_damage(target, damage, location) -> bool:
    roll = False
    if location < 3:
        target.fighter.stability -= damage[2]/100
        roll = True
    elif 2 < location < 11:
        target.fighter.stability -= damage[2]/25
        roll = True
    elif 12 < location < 15:
        target.fighter.stability -= damage[2]/50
        roll = True
    return roll

def add_history(entity) -> None:
    history = entity.fighter.attacker_history
    attacker = entity.fighter.attacker
    atk_tuple = (attacker.fighter.combat_choices[1].name, attacker.fighter.combat_choices[2], attacker.fighter.combat_choices[3])
    history.append(atk_tuple)
    if len(history) > entity.fighter.mem/10:
        del history[0]

def make_attack_roll(hit_chance, damage, location) -> (int, int, int):
    roll = int(roll_dice(1, 100, True))
    new_loc = 0
    #MISS
    if roll > hit_chance:
        damage = 0
    #Hit another loc softly
    elif roll > hit_chance - 10:
        if location <= 2:
            new_loc = location + roll_dice(1,2)
        elif location >= 26:
            new_loc = location - roll_dice(1,2)
        else:
            new_loc = location + (roll_dice(1,3) - roll_dice(1,3))
        damage *= (((hit_chance - roll)/(hit_chance/100))/100)*.4
  
    #Hit another loc glancing
    elif  roll > hit_chance - 20:
        if location <= 3:
            new_loc = location + roll_dice(1,3)
        elif location >= 25:
            new_loc = location - roll_dice(1,3)
        else:
            new_loc = location + (roll_dice(1,4) - roll_dice(1,4))
        damage *= (((hit_chance - roll)/(hit_chance/100))/100)*.1

    else:
        damage *= (((hit_chance - roll)/(hit_chance/100))/100)

    damage = round(damage, 2)
        
    return roll, damage, location

def handle_persistant_effects(entity, entities):
    messages = []
    if entity.fighter:
        #Handle bleeding
        if len(entity.fighter.bleed) != 0:
            messages.append(entity.name + ' has ' + str(round(entity.fighter.vitae)) + 'ml of blood. ')
            former_blood = entity.fighter.vitae
            for cut in entity.fighter.bleed:
                entity.fighter.vitae -= cut[0]
                cut[1] -= 1
                if cut[1] <= 0: entity.fighter.bleed.remove(cut) 
            messages.append(('His ' if entity.fighter.male else 'Her ') + 'cuts bleed for ' + str(round(former_blood - entity.fighter.vitae)) + 
                'ml of loss. ')
        #Handle blood regen
        if entity.fighter.max_vitae > entity.fighter.vitae:
            entity.fighter.vitae += entity.fighter.vitr/12
            #Handle bleeding to death
            if entity.fighter.max_vitae*.25 >= entity.fighter.vitae:
                messages.append(entity.name + ' has passed out from blood loss and will soon be dead. ')
        #Handle suffocation
        if entity.fighter.suffocation:
            if entity.fighter.suffocation == 0:
                messages.append(entity.name + ' has suffocated an died. ')
            else: 
                entity.fighter.suffocation -= 1
                messages.append(entity.name + ' is slowly choking to death from a neck wound. ')
        #Handle AP regen
        entity.fighter.ap = entity.fighter.max_ap
        #Handle stamina regen/drain
        if entity.fighter.stamina < entity.fighter.max_stamina:
            entity.fighter.stamina += entity.fighter.stamr - entity.fighter.stam_drain
        #Handle unconsiousness due to fatigue
        if entity.fighter.stamina <= 0:
            entity.fighter.stamina = 0
            entity.fighter.gen_stance = FighterStance.prone
            if hasattr(entity.fighter, 'ai'): messages.append(entity.name + ' has passed out due to fatigue. ')
            else: messages.append('You have passed out due to fatigue. ')
        #Handle unconsousness
        if entity.state == EntityState.unconscious:
            handle_state_change(entity, entities, EntityState.unconscious)
            if hasattr(entity.fighter, 'ai'): messages.append(entity.name + ' has passed out. ')
            else: messages.append('You have passed out. ')
        #Restore stability
        entity.fighter.stability = entity.fighter.stability_mods
        #Apply stance
        entity.fighter.change_stance(entity.fighter.stance)
        #Reset turn end, acted, wait, opp attack
        entity.fighter.entities_opportunity_attacked.clear()
        entity.fighter.end_turn = False
        entity.fighter.acted = False
        entity.fighter.wait = False
        entity.fighter.feint = False
        #Handle death
        if entity.state == EntityState.dead:
            handle_state_change(entity, entities, EntityState.dead)
        if not hasattr(entity.fighter, 'ai'): messages.append('A new round has begun. ')

    return messages

def handle_mobility_change(entity):
    #DIct containing direction to x,y AOC mapping for square directly in front of entity
    prone_aoc_dict = {0:(0,-1),1:(1,-1),2:(1,0),3:(1,1),4:(0,1),5:(-1,1),6:(-1,0),7:(-1,-1)}
    #Handle unconsciousness
    if entity.state in [EntityState.unconscious,EntityState.dead,EntityState.stunned,EntityState.shock]:
        entity.fighter.can_act = False
    #Handle leg paralysis
    no_walk_locs = (17,18,21,22,23,24,25,26,27,28)
    for loc in no_walk_locs:
        if loc in entity.fighter.paralyzed_locs:
            entity.fighter.can_walk = False
            entity.fighter.paralysis_instability = -50
            break
    if not entity.fighter.can_walk:
        locs_found = []
        for loc in no_walk_locs:
            if loc in entity.fighter.paralyzed_locs:
                locs_found.append(loc)
        #Since even locations are on the left and odd on the right, checking to see if both sides are damaged is done by seeing if all locs are even or odd
        odd = 0
        even = 0
        for i in locs_found:
            if i%2==0: even += 1
            else: odd += 1
        if odd != 0:
            if even != 0: 
                entity.fighter.can_stand = False
                entity.fighter.gen_stance = FighterStance.prone
    if entity.fighter.gen_stance == FighterStance.prone:
        x_mod, y_mod = prone_aoc_dict.get(entity.fighter.facing)
        new_x = entity.x + x_mod
        new_y = entity.y + y_mod
        entity.fighter.aoc = [(new_x, new_y)]
       
def filter_injuries(master_class, location, damage_type, severity, layer, recipient) -> set:
    injuries = set(itersubclasses(master_class))
    loc_matches = set()
    dt_matches = set()
    sev_matches = set()
    layer_matches = set()
    avail_prereqs = []

    for injury in injuries:
        a = injury(location, recipient, damage_type)
        dupes = 0
        #Block below to find duplicates and remove injury if not allowed
        for i in recipient.fighter.injuries:
            if type(i) is type(a):
                if not injury in avail_prereqs:
                    avail_prereqs.append(injury)
                if i.location == location:
                    if not a.duplicable:
                        continue 
                    else:
                        dupes += 1
        if dupes >= a.max_dupes:
            continue 
        if a.prerequisite is not None and a.prerequisite not in avail_prereqs:
            continue
        if location in a.locations:
            loc_matches.add(injury)
        if damage_type in a.damage_type:
            dt_matches.add(injury)
        if severity >= a.severity:
            sev_matches.add(injury)
        if layer == a.layer:
            layer_matches.add(injury) 

    valid = loc_matches.intersection(dt_matches,sev_matches,layer_matches)
    return valid

def apply_injuries(valid_injuries, location, recipient, damage_type) -> (list, int):
    roll = 1
    if len(valid_injuries) > 1:
        roll = roll_dice(1,len(valid_injuries))
    injuries = list(valid_injuries)
    injury = injuries[roll-1](location, recipient, damage_type)
    sev = 0 #Used to signal that this injury is a maximum severity injury
    
    messages = set()
    
    #Remove prereq if one exists
    if injury.prerequisite is not None:
        idx = None
        for i in recipient.fighter.injuries:
            if type(i) is injury.prerequisite:
                idx = recipient.fighter.injuries.index(i)
        #Remove prereq injury
        apply_injury_effects(recipient, recipient.fighter.injuries.pop(idx), location, True) 

    #apply new injury
    messages = set(apply_injury_effects(recipient, injury, location))
    sev = injury.severity
    recipient.fighter.injuries.append(injury)

    return messages, sev

def find_next_location(location, atk_angle, entity_angle) -> int:
    '''Finds the next location along the path in a pass-through attack'''
    if 0 <= entity_angle < 45 or 315 < entity_angle: #Directly in front
        #Key is loc, List is list of next locs based on atk_angle in atk_angle order (clockwise; N->S, NE->SW, etc.)
        loc_dict = {0:[1,1,None,None,None,None,None,1,None],1:[2,3,None,0,0,0,None,4,None],2:[6,5,None,1,1,1,None,6,None],
                    3:[5,7,None,None,None,2,4,6,None],4:[6,5,3,2,None,None,None,8,None], 5:[9,11,9,3,3,2,6,10,None],6:[10,9,5,2,4,4,8,12,None],
                    7:[11,None,None,None,3,3,5,9,None],8:[12,10,6,4,4,None,None,None,None],9:[13,15,11,7,5,6,10,14,None],10:[14,13,9,5,6,8,12,16,None],
                    11:[15,None,None,None,7,5,10,13,None],12:[16,14,10,6,8,None,None,None,None],13:[17,19,15,11,9,10,14,18,None],
                    14:[18,17,13,9,10,12,16,20,None],15:[19,None,None,None,11,9,13,17,None],16:[20,18,14,10,12,None,None,None,None],
                    17:[21,None,19,15,13,14,18,22,None],18:[22,21,17,13,14,20,None,None,None],19:[None,None,None,None,15,13,17,21,None],
                    20:[None,22,18,14,16,None,None,None,None],21:[23,None,None,19,17,18,22,24,None],22:[24,23,21,17,18,20,None,None,None],
                    23:[25,None,None,None,21,22,24,26,None],24:[26,25,23,21,22,None,None,None,None],25:[27,None,None,None,23,24,26,28,None],
                    26:[28,27,25,23,24,None,None,None,None],27:[None,None,None,None,25,26,28,None,None],28:[None,None,27,25,26,None,None,None,None]}
        
    elif 135 < entity_angle < 225: #Directly behind
        loc_dict = {0:[1,1,None,None,None,None,None,1,None],1:[2,4,None,0,0,0,None,3,None],2:[5,6,None,1,1,1,None,5,None],
                    3:[5,6,4,2,None,None,None,7,None],4:[6,8,None,None,None,2,3,5,None], 5:[9,10,6,2,3,3,7,11,None],6:[10,12,8,4,4,2,5,9,None],
                    7:[11,9,5,3,3,None,None,None,None],8:[12,None,None,None,4,4,6,10,None],9:[13,14,10,6,5,7,11,15,None],10:[14,16,12,8,6,5,9,13,None],
                    11:[15,13,10,5,7,None,None,None,None],12:[16,None,None,None,8,6,10,14,None],13:[17,18,14,10,9,11,15,19,None],
                    14:[18,20,16,12,10,9,13,17,None],15:[19,17,13,9,11,None,None,None,None],16:[20,None,None,None,12,10,14,18,None],
                    17:[21,22,18,14,13,15,19,None,None],18:[22,None,20,16,14,13,17,21,None],19:[None,21,17,13,15,None,None,None,None],
                    20:[None,None,None,None,16,14,18,22,None],21:[23,24,22,18,17,19,None,None,None],22:[24,None,None,20,18,17,21,23,None],
                    23:[25,26,24,22,21,None,None,None,None],24:[26,None,None,None,22,21,23,25,None],25:[27,28,26,24,23,None,None,None,None],
                    26:[28,None,None,None,24,27,25,23,None],27:[None,None,28,26,25,None,None,None,None],28:[None,None,None,None,26,27,25,None,None]}
    elif 45 <= entity_angle <= 135: #Left side
        loc_dict = {0:[1,None,None,None,None,None,None,None,None],1:[2,None,None,None,0,None,None,None,None],2:[4,None,None,None,1,None,None,None,None],
                    3:[5,None,None,None,2,None,None,None,None],4:[6,None,None,None,None,None,None,None,3], 5:[9,None,None,None,3,None,None,None,7],6:[10,None,None,None,4,None,None,None,5],
                    7:[11,None,None,None,3,None,None,None,None],8:[12,None,None,None,4,None,None,None,6],9:[13,None,None,None,5,None,None,None,11],10:[14,None,None,None,6,None,None,None,9],
                    11:[15,None,None,None,7,None,None,None,None],12:[16,None,None,None,8,None,None,None,11],13:[17,None,None,None,9,None,None,None,15],
                    14:[18,None,None,None,10,None,None,None,13],15:[19,None,None,None,11,None,None,None,None],16:[20,None,None,None,12,None,None,None,14],
                    17:[21,None,None,None,13,None,None,None,19],18:[22,None,None,None,14,None,None,None,17],19:[None,None,None,None,15,None,None,None,None],
                    20:[None,None,None,None,16,None,None,None,18],21:[23,None,None,None,17,None,None,None,None],22:[24,None,None,None,18,None,None,None,21],
                    23:[25,None,None,None,21,None,None,None,None],24:[26,None,None,None,22,None,None,None,23],25:[27,None,None,None,23,None,None,None,None],
                    26:[28,None,None,None,24,None,None,None,25],27:[None,None,None,None,25,None,None,None,None],28:[None,None,None,None,26,None,None,None,27]}
    else: #Right side
        loc_dict = {0:[1,None,None,None,None,None,None,None,None],1:[2,None,None,None,0,None,None,None,None],2:[3,None,None,None,1,None,None,None,None],
                    3:[5,None,None,None,2,None,None,None,4],4:[6,None,None,None,None,None,None,None,None], 5:[9,None,None,None,3,None,None,None,6],6:[10,None,None,None,4,None,None,None,8],
                    7:[11,None,None,None,3,None,None,None,5],8:[12,None,None,None,4,None,None,None,None],9:[13,None,None,None,5,None,None,None,10],10:[14,None,None,None,6,None,None,None,12],
                    11:[15,None,None,None,7,None,None,None,9],12:[16,None,None,None,8,None,None,None,None],13:[17,None,None,None,9,None,None,None,14],
                    14:[18,None,None,None,10,None,None,None,16],15:[19,None,None,None,11,None,None,None,13],16:[20,None,None,None,12,None,None,None,None],
                    17:[21,None,None,None,13,None,None,None,18],18:[22,None,None,None,14,None,None,None,20],19:[None,None,None,None,15,None,None,None,17],
                    20:[None,None,None,None,16,None,None,None,None],21:[23,None,None,None,17,None,None,None,22],22:[24,None,None,None,18,None,None,None,None],
                    23:[25,None,None,None,21,None,None,None,24],24:[26,None,None,None,22,None,None,None,None],25:[27,None,None,None,23,None,None,None,26],
                    26:[28,None,None,None,24,None,None,None,None],27:[None,None,None,None,25,None,None,None,28],28:[None,None,None,None,26,None,None,None,None]}

    new_loc = loc_dict.get(location)[atk_angle]

    return new_loc

def damage_controller(defender, attacker, location, dam_type, dam_mult, roll, cs, entities, maneuver = False) -> list:
    '''Main damage function.'''
    if maneuver:
        atk_angle = 4
    else:
        atk_angle = angle_id(attacker.fighter.combat_choices[3])
    
    rel_angle = entity_angle(defender, attacker)

    deflect, soak = calc_damage_soak(dam_type, defender)

    messages = []
    
    #Calc pre-soak damage total
    if maneuver:
        dam_amount = dam_mult
    else:
        dam_amount = dam_mult * cs.get(dam_type + ' psi')
    
    #Just to start while loop
    damage = dam_amount

    layer = 0

    #Loops until no more damage is left to do, allowing for pass-through damage
    while location is not None and damage > 0:

        if roll <= deflect[layer]: 
            l_names = ['skin','tissue','bone']
            messages.append(attacker.name + ' hit ' + defender.name +', but the blow deflected harmlessly off of ' + defender.name + '\'s ' + l_names[layer])
            break
        
        #Store previous damage level to avoid repeating damage effects
        prev_health = defender.fighter.locations[location][layer]
        
        #determine how much damage is done to loc/layer and if pass-through occurs
        new_location, new_layer, new_damage = calc_layer_damage(defender, location, layer, dam_type, dam_amount, soak, atk_angle, rel_angle)  

        messages.extend(get_injuries(defender, prev_health, location, layer, dam_type))

        if new_location != location or new_layer != layer:
            damage = new_damage
            layer = new_layer
            location = new_location
        else:
            damage = 0
            location = None

        handle_mobility_change(defender)
        
    cleave_messages = cleave_checker(defender)
    if len(cleave_messages) > 0:
        messages.extend(cleave_messages)
        defender.state = EntityState.dead
    
    #Handle death and unconsciousness
    if defender.state != EntityState.conscious:
        handle_state_change(defender, entities, defender.state)
        

    return messages

def cleave_checker(entity) -> list:
    '''Purpose is to identify when body has been cut in two'''
    messages = []
    severed_locs = set()
    hor_chest = {5,6}
    hor_shoulder = {3,4}
    hor_ribs = {9,10}
    hor_abd = {13,14}
    hor_hips = {17,18}
    hor_sets = [hor_chest, hor_shoulder, hor_ribs, hor_abd, hor_hips]
    vert_l = {4,6,10,14,18}
    vert_r = {3,5,9,13,17}
    vert_sets = [vert_l, vert_r]
    x_1 = {4,5}
    x_2 = {3,6}
    x_3 = {5,2}
    x_4 = {6,2}
    x_5 = {5,10}
    x_6 = {6,9}
    x_7 = {9,14}
    x_8 = {9,6,4}
    x_9 = {10,5,3}
    x_10 = {10,13}
    x_11 = {13,10}
    x_12 = {14,9}
    x_13 = {17,14}
    x_14 = {18,13}
    x_sets = [x_1,x_2,x_3,x_4,x_5,x_6,x_7,x_8,x_9,x_10,x_11,x_12,x_13,x_14]

    for index in range(len(entity.fighter.locations)):
        if entity.fighter.locations[index][2] == 0:
            severed_locs.add(index)

    for s in hor_sets:
        if s.issubset(severed_locs):
            message = entity.name + ' is split in half horizonatally. '
            messages.append(message)
    for s in vert_sets:
        if s.issubset(severed_locs):
            message = entity.name + ' is split in half vertically. '
            messages.append(message)
    for s in x_sets:
        if s.issubset(severed_locs):
            message = entity.name + ' is split in half diagonally. '
            messages.append(message)
    
    return messages

def calc_damage_soak(dam_type, target) -> (list, list):
    if dam_type == 'b':
        deflect = [15, 25, 0]        
        soak =  [.8 + ((((target.fighter.derm)*.75) + ((target.fighter.fat)*.25))/100 *.08),
                 .75 + ((((target.fighter.fat)*.6) + ((target.fighter.str)*.4))/100 *.08), 
                 .4 + (sqrt(target.fighter.flex)/100)]
        for i in soak:
            if i > .95: i = .95

    elif dam_type == 's':
        deflect = [0, 0, 15]
        soak =  [.8, .7, .65]

    elif dam_type == 'p':
        deflect = [0, 0, 90]
        soak =  [.85, .8, .05]


    elif dam_type == 't':
        deflect = [0, 0, 100]
        soak =  [.5 + (sqrt(target.fighter.derm)/50), 
                .5 + (sqrt(target.fighter.fat)/50), 
                0]


    return deflect, soak

def calc_layer_damage(defender, location, layer, dam_type, dam_amount, soak, atk_angle, entity_angle) -> (int, int, int):

    atk_angle = angle_id(atk_angle)

    #Calc final damage
    damage = int(round((1-soak[layer])*dam_amount))

    if defender.fighter.locations[location][layer] < damage:
        damage -= defender.fighter.locations[location][layer]
        defender.fighter.locations[location][layer] = 0
        if layer < 2:
            layer += 1
        else:
            layer = 0
            location = find_next_location(location, atk_angle, entity_angle)
    else:
        defender.fighter.locations[location][layer] -= damage
        if layer == 2 and dam_type == 'p':
            location = find_next_location(location, atk_angle, entity_angle)
            layer = 0
        else:
            damage = 0
    
    return location, layer, damage

def get_injuries(defender, prev_health, location, layer, dam_type) -> list:
    '''Determines damage level and calls filter_injuries and apply_injuries to add injuries'''
    messages = set()
    inj_messages = set()
    sev = 0
    max_sev = 0
    #Determine damage effect level
    #Find % damage
    dam_percent = 0
    prev_percent = (prev_health/defender.fighter.max_locations[location][layer])
    layer_health = defender.fighter.locations[location][layer]

    if layer_health != 0: 
        dam_percent = (defender.fighter.locations[location][layer]/defender.fighter.max_locations[location][layer])

    dam_thresh = find_dam_threshold(dam_percent)
    prev_thresh = find_dam_threshold(prev_percent)

    new_thresh = dam_thresh - prev_thresh

    if new_thresh > 0:
        for i in range(new_thresh + 1):
            valid_injuries = filter_injuries(Injury, location, dam_type, dam_thresh, layer, defender)
            #Max_sev used to clear all lower inujury effecxt messages and only use the max damage one
            inj_messages, sev = apply_injuries(valid_injuries, location, defender, dam_type)
            if sev >= max_sev:
                messages.clear()
                messages.update(inj_messages)
            i += 1

    return messages

def find_dam_threshold(percent) -> int:
    dam_thresh = 0

    if percent <= .9: dam_thresh += 1
    if percent <= .75: dam_thresh += 1
    if percent <= .5: dam_thresh += 1
    if percent <= .25: dam_thresh += 1
    if percent <= .1: dam_thresh += 1
    if percent <= 0: dam_thresh += 1

    return dam_thresh

def apply_injury_effects(recipient, injury, location, remove = False) -> list:
    '''Generic injury effect applier. remove bool reverses any reversible or non-temp effects'''
    messages = []

    
    if not remove:
        messages.append(injury.description)

    if injury.pain_check and not remove:
        check = save_roll_un(recipient.fighter.will, 0)
        if 'f' in check:
            recipient.state = EntityState.stunned
            messages.append(recipient.name + ' is overcome by the pain from the blow, and is stunned for a short while.')

        elif 'cf' in check:
            recipient.fighter.gen_stance = FighterStance.prone
            recipient.state = EntityState.unconscious
            messages.append(recipient.name + ' faints due to the intense pain of the wound.')

    if injury.shock_check and not remove:
        check = save_roll_un(recipient.fighter.shock, 0)
        if 'f' in check:
            recipient.state = EntityState.shock
            messages.append(recipient.name + ' is experiencing the early effects of shock, and is disoriented and unstable.')
            recipient.fighter.mod_attribute('clarity',-20)

        elif 'cf' in check:
            recipient.fighter.gen_stance = FighterStance.prone
            recipient.state = EntityState.unconscious
            recipient.fighter.bleed.append([100,100])
            messages.append(recipient.name + ' rapidly goes into shock and collapses.')

    if injury.balance_check and not remove:
        check = save_roll_un(recipient.fighter.shock, 0)
        if 'f' in check or 'cf' in check:
            recipient.fighter.gen_stance = FighterStance.prone
            messages.append(recipient.name + ' is toppled by the blow.')

    if injury.clarity_reduction is not None:
        if remove:
            recipient.fighter.mod_attribute('clarity',injury.clarity_reduction)
        else:
            recipient.fighter.mod_attribute('clarity',-injury.clarity_reduction)

    if injury.bleed_amount is not None and not remove:
        recipient.fighter.bleed.append([injury.bleed_amount, injury.bleed_duration])

    if injury.attr_name is not None:
        for a in injury.attr_name:
            idx = injury.attr_name.index(a)
            if remove:
                recipient.fighter.mod_attribute(a, -injury.attr_amount[idx])
            else:
                recipient.fighter.mod_attribute(a, injury.attr_amount[idx])

    if injury.loc_reduction is not None and not remove:
        recipient.fighter.locations[location][injury.layer] -= injury.loc_reduction

    if injury.loc_max is not None and not remove:
        recipient.fighter.max_locations[location][injury.layer] = recipient.fighter.max_locations[location][injury.layer]*injury.loc_max
    
    if injury.severed_locs is not None and not remove:
        recipient.fighter.severed_locs.update(injury.severed_locs)

    if injury.paralyzed_locs is not None and not remove:
        recipient.fighter.paralyzed_locs.update(injury.paralyzed_locs)

    if injury.temp_phys_mod is not None and not remove:
        recipient.fighter.temp_physical_mod -= injury.temp_phys_mod

    if injury.suffocation is not None and not remove:
        if recipient.fighter.suffocation is not None and recipient.fighter.suffocation > injury.suffocation:
           recipient.fighter.suffocation = injury.suffocation
    
    if injury.stam_drain is not None:
        if remove:
            recipient.fighter.mod_attribute('stam_drain',-injury.stam_drain)
        else:
            recipient.fighter.mod_attribute('stam_drain',injury.stam_drain)
    
    if injury.stam_regin is not None:
        if remove:
            recipient.fighter.mod_attribute('stamr',recipient.fighter.max_stamr * injury.stam_regin)
        else:
            recipient.fighter.mod_attribute('stamr',-(recipient.fighter.max_stamr * injury.stam_regin))

    if injury.pain_mv_mod is not None:
        if remove:
            recipient.fighter.pain_mod_mov -= injury.pain_mv_mod
        else:
            recipient.fighter.pain_mod_mov += injury.pain_mv_mod

    if injury.diseases is not None and not remove:
        recipient.fighter.diseases.update(injury.diseases)

    if injury.atk_mod_r is not None:
        if remove:
            recipient.fighter.atk_mod_r += -injury.atk_mod_r
        else:
            recipient.fighter.atk_mod_r += injury.atk_mod_r
    
    if injury.atk_mod_l is not None:
        if remove:
            recipient.fighter.atk_mod_l += -injury.atk_mod_l
        else:
            recipient.fighter.atk_mod_l += injury.atk_mod_l
    
    if injury.mv_mod:
        if remove:
            recipient.fighter.mod_attribute('mv',recipient.fighter.max_mv * injury.mv_mod)
        else:
            recipient.fighter.mod_attribute('mv',-(recipient.fighter.max_mv * injury.mv_mod))

    if injury.gen_stance is not None and not remove:
        recipient.fighter.gen_stance = injury.gen_stance
        if recipient.fighter.gen_stance == FighterStance.prone:
            messages.append(recipient.name + ' is knocked prone. ')
        elif recipient.fighter.gen_stance == FighterStance.kneeling:
            messages.append(recipient.name + ' is forced to their knees. ')

    if injury.state is not None and not remove:
        recipient.fighter.state = injury.state

    return messages

def calc_modifiers(weapon, location, angle_id) -> (int, int, int, int):
    #Weapon mods
    atk_mod = weapon.attack_mod
    parry_mod = 0
    dodge_mod = 0
    dam_mult = weapon.b_dam
    #Loc mods
    if location == 0 or 10 < location < 13:
        atk_mod -= 60
    elif location == 1 or 18 < location < 21 or 22 < location < 25:
        atk_mod -= 40
    elif location == 2:
        atk_mod -= 30
    elif 4 < location < 7 or 16 < location < 19:
        atk_mod += 20
    elif 6 < location < 9 or 24 < location < 27:
        atk_mod -= 10
    elif 8 < location < 11 or 12 < location < 15 or 20 < location < 23:
        atk_mod += 10
    elif 14 < location < 17 or 26 < location < 29:
        atk_mod -= 20
    #Angle mods
    if angle_id == 0:
        dam_mult *= 1.2
        atk_mod += 5
        parry_mod += -15
        dodge_mod += -10
    elif angle_id == 1:
        dam_mult *= 1.1
        atk_mod += 5
        parry_mod += -10
        dodge_mod += 5
    elif angle_id == 2:
        atk_mod += -5
        parry_mod += 5
    elif angle_id == 3:
        atk_mod += -5
        parry_mod += 15
        dodge_mod += -15
    elif angle_id == 4:
        dam_mult *= 1.1
        atk_mod -= 10
        parry_mod -= 15
        dodge_mod += 20
    elif angle_id == 5:
        dam_mult *= .9
        atk_mod -= 10
        parry_mod -= 20
        dodge_mod -= 20
    elif angle_id == 6:
        atk_mod -= 10
        parry_mod += -10
    elif angle_id == 7:
        parry_mod += -15
    elif angle_id == 8:
        dam_mult *= .5
        atk_mod += 25
        parry_mod += -25
        dodge_mod += 5
    
    return dam_mult, atk_mod, parry_mod, dodge_mod

def valid_maneuvers(aggressor, target) -> set:
    all_maneuvers = set()
    invalid_maneuvers = set()
    dup_maneuvers = set()
    
    
    for w in aggressor.weapons:
        all_maneuvers = all_maneuvers | set(w.maneuvers)

    #Eliminate duplicates
    for mnvr in all_maneuvers:
        count = 0
        for m in all_maneuvers:
            if mnvr.name == m.name:
                count += 1
        if count > 1:
            dup_maneuvers.add(mnvr)

    all_maneuvers = all_maneuvers.difference(dup_maneuvers)

    for mnvr in all_maneuvers:

        #Find valid locations based on angle/dist
        reachable_locs = set(determine_valid_locs(aggressor, target, mnvr))
        #Remove any maneuvers that cannot reach a valid target
        if reachable_locs.isdisjoint(mnvr.locs_allowed):
            invalid_maneuvers.add(mnvr)
            continue
        
        #Check prereqs and remove maneuvers that do not meet them
        if len(mnvr.prereq) != 0:
            valid = False
            for p in mnvr.prereq:
                for a in aggressor.fighter.maneuvers:
                    if type(p) is type(a) and a.aggressor is aggressor:
                        valid = True
            if not valid: 
                invalid_maneuvers.add(mnvr)
                continue

        #Check if aggressor has ap
        skill_ratings = []
        for s in mnvr.skill:
            skill_ratings.append(getattr(aggressor.fighter, s))
        skill_rating = max(skill_ratings)
        
        final_ap = int(mnvr.base_ap * ((100/skill_rating)**.2 ))
        
        if aggressor.fighter.ap < final_ap:
            invalid_maneuvers.add(mnvr)
            continue  
        
        #See if both hands are free if it's a two handed maneuver
        if mnvr.hand:
            if mnvr.hands == 2:
                if mnvr not in aggressor.weapons[0].maneuvers and mnvr not in aggressor.weapons[1].maneuvers:
                    invalid_maneuvers.add(mnvr)
                    continue 

        #See if aggressor stance is valid for the maneuver
        if aggressor.fighter.gen_stance not in mnvr.agg_stance_pre:
            invalid_maneuvers.add(mnvr)
            continue

        #See if target stance is valid for the maneuver
        if target.fighter.gen_stance not in mnvr.target_stance_pre:
            invalid_maneuvers.add(mnvr)
            continue

    all_maneuvers = all_maneuvers.difference(invalid_maneuvers)


    return all_maneuvers

def apply_maneuver(aggressor, target, maneuver, location, entities, game_map) -> list:
    mnvr = maneuver(aggressor, target, location)
    dam_type = None
    messages = []
    check = []
    damage_list = []
    loc_list = []
    dam_types_list = []
    skill_rating = 0
    mobility_changed = False
    #Dict containing x,y offset based on facing direction  
    offset_dict = {6:(-1,0),5:(-1,1),7:(-1,-1),1:(1,-1),3:(1,1),2:(1,0),4:(0,1),0:(0,-1)}
    
    #Apply any clarity reductions before making balance checks
    if mnvr.clarity_reduction > 0:
        target.fighter.mod_attribute('clarity', -1 * mnvr.clarity_reduction)

    #Apply any direct damage
    if mnvr.random_dam_loc:
        roll = roll_dice(1,99) - 1
        location = target.fighter.find_location(roll)
    
    for i in [mnvr.b_dam,mnvr.s_dam,mnvr.p_dam,mnvr.t_dam]:
        if i > 0:
            if i is mnvr.b_dam: dam_type = 'b'
            elif i is mnvr.s_dam: dam_type = 's'
            elif i is mnvr.p_dam: dam_type = 'p'
            else: dam_type = 't'
            damage_list.append(i * aggressor.fighter.ep)
            loc_list.append(location)
            dam_types_list.append(dam_type)

    #See if target falls
    if mnvr.balance_check:
        check = save_roll_un(target.fighter.bal, target.fighter.stability + mnvr.stability_mod)
        if 'f' in check[0]:
            dam_amount, num_locs = calc_falling_damage(target, target.fighter.height, mnvr.throw_force)
            l = 0
            while l < num_locs:
                damage_list.append(dam_amount)
                roll = roll_dice(1,99) - 1
                location = target.fighter.find_location(roll)
                loc_list.append(location)
                dam_types_list.append('b')
                l += 1
            

    #Pass each damage instgance to the damage controller for application
    idx = 0
    for d in damage_list:
        idx += 1
        roll = roll = roll_dice(1,99) - 1
        cs = dict()
        messages.extend(damage_controller(target, aggressor, loc_list[idx], dam_types_list[idx], d, roll, cs, entities, True))

    #Remove the prereq if one exists
    if len(mnvr.prereq) > 0:
        for p in mnvr.prereq:
                for a in target.fighter.maneuvers:
                    if type(p) is type(a) and a.aggressor is aggressor and a.loc_idx == location:
                        remove_maneuver(target, aggressor, a)
                for a in aggressor.fighter.maneuvers:
                    if type(p) is type(a) and a.aggressor is aggressor and a.loc_idx == location:
                        aggressor.fighter.maneuvers.remove(a)
                        continue
    
    #Subtract the AP
    skill_ratings = []
    for s in mnvr.skill:
        skill_ratings.append(getattr(aggressor.fighter, s))
    skill_rating = max(skill_ratings)
        
    final_ap = int(mnvr.base_ap * ((100/skill_rating)**.2 ))

    aggressor.fighter.mod_attribute('ap', final_ap)

    #Immobilize locations
    for l in mnvr.immobilized_locs:
        target.fighter.immobilize_locs.add(l)
    for l in mnvr.agg_immob_locs: 
        aggressor.fighter.immobilize_locs.add(l)

    #Perform pain check and immobilize for round if failed
    if mnvr.pain_check:
        check = save_roll_un(target.fighter.will, 0)
        if 'f' in check:
            target.state = EntityState.stunned
            messages.append(target.name + ' is overcome by the pain from the blow, and is stunned for a short while.')

        elif 'cf' in check:
            target.fighter.gen_stance = FighterStance.prone
            target.state = EntityState.unconscious
            messages.append(target.name + ' faints due to the intense pain of the wound.')

    #Apply any temp phys mod
    if mnvr.temp_phys_mod is not None:
        target.fighter.temp_physical_mod -= mnvr.temp_phys_mod

    #Add paralyzed locations
    if mnvr.paralyzed_locs is not None:
        target.fighter.paralyzed_locs.update(mnvr.paralyzed_locs)

    #Apply suffocation
    if mnvr.suffocation is not None:
        if target.fighter.suffocation is not None and target.fighter.suffocation > mnvr.suffocation:
           target.fighter.suffocation = mnvr.suffocation

    #Apply Stam drain and regin mods
    if mnvr.stam_drain is not None:
        target.fighter.mod_attribute('stam_drain',mnvr.stam_drain)
    
    if mnvr.stam_regin is not None:
        target.fighter.mod_attribute('stamr',-(target.fighter.max_stamr * mnvr.stam_regin))

    #Apply attack mods
    if mnvr.atk_mod_r is not None:
        target.fighter.atk_mod_r += mnvr.atk_mod_r
    
    if mnvr.atk_mod_l is not None:
        target.fighter.atk_mod_l += mnvr.atk_mod_l
    
    #Apply target stance and state
    if mnvr.gen_stance is not None:
        target.fighter.gen_stance = mnvr.gen_stance
        if target.fighter.gen_stance == FighterStance.prone:
            messages.append(target.name + ' is knocked prone. ')
        elif target.fighter.gen_stance == FighterStance.kneeling:
            messages.append(target.name + ' is forced to their knees. ')

    if mnvr.state is not None:
        target.fighter.state = mnvr.state

    #Apply aggressor stance (succeed)
    if mnvr.agg_suc_stance is not None:
        aggressor.fighter.stance = mnvr.agg_suc_stance

    #Apply movement mods
    if mnvr.mv_scalar is not 1 or mnvr.can_move is False:

        if mnvr.can_move is False:
            mv_mod = target.fighter.max_mv
        else:
            mv_mod = (1-mnvr.mv_scalar) * target.fighter.max_mv

        target.fighter.mod_attribute('mv',-mv_mod)

    #Apply involuntary movement
    if mnvr.inv_move:
        direction = target.fighter.facing
        if mnvr.inv_move_back:
            direction = target.fighter.facing + 4
            #Handle boundary
            if direction > 7:
                direction -= 8  

        mobility_changed = relo_actor(game_map, target, aggressor, entities, direction, 2)    

    if not mobility_changed:
        handle_mobility_change(target)
    
    return messages  

def remove_maneuver(target, aggressor, maneuver):
    mnvr = maneuver
    
    #Apply any clarity reductions before making balance checks
    if mnvr.clarity_reduction > 0:
        target.fighter.mod_attribute('clarity', mnvr.clarity_reduction)

    #Mobilize locations
    for l in mnvr.immobilized_locs:
        #Remove loc from list
        target.fighter.immobilize_locs.remove(l)
        for m in target.fighter.maneuvers:
            if m is not mnvr:
                if l in m:
                    #Re-add loc if included in another maneuver
                    target.fighter.immobilize_locs.add(l)
        
    for l in mnvr.agg_immob_locs: 
        aggressor.fighter.immobilize_locs.remove(l)
        for m in aggressor.fighter.maneuvers:
            if m is not mnvr:
                if l in m:
                    aggressor.fighter.immobilize_locs.add(l)

    #Remove any temp phys mod
    if mnvr.temp_phys_mod is not None:
        target.fighter.temp_physical_mod += mnvr.temp_phys_mod

    #Remove paralyzed locations
    if mnvr.paralyzed_locs is not None:
        for l in mnvr.paralyzed.locs:
            target.fighter.paralyzed_locs.remove(l)
            for m in target.fighter.maneuvers:
                if m is not mnvr:
                    if l in m:
                        target.fighter.paralyzed_locs.add(l)
            #Re-add if injuiries paralyze the loc
            for i in target.fighter.injuries:
                if l in i.paralyzed_locs:
                    target.fighter.paralyzed_locs.add(l)

    #Remove suffocation
    if mnvr.suffocation is not None:
        if target.fighter.suffocation is not None:
            max_suff = None
            #Check each injury and find the one with the lowest suffocation number (min rnds to suffocation) and apply it
            for i in target.fighter.injuries:
               if i.suffocation is not None:
                   if max_suff is None:
                       max_suff = i.suffocation
                   elif i.suffocation < max_suff:
                       max_suff = i.suffocation
            
            target.fighter.suffocation = max_suff

    #Remove Stam drain and regin mods
    if mnvr.stam_drain is not None:
        target.fighter.mod_attribute('stam_drain',-mnvr.stam_drain)
    
    if mnvr.stam_regin is not None:
        target.fighter.mod_attribute('stamr',(target.fighter.max_stamr * mnvr.stam_regin))

    #Remove attack mods
    if mnvr.atk_mod_r is not None:
        target.fighter.atk_mod_r -= mnvr.atk_mod_r
    
    if mnvr.atk_mod_l is not None:
        target.fighter.atk_mod_l -= mnvr.atk_mod_l
    
    #Remove movement mods
    if mnvr.mv_scalar is not 1 or mnvr.can_move is False:
        if mnvr.can_move is False:
            mv_mod = target.fighter.max_mv
        else:
            mv_mod = (1-mnvr.mv_scalar) * target.fighter.max_mv

        for m in target.fighter.maneuvers:
            if m.mv_scalar is not 1 or m.can_move is False:
                if mnvr.can_move is False:
                    mv_mod = target.fighter.max_mv
                else:
                    mv_mod -= (1-m.mv_scalar) * target.fighter.max_mv

        for i in target.fighter.injuries:
            if i.mv_mod is not None:
                mv_mod -= (1-i.mv_mod) * target.fighter.max_mv

        target.fighter.mod_attribute('mv',mv_mod)

def calc_falling_damage(target, distance, add_force = 0, surface_hardness = .8) -> (int, int):
    weight = target.fighter.weight
    g = 9.81 * 3.28 #Convert to feet
    distance = distance / 12 #Convert to feet
    velocity = sqrt(2 * distance * g)

    force = weight * (velocity * velocity)
    force = force / .5 #Account for 6" of compression on impact
    force += add_force
    force = force * surface_hardness #SH is a scalar, 1 is maximum
    force = force / 144 #convert to inches
    
    num_locs = roll_dice(1,3)
    if force > 100 and num_locs < 2:
        num_locs += roll_dice(1,3) - 1
    if force > 200 and num_locs <= 3:
        num_locs += roll_dice(1,3) - 1
    if force > 400 and num_locs <= 5:
        num_locs += roll_dice(1,3) - 1
    if force > 800 and num_locs <= 6:
        num_locs += roll_dice(1,3) - 1

    force = force / num_locs
    force = int(force)

    return force, num_locs

def handle_state_change(entity, entities, state) -> None:
    entity.state = state
    if entity.state == EntityState.dead:
        entity.char = '#'
        entity.color = 'crimson'
        entity.fighter = None
        for item in entities:
            if hasattr(item, 'fighter') and item is not entity:
            #Handle target removal if dead
                for target in item.fighter.targets:
                    if target is entity:
                        del item.fighter.targets[item.fighter.targets.index(target)]

def init_combat(curr_actor, order, command) -> (dict, int, int, list):
    game_state = GameStates.menu
    combat_phase = CombatPhase.action
    messages = []
    menu_dict = dict()

    try:
        if command.get('Wait'):
            if curr_actor.player:
                messages.append('You decide to wait for your opponents to act')
            else:
                messages.append(curr_actor.name + ' waits for you to act')
            curr_actor.fighter.wait = True
            combat_phase = CombatPhase.action
            game_state = GameStates.default
        elif command.get('Maneuver'):
            if curr_actor.player:
                messages.append('You decide to attempt a special maneuver')
            combat_phase = CombatPhase.maneuver
        elif command.get('Change Stance'):
            if curr_actor.player:
                messages.append('You decide to change your stance')
            combat_phase = CombatPhase.stance
        elif command.get('Change Guard'):
            if curr_actor.player:
                messages.append('You decide to change your guard')
            combat_phase = CombatPhase.guard                     
        elif command.get('Attack'):
            if curr_actor.player:
                messages.append('You decide to attack')
            combat_phase = CombatPhase.weapon
        elif command.get('Move'):
            if curr_actor.player:
                messages.append('You decide to move.')
            else:
                messages.append(curr_actor.name + ' moves. ')
            combat_phase = CombatPhase.move
        elif command.get('End Turn'):
            if curr_actor.player:
                messages.append('You decide to end your turn')
            else:
                if curr_actor.fighter.male: pro = 'his'
                else: pro = 'her'
                messages.append(curr_actor.name + ' ends ' + pro + ' turn')
            curr_actor.fighter.end_turn = True
            curr_actor.fighter.action.clear()
            combat_phase = CombatPhase.action
            game_state = GameStates.default 
    except:
        if curr_actor.fighter.can_act:
            #CHeck to see if entity can afford to attack
            wpn_ap = []
            curr_actor.fighter.acted = False
            for wpn in curr_actor.weapons:
                for atk in wpn.attacks:
                    cs = curr_actor.determine_combat_stats(wpn, atk)
                    wpn_ap.append(cs.get('final ap'))
            min_ap = min(wpn_ap)
            curr_actor.fighter.action.clear()
            if len(curr_actor.fighter.entities_opportunity_attacked) != 0:
                curr_actor.fighter.action.append('Attack')
            elif curr_actor.fighter.ap >= min_ap:
                curr_actor.fighter.action.append('Attack')
            if curr_actor.fighter.ap >= curr_actor.fighter.walk_ap and curr_actor.fighter.can_walk:
                curr_actor.fighter.action.append('Move')
            if len(order) > 1 and len(curr_actor.fighter.action) >= 1: 
                curr_actor.fighter.action.append('Wait')
                curr_actor.fighter.action.append('Maneuver')
                curr_actor.fighter.action.append('Change Stance')
                curr_actor.fighter.action.append('Change Guard')
            if len(curr_actor.fighter.action) >= 1:
                curr_actor.fighter.action.append('End Turn')
                game_state = GameStates.menu
            else:
                curr_actor.fighter.end_turn = True
                combat_phase = CombatPhase.action
                game_state = GameStates.default
                return menu_dict, combat_phase, game_state, order, messages

            combat_menu_header = 'What do you wish to do?'

            menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}                       

    if hasattr(curr_actor.fighter, 'ai'):
        game_state = GameStates.default


    return menu_dict, combat_phase, game_state, order, messages

def change_actor(order, entities, curr_actor, combat_phase, game_state, logs) -> (int, int, list, object):
    messages = []
    log = logs[2]
    round_end = False
    
    

    #Exit without making changes if in defend phase
    if combat_phase == CombatPhase.defend:
        return combat_phase, game_state, order, curr_actor

    if len(order) == 0:
        round_end = True
        
    else:
        #Check and see if anyone can still act
        remaining_fighters = 0
        for entity in order:
            if entity.state != EntityState.conscious:
                order.remove(entity)
                global_vars.turn_order.remove(entity)
            elif entity.fighter.end_turn:
                order.remove(entity)
                global_vars.turn_order.remove(entity)
        remaining_fighters = len(order)
        if remaining_fighters == 1:
            targets = 0
            for entity in entities:
                if entity.fighter is not None and entity is not curr_actor:
                    targets += 1
            if targets == 0:
                #Below exits combat when all enemies are dispatched
                combat_phase = CombatPhase.explore
                game_state = GameStates.default
                return combat_phase, game_state, order, curr_actor

        if global_vars.debug and len(order) != len(global_vars.turn_order) : print('order length: ' + str(len(order)) + ', global order length: ' + str(len(global_vars.turn_order)))
        
        if remaining_fighters == 0: 
            round_end = True
        else:
            order = list(global_vars.turn_order)
            if len(order) > 1:
                if order[0].fighter.wait: 
                    if not order[0].fighter.curr_target.fighter.acted: 
                        curr_actor = order[0].fighter.curr_target
                    else: 
                        order[0].fighter.wait = False
                        order[0].fighter.curr_target.fighter.acted = False
                elif order[0] in curr_actor.fighter.entities_opportunity_attacked:
                    pass
                elif order[0].fighter.feint:
                    if not order[0].fighter.curr_target.fighter.acted: 
                        curr_actor = order[0].fighter.curr_target
                    else:
                        order[0].fighter.feint = False
                        order[0].fighter.curr_target.fighter.acted = False
                        #Remove fient dodge/parry mods
                        idx = len(order[0].fighter.combat_choices)
                        option = order[0].fighter.combat_choices[(idx - 1)]
                        order[0].fighter.loc_dodge_mod[option] -= order[0].fighter.best_combat_skill/3
                        order[0].fighter.loc_parry_mod[option] -= order[0].fighter.best_combat_skill/3
                        for t in order[0].fighter.targets:
                            if order[0] in t.fighter.targets:
                                #Adjust perceived hit location modifiers
                                t.fighter.adjust_loc_diffs(order[0], option, 0)
                        order[0].fighter.combat_choices.clear()

                elif combat_phase != CombatPhase.defend:
                    curr_actor = order[0]
            else:
                curr_actor = order[0]

    if round_end:
        log.add_message(Message('The round has ended. '))
        combat_phase = CombatPhase.init
        global_vars.round_num  += 1
        order = entities
        global_vars.turn_order = list(order)
        for entity in order:
            handle_persistant_effects(entity, entities)

    for message in messages:
        log.add_message(Message(message))
        
            
    return combat_phase, game_state, order, curr_actor

def phase_init(entities) -> (int, list):
    active_fighters = 0

    for entity in entities:
        if entity.fighter is not None:
            active_fighters += 1
            entity.fighter.end_turn = False
            entity.fighter.targets = aoc_check(entities, entity)
            if entity.fighter.guard is None:
                entity.set_default_guard()
    
    #Sort the entities by initiative
    if active_fighters > 1:    
        order = turn_order(entities)
        global_vars.turn_order = list(order)
        if global_vars.debug: print('order length: ' + str(len(order)) + ', global order length: ' + str(len(global_vars.turn_order)))
        combat_phase = CombatPhase.action
    else:
        order = entities
        global_vars.turn_order = list(order)
        combat_phase = CombatPhase.explore

    return combat_phase, order

def phase_action(curr_actor, players, entities, order, command, logs, game_map) -> (dict,int,list):
    combat_phase = CombatPhase.action
    game_state = GameStates.default
    menu_dict = dict()
    messages = []
    log = logs[2]
    status_log = logs[1]  


    if len(command) != 0:
        #Check and see if entity has a target in aoc
        if len(curr_actor.fighter.targets) == 0:
            if isinstance(command, str):
                if command == 'strafe': 
                    message = strafe_control(curr_actor)
                    log.add_message(message)
            elif len(command) != 0: 
                if isinstance(command, dict):
                    if command.get('End Turn'):
                        curr_actor.fighter.end_turn = True
                        combat_phase = CombatPhase.action
                elif curr_actor.fighter.ap >= curr_actor.fighter.walk_ap:
                    if command[0] in ['move','spin','prone','stand','kneel']:
                        moved = move_actor(game_map, curr_actor, entities, command, logs)                         

                    if global_vars.debug: print(curr_actor.name + ' ap:' + str(curr_actor.fighter.ap))

                    if len(curr_actor.fighter.targets) != 0:
                        menu_dict, combat_phase, game_state, order, messages = init_combat(curr_actor, order, command)
                                
                else:
                    curr_actor.fighter.end_turn = True
                    combat_phase = CombatPhase.action
        else:
            menu_dict, combat_phase, game_state, order, messages = init_combat(curr_actor, order, command)
    else:
        if len(curr_actor.fighter.targets) != 0:    
            menu_dict, combat_phase, game_state, order, messages = init_combat(curr_actor, order, command)

    for message in messages:
        log.add_message(Message(message))

    return menu_dict, combat_phase, game_state, order

def phase_weapon(curr_actor, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    

    #Choose your weapon
    combat_menu_header = 'Choose your weapon'
    curr_actor.fighter.action.clear()
    for wpn in curr_actor.weapons:
        for atk in wpn.attacks:
            cs = curr_actor.determine_combat_stats(wpn, atk)
            if curr_actor.fighter.ap >= cs.get('final ap'):
                if wpn.name not in curr_actor.fighter.action:
                    curr_actor.fighter.action.append(wpn.name)

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}
    
    for option in curr_actor.fighter.action:
        if len(command) != 0:
            if command.get(option):
                if not hasattr(curr_actor.fighter, 'ai'):
                    messages.append('You decide to use ' + option)
                for wpn in curr_actor.weapons:
                    if option == wpn.name:
                        if len(curr_actor.fighter.combat_choices) == 0:   
                            curr_actor.fighter.combat_choices.append(wpn)
                menu_dict = dict()
                combat_phase = CombatPhase.option
    
    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

        

    return combat_phase, menu_dict

def phase_option(curr_actor, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]

    #Choose the base attack type (stab, slash, etc)
    combat_menu_header = 'How would you like to attack your target?'
    curr_actor.fighter.action.clear()
    #Determine AP needs
    for atk in curr_actor.fighter.combat_choices[0].attacks:
        cs = curr_actor.determine_combat_stats(curr_actor.fighter.combat_choices[0], atk)
        atk_final_ap = cs.get('final ap')
        if len(curr_actor.fighter.entities_opportunity_attacked) != 0 or curr_actor.fighter.ap >= atk_final_ap:
            curr_actor.fighter.action.append(atk.name)

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}
    
    for option in curr_actor.fighter.action:
        if len(command) != 0:
            if command.get(option):
                if not hasattr(curr_actor.fighter, 'ai'):
                    for atk in curr_actor.fighter.combat_choices[0].attacks:
                        if atk.name == option:
                            curr_actor.fighter.combat_choices.append(atk)
                            messages.append('You decide to ' + option)
                menu_dict = dict()
                combat_phase = CombatPhase.location
    
    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default


    return combat_phase, menu_dict

def phase_location(curr_actor, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]

    #Choose the hit location
    combat_menu_header = 'Where do you want to aim?'
    curr_target = curr_actor.fighter.targets[0]
    attack = curr_actor.fighter.combat_choices[1]
    #Determine valid locations
    valid_locs = determine_valid_locs(curr_actor, curr_target, attack)
    #Prune list to only valid
    locations = prune_list(curr_target.fighter.get_locations(), valid_locs, True, False)
    curr_actor.fighter.action = locations
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}
    
    if len(command) != 0:    
        for option in curr_actor.fighter.action:
            if command.get(option):
                choice = command.get(option)
                if choice: 
                    if not hasattr(curr_actor.fighter, 'ai'):
                        curr_actor.fighter.combat_choices.append(curr_target.fighter.name_location(option))
                        messages.append('You aim for ' + curr_target.name + '\'s ' + option)   
                    curr_actor.fighter.action = determine_valid_angles(curr_target.fighter.name_location(option), attack)
                    menu_dict = dict()
                    combat_phase = CombatPhase.option2
    
    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    return combat_phase, menu_dict

def phase_option2(curr_actor, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    #Choose the angle of attack
    combat_menu_header = 'What angle would you like to attack from?'
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}
    if len(command) != 0:
        for option in curr_actor.fighter.action:
            choice = command.get(option)
            if choice:
                if not hasattr(curr_actor.fighter, 'ai'):
                    curr_actor.fighter.combat_choices.append(angle_id(option))
                    messages.append('You decide to use the ' + option + ' angle.')
                    menu_dict = dict()
                curr_actor.fighter.action = ['Accept', 'Restart']
                combat_phase = CombatPhase.confirm

    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

        
    
    return combat_phase, menu_dict

def phase_confirm(curr_actor, entities, command, logs, combat_phase) -> (int, dict, object):
    #Verify choices and continue or restart

    #Variable setup
    active_entity = curr_actor
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    missed = False
    log = logs[2]
    curr_target = curr_actor.fighter.targets[0]
    attack = curr_actor.fighter.combat_choices[1]
    location = curr_actor.fighter.combat_choices[2]
    angle = curr_actor.fighter.combat_choices[3]
    wpn_title = attack.name
    loc_name = curr_actor.fighter.targets[0].fighter.name_location(location)
    angle_name = angle_id(angle)
    
    cs = calc_final_mods(curr_actor, curr_target)

    
    final_to_hit = cs.get('to hit')
    p_hit = cs.get('p_hit')
    p_dodge_mod = cs.get('p_dodge')
    final_ap = cs.get('final ap')
    p_parry_mod = cs.get('p_parry')
    total_ep = cs.get('total ep')


    combat_menu_header = ('You are attacking with ' + wpn_title + ', aiming at ' + curr_target.name + '\'s ' 
        + loc_name + ' from a ' + angle_name + ' angle. ' 
        + ' For this attack, you will have a: ' + str(p_hit) +  '% chance to hit, and do up to ' 
        + str(total_ep) + ' PSI damage.' + ' Your opponent will get a ' + str(p_parry_mod) 
        + '% modifier to parry, and a ' + str(p_dodge_mod) + '% modifier to dodge. \n' + 
        'It will cost you ' + str(final_ap) + ' of your remaining ' + str(curr_actor.fighter.ap) + ' AP to attack. \n'
        + ' Would you like to continue, or modify your choices?')

    curr_actor.fighter.action = ['Accept', 'Restart']

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}

    if len(command) != 0:
        if command.get('Accept'):
            messages, combat_phase, active_entity, missed = perform_attack(curr_actor, entities, final_to_hit, curr_target, cs, combat_phase)
            curr_actor.fighter.last_atk_ap = final_ap
            curr_actor.fighter.acted = True
            curr_actor.fighter.action.clear()
        if command.get('Restart'):
            #Reset vars
            curr_actor.fighter.combat_choices.clear()
            combat_phase = CombatPhase.action
        
        menu_dict = dict()

    if missed:
        min_ap = curr_target.get_min_ap()
        if curr_target.fighter.ap >= min_ap and (curr_actor.x, curr_actor.y) in curr_target.fighter.aoc:
            curr_target.fighter.entities_opportunity_attacked.append(curr_actor)
            curr_target.fighter.counter_attack.append(curr_actor)
            if hasattr(curr_target.fighter, 'ai'):
                messages.append('You missed, allowing ' + curr_target.name + ' to counter-attack.')
            else:
                messages.append(curr_target.name + ' missed, giving you a chance to counter-attack.')
            active_entity = curr_target

    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default


    return combat_phase, menu_dict, active_entity

def phase_repeat(player, command, logs, combat_phase) -> (int, dict):
    #Repeat last attack?
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]

    combat_menu_header = 'Would you like to repeat the last attack, or start a new attack strategy?'
    player.fighter.action = ['Repeat', 'New']
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': player.fighter.action, 'mode': False}
    if len(command) != 0:
        if command.get('Repeat'):
            combat_phase = CombatPhase.confirm
            menu_dict = dict()

                    
        if command.get('New'):
            #Reset vars
            player.fighter.combat_choices.clear()
            combat_phase = CombatPhase.action
            menu_dict = dict()

    for message in messages:
        log.add_message(Message(message))

    

    return combat_phase, menu_dict

def phase_defend(curr_actor, enemy, entities, command, logs, combat_phase) -> (int, int, dict, object):
    #Variable setup
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    cs = enemy.fighter.mods
    message = None
    effects = []
    can_dodge = False
    can_parry = False
    atk_name = enemy.fighter.combat_choices[1].name 
    angle_name = angle_id(enemy.fighter.combat_choices[3])
    location = enemy.fighter.combat_choices[2]
    loc_name = curr_actor.fighter.name_location(enemy.fighter.combat_choices[2])
    game_state = GameStates.default
    header_items = []
    def_margin = None
    atk_margin = None
    rolls = None
    hit = False
    auto_block = False


    cs = calc_final_mods(enemy, curr_actor)
    
    final_to_hit = cs.get('to hit')
    dodge_mod = cs.get('dodge mod')
    parry_mod = cs.get('parry mod')


    


    #Find chances and see if curr_actor can parry/dodge
    cs_p = curr_actor.determine_combat_stats(curr_actor.weapons[0],curr_actor.weapons[0].attacks[0])
    parry_ap = cs_p.get('parry ap')
    if curr_actor.fighter.ap >= curr_actor.fighter.walk_ap: can_dodge = True
    if curr_actor.fighter.ap >= parry_ap: can_parry = True
    if enemy.fighter.counter_attack == curr_actor: 
        can_parry = False
        dodge_mod -= 50
        cs['dodge mod'] = dodge_mod
        enemy.fighter.counter_attack = None


    #Normalized (0-99) percentage scale of probabilities to p/d/b
    parry_chance = find_defense_probability(final_to_hit, (curr_actor.fighter.deflect + parry_mod))
    dodge_chance = find_defense_probability(final_to_hit, (curr_actor.fighter.dodge + dodge_mod))
    block_chance = find_defense_probability(final_to_hit, (curr_actor.fighter.best_combat_skill + parry_mod))


    #Choose how to defend '
    header_items.append(enemy.name + ' is attacking you in the ' + loc_name + ' with a ' + atk_name + ' from a ' + 
                angle_name + ' direction. \n' )
    curr_actor.fighter.action = ['Take the hit']
    if can_dodge:
        header_items.append('You have a ' + str(dodge_chance) + ' percent chance to dodge the attack at a cost of ' + str(curr_actor.fighter.walk_ap) + ' ap. \n')
        curr_actor.fighter.action.append('Dodge')
    if can_parry:
        header_items.append('You have a ' + str(parry_chance) + ' percent chance to parry the attack at a cost of ' + str(parry_ap) + ' ap. \n')
        curr_actor.fighter.action.append('Parry')
        #Determine if can block
        if enemy.fighter.combat_choices[2] <=2:
            if 0 < curr_actor.fighter.l_blocker or curr_actor.fighter.r_blocker:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                curr_actor.fighter.action.append('Block')
        elif enemy.fighter.combat_choices[2] in [3,5,7,9,11,13,15,19]:
            if 0 < curr_actor.fighter.r_blocker:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                curr_actor.fighter.action.append('Block')
        elif enemy.fighter.combat_choices[2] in [4,6,8,10,12,14,16,20]:
            if 0 < curr_actor.fighter.l_blocker:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                curr_actor.fighter.action.append('Block')
        elif enemy.fighter.combat_choices[2] in [17,21,23,25]:
            if 0 < curr_actor.fighter.locations[25][2]:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                curr_actor.fighter.action.append('Block')
        elif enemy.fighter.combat_choices[2] in [18,22,24,26]:
            if 0 < curr_actor.fighter.locations[26][2]:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                curr_actor.fighter.action.append('Block')
    if can_dodge or can_parry:
        game_state = GameStates.menu
        header_items.append('What would you like to do? ')
        combat_menu_header = ''.join(header_items)
        menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}
        if len(command) != 0:
            if command.get('Take the hit'):
                hit = True
                effects = damage_controller(curr_actor, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
            if command.get('Dodge'):
                check, def_margin, atk_margin = save_roll_con(curr_actor.fighter.dodge, dodge_mod, enemy.fighter.atk_result, final_to_hit)
                #Remove ap and stam
                curr_actor.fighter.mod_attribute('ap', -curr_actor.fighter.walk_ap)
                curr_actor.fighter.mod_attribute('stamina', -curr_actor.fighter.base_stam_cost)
                if check == 's':
                    if not hasattr(curr_actor.fighter, 'ai'): message = ('You dodged the attack. ')
                    else: message = (curr_actor.name + ' dodged the attack. ')
                elif location not in curr_actor.fighter.auto_block_locs:
                    hit = True
                    effects = damage_controller(curr_actor, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
                else: auto_block = True
            if command.get('Parry'):
                check, def_margin, atk_margin = save_roll_con(curr_actor.fighter.deflect, parry_mod, enemy.fighter.atk_result, final_to_hit)
                #Remove ap and stam
                curr_actor.fighter.mod_attribute('stamina', -(curr_actor.weapons[0].stamina*curr_actor.fighter.base_stam_cost))
                curr_actor.fighter.mod_attribute('ap', -parry_ap)
                if check == 's':
                    if not hasattr(curr_actor.fighter, 'ai'): message = ('You parried the attack. ')
                    else: message = (curr_actor.name + ' parried the blow. ')
                elif location not in curr_actor.fighter.auto_block_locs:
                    hit = True
                    effects = damage_controller(curr_actor, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
                else: auto_block = True
            if command.get('Block'):
                check, def_margin, atk_margin = save_roll_con(curr_actor.fighter.best_combat_skill, parry_mod, enemy.fighter.atk_result, final_to_hit)
                #Remove ap and stam
                if location not in curr_actor.fighter.auto_block_locs:
                    curr_actor.fighter.mod_attribute('stamina', -(curr_actor.weapons[0].stamina*curr_actor.fighter.base_stam_cost))
                    curr_actor.fighter.mod_attribute('ap', -parry_ap)
                else:
                    auto_block = True
                if check == 's':
                    if not hasattr(curr_actor.fighter, 'ai'): message = ('You blocked the attack. ')
                    else: message = (curr_actor.name + ' blocked the blow. ')
                    #Determine blocker to remove from
                    if enemy.fighter.combat_choices[2] <=2:
                        if curr_actor.fighter.l_blocker > curr_actor.fighter.r_blocker:
                            blocker = 16
                        else: blocker = 15
                    elif enemy.fighter.combat_choices[2] in [3,5,7,9,11,13,15,19]: blocker = 15
                    elif enemy.fighter.combat_choices[2] in [4,6,8,10,12,14,16,20]: blocker = 16
                    elif enemy.fighter.combat_choices[2] in [17,21,23,25]: blocker = 25
                    elif enemy.fighter.combat_choices[2] in [18,22,24,26]: blocker = 26


                    
                    effects = damage_controller(curr_actor, enemy, blocker, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result*.2, enemy.fighter.atk_result, cs, entities)
                else:
                    hit = True
                    effects = damage_controller(curr_actor, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
            
            menu_dict = dict()
    else:
        if location not in curr_actor.fighter.auto_block_locs:
            hit = True
            effects = damage_controller(curr_actor, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
        else:
            auto_block = True
    
    if auto_block:
        if not hasattr(curr_actor.fighter, 'ai'): message = ('Your guard automatically blocked the attack. ')
        else: message = (curr_actor.name + 's guard automatically blocked the blow. ')
        #Determine blocker to remove from
        if enemy.fighter.combat_choices[2] <=2:
            if curr_actor.fighter.l_blocker > curr_actor.fighter.r_blocker:
                blocker = 16
            else: blocker = 15
        elif enemy.fighter.combat_choices[2] in [3,5,7,9,11,13,15,19]: blocker = 15
        elif enemy.fighter.combat_choices[2] in [4,6,8,10,12,14,16,20]: blocker = 16
        elif enemy.fighter.combat_choices[2] in [17,21,23,25]: blocker = 25
        elif enemy.fighter.combat_choices[2] in [18,22,24,26]: blocker = 26

        effects = damage_controller(curr_actor, enemy, blocker, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result*.2, enemy.fighter.atk_result, cs, entities)
        

    if message or effects:
        combat_phase = CombatPhase.action
        
        if message:
            messages.append(message)

        if effects:
            for effect in effects:
                messages.append(effect)
        if curr_actor.state == EntityState.conscious:
            if curr_actor.fighter.disengage:       
                combat_phase = CombatPhase.disengage
                game_state = GameStates.default
                menu_dict = dict()
            elif curr_actor.fighter.feint and not hit:
                curr_actor.fighter.counter_attack = enemy
                enemy.fighter.combat_choices.clear()
                combat_phase = CombatPhase.weapon
            else:
                curr_actor.fighter.action.clear()
        #Show rolls
        if options.show_rolls: 
            if atk_margin is not None and def_margin is not None:
                rolls = curr_actor.name + ' had a margin of success of ' + str(def_margin) + ', while ' + enemy.name + ' had a margin of ' + str(atk_margin) + '. '
            elif atk_margin is not None:
                rolls = enemy.name + ' had a margin of success of ' + str(atk_margin) + '. '
            if rolls is not None: messages.insert(0, rolls)
        
        curr_actor = enemy
        
        if curr_actor.player:
            #See if curr_actor has AP for repeat
            if curr_actor.fighter.ap >= curr_actor.fighter.last_atk_ap:           
                combat_phase = CombatPhase.repeat
                game_state = GameStates.menu
            else:
                curr_actor.fighter.combat_choices.clear()



    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default
        

    return combat_phase, game_state, menu_dict, curr_actor

def phase_disengage(curr_actor, entities, command, logs, combat_phase, game_map) -> (int, dict, object):
    combat_menu_header = 'Use the directional movement keys to move. '
    curr_actor.fighter.disengage = True 
    fov_recompute = False
    messages = []
    log = logs[2]
    
    if curr_actor.fighter.disengage_option is not None or len(command) != 0:
        if curr_actor.fighter.disengage_option is not None:
            action = curr_actor.fighter.disengage_option
        else:
            action = command
        curr_actor.fighter.disengage_option = action

        opp_attackers = []
        #Check and see if anyone can hit with an attack
        for entity in entities:
            if not entity.fighter.end_turn and not curr_actor == entity and not curr_actor in entity.fighter.entities_opportunity_attacked:
                opp_attackers.append(entity)
        if len(opp_attackers) > 0:
            for entity in opp_attackers:
                for coords in entity.fighter.aoc:
                    x = coords[0]
                    y = coords[1]
                    if x == curr_actor.x and y == curr_actor.y:
                        wpn_ap = []
                        cs = []
                        for wpn in curr_actor.weapons:
                            for atk in wpn.attacks:
                                cs = curr_actor.determine_combat_stats(wpn, atk)
                                wpn_ap.append(cs.get('final ap'))
                        min_ap = min(wpn_ap)
                        if entity.fighter.ap >= min_ap:
                            entity.fighter.entities_opportunity_attacked.append(curr_actor)
                            #Give enemy a single attack
                            curr_actor = entity
                            combat_phase = CombatPhase.action
        else:
            #Set strafe to follow enemy, but record current setting to set back
            strafe = curr_actor.fighter.strafe
            curr_actor.fighter.strafe = 'enemy'
            #Move player
            fov_recompute = move_actor(game_map, curr_actor, entities, action, logs)
            if fov_recompute:
                #Subtract move AP and stamina
                curr_actor.fighter.mod_attribute('ap', -curr_actor.fighter.walk_ap)
                curr_actor.fighter.mod_attribute('stamina', -curr_actor.fighter.base_stam_cost)
            curr_actor.fighter.disengage = False
            curr_actor.fighter.disengage_option = None
            for entity in entities:
                if curr_actor in entity.fighter.entities_opportunity_attacked:
                    entity.fighter.entities_opportunity_attacked.remove(curr_actor)
            curr_actor.fighter.strafe = strafe
            combat_phase = CombatPhase.action


    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': True}

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    for message in messages:
        log.add_message(Message(message))

    return combat_phase, menu_dict, curr_actor

def phase_move(curr_actor, entities, command, logs, combat_phase, game_map) -> (int, dict, object):
    combat_menu_header = 'Use the directional movement keys to move. '
    avail_keys, _ = cells_to_keys(get_adjacent_cells(curr_actor, entities, game_map, False), curr_actor)
    avail_keys.append(41)
    _, d_offsets = cells_to_keys(get_adjacent_cells(curr_actor, entities, game_map), curr_actor)
    curr_actor.fighter.disengage = False
    fov_recompute = False
    messages = []
    log = logs[2]
    
    #Fill action with moves
    curr_actor.fighter.action = avail_keys
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': True}
    
    if curr_actor.fighter.disengage_option is not None or len(command) != 0:
        if curr_actor.fighter.disengage_option is not None:
            action = curr_actor.fighter.disengage_option
        else:
            action = command
        curr_actor.fighter.disengage_option = action            

        if action[0] != 'exit':
            action_offset = tuple(command_to_offset(action))
            
            if action_offset in d_offsets:
                curr_actor.fighter.disengage = True
                combat_phase = CombatPhase.disengage

            else:
                #Set strafe to follow enemy, but record current setting to set back
                strafe = curr_actor.fighter.strafe
                curr_actor.fighter.strafe = 'enemy'
                #Move player
                fov_recompute = move_actor(game_map, curr_actor, entities, action, logs)
                if fov_recompute:
                    #Subtract move AP and stamina
                    curr_actor.fighter.mod_attribute('ap', -curr_actor.fighter.walk_ap)
                    curr_actor.fighter.mod_attribute('stamina', -curr_actor.fighter.base_stam_cost)
                curr_actor.fighter.disengage = False
                curr_actor.fighter.disengage_option = None
                curr_actor.fighter.strafe = strafe

                combat_phase = CombatPhase.action


        
    
        if action[0] == 'exit':
            combat_phase = CombatPhase.action
            curr_actor.fighter.disengage_option = None
            menu_dict = dict()

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    for message in messages:
        log.add_message(Message(message))

    return combat_phase, menu_dict, curr_actor

def phase_maneuver(curr_actor, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    min_ap = curr_actor.get_min_ap()
    maneuvers = valid_maneuvers(curr_actor, curr_actor.fighter.curr_target)

    curr_actor.fighter.action = ['Return']

    if curr_actor.fighter.curr_target is not None:
        if curr_actor.fighter.ap >= curr_actor.fighter.walk_ap + min_ap + curr_actor.fighter.curr_target.get_min_ap():
            curr_actor.fighter.action.append('Leave opening and counter')
        if len(maneuvers) > 0:
            for m in maneuvers:
                curr_actor.fighter.action.append(m.name)


    combat_menu_header = 'Choose your maneuver:'
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}
    if len(command) != 0:
        for option in curr_actor.fighter.action:
            choice = command.get(option)
            if choice:
                menu_dict = dict()
                if choice == 'Return':
                    curr_actor.fighter.action.clear()
                    combat_phase = CombatPhase.action
                elif choice == 'Leave opening and counter':
                    combat_phase = CombatPhase.feint

                    if not hasattr(curr_actor.fighter, 'ai'):
                        curr_actor.fighter.combat_choices.append(option)
                        messages.append('You decide to feint.')

    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    return combat_phase, menu_dict

def phase_feint(curr_actor, command, logs, combat_phase) -> (int, dict, object):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    curr_actor.fighter.action = ['Return']

    #Choose the hit location to expose
    combat_menu_header = 'Which location do you want to expose?'
    curr_target = curr_actor.fighter.curr_target
    #Fill action list with locations
    curr_actor.fighter.action = curr_actor.fighter.get_locations()
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}
    
    if len(command) != 0:    
        for option in curr_actor.fighter.action:
            if command.get(option):
                menu_dict = dict()
                choice = command.get(option)
                if choice: 
                    if choice == 'Return':
                        curr_actor.fighter.action.clear()
                        combat_phase = CombatPhase.action
                    else:
                        curr_actor.fighter.combat_choices.append(option)
                        if not hasattr(curr_actor.fighter, 'ai'):
                            messages.append('You expose your ' + option + ' to ' + curr_target.name + ', hoping to tempt an attack. ')
                        curr_actor.fighter.feint = True
                        curr_actor.fighter.loc_dodge_mod[option] += curr_actor.fighter.best_combat_skill/3
                        curr_actor.fighter.loc_parry_mod[option] += curr_actor.fighter.best_combat_skill/3
                        #See target is fooled
                        for t in curr_actor.fighter.targets:
                            if curr_actor in t.fighter.targets:
                                roll = roll_dice(1,100)
                                result,_,_ = save_roll_con(curr_actor.fighter.best_combat_skill, 0, roll, t.fighter.best_combat_skill)
                                if result is 's':
                                    #Adjust perceived hit location modifiers
                                    t.fighter.adjust_loc_diffs(curr_actor, option, 50)


                        curr_actor = curr_target
                        combat_phase = CombatPhase.action
    
    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    return combat_phase, menu_dict, curr_actor

def phase_stance(curr_actor, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    min_ap = curr_actor.get_min_ap()

    curr_actor.fighter.action = ['Return']

    stance_widths = ('Open', 'Closed')
    stance_lengths = ('Long', 'Short')
    stance_heights = ('High', 'Low')
    stance_weights = ('Front', 'Neutral', 'Rear')

    for w in stance_widths:
        for l in stance_lengths:
            for h in stance_heights:
                for g in stance_weights:
                    curr_actor.fighter.action.append(w + ', ' + l + ', ' + h + ', ' + g)


    combat_menu_header = 'Choose your stance:'
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}
    if len(command) != 0:
        for option in curr_actor.fighter.action:
            choice = command.get(option)
            if choice:
                menu_dict = dict()
                combat_phase = CombatPhase.action

                if choice == 'Return':
                    curr_actor.fighter.action.clear()
                else:                    
                    curr_actor.fighter.change_stance(choice)
                
                    if not hasattr(curr_actor.fighter, 'ai'):
                        messages.append('You decide to use the ' + choice + ' stance.')

    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    return combat_phase, menu_dict    

def phase_guard(curr_actor, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]

    curr_actor.fighter.action = ['Return']

    available_guards = []

    for wpn in curr_actor.weapons:
        for guard in wpn.guards:
            for loc in guard.req_locs:
                if loc not in curr_actor.fighter.paralyzed_locs and loc not in curr_actor.fighter.immobilized_locs:
                    if guard not in available_guards:
                        available_guards.append(guard)
                        curr_actor.fighter.action.append(guard.name)
  
    combat_menu_header = 'Choose your guard:'
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}
    if len(command) != 0:
        for option in curr_actor.fighter.action:
            choice = command.get(option)
            if choice:
                menu_dict = dict()
                combat_phase = CombatPhase.action

                if choice == 'Return':
                    curr_actor.fighter.action.clear()
                else:
                    for guard in available_guards:
                        if guard.name == choice:                    
                            curr_actor.fighter.change_guard(guard)
                
                        if not hasattr(curr_actor.fighter, 'ai'):
                            messages.append('You decide to use the ' + choice + ' guard.')

    for message in messages:
        log.add_message(Message(message))

    if hasattr(curr_actor.fighter, 'ai'):
        menu_dict = dict()

    return combat_phase, menu_dict   

