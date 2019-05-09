import tcod as libtcodpy
import time
import global_vars
from math import sqrt
from enums import CombatPhase, MenuTypes, EntityState, GameStates, FighterStance
from entity import get_blocking_entities_at_location
from fov_aoc import modify_fov, change_face, aoc_check
from game_messages import Message
from utilities import inch_conv, gen_status_panel, roll_dice, prune_list, entity_angle, save_roll_con, save_roll_un

def detect_enemies(entities) -> int:
    combat_phase = CombatPhase.explore
    for entity in entities:
        if entity.fighter:
            opponents = entities.copy()
            opponents.remove(entity)
            for opponent in opponents:
                if (opponent.x, opponent.y) in entity.fighter.fov_visible:
                    combat_phase = CombatPhase.init
    return combat_phase

def move_actor(game_map, entity, entities, players, command, logs) -> bool:

    fov_recompute = False
    #Dict containing facing direction based on x,y offset
    facing_dict = {(-1,0):6,(-1,1):5,(-1,-1):7,(1,-1):1,(1,1):3,(1,0):2,(0,1):4,(0,-1):0}
    
    #Name message logs
    message_log = logs[2]
    
    if command[0] == 'move':
        direction = []
        direction.extend(command[1])
        y_mod = 0
        x_mod = 0
        for xy in direction:
            if xy == 'n':
                y_mod = -1
            if xy == 's':
                y_mod = 1
            if xy == 'w':
                x_mod = -1
            if xy == 'e':
                x_mod = 1
        fx, fy =entity.x + x_mod, entity.y + y_mod
        #Boundary and blocker checking
        blocker = get_blocking_entities_at_location(entities, fx, fy)
        if (game_map.width -1 >= fx and game_map.height -1 >= fy):
            if (game_map.walkable[fx, fy] and not (fx < 0  or fy < 0) 
                and blocker is None):
                entity.mod_attribute('x', x_mod)
                entity.mod_attribute('y', y_mod)
                fov_recompute = True
                entity.fighter.facing = facing_dict.get((x_mod,y_mod))
                message = Message('You move ' + command[1], 'black')
                message_log.add_message(message)
            if blocker:
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

            

    if hasattr(entity, 'fighter') and fov_recompute == True:
        t0 = time.time()
        
        fov_radius = int(round(entity.fighter.sit/5))
        game_map.compute_fov(entity.x, entity.y, fov_radius, True, libtcodpy.FOV_SHADOW)
        modify_fov(entity, game_map)

        t1 = time.time()
        total_time = t1 - t0
        print(total_time)



    targets = aoc_check(entities, entity)
    if targets is not None:
        update_targets(entity, targets)
    return fov_recompute #Used to id that entity moved for ap reduction in combat

def turn_order(entities) -> list:
    #Sort entities by highest init and make list of sorted entities
    order = sorted(entities, key=lambda entities: (entities.fighter.init + roll_dice(1,100)), reverse = True)

    return(order)

def update_targets(entity, targets) -> None:
    """Purpose is to remove or change target list when aoc changes"""
    if set(entity.fighter.targets) != set(targets):
        entity.fighter.targets = targets
        if entity.fighter.curr_target not in set(entity.fighter.targets):
            entity.fighter.curr_target = None

def determine_valid_locs(attacker, defender, attack) -> list:
    #Factors and counters:
    #Effective Reach: Distance and Height
    #Specific Limb
    #Relative positions
    
    er = attacker.fighter.er * 1.3 #1.3 multiplier to account for the stretch from twisting
    if hasattr(attack, 'length'):
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

    #List for holding locations to prune
    loc_list = []

    #Remove locations based on defender angle
    if 45 < defender_angle < 135:
        #Locations to remove
        loc_list = [3,5,7,9,11,13,15,17,19,21,23,25,27]
    elif 225 < defender_angle < 315:
        #Locations to remove
        loc_list = [4,6,8,10,12,14,16,18,20,22,24,26,28]

    #modify er based on attacker angle
    if 45 < attacker_angle < 90:
        er -= attacker.fighter.er/2
    elif 270 < attacker_angle < 315:
        er += attacker.fighter.er/2
    #Remove all locations if defender flanks attacker
    elif 90 < attacker_angle < 270:
        locations = []
        return locations

    #Find distance between attacker and defender
    distance = sqrt((defender.x - attacker.x)**2 + (defender.y - attacker.y)**2)
    #Convert squares into inches and round it off
    distance = int(round(distance*36))
    
    #Remove locations that are unreachable due to angle
    for location in locations:
        can_reach = location_angle(attacker, defender, er, distance, attack, location)
        if not can_reach:
            #i = locations.index(location)
            if not location in loc_list:
                loc_list.append(location)
    locations = prune_list(locations, loc_list)


    return locations

def location_angle(attacker, defender, er, distance, attack, location) -> bool:
    can_reach = False
    location_ht = defender.fighter.location_ht[location]
    if attack.hand:
        pivot = attacker.fighter.location_ht[3]
    else:
        pivot = attacker.fighter.location_ht[17]
        er *= 1.2 #Legs average 1.2x longer than arms

    #Find length of hypotenuse(len of reach to hit location)
    reach_req = sqrt(distance**2 + abs(location_ht-pivot)**2)
    if reach_req <= er: can_reach = True
    
    return can_reach

def determine_valid_angles(location) -> list:
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
    return result

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
        for n in curr_attack:
            for x in i:
                if n == x:
                    element_repeat += 1
    mod += (repeats * 15) + (element_repeat * 3)
    return mod

def perform_attack(entity, entities, final_to_hit, curr_target, cs, combat_phase) -> (list, int):
    effects = []
    messages = []
    loc_list = curr_target.fighter.get_locations() 
    attack = entity.fighter.combat_choices[1]  
    final_ap = cs.get('final ap')
    location = entity.fighter.combat_choices[2]

    #Clear history if attacker changed
    if curr_target.fighter.attacker is not entity:
        curr_target.fighter.attacker = entity
        curr_target.fighter.attacker_history.clear
        add_history(curr_target)
    else:
        add_history(curr_target)
    
    atk_result  = make_attack_roll(final_to_hit, 1, entity.fighter.combat_choices[2])
    roll, dam_mult, new_loc = atk_result[0], atk_result[1], atk_result[2]

    #Add result to entity
    if hasattr(entity.fighter, 'ai'):
        entity.fighter.ai.atk_result = atk_result
    
    
    #Subtract attack AP and stamina
    entity.fighter.mod_attribute('ap', -final_ap)
    entity.fighter.mod_attribute('stamina', -(attack.stamina*entity.fighter.base_stam_cost))
    
    #No damage
    if atk_result[1] == 0:
        if not hasattr(entity.fighter, 'ai'):
            messages.append('You missed. ')
        else:
            messages.append(entity.name + ' missed you. ')
        
    #Hit wrong area
    elif new_loc != location:
        if hasattr(curr_target.fighter, 'ai'):
            #Determine the best save to use
            avoid_result, msg = avoid_attack(entity, curr_target, cs, atk_result, final_to_hit)
            if avoid_result == 's': messages.append(msg)
            else:  
                messages.append(entity.name + ' missed the ' + curr_target.name + '\'s ' + curr_target.fighter.name_location(location) + 
                    ', but landed a glancing blow to ' + str(loc_list[new_loc]))
        
                effects = apply_dam(curr_target, entities, roll, attack.damage_type[0], dam_mult, new_loc, cs)
                for effect in effects:
                    messages.append(effect)
        else:
            #Switch to allow player to decide to dodge or parry
            combat_phase = CombatPhase.defend
    #hit
    else:
        if hasattr(curr_target.fighter, 'ai'):
            #Determine best save
            avoid_result, msg = avoid_attack(entity, curr_target, cs, atk_result, final_to_hit)
            if avoid_result == 's': messages.append(msg)
            else:  
                effects = apply_dam(curr_target, entities, roll, attack.damage_type[0], dam_mult, location, cs)
                for effect in effects:
                    messages.append(effect)
        else:
            #Switch to allow player to decide to dodge or parry
            combat_phase = CombatPhase.defend

    if hasattr(entity.fighter, 'ai'):
        entity.fighter.ai.mods = cs

    #Add to history to keep up with who had the last action. Used in disengaging and opportunity attacks
    global_vars.action_id_history.append(id(entity))

    if curr_target.fighter.disengage:
        combat_phase = CombatPhase.disengage

    return messages, combat_phase

def add_history(entity) -> None:
    history = entity.fighter.attacker_history
    attacker = entity.fighter.attacker
    atk_tuple = (attacker.fighter.combat_choices[1].name, attacker.fighter.combat_choices[2], attacker.fighter.combat_choices[3])
    history.append(atk_tuple)
    if len(history) > entity.fighter.mem/10:
        del history[0]

def make_attack_roll(hit_chance, damage, location) -> (int, int, int):
    roll = roll_dice(1, 100, True)
    #MISS
    if roll > hit_chance:
        return roll, 0, 0
    #Hit another loc softly
    elif roll > hit_chance - 10:
        if location <= 2:
            new_loc = location + roll_dice(1,2)
        elif location >= 26:
            new_loc = location - roll_dice(1,2)
        else:
            new_loc = location + (roll_dice(1,3) - roll_dice(1,3))
        damage *= (((hit_chance - roll)/(hit_chance/100))/100)*.4
        return roll, damage, new_loc    
    #Hit another loc glancing
    elif  roll > hit_chance - 20:
        if location <= 3:
            new_loc = location + roll_dice(1,3)
        elif location >= 25:
            new_loc = location - roll_dice(1,3)
        else:
            new_loc = location + (roll_dice(1,4) - roll_dice(1,4))
        damage *= (((hit_chance - roll)/(hit_chance/100))/100)*.1
        return roll, damage, new_loc
    else:
        damage *= (((hit_chance - roll)/(hit_chance/100))/100)
        return roll, damage, location

def avoid_attack(attacker, defender, cs, atk_result, final_to_hit) -> (str, str):
    message = ''
    check = 'f'
    parry = False
    dodge = False
    parry_best = False
    can_dodge = False
    can_parry = False
    attack = attacker.fighter.combat_choices[1]
    atk_name = attack.name 
    #CS Key: 0tot_er, 1b_psi, 2s_psi, 3p_psi, 4t_psi, 5to_hit, 6to_parry, 7dodge_mod, 8final_ap, 9parry_ap, 10parry_mod
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

    #Roll save
    if parry:
        check = save_roll_con(defender.fighter.deflect, parry_mod, atk_result[0], final_to_hit)
        #Remove AP and stamina
        defender.fighter.mod_attribute('ap', -parry_ap)
        defender.fighter.mod_attribute('stamina', -(defender.weapon[0].stamina*defender.fighter.base_stam_cost))
        if check == 's':
            message = str(defender.name + ' parried the attack.')
          
    elif dodge: 
        check = save_roll_con(defender.fighter.dodge, dodge_mod, atk_result[0], final_to_hit)
        #Remove AP and stamina
        defender.fighter.mod_attribute('ap', -defender.fighter.walk_ap)
        defender.fighter.mod_attribute('stamina', -defender.fighter.base_stam_cost)
        if check == 's':
            message = str(defender.name + ' dodged the attack.')
    
    return check, message

def apply_dam(target, entities, roll, dam_type, dam_mult, location, cs) -> set:
    """This  is the  main damage function. dam_effect_finder returns into this. """
    #Set deflect and soak rates
    if dam_type == 'B':
        deflect = [15, 25, 0]        
        soak =  [.7 + ((((target.fighter.derm)*.75) + ((target.fighter.fat)*.25))/100 *.08),
                 .6 + ((((target.fighter.fat)*.6) + ((target.fighter.str)*.4))/100 *.08), 
                 .4 + (sqrt(target.fighter.flex)/100)]
        for i in soak:
            if i > .95: i = .95
        dam_amount = dam_mult * cs.get('b psi')
        multi_apply = True
    elif dam_type == 'S':
        deflect = [0, 0, 15]
        soak =  [.8, .7, .15]
        multi_apply = False
        dam_amount = dam_mult * cs.get('s psi')
    elif dam_type == 'P':
        deflect = [0, 0, 90]
        soak =  [.85, .8, .05]
        multi_apply = False
        dam_amount = dam_mult * cs.get('p psi')
    elif dam_type == 'T':
        deflect = [0, 0, 100]
        soak =  [.5 + (sqrt(target.fighter.derm)/50), 
                .5 + (sqrt(target.fighter.fat)/50), 
                0]
        multi_apply = False
        dam_amount = dam_mult * cs.get('t psi')

    #Store previous damage level to avoid repeating damage effects
    prev_health = [0,0,0]
    i = 0
    for layer in target.fighter.locations[location]:
        prev_health[i] = layer
        i += 1

    #Calc final damage
    damage = [int(round((1-soak[0])*dam_amount)), int(round((1-soak[1])*dam_amount)), int(round((1-soak[2])*dam_amount))]

    #CHeck deflect
    i = 0
    for i in range(3):  
        if roll <= deflect[i]: damage[i] = 0
        i += 1

    #Apply damage
    if multi_apply:
        i = 0
        for i in range(3):
            target.fighter.locations[location][i] -= damage[i]
            if target.fighter.locations[location][i] < 0: target.fighter.locations[location][i] = 0
            i += 1
    else:
        i = 0
        for i in range(3):
            if target.fighter.locations[location][i] <= 0:
                target.fighter.locations[location][i] = 0
                i += 1
            else:
                target.fighter.locations[location][i] -= damage[i]
                i = 3

    #Determine damage effect level
    #Find % damage
    dam_percent = [0,0,0]
    for layer in target.fighter.locations[location]:
        layer_id = target.fighter.locations[location].index(layer)
        if layer == 0: dam_percent[layer_id] = 0
        elif prev_health[layer_id] == layer: dam_percent[layer_id] = 1
        else:
            dam_percent[layer_id] = (target.fighter.locations[location][layer_id]/target.fighter.max_locations[location][layer_id])

    effects = []
    dam_thresh = [0,0,0]
    i = 0
    for layer in dam_percent:
        if layer <= .9: dam_thresh[i] += 1
        if layer <= .75: dam_thresh[i] += 1
        if layer <= .5: dam_thresh[i] += 1
        if layer <= .25: dam_thresh[i] += 1
        if layer <= .1: dam_thresh[i] += 1
        if layer <= 0: dam_thresh[i] += 1
        effects.extend(dam_effect_finder(location, i, dam_thresh[i], target, entities))
        i += 1
        effects_set = set(effects)

    return effects_set

