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

def move_actor(game_map, entity, entities, command, logs):

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

    if command.get('move') and entity.fighter.can_act and entity.fighter.can_walk:
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
                entity.fighter.mod_attribute('stamina', -entity.fighter.base_stam_cost)
                if global_vars.debug: print(entity.name + ' ' + str(entity.x) + ' ' + str(entity.y))
                fov_recompute = True
                if entity.fighter.strafe == 'auto': entity.fighter.facing = facing_dict.get((x_mod,y_mod))
                elif entity.fighter.strafe == 'enemy' and entity.fighter.closest_fighter is not None: 
                    e_angle = entity_angle(entity.fighter.closest_fighter, entity, False)
                    e_angle = (e_angle // 45) * 45
                    entity.fighter.facing = angle_dict.get(e_angle)
                if not hasattr(entity.fighter, 'ai'): 
                    message = Message('You move ' + command.get('move'), 'black')
                    message_log.add_message(message)
            if blocker and not hasattr(entity.fighter, 'ai'):
                message = Message('You can\'t walk over '+blocker.name+'!', 'black')
                message_log.add_message(message)

        
    if command.get('spin'): 
        direction = command.get('spin')
        if direction == 'ccw': entity.fighter.facing -= 1
        else: entity.fighter.facing += 1
        fov_recompute = True
        #Setting boundaries
        if entity.fighter.facing == 8: entity.fighter.facing = 0
        elif entity.fighter.facing == -1: entity.fighter.facing = 7
        #Change facing
        
    if command.get('spin') or command.get('move'):
        entity.fighter.update_aoc_facing()
        entity.fighter.aoc = change_face(entity.fighter.aoc_facing, entity.x, entity.y, entity.fighter.reach)

    if command.get('prone'):
        message = Message('You drop prone', 'black')
        entity.fighter.gen_stance = FighterStance.prone
        fov_recompute = True
    
    if command.get('kneel'):
        message = Message('You kneel', 'black')
        entity.fighter.gen_stance = FighterStance.kneeling
        fov_recompute = True

    if command.get('stand') and entity.fighter.can_stand:
        message = Message('You stand up', 'black')
        entity.fighter.gen_stance = FighterStance.standing
        fov_recompute = True

    if fov_recompute == True:
        entity.fighter.mod_attribute('ap', -ap_cost)
        entity.fighter.mod_attribute('stamina', -entity.fighter.base_stam_cost)

    if hasattr(entity, 'fighter') and fov_recompute == True:
        if global_vars.debug_time: t0 = time.time()
        for e in entities:
            if e.fighter is not None:
                fov_radius = int(round(e.fighter.get_attribute('sit')/5))
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
                fov_radius = int(round(e.fighter.get_attribute('sit')/5))
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

def get_percieved_mods(active_entity, target, location) -> dict:
    idx = active_entity.fighter.targets.index(target)
    p_hit = active_entity.fighter.loc_hit_diff[idx].get(location)
    p_dodge = active_entity.fighter.loc_dodge_diff[idx].get(location)
    p_parry = active_entity.fighter.loc_parry_diff[idx].get(location)

    p_mods = {'p_hit':p_hit, 'p_dodge':p_dodge, 'p_parry': p_parry}

    return p_mods

def determine_valid_locs(active_entity, defender, attack) -> list:
    #Factors and counters:
    #Effective Reach: Distance and Height
    #Specific Limb
    #Relative positions
    
    er = active_entity.fighter.er * 1.3 #1.3 multiplier to account for the stretch from twisting
    er += attack.length

    #Init location pool
    locations = []
    i = 0
    for location in defender.fighter.locations:
        #Skip if no psi left
        if sum(location) > 0:
            locations.append(i)
        
        i += 1
        
    #Determine relative positioning
    #Start by determining defender facing relative to active_entity
    defender_angle = entity_angle(active_entity, defender)

    #Now determine active_entity angle to defender    
    active_entity_angle = entity_angle(defender, active_entity)

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

    #modify er based on active_entity angle
    if 45 < active_entity_angle < 90:
        er -= active_entity.fighter.er/2
    elif 270 < active_entity_angle < 315:
        er += active_entity.fighter.er/2
    #Remove all locations if defender flanks active_entity
    elif 90 < active_entity_angle < 270:
        locations = []
        return locations

    #Find distance between active_entity and defender. 
    distance = sqrt((defender.x - active_entity.x)**2 + (defender.y - active_entity.y)**2)
    #Convert squares into inches and round it off. 36" subtracted due to each combatant being in the middle of a square
    distance = int(round(distance*36))-36
    
    #Remove locations that are unreachable due to angle
    for location in locations:
        can_reach = location_angle(active_entity, defender, er, distance, attack, location)
        if not can_reach:
            if not location in loc_list:
                loc_list.append(location)
    locations = prune_list(locations, loc_list)

    #Remove locations losted as severed
    locations = prune_list(locations, defender.fighter.severed_locs)


    return locations

def location_angle(active_entity, target, er, distance, attack, location) -> bool:
    can_reach = False
    #Determine target height based on stance
    if target.fighter.gen_stance == FighterStance.prone:
        location_ht = target.fighter.location_ht[25]
    elif target.fighter.gen_stance in (FighterStance.kneeling, FighterStance.sitting):
        location_ht = target.fighter.location_ht[location] - target.fighter.location_ht[23]
    else:
        location_ht = target.fighter.location_ht[location]

    #Determine pivot point based on active_entity stance
    if active_entity.fighter.gen_stance == FighterStance.prone:
        pivot = active_entity.fighter.location_ht[25]
        if not attack.hand: er *= 1.2 #Legs average 1.2x longer than arms
    else:
        if attack.hand:
            pivot = active_entity.fighter.location_ht[3]
        else:
            pivot = active_entity.fighter.location_ht[17]
            er *= 1.2 #Legs average 1.2x longer than arms
        if active_entity.fighter.gen_stance in (FighterStance.kneeling, FighterStance.sitting):
            pivot -= active_entity.fighter.location_ht[23]

    #Find length of hypotenuse(len of reach to hit location)
    reach_req = sqrt(distance**2 + abs(location_ht-pivot)**2)
    if (er*.3) <= reach_req <= er: can_reach = True
    
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

def calc_final_mods(active_entity, target) -> dict:
    '''Goal is to bring together all the various hidden and percieved mods for both sides and create a single dict with all of them taken into account'''
    weapon = active_entity.fighter.combat_choices[0]
    attack = active_entity.fighter.combat_choices[1]
    location = active_entity.fighter.combat_choices[2]
    angle = active_entity.fighter.combat_choices[3]
    loc_name = active_entity.fighter.targets[0].fighter.name_location(location)
    
    def_mods = target.fighter.get_defense_modifiers(loc_name)
    cs = active_entity.determine_combat_stats(weapon, attack, location, angle)
    p_mods = get_percieved_mods(active_entity, target, loc_name)
    final_to_hit = cs.get('to hit') + def_mods.get('hit')
    p_hit = p_mods.get('p_hit') + final_to_hit
    dodge_mod = cs.get('dodge mod') + def_mods.get('dodge')
    p_dodge_mod = p_mods.get('p_dodge') + cs.get('dodge mod')
    parry_mod = cs.get('parry mod') + def_mods.get('parry')
    p_parry_mod = p_mods.get('p_parry') + cs.get('parry mod')
    

    total_ep = sum([cs.get('b psi'), cs.get('s psi'), cs.get('p psi'), cs.get('t psi')])

    if len(target.fighter.attacker_history) > 0:
        history_mod = calc_history_modifier(target, attack.name, location, angle)
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

def perform_attack(active_entity, entities, final_to_hit, target, cs, combat_phase) -> (list, int, object, bool):
    effects = []
    messages = []
    attack = active_entity.fighter.combat_choices[1]  
    final_ap = cs.get('final ap')
    missed =  False
    location = active_entity.fighter.combat_choices[2]
    dam_type = active_entity.fighter.combat_choices[1].damage_type[0]
    

    #Clear history if attacker changed
    if target.fighter.attacker is not active_entity:
        target.fighter.attacker = active_entity
        target.fighter.attacker_history.clear
        add_history(target)
    else:
        add_history(target)
    
    atk_result = make_attack_roll(final_to_hit, 1, location)
    active_entity.fighter.atk_result, active_entity.fighter.dam_result, active_entity.fighter.new_loc_result = atk_result[0], atk_result[1], atk_result[2]
    dam_mult = active_entity.fighter.dam_result
    
    
    #Subtract attack AP and stamina
    #Subtract AP from target if this is a disengagement attack or an attack due to a wait

    if target in active_entity.fighter.entities_opportunity_attacked:
        target.fighter.mod_attribute('ap', -final_ap)
    elif target.fighter.wait or target.fighter.feint:
        target.fighter.mod_attribute('ap', -final_ap)
    else:
        active_entity.fighter.mod_attribute('ap', -final_ap)

    active_entity.fighter.mod_attribute('stamina', -(attack.stamina*active_entity.fighter.base_stam_cost))
    

    #No damage
    if atk_result[1] == 0:
        missed = True
        if not hasattr(active_entity.fighter, 'ai'):
            messages.append('You missed. ')
            #Show rolls
            if options.show_rolls: 
                rolls = 'You rolled a ' + str(active_entity.fighter.atk_result) + ', missing. '
                messages.insert(0, rolls)
        else:
            messages.append(active_entity.name + ' missed you. ')
        
        if target.fighter.disengage:       
            combat_phase = CombatPhase.disengage
            active_entity = target
            game_state = GameStates.default
            menu_dict = dict()
        else:
            if active_entity.player:
                #See if active_entity has AP for repeat
                if active_entity.fighter.ap >= active_entity.fighter.last_atk_ap:           
                    combat_phase = CombatPhase.repeat
                    game_state = GameStates.menu
                else:
                    combat_phase = CombatPhase.action        
    else:
        #First, see if this is an attack from behind
        if active_entity in target.fighter.targets:
            combat_phase = CombatPhase.defend
        else:
            effects = damage_controller(target, active_entity, location, dam_type, dam_mult, active_entity.fighter.atk_result, cs, entities)
            combat_phase = CombatPhase.action
            active_entity.fighter.action.clear()

            if effects:
                for effect in effects:
                    messages.append(effect)
                if target.fighter is not None:
                    if target.fighter.disengage:       
                        combat_phase = CombatPhase.disengage
                        active_entity = target
                        game_state = GameStates.default
                        menu_dict = dict()
                    else:
                        if active_entity.player and len(active_entity.fighter.targets) > 0:
                            #See if active_entity has AP for repeat
                            #CC order: Weapon, Attack, Location idx, angle idx
                            if active_entity.fighter.ap >= active_entity.fighter.last_atk_ap:
                                locs = determine_valid_locs(active_entity, target, active_entity.fighter.combat_choices[1])
                                #Make sure location is still valid
                                if active_entity.fighter.combat_choices[2] in locs:           
                                    combat_phase = CombatPhase.repeat
                                    game_state = GameStates.menu
                            else:
                                active_entity.fighter.combat_choices.clear()


            if hasattr(active_entity.fighter, 'ai'):
                menu_dict = dict()
                game_state = GameStates.default

    

    active_entity.fighter.mods = cs

    if combat_phase == CombatPhase.defend:
        active_entity = target

    return messages, combat_phase, active_entity, missed

def perform_maneuver(active_entity, entities, final_to_hit, target, combat_phase, game_map) -> (list, int, object, bool):
    effects = []
    messages = []
    mnvr = active_entity.fighter.combat_choices[0]  
    #Find best skill
    valid_skills = []
    for s in mnvr.skill:
        valid_skills.append(getattr(active_entity.fighter,s))
    
    skill = max(valid_skills)
    final_ap = int(mnvr.base_ap * ((100/skill)**.2 ))
    missed =  True
    location = active_entity.fighter.combat_choices[1]
    
    

    #Clear history if attacker changed
    if target.fighter.attacker is not active_entity:
        target.fighter.attacker = active_entity
        target.fighter.attacker_history.clear


    roll = int(roll_dice(1, 100, True))
    if roll < final_to_hit: 
        missed = False
        active_entity.fighter.atk_result = roll

    
    
    #Subtract attack AP and stamina
    #Subtract AP from target if this is a disengagement attack or an attack due to a wait

    if target in active_entity.fighter.entities_opportunity_attacked:
        target.fighter.mod_attribute('ap', -final_ap)
    elif target.fighter.wait or target.fighter.feint:
        target.fighter.mod_attribute('ap', -final_ap)
    else:
        active_entity.fighter.mod_attribute('ap', -final_ap)

    active_entity.fighter.mod_attribute('stamina', -(mnvr.stamina*active_entity.fighter.base_stam_cost))
    

    #No damage
    if missed:
        if not hasattr(active_entity.fighter, 'ai'):
            messages.append('You missed. ')
            #Show rolls
            if options.show_rolls: 
                rolls = 'You rolled a ' + str(roll) + ', missing. '
                messages.insert(0, rolls)
        else:
            messages.append(active_entity.name + ' missed you. ')
        
        if target.fighter.disengage:       
            combat_phase = CombatPhase.disengage
            active_entity = target

        else:
            combat_phase = CombatPhase.action
        
    else:
        #First, see if this is an attack from behind
        if active_entity in target.fighter.targets:
            combat_phase = CombatPhase.grapple_defense
        else:
            effects = apply_maneuver(active_entity, target, type(mnvr), location, entities, game_map)
    
            if effects:
                combat_phase = CombatPhase.action
                active_entity.fighter.action.clear()
                for effect in effects:
                    messages.append(effect)
                if target.fighter is not None:
                    if target.fighter.disengage:       
                        combat_phase = CombatPhase.disengage
                        active_entity = target
                else:
                    combat_phase = CombatPhase.action



    if combat_phase == CombatPhase.grapple_defense:
        active_entity = target

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
    if len(history) > entity.fighter.get_attribute('mem')/10:
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
                entity.state = EntityState.unconscious
            if entity.fighter.max_vitae*.15 >= entity.fighter.vitae:
                messages.append(entity.name + ' has bled to death. ')
                entity.state = EntityState.dead
        #Handle suffocation
        if entity.fighter.suffocation:
            if entity.fighter.suffocation == 0:
                messages.append(entity.name + ' has suffocated an died. ')
                entity.state = EntityState.dead
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
            entity.state = EntityState.unconscious
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
        entity.fighter.combat_choices.clear()
        entity.fighter.action.clear()
        #Handle death
        if entity.state == EntityState.dead:
            handle_state_change(entity, entities, EntityState.dead)
        else:
            handle_mobility_change(entity)
        if not hasattr(entity.fighter, 'ai'): messages.append('A new round has begun. ')

    return messages

def handle_mobility_change(entity):
    #DIct containing direction to x,y AOC mapping for square directly in front of entity
    prone_aoc_dict = {0:(0,-1),1:(1,-1),2:(1,0),3:(1,1),4:(0,1),5:(-1,1),6:(-1,0),7:(-1,-1)}
    #Handle unconsciousness
    if entity.state in [EntityState.unconscious,EntityState.stunned,EntityState.shock]:
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

def damage_controller(target, active_entity, location, dam_type, dam_mult, roll, cs, entities, maneuver = False) -> list:
    '''Main damage function.'''
    if maneuver:
        atk_angle = 4
    else:
        atk_angle = angle_id(active_entity.fighter.combat_choices[3])
    
    rel_angle = entity_angle(target, active_entity)

    deflect, soak = calc_damage_soak(dam_type, target)

    messages = []

    new_locs = []
    dam_amt_list = []
    dam_type_list = []

    attack = target.fighter.attacker.fighter.combat_choices[1]
    
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

        if len(target.loc_armor[location]) != 0: #Handle armor if any
            new_locs, dam_amt_list, dam_type_list = armor_control(target, location, attack, dam_type, dam_amount)
            if len(new_locs) > 1: #Armor not penetrated, damage dispersed
                for loc in new_locs:
                    idx = new_locs.index(loc)
                    deflect, soak = calc_damage_soak(dam_type_list[idx], target)
                    msgs, _, _, _ = dam_loop(target, loc, layer, active_entity, atk_angle, rel_angle, dam_type_list[idx], dam_amt_list[idx], soak, deflect, roll)
                    messages.extend(msgs)

                    damage = 0 #Exit loop
            else:
                msgs, damage, location, layer = dam_loop(target, location, layer, active_entity, atk_angle, rel_angle, dam_type, dam_amount, soak, deflect, roll)
                messages.extend(msgs)
        else:
            msgs, damage, location, layer = dam_loop(target, location, layer, active_entity, atk_angle, rel_angle, dam_type, dam_amount, soak, deflect, roll)
            messages.extend(msgs)

        
    #Handle weapon removal for severed limbs
    hands_feet = (19,20,27,28)
    hf_severed_locs = target.fighter.severed_locs.intersection(hands_feet)
    if hf_severed_locs != 0:
        for loc in hf_severed_locs:
            if loc in target.fighter.equip_loc:
                target.fighter.equip_loc.pop(loc)



    #Handle chopping folk in two
    cleave_messages = cleave_checker(target)
    if len(cleave_messages) > 0:
        messages.extend(cleave_messages)
        target.state = EntityState.dead
    
    #Handle death and unconsciousness
    if target.state != EntityState.conscious:
        handle_state_change(target, entities, target.state)
        

    return messages

def dam_loop(target, location, layer, active_entity, atk_angle, rel_angle, dam_type, dam_amount, soak, deflect, roll):
    messages = []

    if target.fighter.locations[location][layer] == 0 and layer < 2:
        layer += 1

    if roll <= deflect[layer]: 
        l_names = ['skin','tissue','bone']
        messages.append(active_entity.name + ' hit ' + target.name +', but the blow deflected harmlessly off of ' + target.name + '\'s ' + l_names[layer])
        dam_amount = 0

    
    #Store previous damage level to avoid repeating damage effects
    prev_health = target.fighter.locations[location][layer]
    
    #determine how much damage is done to loc/layer and if pass-through occurs
    new_location, new_layer, new_damage = calc_layer_damage(target, location, layer, dam_type, dam_amount, soak, atk_angle, rel_angle)  

    messages.extend(get_injuries(target, prev_health, location, layer, dam_type))

    if new_location != location or new_layer != layer:
        damage = new_damage
        layer = new_layer
        location = new_location
    else:
        damage = 0
        location = None

    handle_mobility_change(target)

    return messages, damage, location, layer



def armor_control(target, location, attack, dam_type, dam_amount) -> (list, list, list):
    locations = [location]
    dam_amt_list = []
    dam_type_list = [] 
    ao_idx =  1 #Counter. Subtracted from len of loc_armor to determine ao to effect

    if global_vars.debug:
        print('Pre-armor damage is', str(round(dam_amount)), sep=' ')

    if ao_idx == 1:
        idx = len(target.loc_armor[location]) - ao_idx 
        ao = target.loc_armor[location][idx]

        if ao.rigidity == 'rigid':
            locs = []
            #Apply to primary and generate list of secondary locations
            locs, dam_amt_list, dam_type_list = armor_displace(target, location, attack, ao_idx, dam_type, dam_amount)

            if len(locs) > 0:
                for l in locs:
                    if l not in locations:
                        locations.append(l)
            ao_idx += 1
            dam_total = sum(dam_amt_list)
            if global_vars.debug:
                print('Post-displace damage total is', str(dam_total), sep=' ')



    while dam_total > 0 and ao_idx < len(target.loc_armor[location]):
        
        #Apply to locs

        for loc in locations:
            idx = locations.index(loc)
            dam_amt_list[idx], dam_type_list[idx] = armor_protect(target, loc, attack, ao_idx, dam_type_list[idx], dam_amt_list[idx])
            if global_vars.debug:
                ao = target.loc_armor[loc][len(target.loc_armor[location]) - ao_idx]
                print(ao.name, 'hit for', str(round(dam_amt_list[idx])), 'of', dam_type_list[idx], 'damage.', sep=' ')

        dam_total = sum(dam_amt_list)
        ao_idx += 1

    return locations, dam_amt_list, dam_type_list
             
def armor_displace(target, location, attack, ao_idx, dam_type, dam_amount) -> (list, list, list):
    idx = len(target.loc_armor[location]) - ao_idx 
    ao = target.loc_armor[location][idx]
    locs = [location]
    dam_amt_list = []
    dam_type_list = []
    deflect = False
    deflect_max = 0

    #Check deflect
    if dam_type == 'p':
        deflect_max = ao.p_deflect_max
        deflect_chance = ao.p_deflect
    elif dam_type == 's':
        deflect_max = ao.s_deflect_max
        deflect_chance = ao.s_deflect
    elif dam_type == 't':
        deflect_max = ao.t_deflect_max
        deflect_chance = ao.t_deflect
    elif dam_type == 'b':
        deflect_max = ao.b_deflect_max
        deflect_chance = ao.b_deflect

    if dam_amount < deflect_max:
        if roll_dice(1,100) < (deflect_chance * 100):
            deflect = True


    if not deflect:
        #Determine if attack penetrates
        armor_breach_psi = attack.main_area * ao.hits_sq_in
        if dam_amount > armor_breach_psi or dam_amount > ao.hits:
            dam_amount -= min([armor_breach_psi, ao.hits])
            ao.hits -= dam_amount
            dam_amt_list[0] = dam_amount
        #If no penetration, convert damage and apply to next area(s)
        elif dam_type == 'p':
            ao.hits -= dam_amount
            dam_type_list = ['b']
            dam_amt_list = [dam_amount *.3 * ao.b_soak]
        else:
            ao.hits -= dam_amount
            if dam_type == 't': dam_amount *= .1
            if len(ao.covered_locs) < 4:
                locs = ao.covered_locs
            else:
                while len(locs) < 3: 
                    i = 1
                    if location - 2 in ao.covered_locs and location - 2 not in locs:
                        locs.append(location - 2)
                    elif location + 2 in ao.covered_locs and location + 2 not in locs:
                        locs.append(location + 2)
                    elif location - 1 in ao.covered_locs and location - 1 not in locs:
                        locs.append(location - 1)
                    elif location + 1 in ao.covered_locs and location + 1 not in locs:
                        locs.append(location + 1)
                    else:
                        while i < len(ao.covered_locs):
                            if ao.covered_locs[i] != location:
                                locs.append(ao.covered_locs[i])
                            i += 1
                        print('Reached end of armor_displace without reaching while loop condition')#Should never be hit
                        break 
        
            for l in locs:
                dam_type_list.append('b')
                if l == locs[0]:
                    dam_amt_list.append(dam_amount *.5 * (1 - ao.b_soak))
                else:
                    dam_amt_list.append(dam_amount * .25 * (1 - ao.b_soak))        
            
    else: #Deflected
        dam_amount = 0 

    return locs, dam_amt_list, dam_type_list

def armor_protect(target, location, attack, ao_idx, dam_type, dam_amount) -> (int, int):
       
    #Check deflect
    #Damage armor
    #Check soak
    #Return remaining Damage

    idx = len(target.loc_armor[location]) - ao_idx 
    ao = target.loc_armor[location][idx]
    deflect_max = 0
    deflect = False
    penetrate = False

    #Check deflect
    if dam_type == 'p':
        deflect_max = ao.p_deflect_max
        deflect_chance = ao.p_deflect
    elif dam_type == 's':
        deflect_max = ao.s_deflect_max
        deflect_chance = ao.s_deflect
    elif dam_type == 't':
        deflect_max = ao.t_deflect_max
        deflect_chance = ao.t_deflect
    elif dam_type == 'b':
        deflect_max = ao.b_deflect_max
        deflect_chance = ao.b_deflect

    if dam_amount < deflect_max:
        if roll_dice(1,100) < (deflect_chance * 100):
            deflect = True



    if ao.rigidity == 'semi' and not deflect:
        #Determine if attack penetrates
        armor_breach_psi = attack.main_area * ao.hits_sq_in
        if dam_amount > armor_breach_psi or ao.hits:
            dam_amount -= min([armor_breach_psi, ao.hits])
            ao.hits -= dam_amount
        #If no penetration, convert damage and apply to next area(s)
        elif dam_type == 'b':
            ao.hits -= dam_amount * .5
            dam_amount = dam_amount * ao.b_soak
        elif dam_type == 't':
            ao.hits -= dam_amount
            dam_type = 'b'
            dam_amount = dam_amount *.1 * ao.b_soak
        else:
            ao.hits -= dam_amount
            dam_type = 'b'
            dam_amount = dam_amount *.7 * ao.b_soak

    elif not deflect:
        #Determine if attack penetrates
        armor_breach_psi = attack.main_area * ao.hits_sq_in
        if dam_type != 'b':
            if dam_amount > armor_breach_psi or ao.hits:
                dam_amount -= min([armor_breach_psi, ao.hits])
                ao.hits -= dam_amount
                penetrate = True
            else:
                ao.hits -= dam_amount
        #If no penetration, convert damage and apply to next area(s)
        if not penetrate:
            if dam_type == 'b':
                dam_amount = dam_amount * (1 - ao.b_soak)
            elif dam_type == 't':
                ao.hits -= dam_amount
                dam_type = 'b'
                dam_amount = dam_amount *.2 * (1 - ao.b_soak)
            else:
                ao.hits -= dam_amount
                dam_type = 'b'
                dam_amount = dam_amount *.8 * (1 - ao.b_soak)

    else: #Deflected
        dam_amount = 0

    return dam_amount, dam_type

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
        soak =  [.8 + ((((target.fighter.get_attribute('derm'))*.75) + ((target.fighter.get_attribute('fat'))*.25))/100 *.08),
                 .75 + ((((target.fighter.get_attribute('fat'))*.6) + ((target.fighter.get_attribute('str'))*.4))/100 *.08), 
                 .4 + (sqrt(target.fighter.get_attribute('flex'))/100)]
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
        soak =  [.5 + (sqrt(target.fighter.get_attribute('derm'))/50), 
                .5 + (sqrt(target.fighter.get_attribute('fat'))/50), 
                0]


    return deflect, soak

def calc_layer_damage(target, location, layer, dam_type, dam_amount, soak, atk_angle, entity_angle) -> (int, int, int):
    loc_hits = 0
    atk_angle = angle_id(atk_angle)

    #Calc final damage
    damage = int(round((1-soak[layer])*dam_amount))

    if dam_type == 'b':
        if target.fighter.locations[location][layer] < damage:
            if layer == 2:
                layer = 0
                location = find_next_location(location, atk_angle, entity_angle)
                damage -= target.fighter.locations[location][layer]
        
            target.fighter.locations[location][layer] = 0
        else:
            target.fighter.locations[location][layer] -= damage
            if layer < 2:
                layer += 1
    elif target.fighter.locations[location][layer] < damage:
        damage -= target.fighter.locations[location][layer]
        target.fighter.locations[location][layer] = 0
        if layer < 2:
            layer += 1
        else:
            layer = 0
            location = find_next_location(location, atk_angle, entity_angle)
    else:
        target.fighter.locations[location][layer] -= damage
        if layer == 2 and dam_type == 'p':
            location = find_next_location(location, atk_angle, entity_angle)
            layer = 0
        else:
            damage = 0
    
    #Handle severed locs
    if location is not None: 
        loc_hits = sum(target.fighter.locations[location])

    if loc_hits == 0:
        location = None


    return location, layer, damage

def get_injuries(target, prev_health, location, layer, dam_type) -> list:
    '''Determines damage level and calls filter_injuries and apply_injuries to add injuries'''
    messages = set()
    inj_messages = set()
    sev = 0
    max_sev = 0
    #Determine damage effect level
    #Find % damage
    dam_percent = 0

    prev_percent = (prev_health/target.fighter.max_locations[location][layer])
    layer_health = target.fighter.locations[location][layer]

    if layer_health != 0: 
        dam_percent = (target.fighter.locations[location][layer]/target.fighter.max_locations[location][layer])

    dam_thresh = find_dam_threshold(dam_percent)
    prev_thresh = find_dam_threshold(prev_percent)

    new_thresh = dam_thresh - prev_thresh

    if new_thresh > 0:
        for i in range(new_thresh + 1):
            valid_injuries = filter_injuries(Injury, location, dam_type, dam_thresh, layer, target)
            #Max_sev used to clear all lower injury effect messages and only use the max damage one
            if len(valid_injuries) > 0:
                inj_messages, sev = apply_injuries(valid_injuries, location, target, dam_type)
                if sev >= max_sev:
                    messages.clear()
                    messages.update(inj_messages)
                    max_sev = sev
            i += 1

    if len(messages) == 0:
        if target.player:
            messages.add(target.fighter.attacker.name + ' hits you in the ' + target.fighter.name_location(location))
        else:
            messages.add('You hit ' + target.name + ' in the ' + target.fighter.name_location(location))

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

def apply_injury_effects(target, injury, location, remove = False) -> list:
    '''Generic injury effect applier. remove bool reverses any reversible or non-temp effects'''
    messages = []

    
    if not remove:
        messages.append(injury.description)

    if injury.pain_check and not remove:
        check = save_roll_un(target.fighter.get_attribute('will'), 0)
        if 'f' in check:
            target.state = EntityState.stunned
            messages.append(target.name + ' is overcome by the pain from the blow, and is stunned for a short while.')

        elif 'cf' in check:
            target.fighter.gen_stance = FighterStance.prone
            target.state = EntityState.unconscious
            messages.append(target.name + ' faints due to the intense pain of the wound.')

    if injury.shock_check and not remove:
        check = save_roll_un(target.fighter.get_attribute('shock'), 0)
        if 'f' in check:
            target.state = EntityState.shock
            messages.append(target.name + ' is experiencing the early effects of shock, and is disoriented and unstable.')
            target.fighter.mod_attribute('clarity',-20)

        elif 'cf' in check:
            target.fighter.gen_stance = FighterStance.prone
            target.state = EntityState.unconscious
            target.fighter.bleed.append([100,100])
            messages.append(target.name + ' rapidly goes into shock and collapses.')

    if injury.balance_check and not remove:
        check = save_roll_un(target.fighter.get_attribute('shock'), 0)
        if 'f' in check or 'cf' in check:
            target.fighter.gen_stance = FighterStance.prone
            messages.append(target.name + ' is toppled by the blow.')

    if injury.clarity_reduction is not None:
        if remove:
            target.fighter.mod_attribute('clarity',injury.clarity_reduction)
        else:
            target.fighter.mod_attribute('clarity',-injury.clarity_reduction)

    if injury.bleed_amount is not None and not remove:
        target.fighter.bleed.append([injury.bleed_amount, injury.bleed_duration])

    if injury.attr_name is not None:
        for a in injury.attr_name:
            idx = injury.attr_name.index(a)
            if remove:
                attr_amt = target.fighter.get_attribute(a)
                max_attr_amt = target.fighter.get_attribute(a, 'max_val')
                if attr_amt + abs(injury.attr_amount[idx]) > max_attr_amt:
                    amount = max_attr_amt - attr_amt
                else:
                    amount = -injury.attr_amount[idx]
                target.fighter.mod_attribute(a, amount)
            else:
                inj_attr_amount = attr_dam_limiter(a, injury, target)
                target.fighter.mod_attribute(a, inj_attr_amount)
               

    if injury.loc_reduction is not None and not remove:
        target.fighter.locations[location][injury.layer] -= injury.loc_reduction

    if injury.loc_max is not None and not remove:
        target.fighter.max_locations[location][injury.layer] = target.fighter.max_locations[location][injury.layer]*injury.loc_max
    
    if injury.severed_locs is not None and not remove:
        target.fighter.severed_locs.update(injury.severed_locs)

    if injury.paralyzed_locs is not None and not remove:
        target.fighter.paralyzed_locs.update(injury.paralyzed_locs)

    if injury.temp_phys_mod is not None and not remove:
        target.fighter.temp_physical_mod -= injury.temp_phys_mod

    if injury.suffocation is not None and not remove:
        if target.fighter.suffocation is not None and target.fighter.suffocation > injury.suffocation:
           target.fighter.suffocation = injury.suffocation
    
    if injury.stam_drain is not None:
        if remove:
            target.fighter.mod_attribute('stam_drain',-injury.stam_drain)
        else:
            target.fighter.mod_attribute('stam_drain',injury.stam_drain)
    
    if injury.stam_regin is not None:
        if remove:
            target.fighter.mod_attribute('stamr',target.fighter.max_stamr * injury.stam_regin)
        else:
            target.fighter.mod_attribute('stamr',-(target.fighter.max_stamr * injury.stam_regin))

    if injury.pain_mv_mod is not None:
        if remove:
            target.fighter.pain_mod_mov -= injury.pain_mv_mod
        else:
            target.fighter.pain_mod_mov += injury.pain_mv_mod

    if injury.diseases is not None and not remove:
        target.fighter.diseases.update(injury.diseases)

    if injury.atk_mod_r is not None:
        if remove:
            target.fighter.atk_mod_r += -injury.atk_mod_r
        else:
            target.fighter.atk_mod_r += injury.atk_mod_r
    
    if injury.atk_mod_l is not None:
        if remove:
            target.fighter.atk_mod_l += -injury.atk_mod_l
        else:
            target.fighter.atk_mod_l += injury.atk_mod_l
    
    if injury.mv_mod:
        if remove:
            target.fighter.mod_attribute('mv',target.fighter.max_mv * injury.mv_mod)
        else:
            target.fighter.mod_attribute('mv',-(target.fighter.max_mv * injury.mv_mod))

    if injury.gen_stance is not None and not remove:
        target.fighter.gen_stance = injury.gen_stance
        if target.fighter.gen_stance == FighterStance.prone:
            messages.append(target.name + ' is knocked prone. ')
        elif target.fighter.gen_stance == FighterStance.kneeling:
            messages.append(target.name + ' is forced to their knees. ')

    if injury.state is not None and not remove:
        target.fighter.state = injury.state

    return messages

def attr_dam_limiter(attr, injury, entity) -> int:
    
    curr_attr_dam = 0

    arm_attr_limits = {'pwr': (entity.fighter.get_attribute('pwr','max_val')*.15), 'ss': (entity.fighter.get_attribute('ss','max_val')*.15), 'touch': (entity.fighter.get_attribute('touch','max_val')*.3)}
    leg_attr_limits = {'pwr': (entity.fighter.get_attribute('pwr','max_val')*.25), 'ss': (entity.fighter.get_attribute('ss','max_val')*.25), 'touch': (entity.fighter.get_attribute('touch','max_val')*.1)}

    inj_limb = inj_limb_finder(injury)

    if inj_limb == None: 
        a_idx = injury.attr_name.index(attr)
        amount = injury.attr_amount[a_idx]
        return amount

    if inj_limb in ['ra','la']:
        limits = arm_attr_limits
    else:
        limits = leg_attr_limits

    for inj in entity.fighter.injuries:
        limb = inj_limb_finder(inj)
        if limb == inj_limb:
            if inj.attr_name is not None:
                for a in inj.attr_name:
                    if a == attr:
                        a_idx = inj.attr_name.index(a)
                        curr_attr_dam += inj.attr_amount[a_idx]

    for a in injury.attr_name:
        if a == attr:
            a_idx = injury.attr_name.index(a)
            amount = injury.attr_amount[a_idx]
    if limits.get(attr) is not None:
        if abs(curr_attr_dam) >= limits.get(attr):
            amount = 0
        elif abs(amount + curr_attr_dam) >= limits.get(attr):
            amount = limits.get(attr) - abs(curr_attr_dam)
            amount *= -1

    return amount
                
def inj_limb_finder(injury) -> str:
    r_arm_locs = [3,7,11,15,19]
    l_arm_locs = [4,8,12,16,20]
    r_leg_locs = [17,21,23,25,27]
    l_leg_locs = [18,22,24,26,28]

    limb = None

    if injury.location in r_arm_locs:
        limb = 'ra'
    elif injury.location in l_arm_locs:
        limb = 'la'
    elif injury.location in l_leg_locs:
        limb = 'll'
    elif injury.location in r_leg_locs:
        limb = 'rl'
    
    return limb

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

def valid_maneuvers(active_entity, target) -> list:
    all_maneuvers = {}
    invalid_maneuvers = set()

    #Find distance between active_entity and defender. 
    distance = sqrt((target.x - active_entity.x)**2 + (target.y - active_entity.y)**2)
    #Convert squares into inches and round it off. 36" subtracted due to each combatant being in the middle of a square
    distance = int(round(distance*36))-36
        
    #Below complexity is due to objects being different, but being functional duplicates
    for loc in [19,20,27,28]:
        w = active_entity.fighter.equip_loc.get(loc)
        if w == None: continue
        if not w.weapon: continue

        for mnvr in w.maneuvers:
            if mnvr.name not in all_maneuvers:
                all_maneuvers[mnvr.name] = mnvr

    mnvr_set = set(all_maneuvers.values())

    for mnvr in mnvr_set:

        #Find valid locations based on angle/dist
        reachable_locs = set(determine_valid_locs(active_entity, target, mnvr))
        #Remove any maneuvers that cannot reach a valid target
        if reachable_locs.isdisjoint(mnvr.locs_allowed):
            invalid_maneuvers.add(mnvr)
            continue
        
        #Check prereqs and remove maneuvers that do not meet them
        if len(mnvr.prereq) != 0:
            valid = False
            for p in mnvr.prereq:
                for a in active_entity.fighter.maneuvers:
                    if type(p) is type(a) and a.active_entity is active_entity:
                        valid = True
            if not valid: 
                invalid_maneuvers.add(mnvr)
                continue

        #Check if active_entity has ap
        skill_ratings = []
        for s in mnvr.skill:
            skill_ratings.append(getattr(active_entity.fighter, s))
        skill_rating = max(skill_ratings)
        
        final_ap = int(mnvr.base_ap * ((100/skill_rating)**.2 ))
        
        if active_entity.fighter.ap < final_ap:
            invalid_maneuvers.add(mnvr)
            continue  
        
        #See if both hands are free if it's a two handed maneuver
        if mnvr.hand:
            if mnvr.hands == 2:
                r_w = active_entity.fighter.equip_loc.get(19)
                l_w = active_entity.fighter.equip_loc.get(20)
                if not all([r_w is not None, l_w is not None]):
                    invalid_maneuvers.add(mnvr)
                    continue 
                if not all([r_w.weapon,l_w.weapon]):
                    invalid_maneuvers.add(mnvr)
                    continue 
                elif mnvr not in r_w.maneuvers and mnvr not in l_w.maneuvers:
                    invalid_maneuvers.add(mnvr)
                    continue 

        #See if active_entity stance is valid for the maneuver
        if active_entity.fighter.gen_stance not in mnvr.agg_stance_pre:
            invalid_maneuvers.add(mnvr)
            continue

        #See if target stance is valid for the maneuver
        if target.fighter.gen_stance not in mnvr.target_stance_pre:
            invalid_maneuvers.add(mnvr)
            continue

        if distance > active_entity.fighter.er * mnvr.max_dist:
            invalid_maneuvers.add(mnvr)
            continue

        if distance < active_entity.fighter.er * mnvr.min_dist:
            invalid_maneuvers.add(mnvr)
            continue

    mnvr_set = mnvr_set.difference(invalid_maneuvers)

    #Convert to list and sort the list of objects alphabetically using the name attribute     
    mnvr_set = list(mnvr_set)
    mnvr_set.sort(key=lambda x: x.name)


    return mnvr_set

def attack_filter(active_entity, target, weapon, attack) -> bool:
    imm_locs = active_entity.fighter.immobilized_locs | active_entity.fighter.paralyzed_locs | active_entity.fighter.severed_locs
    cs = active_entity.determine_combat_stats(weapon, attack)
    valid = True
    r_w = active_entity.fighter.equip_loc.get(19)
    l_w = active_entity.fighter.equip_loc.get(20)

    if attack.hand:
        if attack.hands == 2:
            if r_w == None or l_w == None:
                valid = False
            if not all([r_w.weapon,l_w.weapon]):
                valid = False
            if attack not in r_w.attacks and attack not in l_w.attacks:
                valid = False
            if not global_vars.arm_locs.isdisjoint(imm_locs):
                valid = False
        elif r_w is not None and attack in r_w.attacks: #R Hand
            if not global_vars.r_arm_locs.isdisjoint(imm_locs):
                valid = False        
        else: #L Hand
            if not global_vars.l_arm_locs.isdisjoint(imm_locs):
                valid = False
    else:
        if not global_vars.leg_locs.isdisjoint(imm_locs):
            valid = False
    
    valid_locs = determine_valid_locs(active_entity, target, attack)
    if len(valid_locs) == 0:
        valid = False
    
    if active_entity.fighter.ap < cs.get('final ap'):
        if len(active_entity.fighter.entities_opportunity_attacked) == 0:
            valid = False

    return valid

def num_valid_attacks(active_entity) -> int:  
    num_valid = 0
    valid = False
    for loc in [19,20,27,28]:
        if active_entity.fighter.equip_loc.get(loc) is None: continue
        weapon = active_entity.fighter.equip_loc.get(loc)
        if weapon.weapon:
            for attack in weapon.attacks:
                valid = attack_filter(active_entity, active_entity.fighter.curr_target, weapon, attack)
                if valid: num_valid += 1
    
    return num_valid

def apply_maneuver(active_entity, target, maneuver, location, entities, game_map) -> list:
    loc_name = target.fighter.name_location(location)
    mnvr = maneuver(active_entity, target, loc_name)
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
    

    #If continuous, apply to list in fighter
    if mnvr.continuous:
        mnvr.aggressor = active_entity
        mnvr.target = target
        active_entity.fighter.maneuvers.append(mnvr)
        target.fighter.maneuvers.append(mnvr)


    #Apply any clarity reductions before making balance checks
    if mnvr.clarity_reduction is not None:
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
            damage_list.append(i * active_entity.fighter.ep)
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
        roll = roll = roll_dice(1,99) - 1
        cs = dict()
        messages.extend(damage_controller(target, active_entity, loc_list[idx], dam_types_list[idx], d, roll, cs, entities, True))
        idx += 1

    #Remove the prereq if one exists
    if len(mnvr.prereq) > 0:
        for p in mnvr.prereq:
                for a in target.fighter.maneuvers:
                    if type(p) is type(a) and a.active_entity is active_entity and a.loc_idx == location:
                        remove_maneuver(target, active_entity, a)
                for a in active_entity.fighter.maneuvers:
                    if type(p) is type(a) and a.active_entity is active_entity and a.loc_idx == location:
                        active_entity.fighter.maneuvers.remove(a)
                        continue
    
    #Immobilize locations
    for l in mnvr.immobilized_locs:
        target.fighter.immobilized_locs.add(l)
    for l in mnvr.agg_immob_locs: 
        active_entity.fighter.immobilized_locs.add(l)

    #Perform pain check and immobilize for round if failed
    if mnvr.pain_check:
        check = save_roll_un(target.fighter.get_attribute('will'), 0)
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
    if mnvr.stance is not None:
        target.fighter.gen_stance = mnvr.gen_stance
        if target.fighter.gen_stance == FighterStance.prone:
            messages.append(target.name + ' is knocked prone. ')
        elif target.fighter.gen_stance == FighterStance.kneeling:
            messages.append(target.name + ' is forced to their knees. ')

    if mnvr.state is not None:
        target.fighter.state = mnvr.state

    #Apply active_entity stance (succeed)
    if mnvr.agg_suc_stance is not None:
        active_entity.fighter.gen_stance = mnvr.agg_suc_stance

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

        mobility_changed = relo_actor(game_map, target, active_entity, entities, direction, 2)    

    if not mobility_changed:
        handle_mobility_change(target)
    
    return messages  

def remove_maneuver(target, active_entity, maneuver):
    mnvr = maneuver
    
    #Apply any clarity reductions before making balance checks
    if mnvr.clarity_reduction is not None:
        target.fighter.mod_attribute('clarity', mnvr.clarity_reduction)

    #Mobilize locations
    for l in mnvr.immobilized_locs:
        #Remove loc from list
        target.fighter.immobilized_locs.remove(l)
        for m in target.fighter.maneuvers:
            if m is not mnvr:
                if l in m:
                    #Re-add loc if included in another maneuver
                    target.fighter.immobilized_locs.add(l)
        
    for l in mnvr.agg_immob_locs: 
        active_entity.fighter.immobilized_locs.remove(l)
        for m in active_entity.fighter.maneuvers:
            if m is not mnvr:
                if l in m:
                    active_entity.fighter.immobilized_locs.add(l)

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
    
    #Remove maneuver
    active_entity.fighter.maneuvers.remove(mnvr)
    target.fighter.maneuvers.remove(mnvr)

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

def init_combat(active_entity, order, command) -> (dict, int, int, list):
    game_state = GameStates.menu
    combat_phase = CombatPhase.action
    messages = []
    menu_dict = dict()
    menu_desc = {}


    if command.get('Wait'):
        if active_entity.player:
            messages.append('You decide to wait for your opponents to act')
        else:
            messages.append(active_entity.name + ' waits for you to act')
        active_entity.fighter.wait = True
        combat_phase = CombatPhase.action
        game_state = GameStates.default
    elif command.get('Maneuver'):
        if active_entity.player:
            messages.append('You decide to attempt a special maneuver')
        combat_phase = CombatPhase.maneuver
    elif command.get('Change Stance'):
        if active_entity.player:
            messages.append('You decide to change your stance')
        combat_phase = CombatPhase.stance
    elif command.get('Change Guard'):
        if active_entity.player:
            messages.append('You decide to change your guard')
        combat_phase = CombatPhase.guard                     
    elif command.get('Attack'):
        if active_entity.player:
            messages.append('You decide to attack')
        combat_phase = CombatPhase.weapon
    elif command.get('Move'):
        if active_entity.player:
            messages.append('You decide to move.')
        else:
            messages.append(active_entity.name + ' moves. ')
        combat_phase = CombatPhase.move
    elif command.get('End Turn'):
        if active_entity.player:
            messages.append('You decide to end your turn')
        else:
            if active_entity.fighter.male: pro = 'his'
            else: pro = 'her'
            messages.append(active_entity.name + ' ends ' + pro + ' turn')
        active_entity.fighter.end_turn = True
        active_entity.fighter.action.clear()
        combat_phase = CombatPhase.action
        game_state = GameStates.default 

    elif active_entity.fighter.can_act:
        #CHeck to see if entity can attack
        valid_attacks = num_valid_attacks(active_entity)
        valid_mnvrs = valid_maneuvers(active_entity, active_entity.fighter.curr_target)
        active_entity.fighter.action.clear()
        if valid_attacks > 0:
            active_entity.fighter.action.append('Attack')
            menu_desc['Attack'] = 'Attack an enemy with a weapon. '
        if active_entity.fighter.ap >= active_entity.fighter.walk_ap and active_entity.fighter.can_walk:
            active_entity.fighter.action.append('Move')
            menu_desc['Move'] = 'Change position. \nIf you move out of an enemy\'s zone of control, this will provoke a free attack, with the enemy\'s AP cost being deducted from your AP. \nIf the enemy hits, you will have failed to disengage. '
        if len(valid_mnvrs) > 0:
            active_entity.fighter.action.append('Maneuver')
            menu_desc['Maneuver'] = 'Perform a combat maneuver, such as a grappling technique or a feint. '
        if len(order) > 1 and len(active_entity.fighter.action) >= 1: 
            active_entity.fighter.action.append('Wait')
            menu_desc['Wait'] = 'Wait for the next enemy to act, taking your turn after they complete thier\'s. '
            active_entity.fighter.action.append('Change Stance')
            menu_desc['Change Stance'] = 'Change your fighting stance, which will change the offensive and defensive bonuses received. '
            active_entity.fighter.action.append('Change Guard')
            menu_desc['Change Guard'] = 'Change your guard, which will change the defensive bonuses received and automatic blocking locations. '
        if len(active_entity.fighter.action) >= 1:
            active_entity.fighter.action.append('End Turn')
            menu_desc['End Turn'] = 'End your turn. AP does not carry forward between turns, but stamina and vitae reginerate between turns. '
            game_state = GameStates.menu
        else:
            active_entity.fighter.end_turn = True
            combat_phase = CombatPhase.action
            game_state = GameStates.default
            return menu_dict, combat_phase, game_state, order, messages

        combat_menu_header = 'What do you wish to do?'

        menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False, 'desc': menu_desc}                       

    if hasattr(active_entity.fighter, 'ai'):
        game_state = GameStates.default


    return menu_dict, combat_phase, game_state, order, messages