def dam_effect_finder(location, hit_layer, dam_thresh, target, entities) -> list:
    """Second damage function. Generates effect titles and feeds them to dam_effects one at a time. 
    Returns output to apply_dam"""
    effects = []
    #Skin
    if hit_layer == 0:
        if dam_thresh == 0: effects.append('None')
        elif location == 0:
            if dam_thresh == 1: effects.append('Light Scraping')
            elif dam_thresh == 2: effects.append('Major Scraping')
            elif dam_thresh == 3: effects.append('Torn Scalp')
            elif dam_thresh == 4: effects.append('Severe Torn Scalp')
            elif dam_thresh == 5: effects.append('Partial Loss of Scalp')
            elif dam_thresh == 6: effects.append('Scalped')
        elif location == 1:
            if dam_thresh == 1: effects.append('Light Scraping')
            elif dam_thresh == 2: effects.append('Major Scraping')
            elif dam_thresh == 3: effects.append('Light Disfigurement')
            elif dam_thresh == 4: effects.append('Mild Disfigurement')
            elif dam_thresh == 5: effects.append('Heavy Disfigurement')
            elif dam_thresh == 6: effects.append('Horrid Disfigurement')
        else:
            if dam_thresh == 1: effects.append('Light Scraping')
            elif dam_thresh == 2: effects.append('Major Scraping')
            elif dam_thresh == 3: effects.append('Torn Skin')
            elif dam_thresh == 4: effects.append('Severe Torn Skin')
            elif dam_thresh == 5: effects.append('Partial Loss of Skin')
            elif dam_thresh == 6: effects.append('Complete Loss of Skin')
    #Tissue
    elif hit_layer == 1:
        if dam_thresh == 0: effects.append('None')
        elif location == 0: effects.append('None')
        elif location == 1:
            if dam_thresh <= 3: effects.append('None')
            elif dam_thresh == 4: effects.append('Cut Facial Muscles')
            elif dam_thresh == 5: effects.append('Light Nerve Damage')
            elif dam_thresh == 6: effects.append('Heavy Nerve Damage')
        elif location == 2:
            if dam_thresh >= 1: effects.append('Light Muscle Bruising')
            if dam_thresh >= 2: effects.append('Heavy Muscle Bruising')
            if dam_thresh >= 3: effects.append('Mild Bleeding')
            if dam_thresh >= 4: effects.append('Major Bleeding')
            if dam_thresh >= 5: effects.append('Massive Bleeding')
            if dam_thresh == 6: effects.append('Windpipe Damaged')
        elif 2 < location < 5:
            if dam_thresh == 1: effects.append('Light Muscle Bruising')
            elif dam_thresh == 2: effects.append('Moderate Muscle Bruising')
            elif dam_thresh == 3: effects.append('Heavy Muscle Bruising')
            if dam_thresh >= 4: effects.append('Deltoid Muscle Damage')
            if dam_thresh == 5: effects.append('Light Nerve Damage')
            if dam_thresh == 6: effects.append('Heavy Nerve Damage')
        elif 4 < location < 7:
            if dam_thresh == 1: effects.append('Light Muscle Bruising')
            elif dam_thresh == 2: effects.append('Heavy Muscle Bruising')
            elif dam_thresh == 3: effects.append('Pectoral Muscle Damage')
            elif dam_thresh >= 4: effects.append('Heavy Pectoral Muscle Damage')
            if dam_thresh >= 5: effects.append('Lung Damage')
            if dam_thresh == 6: 
                if location == 5: effects.append('Lung Destroyed')
                else: effects.append('Dead')
        elif 6 < location < 9:
            if dam_thresh == 1: effects.append('Light Muscle Bruising')
            elif dam_thresh == 2: effects.append('Moderate Muscle Bruising')
            elif dam_thresh == 3: effects.append('Heavy Muscle Bruising')
            elif dam_thresh >= 4: effects.append('Biceps Muscle Damage')
            if dam_thresh == 5: effects.append('Light Nerve Damage')
            if dam_thresh == 6: effects.append('Heavy Nerve Damage')
        elif 8 < location < 11:
            if dam_thresh == 1: effects.append('Light Muscle Bruising')
            elif dam_thresh == 2: effects.append('Heavy Muscle Bruising')
            elif dam_thresh == 3: effects.append('Mid-abdominal Muscle Damage')
            if dam_thresh >= 4: effects.append('Heavy Mid-abdominal Muscle Damage')
            if dam_thresh >= 5: 
                if location == 7: effects.append('Upper Right Digestive Organ Damage')
                else: effects.append('Upper Left Digestive Organ Damage')
            if dam_thresh == 6: 
                if location == 7: effects.append('Upper Right Digestive Organs Damaged')
                else: effects.append('Upper Left Digestive Organs Damaged')
        elif 10 < location < 13:
            if dam_thresh == 1: effects.append('Heavy Muscle Bruising')
            elif 1 < dam_thresh < 4: effects.append('Arm Tendon Damage')
            elif dam_thresh >= 4: effects.append('Heavy Arm Tendon Damage')
            if dam_thresh == 5: effects.append('Light Nerve Damage')
            if dam_thresh == 6: effects.append('Heavy Nerve Damage')
        elif 12 < location < 15:
            if dam_thresh == 1: effects.append('Light Muscle Bruising')
            elif dam_thresh == 2: effects.append('Moderate Muscle Bruising')
            elif dam_thresh == 3: effects.append('Heavy Muscle Bruising')
            elif dam_thresh == 4: effects.append('Abdominal Muscle Damage')
            if dam_thresh >= 5: effects.append('Heavy Abdominal Muscle Damage')
            elif dam_thresh == 6: effects.append('Intestinal Damage')
        elif 14 < location < 17:
            if dam_thresh == 1: effects.append('Light Muscle Bruising')
            elif dam_thresh == 2: effects.append('Heavy Muscle Bruising')
            elif dam_thresh >= 3: effects.append('Extensors Damaged')
            elif dam_thresh >= 4: effects.append('Flexors Damaged')
            if dam_thresh == 5: effects.append('Light Nerve Damage')
            if dam_thresh == 6: effects.append('Heavy Nerve Damage')
        elif 16 < location < 19:
            if dam_thresh == 1: effects.append('Light Muscle Bruising')
            elif dam_thresh == 2: effects.append('Heavy Muscle Bruising')
            elif dam_thresh >= 3: effects.append('Oblique Muscle Damage')
            if dam_thresh >= 4: effects.append('Damaged Reproductive Organs')
            if dam_thresh >= 5: effects.append('Damaged Kidney')
            if dam_thresh == 6: effects.append('Damaged Bladder')
        elif 18 < location < 21:
            if dam_thresh == 1: effects.append('Finger Damaged')
            elif 1 < dam_thresh < 6: effects.append('Hand Tendons Damaged')
            elif dam_thresh == 6: effects.append('Hand Mutilated')
        elif 20 < location < 23:
            if dam_thresh == 1: effects.append('Light Muscle Bruising')
            elif dam_thresh == 2: effects.append('Heavy Muscle Bruising')
            elif dam_thresh == 3: effects.append('Quadriceps Damage')
            if dam_thresh >= 4: effects.append('Heavy Quadriceps Damage')
            if dam_thresh == 5: effects.append('Light Nerve Damage')
            elif dam_thresh == 6: effects.append('Heavy Nerve Damage')
        elif 22 < location < 25:
            if dam_thresh == 1: effects.append('Heavy Muscle Bruising')
            elif 1 < dam_thresh < 4: effects.append('Leg Tendon Damage')
            if dam_thresh >= 4: effects.append('Heavy Leg Tendon Damage')
            if dam_thresh == 5: effects.append('Light Nerve Damage')
            elif dam_thresh == 6: effects.append('Heavy Nerve Damage')
        elif 24 < location < 27:
            if dam_thresh == 1: effects.append('Light Muscle Bruising')
            elif dam_thresh == 2: effects.append('Heavy Muscle Bruising')
            elif dam_thresh == 3: effects.append('Calf Muscle Damage')
            if dam_thresh >= 4: effects.append('Heavy Calf Muscle Damage')
            if dam_thresh == 5: effects.append('Light Nerve Damage')
            elif dam_thresh == 6: effects.append('Heavy Nerve Damage')
        else:
            if dam_thresh == 1: effects.append('Toe Damaged')
            elif 1 < dam_thresh < 6: effects.append('Foot Tendons Severed')
            elif dam_thresh == 6: effects.append('Foot Mutilated')
    #Bone
    else:
        if dam_thresh == 0: effects.append('None')
        elif location == 0:
            if dam_thresh == 1: effects.append('Light Concussion')
            elif dam_thresh == 2: effects.append('Moderate Concussion')
            elif dam_thresh == 3: effects.append('Severe Concussion')
            elif dam_thresh == 4: effects.append('Brain Damage')
            elif dam_thresh == 5: effects.append('Crushed Skull')
            elif dam_thresh == 6: effects.append('Dead')
        elif location == 1:
            if dam_thresh >= 1: effects.append('Mild Disfigurement')
            if dam_thresh == 2: effects.append('Minor loss of sense')
            if dam_thresh >= 3: effects.append('Major loss of sense')
            if dam_thresh == 4: effects.append('Brain Damage')
            if dam_thresh == 5: effects.append('Crushed Skull')
            if dam_thresh == 6: effects.append('Dead')
        elif location == 2:
            if dam_thresh == 1: effects.append('Chipped Vertebra')
            elif 1 < dam_thresh < 4: effects.append('Cracked Vertebra')
            elif 3 < dam_thresh < 6: effects.append('Paralysis (Neck Down)')
            elif dam_thresh == 6: effects.append('Dead')
        elif 2 < location < 5:
            if dam_thresh == 1: effects.append('Bruised Bone')
            elif 1 < dam_thresh < 4: effects.append('Simple Collarbone Fracture')
            elif 3 < dam_thresh < 6: effects.append('Complex Collarbone Fracture')
            elif dam_thresh == 6: effects.append('Shattered Shoulder')
        elif 4 < location < 7:
            if dam_thresh == 1: effects.append('Bruised Bone')
            elif 1 < dam_thresh < 4: effects.append('Cracked Ribs')
            elif 3 < dam_thresh < 6: effects.append('Badly Broken Ribs')
            elif dam_thresh == 6: 
                if location == 5: effects.append('Shattered Ribs')
                else: effects.append('Dead')
        elif 6 < location < 9:
            if dam_thresh <= 2: effects.append('Bruised Bone')
            elif 2 < dam_thresh < 5: effects.append('Simple Humerus Fracture')
            elif dam_thresh == 5: effects.append('Complex Humerus Fracture')
            elif dam_thresh == 6: effects.append('Shattered Humerus')
        elif 8 < location < 11:
            if dam_thresh <= 3: effects.append('Chipped Vertebra')
            elif dam_thresh == 4: effects.append('Cracked Vertebra')
            elif dam_thresh > 4: effects.append('Paralysis (Waist Down)')
        elif 10 < location < 13:
            if dam_thresh <= 2: effects.append('Bruised Bone')
            elif dam_thresh == 3: effects.append('Hyper-extended Elbow')
            elif 3 < dam_thresh < 6: effects.append('Broken Elbow')
            elif dam_thresh == 6: effects.append('Shattered Elbow')
        elif 12 < location < 15:
            if dam_thresh <= 3: effects.append('Chipped Vertebra')
            elif dam_thresh == 4: effects.append('Cracked Vertebra')
            elif dam_thresh > 4: effects.append('Paralysis (Chest Down)')
        elif 14 < location < 17:
            if dam_thresh <= 2: effects.append('Bruised Bone')
            if dam_thresh >= 3: effects.append('Radius Broken')
            if dam_thresh == 5: effects.append('Ulna Broken')
            if dam_thresh == 6: effects.append('Shattered Forearm')
        elif 16 < location < 19:
            if dam_thresh <= 2: effects.append('Bruised Bone')
            elif dam_thresh == 3: effects.append('Cracked Pelvis')
            elif dam_thresh == 4: effects.append('Broken Pelvis')
            elif dam_thresh >= 5: effects.append('Crushed Pelvis')
            elif dam_thresh == 6: effects.append('Paralysis (Waist Down)')
        elif 18 < location < 21:
            if dam_thresh == 1: effects.append('Sprained Wrist')
            if dam_thresh >= 2: effects.append('Crushed/Severed Little Finger')
            if dam_thresh >= 3: effects.append('Crushed/Severed Ring Finger')
            if dam_thresh >= 4: effects.append('Crushed/Severed Middle Finger')
            if dam_thresh >= 5: effects.append('Crushed/Severed Index Finger')
            if dam_thresh == 6: effects.append('Crushed/Severed Hand')
        elif 20 < location < 23:
            if dam_thresh <= 2: effects.append('Bruised Bone')
            elif 2 < dam_thresh < 5: effects.append('Simple Femur Fracture')
            elif dam_thresh == 5: effects.append('Complex Femur Fracture')
            elif dam_thresh == 6: effects.append('Shattered Femur')
        elif 22 < location < 25:
            if dam_thresh <= 2: effects.append('Bruised Bone')
            elif dam_thresh == 3: effects.append('Hyper-extended Knee')
            elif 3 < dam_thresh < 6: effects.append('Broken Knee')
            elif dam_thresh == 6: effects.append('Shattered Knee')
        elif 24 < location < 27:
            if dam_thresh <= 2: effects.append('Bruised Bone')
            if dam_thresh >= 3: effects.append('Fibula Broken')
            if dam_thresh == 5: effects.append('Tibia Broken')
            if dam_thresh == 6: effects.append('Shattered Shin')
        else:
            if dam_thresh == 1: effects.append('Sprained Ankle')
            elif dam_thresh == 2: effects.append('1 toe destroyed')
            elif dam_thresh == 3: effects.append('2 toes destroyed')
            elif dam_thresh == 4: effects.append('3 toes destroyed')
            elif dam_thresh == 5: effects.append('4 toes destroyed')
            elif dam_thresh == 6: effects.append('Crushed/Severed Foot')
    
    #Check and see if pre-existing injury, skip effect if so
    for effect in effects:
        if str(target.fighter.name_location(location) + ': ' + effect) in target.fighter.injuries:
            effects.remove(effect)   
    #Add null effect if effect empty
    if len(effects) == 0:
        effects.append('None')

    dam_result = dam_effects(effects, target, entities, location)

    return dam_result