def change_actor(order, entities, active_entity, combat_phase, game_state, logs) -> (int, int, list, object):
    messages = []
    log = logs[2]
    round_end = False
    
    

    #Exit without making changes if in defend phase
    if combat_phase in [CombatPhase.defend, CombatPhase.grapple_defense]:
        return combat_phase, game_state, order, active_entity

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
                if entity.fighter is not None and entity is not active_entity:
                    targets += 1
            if targets == 0:
                #Below exits combat when all enemies are dispatched
                combat_phase = CombatPhase.explore
                game_state = GameStates.default
                return combat_phase, game_state, order, active_entity

        if global_vars.debug and len(order) != len(global_vars.turn_order) : print('order length: ' + str(len(order)) + ', global order length: ' + str(len(global_vars.turn_order)))
        
        if remaining_fighters == 0: 
            round_end = True
        else:
            order = list(global_vars.turn_order)
            if len(order) > 1:
                if order[0].fighter.wait: 
                    if not order[0].fighter.curr_target.fighter.acted: 
                        active_entity = order[0].fighter.curr_target
                    else: 
                        order[0].fighter.wait = False
                        order[0].fighter.curr_target.fighter.acted = False
                elif order[0] in active_entity.fighter.entities_opportunity_attacked:
                    pass
                elif order[0].fighter.feint:
                    if not order[0].fighter.curr_target.fighter.acted: 
                        active_entity = order[0].fighter.curr_target
                    else:
                        order[0].fighter.feint = False
                        order[0].fighter.curr_target.fighter.acted = False
                        #Remove fient dodge/parry mods
                        idx = len(order[0].fighter.combat_choices)
                        option = order[0].fighter.combat_choices[(idx - 1)]
                        order[0].fighter.loc_dodge_mod[option] -= order[0].fighter.best_combat_skill.rating/3
                        order[0].fighter.loc_parry_mod[option] -= order[0].fighter.best_combat_skill.rating/3
                        for t in order[0].fighter.targets:
                            if order[0] in t.fighter.targets:
                                #Adjust perceived hit location modifiers
                                t.fighter.adjust_loc_diffs(order[0], option, 0)
                        order[0].fighter.combat_choices.clear()

                elif combat_phase != CombatPhase.defend:
                    active_entity = order[0]
            else:
                active_entity = order[0]

    if round_end:
        log.add_message(Message('The round has ended. '))
        combat_phase = CombatPhase.init
        global_vars.round_num  += 1
        order = entities
        global_vars.turn_order = list(order)
        for entity in order:
            messages = handle_persistant_effects(entity, entities)

    for message in messages:
        log.add_message(Message(message))
        
            
    return combat_phase, game_state, order, active_entity