def dam_effects(titles, entity, entities, location, dam_type = 'B') -> list:
    description = []

    #Main effect gen code
    for title in titles:
        if title == 'None':
            description.append(entity.name + ' was hit in the ' + entity.fighter.name_location(location))
        if title == 'Light Scraping':
            description.append(entity.name +' has been lightly scraped and lacerated. ')
            entity.fighter.vitae -= 10
        if title == 'Major Scraping':
            description.append(entity.name + ' has been badly lacerated. ')
            entity.fighter.vitae -= 20
        if title == 'Torn Scalp':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' has been torn open and is bleeding. ')
            entity.fighter.bleed.append([5,100])
        if title == 'Severe Torn Scalp':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' has been torn badly and is bleeding profusely. ')
            entity.fighter.bleed.append([10,100])
        if title == 'Partial Loss of Scalp':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' has been nearly torn off and is bleeding profusely, causing the face to sag. ')
            entity.fighter.bleed.append([20,1000])
            entity.fighter.mod_attribute('fac', -10)
            entity.fighter.adjust_max_locations(0,0,(entity.fighter.max_locations[0][0] * .5))
            
        if title == 'Scalped':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' has been completely torn off and is bleeding profusely, causing the face to sag. ')
            entity.fighter.bleed.append([40,1000])
            entity.fighter.mod_attribute('fac', -20)
            entity.fighter.locations[0][0] == 0
            entity.fighter.adjust_max_locations(0,0,(entity.fighter.max_locations[0][0]))
        if title == 'Torn Skin':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' skin has been torn open and is bleeding. ')
            entity.fighter.bleed.append([5,100])
        if title == 'Severe Torn Skin':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' skin has been torn badly and is bleeding profusely. ')
            entity.fighter.bleed.append([10,100])
        if title == 'Partial Loss of Skin':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' skin has been nearly torn off and is bleeding profusely. ')
            entity.fighter.bleed.append([10,1000])
            entity.fighter.adjust_max_locations(location,0,(entity.fighter.max_locations[location][0] * .5))
        if title == 'Complete Loss of Skin':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' skin has been completely torn off and is bleeding profusely. ')
            entity.fighter.bleed.append([20,1000])
            entity.fighter.locations[location][0] = 0
            entity.fighter.adjust_max_locations(location,0,entity.fighter.max_locations[location][0])
        if title == 'Light Disfigurement':
            description.append(entity.name + ' has suffered a small facial wound that is disfiguring. ')
            entity.fighter.vitae -= 20
            entity.fighter.mod_attribute('fac', -20)
        if title == 'Mild Disfigurement':
            description.append(entity.name + ' has suffered a moderate sized facial wound that is disfiguring. ')
            entity.fighter.vitae -= 30
            entity.fighter.mod_attribute('fac', -30)
        if title == 'Heavy Disfigurement':
            feature = roll_dice(1,6)

            if feature == 1:
                description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'nose torn off. ')
                entity.fighter.mod_attribute('ts', -20)
            elif feature == 2:
                description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'left ear ripped off. ')
                entity.fighter.mod_attribute('hear', -10)
            elif feature == 3:
                description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'right ear ripped off. ')
                entity.fighter.mod_attribute('hear', -10)
            elif feature == 4:
                description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'upper lip ripped off. ')
            elif feature == 5:
                description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'lower lip ripped off. ')
            elif feature == 6:
                description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'front row of teeth shattered. ')
            entity.fighter.vitae -= 30
            entity.fighter.mod_attribute('fac', -50)
            entity.fighter.adjust_max_locations(1,0,entity.fighter.max_locations[1][0] * .5)
        if title == 'Horrid Disfigurement':
            features = []
            i = 0
            while i < 3:
                roll = roll_dice(1,6)
                if roll in features:
                    continue
                else:
                    features.append(roll)
                    i += 1
            for feature in features:
                if feature == 1:
                    description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'nose torn off. ')
                    entity.fighter.mod_attribute('ts', -20)
                elif feature == 2:
                    description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'left ear ripped off. ')
                    entity.fighter.mod_attribute('hear', -10)
                elif feature == 3:
                    description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'right ear ripped off. ')
                    entity.fighter.mod_attribute('hear', -10)
                elif feature == 4:
                    description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'upper lip ripped off. ')
                elif feature == 5:
                    description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'lower lip ripped off. ')
                elif feature == 6:
                    description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'front row of teeth shattered. ')
            entity.fighter.vitae -= 60
            entity.fighter.mod_attribute('fac', -80)
            entity.fighter.adjust_max_locations(1,0,entity.fighter.max_locations[1][0] * .2)
            
        if title == 'Light Muscle Bruising':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' muscles have been bruised, mildly affecting physical actions. ')
            entity.fighter.temp_physical_mod -= 5
        if title == 'Moderate Muscle Bruising':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' muscles have been badly bruised, moderately affecting physical actions. ')
            entity.fighter.temp_physical_mod -= 10
        if title == 'Heavy Muscle Bruising':
            description.append(entity.name + '\'s ' + entity.fighter.name_location(location) + ' muscles have been severely bruised, heavily affecting physical actions. ')
            entity.fighter.temp_physical_mod -= 20
        if title == 'Cut Facial Muscles':
            description.append(entity.name + ' has had '+ ('his ' if entity.fighter.male else 'her ') + 'facial muscles damaged, resulting in a permanent droop. ')
            entity.fighter.mod_attribute('fac', -10)
        if title == 'Light Nerve Damage':
            description.append(entity.name + '\'s nerves have been damaged, leading to a loss of feeling. ')
            entity.fighter.mod_attribute('touch', -10)
        if title == 'Heavy Nerve Damage':
            description.append(entity.name + '\'s nerves have been destroyed in '+ ('his ' if entity.fighter.male else 'her ') + entity.fighter.name_location(location) + '.')
            entity.fighter.paralyzed_locs.append(location)
        if title == 'Mild Bleeding':
            description.append(entity.name + ' has begun bleeding from the neck wound. ')
            entity.fighter.bleed.append([10,100])
        if title == 'Major Bleeding':
            description.append(entity.name + ' is bleeding badly from the neck wound. ')
            entity.fighter.bleed.append([20,100])
        if title == 'Massive Bleeding':
            description.append(entity.name + ' is bleeding profusely from the neck wound. ')
            entity.fighter.bleed.append([(entity.fighter.max_vitae*.04),1000])
        if title == 'Windpipe Damaged':
            description.append(entity.name + '\'s windpipe has been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'is choking to death. ')
            entity.fighter.suffocation = (entity.fighter.sta/10)*12
        if title == 'Deltoid Muscle Damage':
            if location == 3:
                entity.fighter.paralyzed_locs.extend([3, 7, 11, 15, 19])
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.2)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.2)*-1)
                entity.fighter.bleed.append([10,1000])
                description.append(entity.name + '\'s right shoulder muscle has been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will not be able to use '
                    + ('his ' if entity.fighter.male else 'her ') + 'right arm until it is healed. ')
            else:
                entity.fighter.paralyzed_locs.extend([4, 8, 12, 16, 20])
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.2)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.2)*-1)
                entity.fighter.bleed.append([10,1000])
                description.append(entity.name + '\'s left shoulder muscle has been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will not be able to use '
                    + ('his ' if entity.fighter.male else 'her ') + 'left arm until it is healed. ')
        if title == 'Pectoral Muscle Damage':
            if location == 5:
                entity.fighter.paralyzed_locs.extend([3, 7, 11, 15, 19])
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
                description.append(entity.name + '\'s right chest muscle has been damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will not be able to use '
                    + ('his ' if entity.fighter.male else 'her ') + 'right arm until it is healed. ')
            else:
                entity.fighter.paralyzed_locs.extend([4, 8, 12, 16, 20])
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
                description.append(entity.name + '\'s left chest muscle has been damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will not be able to use '
                    + ('his ' if entity.fighter.male else 'her ') + 'left arm until it is healed. ')
        if title == 'Heavy Pectoral Muscle Damage':
            if location == 5:
                entity.fighter.paralyzed_locs.extend([3, 7, 11, 15, 19])
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.15)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.15)*-1)
                entity.fighter.bleed.append([5,1000])
                description.append(entity.name + '\'s right chest muscle has been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will not be able to use '
                    + ('his ' if entity.fighter.male else 'her ') + 'right arm until it is healed. ')
            else:
                entity.fighter.paralyzed_locs.extend([4, 8, 12, 16, 20])
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.15)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.15)*-1)
                entity.fighter.bleed.append([5,1000])
                description.append(entity.name + '\'s left chest muscle has been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will not be able to use '
                    + ('his ' if entity.fighter.male else 'her ') + 'left arm until it is healed. ')
        if title == 'Lung Damage':
            entity.fighter.stam_drain += 50
            entity.fighter.mod_attribute('sta', (entity.fighter.sta*.5)*-1)
            entity.fighter.bleed.append([5,1000])
            description.append(entity.name + '\'s lung has collapsed, and '+ ('he ' if entity.fighter.male else 'she ') + 'begins gasping for breath. ')
        if title == 'Lung Destroyed':
            entity.fighter.stam_drain += 100
            entity.fighter.mod_attribute('sta', (entity.fighter.sta*.5)*-1)
            entity.fighter.bleed.append([entity.fighter.max_vitae*.02,1000])
            description.append(entity.name + '\'s lung has been destroyed, and '+ ('he ' if entity.fighter.male else 'she ') + 'begins gasping for breath. ')
        if title == 'Dead':
            description.append(entity.name + ' was mortally injured due to damage to a vital organ. '+ ('He ' if entity.fighter.male else 'She ') +
            'is dead. ')
        if title == 'Mid-abdominal Muscle Damage':
            description.append(entity.name + '\'s mid-abdominal muscles have been damaged, rendering those muscles inoperative until healed. '
                +  'All movement is very painful. ')
            entity.fighter.pain_mod_mov += 40
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
        if title == 'Heavy Mid-abdominal Muscle Damage':
            description.append(entity.name + '\'s mid-abdominal muscles have been badly damaged, rendering those muscles inoperative until healed. '
                +  'All movement is excruciatingly painful. The wound bleeds heavily.')
            entity.fighter.pain_mod_mov += 80
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
            entity.fighter.bleed.append([5,1000])
        if title == 'Upper Right Digestive Organ Damage':
            organ = roll_dice(1, 6)
            if organ < 3:
                entity.fighter.diseases.append('Cirrhosis')
                description.append(entity.name + '\'s liver is badly damaged. The injury bleeds heavily. Additionally, liver damage will kill '
                        + ('him ' if entity.fighter.male else 'her ') +  'within several months. ')
            if 2 < organ < 5:
                entity.fighter.mod_attribute('immune', (entity.fighter.immune*.05)*-1)
                description.append(entity.name + '\'s omentum is badly damaged. This makes '
                        + ('him ' if entity.fighter.male else 'her ') +  'more succeptable to disease. The injury also bleeds heavily.')
            if organ == 5:
                entity.fighter.diseases.append('Pancreatitis')
                description.append(entity.name + '\'s pancreas is badly damaged. The injury bleeds heavily. ')
            if organ == 6:
                description.append(entity.name + '\'s gallbladder is badly damaged. The injury bleeds heavily inside the body. ')
            entity.fighter.bleed.append([entity.fighter.max_vitae*.04,10])
        if title == 'Upper Right Digestive Organ Damage':
            organ = roll_dice(1, 6)
            if organ < 3:
                entity.fighter.diseases.append('Cirrhosis')
                description.append(entity.name + '\'s liver is badly damaged. The injury bleeds heavily. Additionally, liver damage will kill '
                        + ('him ' if entity.fighter.male else 'her ') +  'within several months. ')
            if 2 < organ < 5:
                entity.fighter.mod_attribute('immune', (entity.fighter.immune*.05)*-1)
                description.append(entity.name + '\'s omentum is badly damaged. This makes '
                        + ('him ' if entity.fighter.male else 'her ') +  'more succeptable to disease. The injury also bleeds heavily.')
            if organ == 5:
                entity.fighter.diseases.append('Pancreatitis')
                description.append(entity.name + '\'s pancreas is badly damaged. The injury bleeds heavily internally. ')
            if organ == 6:
                description.append(entity.name + '\'s gallbladder is badly damaged. The injury bleeds heavilyinternally. ')
            entity.fighter.bleed.append([entity.fighter.max_vitae*.04,10])
        if title ==' Upper Right Digestive Organs Damaged':
            description.append(entity.name + '\'s liver, pancreas, and omentum are all damaged badly. The injury bleeds heavily internally, and '
                + entity.name + 'will slowly die without these organs. ')
            entity.fighter.diseases.extend('Cirrhosis', 'Pancreatitis')
            entity.fighter.mod_attribute('immune', (entity.fighter.immune*.05)*-1)
            entity.fighter.bleed.append([entity.fighter.max_vitae*.08,10])
        if title == 'Upper Left Digestive Organ Damage':
            organ = roll_dice(1, 6)
            if organ < 4:
                description.append(entity.name + '\'s spleen has ruptured. The injury bleeds heavily inside the body cavity, and will not stop without treatment. ')
                entity.fighter.bleed.append([entity.fighter.max_vitae*.04,1000])
                entity.fighter.mod_attribute('immune', (entity.fighter.immune*.05)*-1)
            if 3 < organ < 6:
                description.append(entity.name + '\'s stomach has ruptured. This injury will cause a slow and painful death. ')
                entity.fighter.diseases.append('Stomach Rupture')
            if organ == 6:
                entity.fighter.diseases.append('Pancreatitis')
                description.append(entity.name + '\'s pancreas is badly damaged. The injury bleeds heavily internally. ')
            entity.fighter.bleed.append([entity.fighter.max_vitae*.04,10])
        if title == 'Upper Left Digestive Organs Damaged':
            description.append(entity.name + '\'s spleen, pancreas, and stomach are all damaged badly. The injury bleeds heavily internally, and '
                + entity.name + 'will slowly die without these organs. ')
            entity.fighter.diseases.extend('Stomach Rupture', 'Pancreatitis')
            entity.fighter.bleed.append([entity.fighter.max_vitae*.04,10])
            entity.fighter.bleed.append([10,1000])
        if title == 'Abdominal Muscle Damage':
            description.append(entity.name + '\'s abdominal muscles have been damaged, rendering those muscles inoperative until healed. '
                +  'All movement is very painful. ')
            entity.fighter.pain_mod_mov += 60
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
        if title == 'Heavy Abdominal Muscle Damage':
            description.append(entity.name + '\'s abdominal muscles have been badly damaged, rendering those muscles inoperative until healed. '
                +  'All movement is excruciatingly painful. The wound bleeds heavily.')
            entity.fighter.pain_mod_mov += 120
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
            entity.fighter.bleed.append([10,100])
        if title == 'Intestinal Damage':
            description.append(entity.name + '\'s intestines have been ruptured, and ' + ('he ' if entity.fighter.male else 'she ') 
                + 'is doomed to die a slow, painful death. ')
            entity.fighter.diseases.append('Intestinal Rupture')
            entity.fighter.bleed.append([entity.fighter.max_vitae*.02,1000])
        if title == 'Oblique Muscle Damage':
            description.append(entity.name + '\'s oblique muscles have been damaged, rendering those muscles inoperative until healed. '
                +  'All movement is painful. ')
            entity.fighter.pain_mod_mov += 30
        if title == 'Damaged Reproductive Organs':
            check = save_roll_un(entity.fighter.will, -100)
            if check[0] == 'cs':
                description.append(entity.name + '\'s ' + ('testicles ' if entity.fighter.male else 'ovaries ') + 'have been damaged. '
                +  'Despite the intense pain, however, ' + entity.name + ' continues to fight unimpeded.')
            elif check[0] == 'cf':
                description.append(entity.name + '\'s ' + ('testicles ' if entity.fighter.male else 'ovaries ') + 'have been damaged. '
                + entity.name + ' falls unconscious from the pain.')
                handle_state_change(entity, entities, EntityState.unconscious)
            elif check[0] == 's':
                description.append(entity.name + '\'s ' + ('testicles ' if entity.fighter.male else 'ovaries ') + 'have been damaged. '
                + entity.name + ' manages to remain fighting, but the pain will affect ' + ('him ' if entity.fighter.male else 'her ') + 
                'until treated. ')
                entity.fighter.pain_mod_mov += 30
            else:
                description.append(entity.name + '\'s ' + ('testicles ' if entity.fighter.male else 'ovaries ') + 'have been damaged. '
                + entity.name + ' drops to the ground, writhing in pain. ')
                handle_state_change(entity, entities, EntityState.stunned)
        if title == 'Damaged Kidney':
            check = save_roll_un(entity.fighter.will, -50)
            if check[0] == 'cs':
                description.append(entity.name + '\'s kidney has been ruptured. This causes blinding pain and internal bleeding. '
                +  'Despite the intense pain, however, ' + entity.name + ' continues to fight unimpeded.')
            elif check[0] == 'cf':
                description.append(entity.name + '\'s kidney has been ruptured. This causes blinding pain and internal bleeding. '
                + entity.name + ' falls unconscious from the pain.')
                handle_state_change(entity, entities, EntityState.unconscious)
            elif check[0] == 's':
                description.append(entity.name + '\'s kidney has been ruptured. This causes blinding pain and internal bleeding. '
                + entity.name + ' manages to remain fighting, but the pain will affect ' + ('him ' if entity.fighter.male else 'her ') + 
                'until treated. ')
                entity.fighter.pain_mod_mov += 10
            else:
                description.append(entity.name + '\'s kidney has been ruptured. This causes blinding pain and internal bleeding. '
                + entity.name + ' drops to the ground, writhing in pain. ')
                handle_state_change(entity, entities, EntityState.stunned)
            entity.fighter.bleed.append([5,1000])
        if title == 'Damaged Bladder':
            entity.fighter.diseases.append('Ruptured Bladder')
            description.append(entity.name + '\'s bladder has ruptured. This will not kill ' + ('him ' if entity.fighter.male else 'her ') + 
                'directly, but the rest of ' + ('him ' if entity.fighter.male else 'her ') + 'life will be messy and infection-prone.')
            entity.fighter.mod_attribute('immune', (entity.fighter.immune*.1)*-1)
        if title == 'Biceps Muscle Damage':
            if location == 7:
                entity.fighter.paralyzed_locs.extend([15, 19])
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
                entity.fighter.bleed.append([5,100])
                description.append(entity.name + '\'s right biceps muscles have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will not be able to use '
                    + ('his ' if entity.fighter.male else 'her ') + 'right forearm until it is healed. ')
            else:
                entity.fighter.paralyzed_locs.extend([16, 20])
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
                entity.fighter.bleed.append([5,100])
                description.append(entity.name + '\'s left biceps muscles have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will not be able to use '
                    + ('his ' if entity.fighter.male else 'her ') + 'left forearm until it is healed. ')
        if title == 'Arm Tendon Damage':
            if location == 11:
                entity.fighter.atk_mod_r += -40
                description.append(entity.name + '\'s right arm tendons have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'right forearm until it is healed. ')
            else:
                entity.fighter.atk_mod_l += -40
                description.append(entity.name + '\'s left arm tendons have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'left forearm until it is healed. ')
        if title == 'Heavy Arm Tendon Damage':
            if location == 11:
                entity.fighter.paralyzed_locs.extend([15, 19])
                description.append(entity.name + '\'s right arm tendons have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'right forearm until it is healed. ')
            else:
                entity.fighter.paralyzed_locs.extend([16, 20])
                description.append(entity.name + '\'s left arm tendons have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'left forearm until it is healed. ')
        if title == 'Extensors Damaged':
            if location == 15:
                entity.fighter.atk_mod_r += -20
                description.append(entity.name + '\'s right forearm muscles have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'right forearm until it is healed. ')
            else:
                entity.fighter.atk_mod_l += -20
                description.append(entity.name + '\'s left forearm muscles have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'left forearm until it is healed. ')
        if title == 'Flexors Damaged':
            if location == 15:
                entity.fighter.atk_mod_r += -40
                description.append(entity.name + '\'s right forearm muscles have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'right forearm until it is healed. ')
            else:
                entity.fighter.atk_mod_l += -40
                description.append(entity.name + '\'s left forearm muscles have been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'left forearm until it is healed. ')
        if title == 'Finger Damaged':
            if location == 19:
                entity.fighter.atk_mod_r += -20
                description.append(entity.name + '\'s right index finger has been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'right hand until it is healed. ')
            else:
                entity.fighter.atk_mod_l += -20
                description.append(entity.name + '\'s left index finger has been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulthy using '
                    + ('his ' if entity.fighter.male else 'her ') + 'left hand until it is healed. ')
        if title == 'Hand Tendons Damaged':
            if location == 19:
                entity.fighter.paralyzed_locs.extend([19])
                description.append(entity.name + '\'s right hand tendons have been torn. '+ ('His ' if entity.fighter.male else 'Her ') + 'fingers are limp, and '
                    + ('he ' if entity.fighter.male else 'she ') + 'will be unable to use' + ('his ' if entity.fighter.male else 'her ') 
                    + 'right hand until it is healed. ')
            else:
                entity.fighter.paralyzed_locs.extend([20])
                description.append(entity.name + '\'s right hand tendons have been torn. '+ ('His ' if entity.fighter.male else 'Her ') + 'fingers are limp, and '
                    + ('he ' if entity.fighter.male else 'she ') + 'will be unable to use' + ('his ' if entity.fighter.male else 'her ') 
                    + 'right hand until it is healed. ')
        if title == 'Hand Mutilated':
            if location == 19:
                description.append(entity.name + '\'s right hand has been mutilated beyond repair. '+ ('His ' if entity.fighter.male else 'Her ') + 
                    'tendons, veins, and nerves are so extensively damaged that the hand will never function again. ')
            else:
                description.append(entity.name + '\'s left hand has been mutilated beyond repair. '+ ('His ' if entity.fighter.male else 'Her ') + 
                    'tendons, veins, and nerves are so extensively damaged that the hand will never function again. ')
            entity.fighter.paralyzed_locs.extend([location])
            entity.fighter.locations[location][1] = 0
            entity.fighter.adjust_max_locations(location,1,entity.fighter.max_locations[location][1])
        if title == 'Quadriceps Damage':
            description.append(entity.name + '\'s frontal thigh muscles have been torn, rendering those muscles greatly compromised until healed. '
                + ('He ' if entity.fighter.male else 'She ') + 'can still move, but it is painful and slow. ')
            entity.fighter.pain_mod_mov += 60
            entity.fighter.mv *= .4
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
        if title == 'Heavy Quadriceps Damage':
            description.append(entity.name + '\'s frontal thigh muscles have been severed, rendering those muscles inoperative until healed. '
                + 'Additionally, the femoral artery has hemmorhaged, and bleeding is severe. ' +
                ('He ' if entity.fighter.male else 'She ') + 'can no longer use this leg. Movement is possible via hopping or crawling.')
            entity.fighter.paralyzed_locs.extend([location])
            entity.fighter.mv *= .1
            entity.fighter.temp_physical_mod -= 70
            entity.fighter.bleed.append([entity.fighter.max_vitae*.02,1000])
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
        if title == 'Leg Tendon Damage':
            description.append(entity.name + '\'s ligaments and tendons have been torn, rendering the knee greatly compromised until healed. '
                + ('He ' if entity.fighter.male else 'She ') + 'can still move, but it is painful and slow. ')
            entity.fighter.pain_mod_mov += 40
            entity.fighter.mv *= .6
        if title == 'Heavy Leg Tendon Damage':
            description.append(entity.name + '\'s ligaments and tendons have been severed, rendering the knee inoperative until healed. '
                + ('He ' if entity.fighter.male else 'She ') + 'can no longer use this leg. Movement is possible via hopping or crawling.')
            entity.fighter.paralyzed_locs.extend([location, location + 2, location + 4])
            entity.fighter.mv *= .1
            entity.fighter.temp_physical_mod -= 70
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
        if title == 'Calf Muscle Damage':
            description.append(entity.name + '\'s calf muscle has been torn. ' + ('He ' if entity.fighter.male else 'She ') + 'can still move, but it is painful and slow. ')
            entity.fighter.pain_mod_mov += 30
            entity.fighter.mv *= .8
        if title == 'Heavy Calf Muscle Damage':
            description.append(entity.name + '\'s calf muscle has been severed. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still move, but that foot is inoperable, making it unstable, painful, and very slow. ')
            entity.fighter.pain_mod_mov += 60
            entity.fighter.mv *= .4
            entity.fighter.paralyzed_locs.extend([location + 2])
            entity.fighter.temp_physical_mod -= 40
        if title == 'Toe Damaged':
            description.append(entity.name + '\'s big toe has been badly damaged, and '+ ('he ' if entity.fighter.male else 'she ') + 'will have difficulty using '
                    + ('his ' if entity.fighter.male else 'her ') + 'foot until it is healed. ')
            entity.fighter.pain_mod_mov += 20
            entity.fighter.mv *= .8
            entity.fighter.temp_physical_mod -= 10
        if title == 'Foot Tendons Severed':
            description.append(entity.name + '\'s foot tendons have been torn, and '+ ('he ' if entity.fighter.male else 'she ') + 'will be unable to use '
                    + ('his ' if entity.fighter.male else 'her ') + 'foot until it is healed. ')
            entity.fighter.pain_mod_mov += 40
            entity.fighter.mv *= .4
            entity.fighter.paralyzed_locs.extend([location])
            entity.fighter.temp_physical_mod -= 40
        if title == 'Foot Mutilated':
            description.append(entity.name + '\'s foot has been mutilated beyond repair. '+ ('His ' if entity.fighter.male else 'Her ') + 
                    'tendons, veins, and nerves are so extensively damaged that the foot will never function again. ')
            entity.fighter.paralyzed_locs.extend([location])
            entity.fighter.locations[location][1] = 0
            entity.fighter.max_locations[location][1] = 0
            entity.fighter.pain_mod_mov += 50
            entity.fighter.mv *= .4
            entity.fighter.temp_physical_mod -= 40
        if title == 'Light Concussion':
            description.append('The blow to the head has concussed ' + entity.name + '. ')
            check = save_roll_un(entity.fighter.shock, 0)
            if check[0] == 'cs':
                description.append('However, ' + entity.name + ' continues to fight unimpeded.')
            elif check[0] == 'cf':
                description.append(entity.name + ' falls unconscious from the blow.')
                handle_state_change(entity, entities, EntityState.unconscious)
                entity.fighter.temp_physical_mod -= 10
            elif check[0] == 's':
                description.append('This renders ' + ('him ' if entity.fighter.male else 'her ') + 
                'dizzy. ')
                entity.fighter.temp_physical_mod -= 10
            else:
                description.append(('He ' if entity.fighter.male else 'She ') + 
                'is dazed by the attack. ')
                handle_state_change(entity, entities, EntityState.stunned)
                entity.fighter.temp_physical_mod -= 10
            
        if title == 'Moderate Concussion':
            description.append('The blow to the head has concussed ' + entity.name + '. ')
            check = save_roll_un(entity.fighter.shock, -40)
            if check[0] == 'cs':
                description.append('However, ' + entity.name + ' continues to fight with only minor difficulty.')
                entity.fighter.temp_physical_mod -= 10
                entity.fighter.diseases.append(title)
            elif check[0] == 'cf':
                description.append(entity.name + ' falls unconscious from the blow.')
                handle_state_change(entity, entities, EntityState.unconscious)
                entity.fighter.temp_physical_mod -= 20
                entity.fighter.diseases.append(title)
            elif check[0] == 's':
                description.append('This renders ' + ('him ' if entity.fighter.male else 'her ') + 
                'very dizzy and disoriented. ')
                entity.fighter.temp_physical_mod -= 20
                entity.fighter.diseases.append(title)
            else:
                description.append(('He ' if entity.fighter.male else 'She ') + 
                'is dazed by the attack. ')
                handle_state_change(entity, entities, EntityState.stunned)
                entity.fighter.temp_physical_mod -= 20
                entity.fighter.diseases.append(title)
            
        if title == 'Severe Concussion':
            description.append('The blow to the head has badly fractured ' + entity.name + '\'s skull. ')
            check = save_roll_un(entity.fighter.shock, -80)
            if check[0] == 'cs':
                description.append('However, ' + entity.name + ' manages to largely keep ' + ('his ' if entity.fighter.male else 'her ') 
                + 'wits.')
                entity.fighter.temp_physical_mod -= 20
                entity.fighter.diseases.append(title)
            elif check[0] == 'cf':
                description.append(entity.name + ' suffers a brain hemorrhage and dies.')
                handle_state_change(entity, entities, EntityState.dead)
            elif check[0] == 's':
                description.append('This renders ' + ('him ' if entity.fighter.male else 'her ') + 
                'very dizzy and disoriented. ')
                entity.fighter.temp_physical_mod -= 30
                entity.fighter.diseases.append(title)
            else:
                description.append(('He ' if entity.fighter.male else 'She ') + 
                'is knocked unconscious by the attack. ')
                handle_state_change(entity, entities, EntityState.unconscious)
                entity.fighter.temp_physical_mod -= 30
                entity.fighter.diseases.append(title)

        if title == 'Brain Damage':
            description.append('The blow to the head has caused permanent brain damage to ' + entity.name + 
            '. ' + ('He ' if entity.fighter.male else 'She ') + 'immediately falls into a coma. ')
            handle_state_change(entity, entities, EntityState.unconscious)
            entity.fighter.diseases.extend('Coma')
            roll = roll_dice(1,100)
            if roll <= 30: 
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.mod_attribute('log', -40)
                entity.fighter.mod_attribute('wis', -40)
            elif roll <= 60:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.mod_attribute('log', -10)
                entity.fighter.mod_attribute('wis', -10)
                entity.fighter.mod_attribute('mem', -10)
                entity.fighter.mod_attribute('comp', -10)
                entity.fighter.mod_attribute('con', -10)
                entity.fighter.mod_attribute('cre', -10)
                entity.fighter.mod_attribute('men', -10)
            elif roll <= 70:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.sit = 0
            elif roll <= 80:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.hear = 0
            elif roll <= 90:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.ts = 0
            elif roll <= 95:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.diseases.append('Epilepsy')
            elif roll <= 97:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                loc_roll = roll_dice(1,4)
                if loc_roll == 1: 
                    entity.fighter.paralyzed_locs.extend([7, 11, 15, 19])
                    entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
                    entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
                if loc_roll == 2: 
                    entity.fighter.paralyzed_locs.extend([8, 12, 16, 20])
                    entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
                    entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
                if loc_roll == 3: 
                    entity.fighter.paralyzed_locs.extend([21, 23, 25, 27])
                    entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
                    entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
                    entity.fighter.mv *= .4
                if loc_roll == 4: 
                    entity.fighter.paralyzed_locs.extend([22, 24, 26, 28])
                    entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
                    entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
                    entity.fighter.mv *= .4
            elif roll == 98:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                i = 0
                limbs = [[7, 11, 15, 19], [8, 12, 16, 20], [21, 23, 25, 27], [22, 24, 26, 28]]
                while i < 2:
                    loc_roll = roll_dice(1,len(limbs))-1
                    entity.fighter.paralyzed_locs.extend([limbs.pop(roll)])
                    i += 1
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.4)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.4)*-1)
                if [21, 23, 25, 27] in entity.fighter.paralyzed_locs:
                    entity.fighter.mv *= .4
                if [22, 24, 26, 28] in entity.fighter.paralyzed_locs:
                    entity.fighter.mv *= .4
            elif roll == 99:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.paralyzed_locs.extend([7, 11, 15, 19, 8, 12, 16, 20, 21, 23, 25, 27, 22, 24, 26, 28])
                entity.fighter.mv = 0
            else: 
                description.append(entity.name + 'begins doing the dead man\'s shuffle, foam and blood bubbling from ' + 
                    ('his ' if entity.fighter.male else 'her ') + 'lips, and eyes wandering in alternate directions. ' +
                    ('He ' if entity.fighter.male else 'She ') + 'is dead in moments. ')
                handle_state_change(entity, entities, EntityState.dead)

        if title == 'Crushed Skull':
            description.append('The blow to the head has caved ' + entity.name + 
            '\'s skull in. ' + ('He ' if entity.fighter.male else 'She ') + 'immediately falls into a coma. ')
            #Reduce INT attribs by 50%
            attrib_list = ['log', 'wis', 'mem', 'comp', 'con', 'cre', 'men']
            for attrib in attrib_list:
                atr = getattr(entity.fighter, attrib)
                entity.fighter.mod_attribute(attrib, (atr*.5)*-1)

            entity.fighter.mod_attribute('fac', -30)

            handle_state_change(entity, entities, EntityState.unconscious)
            entity.fighter.diseases.extend('Coma')

            roll = roll_dice(1,100)
            if roll <= 30: 
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.mod_attribute('log', -40)
                entity.fighter.mod_attribute('wis', -40)
            elif roll <= 60:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.mod_attribute('log', -10)
                entity.fighter.mod_attribute('wis', -10)
                entity.fighter.mod_attribute('mem', -10)
                entity.fighter.mod_attribute('comp', -10)
                entity.fighter.mod_attribute('con', -10)
                entity.fighter.mod_attribute('cre', -10)
                entity.fighter.mod_attribute('men', -10)
            elif roll <= 70:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.sit = 0
            elif roll <= 80:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.hear = 0
            elif roll <= 90:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.ts = 0
            elif roll <= 95:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.diseases.append('Epilepsy')
            elif roll <= 97:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                loc_roll = roll_dice(1,4)
                if loc_roll == 1: 
                    entity.fighter.paralyzed_locs.extend([7, 11, 15, 19])
                    entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
                    entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
                if loc_roll == 2: 
                    entity.fighter.paralyzed_locs.extend([8, 12, 16, 20])
                    entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
                    entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
                if loc_roll == 3: 
                    entity.fighter.paralyzed_locs.extend([21, 23, 25, 27])
                    entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
                    entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
                    entity.fighter.mv *= .4
                if loc_roll == 4: 
                    entity.fighter.paralyzed_locs.extend([22, 24, 26, 28])
                    entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
                    entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
                    entity.fighter.mv *= .4
            elif roll == 98:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                i = 0
                limbs = [[7, 11, 15, 19], [8, 12, 16, 20], [21, 23, 25, 27], [22, 24, 26, 28]]
                while i < 2:
                    loc_roll = roll_dice(1,len(limbs))-1
                    entity.fighter.paralyzed_locs.extend([limbs.pop(roll)])
                    i += 1
                entity.fighter.mod_attribute('ss', (entity.fighter.ss*.4)*-1)
                entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.4)*-1)
                if [21, 23, 25, 27] in entity.fighter.paralyzed_locs:
                    entity.fighter.mv *= .4
                if [22, 24, 26, 28] in entity.fighter.paralyzed_locs:
                    entity.fighter.mv *= .4
            elif roll == 99:
                description.append('If ' + ('he ' if entity.fighter.male else 'she ') + 'survives, ' +
                    ('he ' if entity.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
                entity.fighter.paralyzed_locs.extend([7, 11, 15, 19, 8, 12, 16, 20, 21, 23, 25, 27, 22, 24, 26, 28])
            else: 
                description.append(entity.name + 'begins doing the dead man\'s shuffle, foam and blood bubbling from ' + 
                    ('his ' if entity.fighter.male else 'her ') + 'lips, and eyes wandering in alternate directions. ' +
                    ('He ' if entity.fighter.male else 'She ') + 'is dead in moments. ')
                handle_state_change(entity, entities, EntityState.dead)

        if title == 'Minor loss of sense':
            attrib_list = ['sit', 'ts', 'hear']
            roll = roll_dice(1,3) - 1
            attrib = attrib_list[roll]
            atr = getattr(entity.fighter, attrib)
            entity.fighter.mod_attribute(attrib, (atr*.5)*-1)
            description.append('The damage to ' + entity.name + '\'s deep facial nerves has caused a minor loss to one of ' + 
                ('his ' if entity.fighter.male else 'her ') + 'senses. ')
        
        if title == 'Major loss of sense':
            attrib_list = ['sit', 'ts', 'hear']
            roll = roll_dice(1,3) - 1
            attrib = attrib_list[roll]
            atr = getattr(entity.fighter, attrib)
            entity.fighter.mod_attribute(attrib, (atr*.9)*-1)
            description.append('The damage to ' + entity.name + '\'s deep facial nerves has caused a major loss to one of ' + 
                ('his ' if entity.fighter.male else 'her ') + 'senses. ')
        
        if title == 'Chipped Vertebra':
            description.append('The blow seemes to have chipped a vertebra in ' + entity.name + '\'s spine. ')
            entity.fighter.diseases.extend('Chronic pain, minor')
            entity.fighter.adjust_max_locations(location,2,5)
            entity.fighter.pain_mod_mov += 10

        if title == 'Cracked Vertebra':
            description.append('The blow seemes to have cracked a vertebra in ' + entity.name + '\'s spine. ' + 
                'This is intensely painful and immediately reduces ' + ('his ' if entity.fighter.male else 'her ') + 
                'physical ability tremendously. ')
            entity.fighter.diseases.extend('Chronic pain, major')
            entity.fighter.adjust_max_locations(location,2,5)
            attrib_list = ['ss', 'pwr']
            for attrib in attrib_list:
                atr = getattr(entity.fighter, attrib)
                entity.fighter.mod_attribute(attrib, (atr*.5)*-1)
            entity.fighter.pain_mod_mov += 40

        if title == 'Paralysis (Neck Down)':
            description.append('The blow seemes to have severed something in ' + entity.name + '\'s spine. ' + 
                ('He ' if entity.fighter.male else 'She ') + 'is now paralyzed from the neck down, and will die within minutes. ')
            handle_state_change(entity, entities, EntityState.dead)
        
        if title == 'Bruised Bone':
            description.append('A bone has been bruised, leading to serious pain whenever pressure is placed upon the bone. ')
            entity.fighter.pain_mod_mov += 10

        if title == 'Simple Collarbone Fracture':
            description.append(entity.name + '\'s collarbone has been cracked, but is still capable of supporting weight, albeit painfully. ')
            entity.fighter.pain_mod_mov += 20

        if title == 'Complex Collarbone Fracture':
            description.append(entity.name + '\'s collarbone has been badly broken, and bone is protruding from the skin. ' + 
                ('He ' if entity.fighter.male else 'She ') + 'may not use the arm supported by the bone until healed. ')
            entity.fighter.pain_mod_mov += 40
            entity.fighter.paralyzed_locs.extend([location, location + 4, location + 8, location + 12, location + 16])
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)

        if title == 'Shattered Shoulder':
            description.append(entity.name + '\'s shoulder is shattered, and will never heal well enough to be used. ')
            entity.fighter.pain_mod_mov += 60
            entity.fighter.paralyzed_locs.extend([location, location + 4, location + 8, location + 12, location + 16])
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)

        if title == 'Cracked Ribs':
            description.append(entity.name + '\'s ribs have been cracked, making movement and deep breathing incredibly painful. ')
            entity.fighter.pain_mod_mov += 20
            entity.fighter.stamr *= 0.5

        if title == 'Badly Broken Ribs':
            description.append(entity.name + '\'s ribs are broken and protruding through the skin. All movement is intensely painful, and only short, quick breaths may be taken. ')
            entity.fighter.pain_mod_mov += 60
            entity.fighter.stamr *= 0.1
            entity.fighter.adjust_max_locations(location,2,entity.fighter.max_locations[location][2] * 0.5)
            

        if title == 'Shattered Ribs':
            description.append(entity.name + '\'s ribs are shattered, just collection of loose, bleeding bones in the body cavity.' + 
                ('He ' if entity.fighter.male else 'She ') + 'will always be more prone to internal damage in this location. ' + 
                'All movement is intensely painful, and breathing is incredibly difficult. ')
            entity.fighter.pain_mod_mov += 80
            entity.fighter.stamr *= 0.05
            entity.fighter.adjust_max_locations(location,2,entity.fighter.max_locations[location][2])
            entity.fighter.adjust_max_locations(location,1,entity.fighter.max_locations[location][1] * 0.2)            

        if title == 'Paralysis (Chest Down)':
            description.append('The blow seemes to have severed something in ' + entity.name + '\'s spine. ' + 
                ('He ' if entity.fighter.male else 'She ') + 'is now paralyzed from the chest down. ')
            i = location
            while i < 29:
                entity.fighter.paralyzed_locs.extend([i])
                i += 1
            entity.fighter.stance = FighterStance.prone
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.6)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.6)*-1)
            entity.fighter.mv *= .1
        
        if title == 'Paralysis (Waist Down)':
            description.append('The blow seemes to have severed something in ' + entity.name + '\'s spine. ' + 
                ('He ' if entity.fighter.male else 'She ') + 'is now paralyzed from the chest down. ')
            i = location
            while i < 29:
                entity.fighter.paralyzed_locs.extend([i])
                i += 1
            entity.fighter.stance = FighterStance.prone
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.5)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.5)*-1)
            entity.fighter.mv *= .1

        if title == 'Broken Pelvis':
            description.append('A sharp crack and stab of pain seems to indicate that ' + entity.name + '\'s pelvis is broken. ' + 
                ('He ' if entity.fighter.male else 'She ') + 'finds moving very painful. ')
            entity.fighter.pain_mod_mov += 30

        if title == 'Crushed Pelvis':
            description.append('An intense, radiant pain and the immediate loss of support for both legs signals that ' + entity.name + 
            '\'s pelvis is shattered. ' + ('He ' if entity.fighter.male else 'She ') + 'will never walk again. ')
            check = save_roll_un(entity.fighter.will, -40)

            if check[0] == 'cs':
                description.append('Despite the pain, ' + entity.name + ' manages to stay conscious and ease into a seated position. ')
                entity.fighter.stance = FighterStance.sitting
                entity.fighter.temp_physical_mod -= 30
            elif check[0] == 'cf':
                description.append(entity.name + ' collapses from the pain, and a portion of the shattered pelvis tears ' +
                    ('his ' if entity.fighter.male else 'her ') + 'femoral artery. ' + ('He ' if entity.fighter.male else 'She ') +
                    'is rapidly bleeding out. ')
                handle_state_change(entity, entities, EntityState.unconscious)
                entity.fighter.bleed.append([entity.fighter.max_vitae*.02,1000])
            elif check[0] == 's':
                description.append('Despite the pain of the fall, ' + ('he ' if entity.fighter.male else 'she ') + 
                'manages to remain conscious. ')
                entity.fighter.temp_physical_mod -= 40
                entity.fighter.stance = FighterStance.prone
            else:
                description.append(('He ' if entity.fighter.male else 'She ') + 
                'is knocked unconscious by the attack. ')
                handle_state_change(entity, entities, EntityState.unconscious)
                entity.fighter.temp_physical_mod -= 40
                entity.fighter.stance = FighterStance.prone

            entity.fighter.pain_mod_mov += 50
            i = location
            while i < 29:
                entity.fighter.paralyzed_locs.extend([i])
                i += 1
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.5)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.5)*-1)
            entity.fighter.mv *= .1
        
        if title == 'Simple Humerus Fracture':
            description.append('An audible crack accompanies the pain of a broken upper arm. ' + 
                entity.name + ' instantly finds ' + ('his ' if entity.fighter.male else 'her ') + 
                'arm difficult to use without pain. ')

            entity.fighter.pain_mod_mov += 20
            if location % 2 == 0: entity.fighter.atk_mod_r += -10
            else: entity.fighter.atk_mod_l += -10

        if title == 'Complex Humerus Fracture':
            description.append('A loud pop and a shard of bone poking rudely through skin announce that ' + 
                entity.name + '\'s upper arm is badly broken. ' + ('He ' if entity.fighter.male else 'She ') + 
                'will be unable to use it until healed, and every movement is agony. ')

            entity.fighter.pain_mod_mov += 40
            entity.fighter.temp_physical_mod -= 20
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
            entity.fighter.paralyzed_locs.extend([location, location + 4, location + 8, location + 12, location + 16])

        if title == 'Shattered Humerus':
            description.append('A horrifying crunch and ' + entity.name + 
                '\'s upper arm goes completely limp, the flesh bending in unnatural angles. ' + ('He ' if entity.fighter.male else 'She ') + 
                'will never again be able to use this shattered limb. ')

            entity.fighter.pain_mod_mov += 60
            entity.fighter.temp_physical_mod -= 20
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
            entity.fighter.paralyzed_locs.extend([location, location + 4, location + 8, location + 12, location + 16])
            entity.fighter.adjust_max_locations(location,2,entity.fighter.max_locations[location][2])
        
        if title == 'Hyper-extended Elbow':
            description.append('A small pop and an explosion of pain signals that ' + entity.name + 
                '\'s elbow has bent in the wrong direction. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use it if the pain of doing so can be resisted. ')
            entity.fighter.pain_mod_mov += 20
            if location % 2 == 0: entity.fighter.atk_mod_r += -10
            else: entity.fighter.atk_mod_l += -10

        if title == 'Broken Elbow':
            description.append('A loud cracking sound, sharp pain, and instability in ' + entity.name + 
                '\'s elbow shows that it has been broken. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use it if the pain of doing so can be resisted, but strength and accuracy are affected. ')
            entity.fighter.pain_mod_mov += 30
            entity.fighter.temp_physical_mod -= 20
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.05)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.05)*-1)

        if title == 'Shattered Elbow':
            description.append('The crunching, grinding noise that accompanies the blow to ' + entity.name + 
                '\'s elbow tells the tale nearly as well as the sickening way ' + ('his ' if entity.fighter.male else 'her ') + 
                'forearm goes limp. The elbow is shattered irreparably. ')
            entity.fighter.pain_mod_mov += 30
            entity.fighter.temp_physical_mod -= 20
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
            entity.fighter.paralyzed_locs.extend([location, location + 4, location + 8])
            entity.fighter.adjust_max_locations(location,2,entity.fighter.max_locations[location][2])

        if title == 'Radius Broken':
            description.append('A small pop and sharp pain is the only sign that ' + entity.name + 
                '\'s radius has been broken. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use the arm if the pain of doing so can be resisted. ')
            entity.fighter.pain_mod_mov += 10

        if title == 'Ulna Broken':
            description.append('A loud pop accompanies a new bend in ' + entity.name + 
                '\'s forearm as the second arm bone gives way. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can no longer use the arm until it is set and healed. ')
            entity.fighter.pain_mod_mov += 20
            entity.fighter.temp_physical_mod -= 20
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
            entity.fighter.paralyzed_locs.extend([location, location + 4])

        if title == 'Shattered Forearm':
            description.append('A bright stab of blinding pain, a sound like wet twigs crunching under foot, and the sight of ' + entity.name + 
                '\'s hand drooping bonelessly signals the shattering of ' + ('his ' if entity.fighter.male else 'her ') + 
                'forearm. If ' + ('he ' if entity.fighter.male else 'she ') + 'ever fights again, it will be with one arm. ')
            entity.fighter.pain_mod_mov += 30
            entity.fighter.temp_physical_mod -= 20
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.1)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.1)*-1)
            entity.fighter.paralyzed_locs.extend([location, location + 4])
            entity.fighter.adjust_max_locations(location,2,entity.fighter.max_locations[location][2])

        if title == 'Sprained Wrist':
            description.append(entity.name + '\'s wrist gives a little to the blow and now exhibits pain when used. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use it if the pain of doing so can be resisted. ')
            entity.fighter.pain_mod_mov += 10

        if title == 'Crushed/Severed Little Finger':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow catches ' + entity.name + '\'s little finger, ' + adj + 'ing it.' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use it the hand if the pain of doing so can be resisted. ')
            entity.fighter.pain_mod_mov += 10

        if title == 'Crushed/Severed Ring Finger':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow catches ' + entity.name + '\'s ring finger, ' + adj + 'ing it.' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use it the hand if the pain of doing so can be resisted, but the loss of two fingers will reduce ' +
                ('his ' if entity.fighter.male else 'her ') + 'effectiveness somewhat.')
            entity.fighter.pain_mod_mov += 20
            if location % 2 == 0: entity.fighter.atk_mod_r += -10
            else: entity.fighter.atk_mod_l += -10

        if title == 'Crushed/Severed Middle Finger':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow catches ' + entity.name + '\'s middle finger, ' + adj + 'ing it.' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use it the hand if the pain of doing so can be resisted, but the loss of three fingers will reduce ' +
                ('his ' if entity.fighter.male else 'her ') + 'effectiveness significantly.')
            entity.fighter.pain_mod_mov += 30
            if location % 2 == 0: entity.fighter.atk_mod_r += -40
            else: entity.fighter.atk_mod_l += -40

        if title == 'Crushed/Severed Index Finger':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow catches ' + entity.name + '\'s index finger, ' + adj + 'ing it.' +  
                'With only the thumb remaining, ' + ('his ' if entity.fighter.male else 'her ') + 'hand is effectively useless.')
            entity.fighter.pain_mod_mov += 40
            entity.fighter.paralyzed_locs.extend([location])
            entity.fighter.adjust_max_locations(location,2,entity.fighter.max_locations[location][2] * .5)

        if title == 'Crushed/Severed Hand':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow has ' + adj + 'ed '+ entity.name + '\'s hand. '+  
                ('His ' if entity.fighter.male else 'Her ') + 'hand is destroyed.')
            entity.fighter.pain_mod_mov += 60
            entity.fighter.paralyzed_locs.extend([location])
            entity.fighter.adjust_max_locations(location,2,entity.fighter.max_locations[location][2])
            if dam_type != 'B':
                description.append('Aterial blood spurts from the stump with every heartbeat.')
                entity.fighter.bleed.append([entity.fighter.max_vitae*.02,1000])
                entity.fighter.adjust_max_locations(location,0,entity.fighter.max_locations[location][0])
                entity.fighter.adjust_max_locations(location,1,entity.fighter.max_locations[location][1])

        if title == 'Simple Femur Fracture':
            description.append('A sharp pain signals that ' + entity.name + 
                '\'s femur has been cracked. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use the leg if the pain of doing so can be resisted. ')
            entity.fighter.pain_mod_mov += 20

        if title == 'Complex Femur Fracture':
            description.append('A wet pop is followed searing pain as ' + entity.name + 
                '\'s femur splinters and breaks. ')

            check = save_roll_un(entity.fighter.bal, -20)
            if check[0] == 'cs' or 's':
                    description.append(('He ' if entity.fighter.male else 'She ') + 'manages to remain standing. ')
            else: 
                check = save_roll_un(entity.fighter.will, -40)
                if check[0] == 'cs':
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        'Despite the pain, ' + entity.name + ' manages to stay conscious and ease into a seated position. ')
                    entity.fighter.stance = FighterStance.sitting
                    entity.fighter.temp_physical_mod -= 30
                elif check[0] == 'cf':
                    description.append(entity.name + ' collapses, and a portion of the broken femur tears ' +
                        'open an artery. ' + ('He ' if entity.fighter.male else 'She ') + 'is bleeding profusely. The pain is more than ' 
                        + ('he ' if entity.fighter.male else 'she ') + ' can take, and' + ('he ' if entity.fighter.male else 'she ') + 'falls unconscious. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.bleed.append([entity.fighter.max_vitae*.04,10])
                elif check[0] == 's':
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        'Despite the pain of the fall, ' + ('he ' if entity.fighter.male else 'she ') + 
                        'manages to remain conscious. ')
                    entity.fighter.temp_physical_mod -= 40
                    entity.fighter.stance = FighterStance.prone
                else:
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        ('He ' if entity.fighter.male else 'She ') + 'is knocked unconscious by the pain. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.temp_physical_mod -= 40
                    entity.fighter.stance = FighterStance.prone

            entity.fighter.pain_mod_mov += 40
            entity.fighter.paralyzed_locs.extend([location, location + 2, location + 4, location + 6])
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
            entity.fighter.mv *= .4

        if title == 'Shattered Femur':
            description.append('Several loud, wet pops herald the shattering of ' + entity.name + 
                '\'s femur in several smaller pieces. The leg unloads completely, wiggling like something made of jelly as '
                + entity.name + 'is thrown unceremoniously off balance. ')
                    
            check = save_roll_un(entity.fighter.bal, -40)
            if check[0] == 'cs' or 's':
                    description.append('Amazingly, ' + ('he ' if entity.fighter.male else 'she ') + 'manages to remain standing. ')
            else: 
                check = save_roll_un(entity.fighter.will, -40)
                if check[0] == 'cs':
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        'Despite the pain, ' + entity.name + ' manages to stay conscious and ease into a seated position. ')
                    entity.fighter.stance = FighterStance.sitting
                    entity.fighter.temp_physical_mod -= 30
                elif check[0] == 'cf':
                    description.append(entity.name + ' collapses, and a portion of the broken femur tears ' +
                        'open the femoral artery. ' + ('He ' if entity.fighter.male else 'She ') + 'is bleeding out rapidly. The pain is more than ' 
                        + ('he ' if entity.fighter.male else 'she ') + ' can take, and' + ('he ' if entity.fighter.male else 'she ') + 'falls unconscious. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.bleed.append([entity.fighter.max_vitae*.02,1000])
                elif check[0] == 's':
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        'Despite the pain of the fall, ' + ('he ' if entity.fighter.male else 'she ') + 
                        'manages to remain conscious. ')
                    entity.fighter.temp_physical_mod -= 40
                    entity.fighter.stance = FighterStance.prone
                else:
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        ('He ' if entity.fighter.male else 'She ') + 'is knocked unconscious by the pain. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.temp_physical_mod -= 40
                    entity.fighter.stance = FighterStance.prone

            entity.fighter.pain_mod_mov += 80
            entity.fighter.paralyzed_locs.extend([location, location + 2, location + 4, location + 6])
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
            entity.fighter.mv *= .4

        if title == 'Hyper-extended Knee':
            description.append('A small pop and a burst of pain signals that ' + entity.name + 
                '\'s knee has bent in the wrong direction. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use it if the pain of doing so can be resisted. ')
            entity.fighter.pain_mod_mov += 40
            entity.fighter.mv *= .9

        if title == 'Broken Knee':
            description.append('A wet pop and the feeling of something being very out of place is followed searing pain as ' + entity.name + 
                '\'s knee breaks. ' + ('His ' if entity.fighter.male else 'Her ') + 'leg immediately buckles. ')

            check = save_roll_un(entity.fighter.bal, -20)
            if check[0] == 'cs' or 's':
                    description.append('However, ' + ('he ' if entity.fighter.male else 'she ') + 'manages to remain standing. ')
            else: 
                check = save_roll_un(entity.fighter.will, -40)
                if check[0] == 'cs':
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the leg. ' + 
                        'Despite the pain, ' + entity.name + ' manages to stay conscious and ease into a seated position. ')
                    entity.fighter.stance = FighterStance.sitting
                    entity.fighter.temp_physical_mod -= 20
                elif check[0] == 'cf':
                    description.append(entity.name + ' collapses, and lands on the leg. ' 
                        + ' The pain is more than ' + ('he ' if entity.fighter.male else 'she ') + ' can take, and' 
                        + ('he ' if entity.fighter.male else 'she ') + 'falls unconscious. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.temp_physical_mod -= 40
                    entity.fighter.stance = FighterStance.prone
                elif check[0] == 's':
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        'Despite the pain of the fall, ' + ('he ' if entity.fighter.male else 'she ') + 
                        'manages to remain conscious. ')
                    entity.fighter.temp_physical_mod -= 30
                    entity.fighter.stance = FighterStance.prone
                else:
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        ('He ' if entity.fighter.male else 'She ') + 'is knocked unconscious by the pain. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.temp_physical_mod -= 30
                    entity.fighter.stance = FighterStance.prone

            entity.fighter.pain_mod_mov += 20
            entity.fighter.paralyzed_locs.extend([location, location + 2, location + 4, location + 6])
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
            entity.fighter.mv *= .4

        if title == 'Shattered Knee':
            description.append('A horrible crunching, grating sound and starburst of pain signal that ' + entity.name + 
                '\'s knee has been shattered. ' + ('His ' if entity.fighter.male else 'Her ') + 'leg immediately buckles. ')

            check = save_roll_un(entity.fighter.bal, -30)
            if check[0] == 'cs' or 's':
                    description.append('However, ' + ('he ' if entity.fighter.male else 'she ') + 'manages to remain standing. ')
            else: 
                check = save_roll_un(entity.fighter.will, -60)
                if check[0] == 'cs':
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the leg. ' + 
                        'Despite the pain, ' + entity.name + ' manages to stay conscious and ease into a seated position. ')
                    entity.fighter.stance = FighterStance.sitting
                    entity.fighter.temp_physical_mod -= 20
                elif check[0] == 'cf':
                    description.append(entity.name + ' collapses, and lands on the leg. ' 
                        + ' The pain is more than ' + ('he ' if entity.fighter.male else 'she ') + ' can take, and' 
                        + ('he ' if entity.fighter.male else 'she ') + 'falls unconscious. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.temp_physical_mod -= 40
                    entity.fighter.stance = FighterStance.prone
                elif check[0] == 's':
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        'Despite the pain of the fall, ' + ('he ' if entity.fighter.male else 'she ') + 
                        'manages to remain conscious. ')
                    entity.fighter.temp_physical_mod -= 30
                    entity.fighter.stance = FighterStance.prone
                else:
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        ('He ' if entity.fighter.male else 'She ') + 'is knocked unconscious by the pain. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.temp_physical_mod -= 30
                    entity.fighter.stance = FighterStance.prone

            entity.fighter.pain_mod_mov += 20
            entity.fighter.paralyzed_locs.extend([location, location + 2, location + 4, location + 6])
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
            entity.fighter.mv *= .4

        if title == 'Fibula Broken':
            description.append('A bright flash of pain in ' + entity.name + 
                '\'s shin signals that something has cracked. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use the leg if the pain of doing so can be resisted. ')
            entity.fighter.pain_mod_mov += 20

        if title == 'Tibia Broken':
            description.append('A second sharp pain and muted crack is a message that ' + entity.name + 
                '\'s second shin bone has broken. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use the leg, but it is incredibly painful. ')
            entity.fighter.pain_mod_mov += 30

        if title == 'Shattered Shin':
            description.append('A sound like a wet piece of wood being split accompanies a roaring pain in ' + entity.name + 
                '\'s shin. It shatters, and the foot bends unnaturally as the shin buckles under ' + entity.name + 
                '\'s weight. ')

            check = save_roll_un(entity.fighter.bal, -30)
            if check[0] == 'cs' or 's':
                    description.append('Amazingly, ' + ('he ' if entity.fighter.male else 'she ') + 'manages to remain standing. ')
            else: 
                check = save_roll_un(entity.fighter.will, -40)
                if check[0] == 'cs':
                    description.append(entity.name + 'falls bodily to the floor. ' + 
                        'Despite the pain of the fall, ' + entity.name + ' manages to stay conscious and ease into a seated position. ')
                    entity.fighter.stance = FighterStance.sitting
                    entity.fighter.temp_physical_mod -= 20
                elif check[0] == 'cf':
                    description.append(entity.name + ' collapses, and a portion of the broken shin tears ' +
                        'open an artery. ' + ('He ' if entity.fighter.male else 'She ') + 'is bleeding profusely. The pain is more than ' 
                        + ('he ' if entity.fighter.male else 'she ') + ' can take, and' + ('he ' if entity.fighter.male else 'she ') + 'falls unconscious. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.bleed.append([entity.fighter.max_vitae*.04,10])
                    entity.fighter.temp_physical_mod -= 40
                elif check[0] == 's':
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        'Despite the pain of the fall, ' + ('he ' if entity.fighter.male else 'she ') + 
                        'manages to remain conscious. ')
                    entity.fighter.temp_physical_mod -= 30
                    entity.fighter.stance = FighterStance.prone
                else:
                    description.append(entity.name + 'falls bodily to the floor, landing hard on the broken leg. ' + 
                        ('He ' if entity.fighter.male else 'She ') + 'is knocked unconscious by the pain. ')
                    handle_state_change(entity, entities, EntityState.unconscious)
                    entity.fighter.temp_physical_mod -= 40
                    entity.fighter.stance = FighterStance.prone

            entity.fighter.pain_mod_mov += 30
            entity.fighter.paralyzed_locs.extend([location, location + 2])
            entity.fighter.mod_attribute('ss', (entity.fighter.ss*.25)*-1)
            entity.fighter.mod_attribute('pwr', (entity.fighter.pwr*.25)*-1)
            entity.fighter.mv *= .4

        if title == 'Sprained Ankle':
            description.append(entity.name + '\'s ankle gives a little to the blow and each step is now painful. ' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use it if the pain of doing so can be resisted. ')
            entity.fighter.pain_mod_mov += 20

        if title == '1 toe destroyed':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow catches ' + entity.name + '\'s toe, ' + adj + 'ing it.' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use it the foot if the pain of doing so can be resisted. ')
            entity.fighter.pain_mod_mov += 10

        if title == '2 toes destroyed':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow catches two of ' + entity.name + '\'s toes, ' + adj + 'ing them.' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use the foot if the pain of doing so can be resisted, but the loss of two toes will reduce ' +
                ('his ' if entity.fighter.male else 'her ') + 'speed somewhat.')
            entity.fighter.pain_mod_mov += 20
            entity.fighter.mv *= .9

        if title == '3 toes destroyed':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow catches three of ' + entity.name + '\'s toes, ' + adj + 'ing them.' + ('He ' if entity.fighter.male else 'She ') + 
                'can still use the foot if the pain of doing so can be resisted, but the loss of three toes will reduce ' +
                ('his ' if entity.fighter.male else 'her ') + 'speed significantly.')
            entity.fighter.pain_mod_mov += 40
            entity.fighter.mv *= .6

        if title == '4 toes destroyed':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow catches four of ' + entity.name + '\'s toes, ' + adj + 'ing them.' + ('He ' if entity.fighter.male else 'She ') + 
                'will find it difficult to maintain balance or move with nearly all of ' +
                ('his ' if entity.fighter.male else 'her ') + 'toes' + adj + 'ed. ')
            entity.fighter.pain_mod_mov += 50
            entity.fighter.mv *= .5
            entity.fighter.temp_physical_mod -= 20

        if title == 'Crushed/Severed Foot':
            adj = ''
            if dam_type == 'B': adj = 'crush'
            else: adj = 'sever'
            description.append('The blow ' + adj + 'ed ' + entity.name + '\'s foot.' + ('He ' if entity.fighter.male else 'She ') + 
                'must balance on the heel, as the rest of the foot is destroyed. ')
            entity.fighter.pain_mod_mov += 60
            entity.fighter.mv *= .4
            entity.fighter.temp_physical_mod -= 30
            entity.fighter.paralyzed_locs.extend([location])
            entity.fighter.adjust_max_locations(location,2,entity.fighter.max_locations[location][2])
            if dam_type != 'B':
                entity.fighter.adjust_max_locations(location,0,entity.fighter.max_locations[location][0])
                entity.fighter.adjust_max_locations(location,1,entity.fighter.max_locations[location][1])

        if title != 'None' and entity.state is not EntityState.dead:
            entity.fighter.injuries.extend([entity.fighter.name_location(location) + ': ' + title])
                

    return description

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

def handle_state_change(entity, entities, state) -> None:
    entity.state = state
    if entity.state == EntityState.dead:
        entity.char = '#'
        entity.color = libtcodpy.crimson
        entity.fighter = None
        for item in entities:
            if hasattr(item, 'fighter'):
            #Handle target removal if dead
                for target in item.fighter.targets:
                    if target is entity:
                        del item.fighter.targets[item.fighter.targets.index(target)]

def init_combat(curr_actor, order, command) -> (dict, int, int, list):
    game_state = GameStates.menu
    combat_phase = CombatPhase.action
    messages = []
    #CHeck to see if player can afford to attack
    wpn_ap = []
    for wpn in curr_actor.weapons:
        for atk in wpn.attacks:
            cs = curr_actor.determine_combat_stats(wpn, atk)
            wpn_ap.append(cs.get('final ap'))
    min_ap = min(wpn_ap)
    curr_actor.fighter.action = []
    if curr_actor.fighter.ap >= min_ap:
        curr_actor.fighter.action.append('Engage')
    if curr_actor.fighter.ap >= curr_actor.fighter.walk_ap:
        curr_actor.fighter.action.append('Disengage')
    if len(order) > 1 and len(curr_actor.fighter.action) >= 1: 
        curr_actor.fighter.action.append('Wait')
    if len(curr_actor.fighter.action) >= 2:
        curr_actor.fighter.action.append('End Turn')
        game_state = GameStates.menu
    else:
        curr_actor.fighter.end_turn = True
        combat_phase = CombatPhase.action
        menu_dict = None
        game_state = GameStates.default
        return menu_dict, combat_phase, game_state, order, messages

    combat_menu_header = 'What do you wish to do?'

    try:
        if command.get('Wait'):
            messages.append('You decide to wait for your opponents to act')
            order.append(order.pop(0))
            combat_phase = CombatPhase.action
            game_state = GameStates.default                  
        elif command.get('Engage'):
            messages.append('You decide to attack')
            combat_phase = CombatPhase.weapon
        elif command.get('Disengage'):
            messages.append('You decide to disengage from ' + curr_actor.fighter.targets[0].name)
            combat_phase = CombatPhase.disengage
            game_state = GameStates.default 
        elif command.get('End Turn'):
            messages.append('You decide to end your turn')
            curr_actor.fighter.end_turn = True
            order.append(order.pop(0))
            combat_phase = CombatPhase.action
            game_state = GameStates.default 
    except:
        pass


    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}

    return menu_dict, combat_phase, game_state, order, messages

def change_actor(order, entities, combat_phase, logs) -> (int, list):
    messages = []
    log = logs[2]
    if len(order) == 0:
        log.add_message(Message('The round has ended. '))
        combat_phase = CombatPhase.init
        global_vars.round_num  += 1
        order = entities
    else:
        #Check and see if anyone can still act
        remaining_fighters = 0
        for entity in order:
            if entity.fighter.end_turn or entity.state == EntityState.unconscious:
                order.remove(entity)
            remaining_fighters = len(order)
        
        if remaining_fighters == 0: 
            log.add_message(Message('The round has ended. '))
            combat_phase = CombatPhase.init
            global_vars.round_num  += 1
            order = entities

    for message in messages:
            log.add_message(Message(message))

    return combat_phase, order




def phase_init(entities) -> list:
    fighters = []
    for entity in entities:
        if hasattr(entity, 'fighter'):
            fighters.append(entity)
            entity.fighter.end_turn = False
    

    #Sort the entities by initiative
    if len(entities) > 1:    
        order = turn_order(entities)
    else:
        order = entities

    return order

def phase_action(curr_actor, players, entities, order, command, logs, game_map) -> (dict,int,list):
    combat_phase = CombatPhase.action
    game_state = GameStates.default
    menu_dict = None
    messages = []
    log = logs[2]
    status_log = logs[1]  


    if hasattr(curr_actor.fighter, 'ai'):
        messages, combat_phase = order[0].fighter.ai.take_turn(order[0], entities, combat_phase)
        combat_menu_header = '' 
        
    
    else:
        if command is not None:
            #Check and see if player has a target in zoc
            if len(curr_actor.fighter.targets) == 0:
                if curr_actor.fighter.ap >= curr_actor.fighter.walk_ap:
                    if command[0] == 'move' or 'spin':
                        moved = move_actor(game_map, curr_actor, entities, players, command, logs)
                        if moved:
                            curr_actor.fighter.mod_attribute('ap', -curr_actor.fighter.walk_ap)
                            curr_actor.fighter.targets = aoc_check(entities, curr_actor)
                            if len(curr_actor.fighter.targets) != 0:
                                entries = gen_status_panel(curr_actor.fighter.targets[0])
                                status_log.messages.clear()
                                for entry in entries:
                                    status_log.add_message(Message(entry))
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

def phase_weapon(player, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = None
    messages = []
    log = logs[2]

    #Choose your weapon
    combat_menu_header = 'Choose your weapon'
    player.fighter.action.clear()
    for wpn in player.weapons:
        if wpn.name not in player.fighter.action:
            player.fighter.action.append(wpn.name)
    for option in player.fighter.action:
        if command is not None:
            if command.get(option):
                messages.append('You decide to use ' + option)
                for wpn in player.weapons:
                    if option == wpn.name:
                        if len(player.fighter.combat_choices) == 0:   
                            player.fighter.combat_choices.append(wpn)
                combat_phase = CombatPhase.option
    
    for message in messages:
            log.add_message(Message(message))

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': player.fighter.action, 'mode': False}

    return combat_phase, menu_dict

def phase_option(player, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = None
    messages = []
    log = logs[2]

    #Choose the base attack type (stab, slash, etc)
    combat_menu_header = 'How would you like to attack your target?'
    player.fighter.action.clear()
    #Determine AP needs
    for atk in player.fighter.combat_choices[0].attacks:
        cs = player.determine_combat_stats(player.fighter.combat_choices[0], atk)
        atk_final_ap = cs.get('final ap')
        if player.fighter.ap >= atk_final_ap:
            player.fighter.action.append(atk.name)
    for option in player.fighter.action:
        if command is not None:
            if command.get(option):
                for atk in player.fighter.combat_choices[0].attacks:
                    if atk.name == option:
                        player.fighter.combat_choices.append(atk)
                messages.append('You decide to ' + option)
                combat_phase = CombatPhase.location
    
    for message in messages:
            log.add_message(Message(message))

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': player.fighter.action, 'mode': False}

    return combat_phase, menu_dict

def phase_location(player, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = None
    messages = []
    log = logs[2]

    #Choose the hit location
    combat_menu_header = 'Where do you want to aim?'
    curr_target = player.fighter.targets[0]
    attack = player.fighter.combat_choices[1]
    #Determine valid locations
    valid_locs = determine_valid_locs(player, curr_target, attack)
    #Prune list to only valid
    locations = prune_list(curr_target.fighter.get_locations(), valid_locs, True, False)
    player.fighter.action = locations
    if command is not None:    
        for option in player.fighter.action:
            if command.get(option):
                choice = command.get(option)
                if choice: 
                    player.fighter.combat_choices.append(curr_target.fighter.name_location(option))   
                    player.fighter.action = determine_valid_angles(curr_target.fighter.name_location(option))
                    messages.append('You aim for ' + player.fighter.targets[0].name + '\'s ' + option)
                    combat_phase = CombatPhase.option2
    
    for message in messages:
            log.add_message(Message(message))

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': player.fighter.action, 'mode': False}
    
    return combat_phase, menu_dict

def phase_option2(player, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = None
    messages = []
    log = logs[2]
    #Choose the angle of attack
    combat_menu_header = 'What angle would you like to attack from?'
    if command is not None:
        for option in player.fighter.action:
            choice = command.get(option)
            if choice:
                player.fighter.combat_choices.append(angle_id(option))
                messages.append('You decide to use the ' + option + ' angle.')
                player.fighter.action = ['Accept', 'Restart']
                combat_phase = CombatPhase.confirm

    for message in messages:
            log.add_message(Message(message))

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': player.fighter.action, 'mode': False}
    
    return combat_phase, menu_dict

def phase_confirm(player, entities, command, logs, combat_phase) -> (int, dict):
    #Verify choices and continue or restart

    #Variable setup
    combat_menu_header = None
    menu_dict = None
    messages = []
    log = logs[2]
    curr_target = player.fighter.targets[0]
    weapon = player.fighter.combat_choices[0]
    attack = player.fighter.combat_choices[1]
    location = player.fighter.combat_choices[2]
    angle = player.fighter.combat_choices[3]
    cs = player.determine_combat_stats(weapon, attack, location, angle)

    final_to_hit = cs.get('to hit')
    dodge_mod = cs.get('dodge mod')
    final_ap = cs.get('final ap')
    parry_mod = cs.get('parry mod')
    total_ep = sum([cs.get('b psi'), cs.get('s psi'), cs.get('p psi'), cs.get('t psi')])

    if len(curr_target.fighter.attacker_history) > 0:
        history_mod = calc_history_modifier(curr_target, attack.name, location, angle)
        dodge_mod += history_mod
        parry_mod += history_mod
    wpn_title = attack.name
    loc_name = player.fighter.targets[0].fighter.name_location(location)
    angle_name = angle_id(angle)
    

    combat_menu_header = ('You are attacking with ' + wpn_title + ', aiming at ' + curr_target.name + '\'s ' 
        + loc_name + ' from a ' + angle_name + ' angle. ' 
        + ' For this attack, you will have a: ' + str(final_to_hit) +  '% chance to hit, and do up to ' 
        + str(total_ep) + ' PSI damage.' + ' Your opponent will get a ' + str(parry_mod) 
        + '% modifier to parry, and a ' + str(dodge_mod) + '% modifier to dodge. \n' + 
        'It will cost you ' + str(final_ap) + ' of your remaining ' + str(player.fighter.ap) + ' AP to attack. \n'
        + ' Would you like to continue, or modify your choices?')

    player.fighter.action = ['Accept', 'Restart']
    if command is not None:
        if command.get('Accept'):
            messages, combat_phase = perform_attack(player, entities, final_to_hit, curr_target, cs, combat_phase)
            
            #See if player has AP for repeat
            if player.fighter.ap >= final_ap:           
                combat_phase = CombatPhase.repeat
            else:
                combat_phase = combat_phase.action

        if command.get('Restart'):
            #Reset vars
            player.fighter.combat_choices.clear()
            combat_phase = CombatPhase.action

    for message in messages:
            log.add_message(Message(message))

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': player.fighter.action, 'mode': False}

    return combat_phase, menu_dict

def phase_repeat(player, command, logs, combat_phase) -> (int, dict):
    #Repeat last attack?
    combat_menu_header = None
    menu_dict = None
    messages = []
    log = logs[2]

    combat_menu_header = 'Would you like to repeat the last attack, or start a new attack strategy?'
    player.fighter.action = ['Repeat', 'New']
    if command is not None:
        if command.get('Repeat'):
            combat_phase = CombatPhase.confirm

                    
        if command.get('New'):
            #Reset vars
            player.fighter.combat_choices.clear()
            combat_phase = CombatPhase.action

    for message in messages:
            log.add_message(Message(message))

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': player.fighter.action, 'mode': False}

    return combat_phase, menu_dict

def phase_defend(player, enemy, entities, command, logs, combat_phase) -> (int, int, dict):
    #Variable setup
    combat_menu_header = None
    menu_dict = None
    messages = []
    log = logs[2]
    cs = enemy.fighter.ai.mods
    message = None
    effects = []
    can_dodge = False
    can_parry = False
    attack = enemy.fighter.combat_choices[1]
    atk_name = enemy.fighter.combat_choices[1].name 
    angle_name = angle_id(enemy.fighter.combat_choices[3])
    loc_name = player.fighter.name_location(enemy.fighter.combat_choices[2])
    final_to_hit = cs.get('to hit')
    parry_mod = cs.get('parry mod')
    dodge_mod = cs.get('dodge mod')
    game_state = GameStates.default

    #Find history mod
    if len(player.fighter.attacker_history) > 0:
        history_mod = calc_history_modifier(player, atk_name, enemy.fighter.combat_choices[2], enemy.fighter.combat_choices[3])
        dodge_mod += history_mod
        parry_mod += history_mod

    #Find chances and see if player can parry/dodge
    parry_chance = player.fighter.deflect + parry_mod
    dodge_chance = player.fighter.dodge + dodge_mod
    cs_p = player.determine_combat_stats(player.weapons[0],player.weapons[0].attacks[0])
    parry_ap = cs_p.get('parry ap')
    if player.fighter.ap >= player.fighter.walk_ap: can_dodge = True
    if player.fighter.ap >= parry_ap: can_parry = True
    header_items = []

    #Choose how to defend '
    header_items.append(enemy.name + ' is attacking you in the ' + loc_name + ' with a ' + atk_name + ' from a ' + 
                angle_name + ' direction. \n' )
    player.fighter.action = ['Take the hit. ']
    if can_dodge:
        header_items.append('You have a ' + str(dodge_chance) + ' percent chance to dodge the attack at a cost of ' + str(player.fighter.walk_ap) + ' ap. \n')
        player.fighter.action.append('Dodge')
    if can_parry:
        header_items.append('You have a ' + str(parry_chance) + ' percent chance to parry the attack at a cost of ' + str(parry_ap) + ' ap. \n')
        player.fighter.action.append('Parry')
    if can_dodge or can_parry:
        game_state = GameStates.menu
        header_items.append('What would you like to do? ')
        combat_menu_header = ''.join(header_items)
        if command is not None:
            if command.get('Take the hit. '):
                effects = apply_dam(player, entities, enemy.fighter.ai.atk_result[0], enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.ai.atk_result[1], enemy.fighter.combat_choices[2], cs)
            if command.get('Dodge'):
                check = save_roll_con(player.fighter.dodge, dodge_mod, enemy.fighter.ai.atk_result[0], final_to_hit)
                #Remove ap and stam
                player.fighter.mod_attribute('ap', -player.fighter.walk_ap)
                player.fighter.mod_attribute('stamina', -player.fighter.base_stam_cost)
                if check == 's':
                    message = ('You dodged the attack. ')
                else:
                    effects = apply_dam(player, entities, enemy.fighter.ai.atk_result[0], enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.ai.atk_result[1], enemy.fighter.combat_choices[2], cs)
            if command.get('Parry'):
                check = save_roll_con(player.fighter.deflect, parry_mod, enemy.fighter.ai.atk_result[0], final_to_hit)
                #Remove ap and stam
                player.fighter.mod_attribute('stamina', -(player.weapons[0].stamina*player.fighter.base_stam_cost))
                player.fighter.mod_attribute('ap', -parry_ap)
                if check == 's':
                    message = ('You parried the attack. ')
                else:
                    effects = apply_dam(player, entities, enemy.fighter.ai.atk_result[0], enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.ai.atk_result[1], enemy.fighter.combat_choices[2], cs)
    else:
        effects = apply_dam(player, entities, enemy.fighter.ai.atk_result[0], enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.ai.atk_result[1], enemy.fighter.combat_choices[2], cs)
    
    if message:
        messages.append(message)
        combat_phase = CombatPhase.action
    if effects:
        enemy.fighter.ai.atk_success = True
        for effect in effects:
            messages.append(effect)
        combat_phase = CombatPhase.action
    
    if player.fighter.disengage:
        combat_phase == CombatPhase.disengage
        
    for message in messages:
            log.add_message(Message(message))

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': player.fighter.action, 'mode': False}

    return combat_phase, game_state, menu_dict




