import global_vars
import options
from enums import CombatPhase, MenuTypes, EntityState, GameStates, FighterStance
from game_messages import Message
from utilities import inch_conv, roll_dice, prune_list, entity_angle, save_roll_con, save_roll_un, find_defense_probability, itersubclasses
from game_map import cells_to_keys, get_adjacent_cells, command_to_offset
from combat_functions import (aoc_check, turn_order, strafe_control, move_actor, init_combat, attack_filter, determine_valid_angles, determine_valid_locs, angle_id, 
    calc_final_mods, perform_attack, perform_maneuver, find_defense_probability, damage_controller, get_adjacent_cells, valid_maneuvers, remove_maneuver, apply_maneuver,
    apply_injuries, apply_injury_effects, apply_stability_damage )

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

def phase_action(active_entity, players, entities, order, command, logs, game_map) -> (dict,int,list):
    combat_phase = CombatPhase.action
    game_state = GameStates.default
    menu_dict = dict()
    messages = []
    log = logs[2]
    status_log = logs[1]  


    if len(command) != 0:
        #Check and see if entity has a target in aoc
        if len(active_entity.fighter.targets) == 0:
            if isinstance(command, str):
                if command == 'strafe': 
                    message = strafe_control(active_entity)
                    log.add_message(message)
            elif len(command) != 0: 
                if isinstance(command, dict):
                    if command.get('End Turn'):
                        active_entity.fighter.end_turn = True
                        combat_phase = CombatPhase.action
                elif active_entity.fighter.ap >= active_entity.fighter.walk_ap:
                    if command[0] in ['move','spin','prone','stand','kneel']:
                        moved = move_actor(game_map, active_entity, entities, command, logs)                         

                    if global_vars.debug: print(active_entity.name + ' ap:' + str(active_entity.fighter.ap))

                    if len(active_entity.fighter.targets) != 0:
                        menu_dict, combat_phase, game_state, order, messages = init_combat(active_entity, order, command)
                                
                else:
                    active_entity.fighter.end_turn = True
                    combat_phase = CombatPhase.action
        else:
            menu_dict, combat_phase, game_state, order, messages = init_combat(active_entity, order, command)
    else:
        if len(active_entity.fighter.targets) != 0:    
            menu_dict, combat_phase, game_state, order, messages = init_combat(active_entity, order, command)

    for message in messages:
        log.add_message(Message(message))

    return menu_dict, combat_phase, game_state, order

def phase_weapon(active_entity, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    valid = False
    

    #Choose your weapon
    combat_menu_header = 'Choose your weapon'
    active_entity.fighter.action.clear()
    weapons = set()
    for loc in [19,20,27,28]:
        w = active_entity.fighter.equip_loc.get(loc)
        if w is None: continue
        if w.weapon:
            weapons.add(w)

    for wpn in weapons:
        for atk in wpn.attacks:
            valid = attack_filter(active_entity, active_entity.fighter.curr_target, wpn, atk)
            if valid:              
                if wpn.name not in active_entity.fighter.action:
                    active_entity.fighter.action.append(wpn.name)

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
    
    for option in active_entity.fighter.action:
        if len(command) != 0:
            if command.get(option):
                if not hasattr(active_entity.fighter, 'ai'):
                    messages.append('You decide to use ' + option)
                for wpn in weapons:
                    if option == wpn.name:
                        if len(active_entity.fighter.combat_choices) == 0:   
                            active_entity.fighter.combat_choices.append(wpn)
                menu_dict = dict()
                combat_phase = CombatPhase.option
    
    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

        

    return combat_phase, menu_dict

def phase_option(active_entity, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    valid = False

    weapons = set()
    for loc in [19,20,27,28]:
        w = active_entity.fighter.equip_loc.get(loc)
        if w is None: continue
        if w.weapon:
            weapons.add(w)

    #Choose the base attack type (stab, slash, etc)
    combat_menu_header = 'How would you like to attack your target?'
    active_entity.fighter.action.clear()
    #Create a set of possible attacks for all weapons that match the weapon name
    possible_attacks = set()
    for wpn in weapons:
        if wpn.name == active_entity.fighter.combat_choices[0].name:
            possible_attacks.update(wpn.attacks)

    #Determine if attack is valid and enter it as an option if so
    for atk in possible_attacks:
        valid = attack_filter(active_entity, active_entity.fighter.curr_target, active_entity.fighter.combat_choices[0], atk)
        if valid and not atk.name in active_entity.fighter.action:
            active_entity.fighter.action.append(atk.name)
    
    
    #Sort the list of objects alphabetically using the name attribute     
    active_entity.fighter.action.sort()

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
    
    for option in active_entity.fighter.action:
        if len(command) != 0:
            if hasattr(active_entity.fighter,'ai') or len(active_entity.fighter.combat_choices) <= 2:
                if command.get(option):
                    if not hasattr(active_entity.fighter, 'ai'):
                        for w in weapons:
                            if w.name == active_entity.fighter.combat_choices[0].name:
                                for atk in w.attacks:
                                    if atk.name == option:
                                        active_entity.fighter.combat_choices.append(atk)
                                        active_entity.fighter.combat_choices[0] = w #Used to make sure correct unarmed 'weapon' is used
                                        messages.append('You decide to ' + option)
                                        break
                    menu_dict = dict()
                    combat_phase = CombatPhase.location
            elif len(command) != 0: #Bug catcher
                if global_vars.debug: print('Too many combat choices')
    
    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default


    return combat_phase, menu_dict

def phase_location(active_entity, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]

    #Choose the hit location
    combat_menu_header = 'Where do you want to aim?'
    curr_target = active_entity.fighter.curr_target
    attack = active_entity.fighter.combat_choices[1]
    #Determine valid locations
    valid_locs = determine_valid_locs(active_entity, curr_target, attack)
    #Prune list to only valid
    locations = prune_list(curr_target.fighter.get_locations(), valid_locs, True, False)
    active_entity.fighter.action = locations
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
    
    if len(command) != 0:    
        for option in active_entity.fighter.action:
            if command.get(option):
                choice = command.get(option)
                if choice: 
                    if not hasattr(active_entity.fighter, 'ai'):
                        active_entity.fighter.combat_choices.append(curr_target.fighter.name_location(option))
                        messages.append('You aim for ' + curr_target.name + '\'s ' + option)   
                    active_entity.fighter.action = determine_valid_angles(curr_target.fighter.name_location(option), attack)
                    menu_dict = dict()
                    combat_phase = CombatPhase.option2
    
    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    return combat_phase, menu_dict

def phase_option2(active_entity, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    #Choose the angle of attack
    combat_menu_header = 'What angle would you like to attack from?'
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
    if len(command) != 0:
        for option in active_entity.fighter.action:
            choice = command.get(option)
            if choice:
                if not hasattr(active_entity.fighter, 'ai'):
                    active_entity.fighter.combat_choices.append(angle_id(option))
                    messages.append('You decide to use the ' + option + ' angle.')
                    menu_dict = dict()
                active_entity.fighter.action = ['Accept', 'Restart']
                combat_phase = CombatPhase.confirm

    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

        
    
    return combat_phase, menu_dict

def phase_confirm(active_entity, entities, command, logs, combat_phase) -> (int, dict, object):
    #Verify choices and continue or restart

    #Variable setup
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    missed = False
    log = logs[2]
    curr_target = active_entity.fighter.targets[0]
    attack = active_entity.fighter.combat_choices[1]
    location = active_entity.fighter.combat_choices[2]
    angle = active_entity.fighter.combat_choices[3]
    wpn_title = attack.name
    loc_name = active_entity.fighter.targets[0].fighter.name_location(location)
    angle_name = angle_id(angle)
    
    cs = calc_final_mods(active_entity, curr_target)

    
    final_to_hit = cs.get('to hit')
    p_hit = cs.get('p_hit')
    p_dodge_mod = cs.get('p_dodge')
    final_ap = cs.get('final ap')
    p_parry_mod = cs.get('p_parry')
    total_ep = cs.get('total ep')

    #Normalize hit chance if over 100%
    if p_hit >= 100: p_hit = 99

    combat_menu_header = ('You are attacking with ' + wpn_title + ', aiming at ' + curr_target.name + '\'s ' 
        + loc_name + ' from a ' + angle_name + ' angle. ' 
        + ' For this attack, you will have a: ' + str(p_hit) +  '% chance to hit, and do up to ' 
        + str(total_ep) + ' PSI damage.' + ' Your opponent will get a ' + str(p_parry_mod) 
        + '% modifier to parry, and a ' + str(p_dodge_mod) + '% modifier to dodge. \n' + 
        'It will cost you ' + str(final_ap) + ' of your remaining ' + str(active_entity.fighter.ap) + ' AP to attack. \n'
        + ' Would you like to continue, or modify your choices?')

    active_entity.fighter.action = ['Accept', 'Restart']

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}

    if len(command) != 0:
        if command.get('Accept'):
            active_entity.fighter.last_atk_ap = final_ap
            messages, combat_phase, active_entity, missed = perform_attack(active_entity, entities, final_to_hit, curr_target, cs, combat_phase)
            active_entity.fighter.acted = True
            active_entity.fighter.action.clear()
        if command.get('Restart'):
            #Reset vars
            combat_phase = CombatPhase.action
        
        menu_dict = dict()

    if missed:
        min_ap = curr_target.get_min_ap()
        if curr_target.fighter.ap >= min_ap and (active_entity.x, active_entity.y) in curr_target.fighter.aoc:
            curr_target.fighter.entities_opportunity_attacked.append(active_entity)
            curr_target.fighter.counter_attack.append(active_entity)
            if hasattr(curr_target.fighter, 'ai'):
                messages.append('You missed, allowing ' + curr_target.name + ' to counter-attack.')
            else:
                messages.append(active_entity.name + ' missed, giving you a chance to counter-attack.')
            active_entity = curr_target

        else:
            if hasattr(curr_target.fighter, 'ai'):
                messages.append('You missed.')
            else:
                messages.append(active_entity.name + ' missed.')
                
        combat_phase = CombatPhase.action

    if combat_phase not in [CombatPhase.repeat, CombatPhase.defend, CombatPhase.confirm]:
        for e in entities:
            if e.fighter is not None:
                e.fighter.combat_choices.clear()

    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
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

def phase_defend(active_entity, enemy, entities, command, logs, combat_phase) -> (int, int, dict, object):
    #Variable setup
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    message = None
    effects = []
    can_dodge = False
    can_parry = False
    atk_name = enemy.fighter.combat_choices[1].name 
    angle_name = angle_id(enemy.fighter.combat_choices[3])
    location = enemy.fighter.combat_choices[2]
    loc_name = active_entity.fighter.name_location(enemy.fighter.combat_choices[2])
    game_state = GameStates.default
    header_items = []
    def_margin = None
    atk_margin = None
    rolls = None
    hit = False
    auto_block = False


    cs = calc_final_mods(enemy, active_entity)
    
    final_to_hit = cs.get('to hit')
    dodge_mod = cs.get('dodge mod')
    parry_mod = cs.get('parry mod')

    for loc in [19,20,27,28]:
        if active_entity.fighter.equip_loc.get(loc).weapon:
            block_w = active_entity.fighter.equip_loc.get(loc)
    


    #Find chances and see if active_entity can parry/dodge
    cs_p = active_entity.determine_combat_stats(block_w,block_w.attacks[0])
    parry_ap = cs_p.get('parry ap')
    if active_entity.fighter.ap >= active_entity.fighter.walk_ap: can_dodge = True
    if active_entity.fighter.ap >= parry_ap: can_parry = True
    if active_entity in enemy.fighter.counter_attack: 
        can_parry = False
        dodge_mod -= 50
        cs['dodge mod'] = dodge_mod
        enemy.fighter.counter_attack.clear()


    #Normalized (0-99) percentage scale of probabilities to p/d/b
    parry_chance = find_defense_probability(final_to_hit, (active_entity.fighter.get_attribute('deflect') + parry_mod))
    dodge_chance = find_defense_probability(final_to_hit, (active_entity.fighter.get_attribute('dodge') + dodge_mod))
    block_chance = find_defense_probability(final_to_hit, (active_entity.fighter.best_combat_skill.rating + parry_mod))


    #Choose how to defend '
    header_items.append(enemy.name + ' is attacking you in the ' + loc_name + ' with a ' + atk_name + ' from a ' + 
                angle_name + ' direction. \n' )
    active_entity.fighter.action = ['Take the hit']
    if can_dodge:
        header_items.append('You have a ' + str(dodge_chance) + ' percent chance to dodge the attack at a cost of ' + str(active_entity.fighter.walk_ap) + ' ap. \n')
        active_entity.fighter.action.append('Dodge')
    if can_parry:
        header_items.append('You have a ' + str(parry_chance) + ' percent chance to parry the attack at a cost of ' + str(parry_ap) + ' ap. \n')
        active_entity.fighter.action.append('Parry')
        #Determine if can block
        if enemy.fighter.combat_choices[2] <=2:
            if 0 < active_entity.fighter.l_blocker or active_entity.fighter.r_blocker:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                active_entity.fighter.action.append('Block')
        elif enemy.fighter.combat_choices[2] in [3,5,7,9,11,13,15,19]:
            if 0 < active_entity.fighter.r_blocker:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                active_entity.fighter.action.append('Block')
        elif enemy.fighter.combat_choices[2] in [4,6,8,10,12,14,16,20]:
            if 0 < active_entity.fighter.l_blocker:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                active_entity.fighter.action.append('Block')
        elif enemy.fighter.combat_choices[2] in [17,21,23,25]:
            if 0 < active_entity.fighter.locations[25][2]:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                active_entity.fighter.action.append('Block')
        elif enemy.fighter.combat_choices[2] in [18,22,24,26]:
            if 0 < active_entity.fighter.locations[26][2]:
                header_items.append('You have a ' + str(block_chance) + ' percent chance to block the attack at a cost of ' + str(parry_ap) + ' ap. \n')
                active_entity.fighter.action.append('Block')
    if can_dodge or can_parry:
        game_state = GameStates.menu
        header_items.append('What would you like to do? ')
        combat_menu_header = ''.join(header_items)
        menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
        if len(command) != 0:
            if command.get('Take the hit'):
                hit = True
                effects = damage_controller(active_entity, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
            if command.get('Dodge'):
                check, def_margin, atk_margin = save_roll_con(active_entity.fighter.get_attribute('dodge'), dodge_mod, enemy.fighter.atk_result, final_to_hit)
                #Remove ap and stam
                active_entity.fighter.mod_attribute('ap', -active_entity.fighter.walk_ap)
                active_entity.fighter.mod_attribute('stamina', -active_entity.fighter.base_stam_cost)
                if check == 's':
                    if not hasattr(active_entity.fighter, 'ai'): message = ('You dodged the attack. ')
                    else: message = (active_entity.name + ' dodged the attack. ')
                elif location not in active_entity.fighter.auto_block_locs:
                    hit = True
                    effects = damage_controller(active_entity, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
                else: auto_block = True
            if command.get('Parry'):
                check, def_margin, atk_margin = save_roll_con(active_entity.fighter.get_attribute('deflect'), parry_mod, enemy.fighter.atk_result, final_to_hit)
                #Remove ap and stam
                active_entity.fighter.mod_attribute('stamina', -(block_w.stamina*active_entity.fighter.base_stam_cost))
                active_entity.fighter.mod_attribute('ap', -parry_ap)
                if check == 's':
                    if not hasattr(active_entity.fighter, 'ai'): message = ('You parried the attack. ')
                    else: message = (active_entity.name + ' parried the blow. ')
                elif location not in active_entity.fighter.auto_block_locs:
                    hit = True
                    effects = damage_controller(active_entity, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
                else: auto_block = True
            if command.get('Block'):
                check, def_margin, atk_margin = save_roll_con(active_entity.fighter.best_combat_skill.rating, parry_mod, enemy.fighter.atk_result, final_to_hit)
                #Remove ap and stam
                if location not in active_entity.fighter.auto_block_locs:
                    active_entity.fighter.mod_attribute('stamina', -(block_w.stamina*active_entity.fighter.base_stam_cost))
                    active_entity.fighter.mod_attribute('ap', -parry_ap)
                else:
                    auto_block = True
                if check == 's':
                    if not hasattr(active_entity.fighter, 'ai'): message = ('You blocked the attack. ')
                    else: message = (active_entity.name + ' blocked the blow. ')
                    #Determine blocker to remove from
                    if enemy.fighter.combat_choices[2] <=2:
                        if active_entity.fighter.l_blocker > active_entity.fighter.r_blocker:
                            blocker = 16
                        else: blocker = 15
                    elif enemy.fighter.combat_choices[2] in [3,5,7,9,11,13,15,19]: blocker = 15
                    elif enemy.fighter.combat_choices[2] in [4,6,8,10,12,14,16,20]: blocker = 16
                    elif enemy.fighter.combat_choices[2] in [17,21,23,25]: blocker = 25
                    elif enemy.fighter.combat_choices[2] in [18,22,24,26]: blocker = 26


                    
                    effects = damage_controller(active_entity, enemy, blocker, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result*.2, enemy.fighter.atk_result, cs, entities)
                else:
                    hit = True
                    effects = damage_controller(active_entity, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
            
            menu_dict = dict()
    else:
        if location not in active_entity.fighter.auto_block_locs:
            hit = True
            effects = damage_controller(active_entity, enemy, location, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result, enemy.fighter.atk_result, cs, entities)
        else:
            auto_block = True
    
    if auto_block:
        if not hasattr(active_entity.fighter, 'ai'): message = ('Your guard automatically blocked the attack. ')
        else: message = (active_entity.name + 's guard automatically blocked the blow. ')
        #Determine blocker to remove from
        if enemy.fighter.combat_choices[2] <=2:
            if active_entity.fighter.l_blocker > active_entity.fighter.r_blocker:
                blocker = 16
            else: blocker = 15
        elif enemy.fighter.combat_choices[2] in [3,5,7,9,11,13,15,19]: blocker = 15
        elif enemy.fighter.combat_choices[2] in [4,6,8,10,12,14,16,20]: blocker = 16
        elif enemy.fighter.combat_choices[2] in [17,21,23,25]: blocker = 25
        elif enemy.fighter.combat_choices[2] in [18,22,24,26]: blocker = 26

        effects = damage_controller(active_entity, enemy, blocker, enemy.fighter.combat_choices[1].damage_type[0], enemy.fighter.dam_result*.2, enemy.fighter.atk_result, cs, entities)
        

    if message or effects:
        combat_phase = CombatPhase.action
        
        if message:
            messages.append(message)

        if effects:
            for effect in effects:
                messages.append(effect)
        if active_entity.state == EntityState.conscious:
            if active_entity.fighter.disengage:       
                combat_phase = CombatPhase.disengage
                game_state = GameStates.default
                menu_dict = dict()
            elif active_entity.fighter.feint and not hit:
                active_entity.fighter.counter_attack.append(enemy)
                enemy.fighter.combat_choices.clear()
                combat_phase = CombatPhase.weapon
            else:
                active_entity.fighter.action.clear()
        #Show rolls
        if options.show_rolls: 
            if atk_margin is not None and def_margin is not None:
                rolls = active_entity.name + ' had a margin of success of ' + str(def_margin) + ', while ' + enemy.name + ' had a margin of ' + str(atk_margin) + '. '
            elif atk_margin is not None:
                rolls = enemy.name + ' had a margin of success of ' + str(atk_margin) + '. '
            if rolls is not None: messages.insert(0, rolls)
        
        active_entity = enemy
        
        if active_entity.player:
            #See if active_entity has AP for repeat
            if active_entity.fighter.ap >= active_entity.fighter.last_atk_ap:           
                locs = determine_valid_locs(active_entity, enemy, active_entity.fighter.combat_choices[1])
                #Make sure location is still valid
                if active_entity.fighter.combat_choices[2] in locs:           
                    combat_phase = CombatPhase.repeat
                    game_state = GameStates.menu
            else:
                active_entity.fighter.combat_choices.clear()



    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default
        

    return combat_phase, game_state, menu_dict, active_entity

def phase_disengage(active_entity, entities, command, logs, combat_phase, game_map) -> (int, dict, object):
    combat_menu_header = 'Use the directional movement keys to move. '
    active_entity.fighter.disengage = True 
    fov_recompute = False
    messages = []
    log = logs[2]

    weapons = []
    for loc in [19,20,27,28]:
        w = active_entity.fighter.equip_loc.get(loc)
        if w is None: continue
        if w.weapon:
            weapons.append(w)

    
    if active_entity.fighter.disengage_option is not None or len(command) != 0:
        if active_entity.fighter.disengage_option is not None:
            action = active_entity.fighter.disengage_option
        else:
            action = command
        active_entity.fighter.disengage_option = action

        opp_attackers = []
        #Check and see if anyone can hit with an attack
        for entity in entities:
            if not entity.fighter.end_turn and not active_entity == entity and not active_entity in entity.fighter.entities_opportunity_attacked:
                opp_attackers.append(entity)
        if len(opp_attackers) > 0:
            for entity in opp_attackers:
                for coords in entity.fighter.aoc:
                    x = coords[0]
                    y = coords[1]
                    if x == active_entity.x and y == active_entity.y:
                        wpn_ap = []
                        cs = []
                        for wpn in weapons:
                            for atk in wpn.attacks:
                                cs = active_entity.determine_combat_stats(wpn, atk)
                                wpn_ap.append(cs.get('final ap'))
                        min_ap = min(wpn_ap)
                        if entity.fighter.ap >= min_ap:
                            entity.fighter.entities_opportunity_attacked.append(active_entity)
                            #Give enemy a single attack
                            active_entity = entity
                            combat_phase = CombatPhase.action
        else:
            #Set strafe to follow enemy, but record current setting to set back
            strafe = active_entity.fighter.strafe
            active_entity.fighter.strafe = 'enemy'
            #Move player
            fov_recompute = move_actor(game_map, active_entity, entities, action, logs)
            if fov_recompute:
                #Subtract move AP and stamina
                active_entity.fighter.mod_attribute('ap', -active_entity.fighter.walk_ap)
                active_entity.fighter.mod_attribute('stamina', -active_entity.fighter.base_stam_cost)
            active_entity.fighter.disengage = False
            active_entity.fighter.disengage_option = None
            for entity in entities:
                if active_entity in entity.fighter.entities_opportunity_attacked:
                    entity.fighter.entities_opportunity_attacked.remove(active_entity)
            active_entity.fighter.strafe = strafe
            combat_phase = CombatPhase.action


    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': True}

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    for message in messages:
        log.add_message(Message(message))

    return combat_phase, menu_dict, active_entity

def phase_move(active_entity, entities, command, logs, combat_phase, game_map) -> (int, dict, object):
    combat_menu_header = 'Use the directional movement keys to move. '
    avail_keys, _ = cells_to_keys(get_adjacent_cells(active_entity, entities, game_map, False), active_entity)
    avail_keys.append(41)
    _, d_offsets = cells_to_keys(get_adjacent_cells(active_entity, entities, game_map), active_entity)
    active_entity.fighter.disengage = False
    fov_recompute = False
    messages = []
    log = logs[2]
    
    #Fill action with moves
    active_entity.fighter.action = avail_keys
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': True}
    
    if active_entity.fighter.disengage_option is not None or len(command) != 0:
        if active_entity.fighter.disengage_option is not None:
            action = active_entity.fighter.disengage_option
        else:
            action = command
        active_entity.fighter.disengage_option = action            

        if action[0] != 'exit':
            action_offset = tuple(command_to_offset(action))
            
            if action_offset in d_offsets:
                active_entity.fighter.disengage = True
                combat_phase = CombatPhase.disengage

            else:
                #Set strafe to follow enemy, but record current setting to set back
                strafe = active_entity.fighter.strafe
                active_entity.fighter.strafe = 'enemy'
                #Move player
                fov_recompute = move_actor(game_map, active_entity, entities, action, logs)
                if fov_recompute:
                    #Subtract move AP and stamina
                    active_entity.fighter.mod_attribute('ap', -active_entity.fighter.walk_ap)
                    active_entity.fighter.mod_attribute('stamina', -active_entity.fighter.base_stam_cost)
                active_entity.fighter.disengage = False
                active_entity.fighter.disengage_option = None
                active_entity.fighter.strafe = strafe

                combat_phase = CombatPhase.action


        
    
        if action[0] == 'exit':
            combat_phase = CombatPhase.action
            active_entity.fighter.disengage_option = None
            menu_dict = dict()

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    for message in messages:
        log.add_message(Message(message))

    return combat_phase, menu_dict, active_entity

def phase_maneuver(active_entity, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    min_ap = active_entity.get_min_ap()
    maneuvers = valid_maneuvers(active_entity, active_entity.fighter.curr_target)

    active_entity.fighter.action = ['Return']

    if active_entity.fighter.curr_target is not None:
        if active_entity.fighter.ap >= active_entity.fighter.walk_ap + min_ap + active_entity.fighter.curr_target.get_min_ap():
            active_entity.fighter.action.append('Leave opening and counter')
        if len(maneuvers) > 0:
            for m in maneuvers:
                active_entity.fighter.action.append(m.name)
        for m in active_entity.fighter.maneuvers:
            if m.aggressor is active_entity:
                active_entity.fighter.action.append('Release ' + m.name)


    combat_menu_header = 'Choose your maneuver:'
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
    if len(command) != 0:
        for option in active_entity.fighter.action:
            choice = command.get(option)
            if choice:
                menu_dict = dict()
                if choice == 'Return':
                    active_entity.fighter.action.clear()
                    combat_phase = CombatPhase.action
                elif choice == 'Leave opening and counter':
                    combat_phase = CombatPhase.feint
                    
                    if not hasattr(active_entity.fighter, 'ai'):
                        active_entity.fighter.combat_choices.append(option)
                        messages.append('You decide to feint.')
                else:
                    for m in maneuvers:
                        if choice == m.name: 
                            combat_phase = CombatPhase.grapple
                            if not hasattr(active_entity.fighter, 'ai'):
                                active_entity.fighter.combat_choices.append(m)
                                messages.append('You decide to attempt a ' + m.name + '.')
                    for m in active_entity.fighter.maneuvers:
                        if choice == 'Release ' + m.name:
                            combat_phase = CombatPhase.action
                            if not hasattr(active_entity.fighter, 'ai'):
                                messages.append('You release the ' + m.name + ' on ' + m.target.name + '.')
                            else:
                                messages.append(m.aggressor.name + ' releases the ' + m.name + ' on ' + m.target.name + '.')
                            remove_maneuver(m.target, active_entity, m)


    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    return combat_phase, menu_dict

def phase_feint(active_entity, command, logs, combat_phase) -> (int, dict, object):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    active_entity.fighter.action = ['Return']

    #Choose the hit location to expose
    combat_menu_header = 'Which location do you want to expose?'
    curr_target = active_entity.fighter.curr_target
    #Fill action list with locations
    active_entity.fighter.action = active_entity.fighter.get_locations()
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
    
    if len(command) != 0:    
        for option in active_entity.fighter.action:
            if command.get(option):
                menu_dict = dict()
                choice = command.get(option)
                if choice: 
                    if choice == 'Return':
                        active_entity.fighter.action.clear()
                        combat_phase = CombatPhase.action
                    else:
                        active_entity.fighter.combat_choices.append(option)
                        if not hasattr(active_entity.fighter, 'ai'):
                            messages.append('You expose your ' + option + ' to ' + curr_target.name + ', hoping to tempt an attack. ')
                        active_entity.fighter.feint = True
                        active_entity.fighter.loc_dodge_mod[option] += active_entity.fighter.best_combat_skill.rating/3
                        active_entity.fighter.loc_parry_mod[option] += active_entity.fighter.best_combat_skill.rating/3
                        #See target is fooled
                        for t in active_entity.fighter.targets:
                            if active_entity in t.fighter.targets:
                                roll = roll_dice(1,100)
                                result,_,_ = save_roll_con(active_entity.fighter.best_combat_skill.rating, 0, roll, t.fighter.best_combat_skill)
                                if result is 's':
                                    #Adjust perceived hit location modifiers
                                    t.fighter.adjust_loc_diffs(active_entity, option, 50)


                        active_entity = curr_target
                        combat_phase = CombatPhase.action
    
    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    return combat_phase, menu_dict, active_entity

def phase_stance(active_entity, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    min_ap = active_entity.get_min_ap()

    active_entity.fighter.action = ['Return']

    stance_widths = ('Open', 'Closed')
    stance_lengths = ('Long', 'Short')
    stance_heights = ('High', 'Low')
    stance_weights = ('Front', 'Neutral', 'Rear')

    for w in stance_widths:
        for l in stance_lengths:
            for h in stance_heights:
                for g in stance_weights:
                    active_entity.fighter.action.append(w + ', ' + l + ', ' + h + ', ' + g)


    combat_menu_header = 'Choose your stance:'
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
    if len(command) != 0:
        for option in active_entity.fighter.action:
            choice = command.get(option)
            if choice:
                menu_dict = dict()
                combat_phase = CombatPhase.action

                if choice == 'Return':
                    active_entity.fighter.action.clear()
                else:                    
                    active_entity.fighter.change_stance(choice)
                
                    if not hasattr(active_entity.fighter, 'ai'):
                        messages.append('You decide to use the ' + choice + ' stance.')

    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    return combat_phase, menu_dict    

def phase_guard(active_entity, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]

    active_entity.fighter.action = ['Return']

    available_guards = []

    weapons = []
    for loc in [19,20,27,28]:
        w = active_entity.fighter.equip_loc.get(loc)
        if w is None: continue
        if w.weapon:
            weapons.append(w)

    for wpn in weapons:
        for guard in wpn.guards:
            for loc in guard.req_locs:
                if loc not in active_entity.fighter.paralyzed_locs and loc not in active_entity.fighter.immobilized_locs and loc not in active_entity.fighter.severed_locs:
                    if guard not in available_guards:
                        available_guards.append(guard)
                        active_entity.fighter.action.append(guard.name)
  
    combat_menu_header = 'Choose your guard:'
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
    if len(command) != 0:
        for option in active_entity.fighter.action:
            choice = command.get(option)
            if choice:
                menu_dict = dict()
                combat_phase = CombatPhase.action

                if choice == 'Return':
                    active_entity.fighter.action.clear()
                else:
                    for guard in available_guards:
                        if guard.name == choice:                    
                            active_entity.fighter.change_guard(guard)
                
                        if not hasattr(active_entity.fighter, 'ai'):
                            messages.append('You decide to use the ' + choice + ' guard.')

    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()

    return combat_phase, menu_dict   

def phase_grapple(active_entity, command, logs, combat_phase) -> (int, dict):
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]

    #Choose the hit location
    combat_menu_header = 'Where do you want to aim?'
    curr_target = active_entity.fighter.targets[0]
    mnvr = active_entity.fighter.combat_choices[0]
    #Determine valid locations
    valid_locs = list()
    for l in mnvr.locs_allowed:
        valid_locs.append(l)
    #Prune list to only valid
    locations = prune_list(curr_target.fighter.get_locations(), valid_locs, True, False)
    active_entity.fighter.action = locations
    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
    
    if len(command) != 0:    
        for option in active_entity.fighter.action:
            if command.get(option):
                choice = command.get(option)
                if choice: 
                    if not hasattr(active_entity.fighter, 'ai'):
                        active_entity.fighter.combat_choices.append(curr_target.fighter.name_location(option))
                        messages.append('You aim for ' + curr_target.name + '\'s ' + option)   

                    menu_dict = dict()
                    combat_phase = CombatPhase.grapple_confirm
    
    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default

    return combat_phase, menu_dict

def phase_grapple_defense(active_entity, enemy, entities, command, logs, combat_phase, game_map) -> (int, int, dict, object):
    #Variable setup
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    log = logs[2]
    message = None
    effects = []
    mnvr = enemy.fighter.combat_choices[0]
    can_dodge = False
    can_reverse = mnvr.reversible
    can_counter = mnvr.counterable
    mnvr_name = enemy.fighter.combat_choices[0].name 
    location = enemy.fighter.combat_choices[1]
    loc_name = active_entity.fighter.name_location(enemy.fighter.combat_choices[1])
    game_state = GameStates.default
    header_items = []
    def_margin = None
    atk_margin = None
    rolls = None
    hit = False
    counter_mnvrs = []
    counter_costs = []

    #Find best skill for attack
    valid_skills = []
    for s in mnvr.skill:
        valid_skills.append(getattr(enemy.fighter,s))
    
    attacker_skill = max(valid_skills)


    #Calc loc mods
    loc_mods = active_entity.fighter.get_defense_modifiers(loc_name)
    
    final_to_hit = attacker_skill + mnvr.mnvr_mod + loc_mods.get('hit')
    dodge_mod = loc_mods.get('dodge')

    #Find best skill for counter/reverse
    valid_skills = []
    for s in mnvr.skill:
        valid_skills.append(getattr(active_entity.fighter,s))
    
    skill = max(valid_skills)

    reverse_ap = int(mnvr.base_ap * ((100/skill)**.2 ))

    #Find valid manuevers to counter reverse with
    valid_mnvrs = valid_maneuvers(active_entity, enemy)

    #Find chances and see if active_entity can dodge/counter/reverse
    dodge_mod += mnvr.dodge_mod
    if active_entity.fighter.ap >= active_entity.fighter.walk_ap: can_dodge = True
    
    if mnvr.reversible:
        for m in valid_mnvrs:
            if type(m) is type(mnvr):
                if active_entity.fighter.ap >= reverse_ap:
                    can_reverse = True

    if mnvr.counterable:
        for m in valid_mnvrs:
            for c in mnvr.counters:
                if type(m) is c:                  
                    c_skills = []
                    for s in c.skills:
                        c_skills.append(getattr(active_entity.fighter,s))
                    
                    max_c_skill = max(c_skills)
                    cost = int(m.base_ap * ((100/max_c_skill)**.2 ))
                    if active_entity.fighter.ap >= cost:
                        can_counter = True
                        break

    

    #Normalized (0-99) percentage scale of probabilities to p/d/b
    dodge_chance = find_defense_probability(final_to_hit, (active_entity.fighter.get_attribute('dodge') + dodge_mod))
    reverse_chance = find_defense_probability(final_to_hit, (skill + mnvr.reversal_mod + mnvr.mnvr_mod))


    #Choose how to defend '
    header_items.append(enemy.name + ' is attempting to apply a ' + mnvr.name + ' maneuver to your ' + loc_name + '. \n' )
    active_entity.fighter.action = ['Allow the manuever']
    if can_dodge:
        header_items.append('You have a ' + str(dodge_chance) + ' percent chance to dodge the maneuver at a cost of ' + str(active_entity.fighter.walk_ap) + ' ap. \n')
        active_entity.fighter.action.append('Dodge')
    if can_reverse:
        header_items.append('You have a ' + str(reverse_chance) + ' percent chance to reverse the maneuver at a cost of ' + str(reverse_ap) + ' ap. \n')
        active_entity.fighter.action.append('Reverse')

    if can_counter:
        for m in valid_mnvrs:
            for c in mnvr.counters:
                if type(m) is c:
                    c_skills = []
                    for s in c.skills:
                        c_skills.append(getattr(active_entity.fighter,s))
                    
                    max_c_skill = max(c_skills)

                    counter_chance = find_defense_probability(final_to_hit, (max_c_skill + mnvr.counter_mod + m.mnvr_mod))

                    counter_ap = int(m.base_ap * ((100/max_c_skill)**.2 ))

                    if active_entity.fighter.ap >= counter_ap:
                        header_items.append('You have a ' + str(counter_chance) + ' percent chance to counter with a ' + c.name + ' at a cost of ' + str(counter_ap) + ' ap. \n')
                        active_entity.fighter.action.append('Counter with ' + m.name)

       
    if can_dodge or can_counter or can_reverse:
        game_state = GameStates.menu
        header_items.append('What would you like to do? ')
        combat_menu_header = ''.join(header_items)
        menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}
        if len(command) != 0:
            if command.get('Allow the manuever'):
                hit = True
                effects = apply_maneuver(enemy, active_entity, type(mnvr), location, entities, game_map)
                
            if command.get('Dodge'):
                check, def_margin, atk_margin = save_roll_con(active_entity.fighter.get_attribute('dodge'), dodge_mod, enemy.fighter.atk_result, final_to_hit)
                #Remove ap and stam
                active_entity.fighter.mod_attribute('ap', -active_entity.fighter.walk_ap)
                active_entity.fighter.mod_attribute('stamina', -active_entity.fighter.base_stam_cost)
                if check == 's':
                    if not hasattr(active_entity.fighter, 'ai'): message = ('You dodged the attack. ')
                    else: message = (active_entity.name + ' dodged the attack. ')
                    
                else:
                    hit = True
                    effects = apply_maneuver(enemy, active_entity, type(mnvr), location, entities, game_map)
                    

            if command.get('Reverse'):
                check, def_margin, atk_margin = save_roll_con(getattr(active_entity.fighter,mnvr.skill), mnvr.reversal_mod, enemy.fighter.atk_result, final_to_hit)
                #Remove ap and stam
                active_entity.fighter.mod_attribute('stamina', -(mnvr.stamina*active_entity.fighter.base_stam_cost))
                active_entity.fighter.mod_attribute('ap', -reverse_ap)
                if check == 's':
                    if not hasattr(active_entity.fighter, 'ai'): message = ('You reversed the maneuver. ')
                    else: message = (active_entity.name + ' reversed the maneuver. ')
                    effects = apply_maneuver(active_entity, enemy, type(mnvr), location, entities, game_map)
                else:
                    hit = True
                    effects = apply_maneuver(enemy, active_entity, type(mnvr), location, entities, game_map)
                    

                
    else:
        for m in valid_mnvrs:
            if command.get('Counter with ' + m.name):
                c_skills = []
                for s in m.skill:
                    c_skills.append(getattr(active_entity.fighter,s))
                    
                max_c_skill = max(c_skills)
                counter_ap = int(m.base_ap * ((100/max_c_skill)**.2 ))
                check, def_margin, atk_margin = save_roll_con(max_c_skill, mnvr.counter_mod + m.mnvr_mod, enemy.fighter.atk_result, final_to_hit)
                if check == 's':
                    if not hasattr(active_entity.fighter, 'ai'): message = ('You countered the maneuver. ')
                    else: message = (active_entity.name + ' countered the maneuver. ')
                    effects = apply_maneuver(active_entity, enemy, type(mnvr), location, entities, game_map)
                else:
                    hit = True
                    effects = apply_maneuver(enemy, active_entity, type(mnvr), location, entities, game_map)
                    
                break
                    
    
    if message or effects:
        combat_phase = CombatPhase.action
        
        if message:
            messages.append(message)

        if effects:
            for effect in effects:
                messages.append(effect)
        if active_entity.state == EntityState.conscious:
            if active_entity.fighter.disengage:       
                combat_phase = CombatPhase.disengage
                game_state = GameStates.default
                
            elif active_entity.fighter.feint and not hit:
                active_entity.fighter.counter_attack.append(enemy)
                enemy.fighter.combat_choices.clear()
                combat_phase = CombatPhase.weapon
            else:
                active_entity.fighter.action.clear()
                active_entity = enemy
        #Show rolls
        if options.show_rolls: 
            if atk_margin is not None and def_margin is not None:
                rolls = active_entity.name + ' had a margin of success of ' + str(def_margin) + ', while ' + enemy.name + ' had a margin of ' + str(atk_margin) + '. '
            elif atk_margin is not None:
                rolls = enemy.name + ' had a margin of success of ' + str(atk_margin) + '. '
            if rolls is not None: messages.insert(0, rolls)
        
        
        
        if active_entity.player:
            active_entity.fighter.combat_choices.clear()

        menu_dict = dict()


    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()
        game_state = GameStates.default
        

    return combat_phase, game_state, menu_dict, active_entity

def phase_grapple_confirm(active_entity, entities, command, logs, combat_phase, game_map) -> (int, dict, object):
    #Verify choices and continue or restart

    #Variable setup
    combat_menu_header = None
    menu_dict = dict()
    messages = []
    missed = False
    log = logs[2]
    curr_target = active_entity.fighter.curr_target
    mnvr = active_entity.fighter.combat_choices[0]
    location = active_entity.fighter.combat_choices[1]
    loc_name = active_entity.fighter.targets[0].fighter.name_location(location)

    #Find best skill for attack
    valid_skills = []
    for s in mnvr.skill:
        valid_skills.append(getattr(active_entity.fighter,s))
    
    attacker_skill = max(valid_skills)

    #Calc loc mods
    loc_mods = curr_target.fighter.get_defense_modifiers(loc_name)
    
    final_to_hit = attacker_skill + mnvr.mnvr_mod + loc_mods.get('hit')
    p_hit = final_to_hit

    if p_hit > 99:
        p_hit = 99

    final_ap = int(mnvr.base_ap * ((100/attacker_skill)**.2 ))


    combat_menu_header = ('You are performing a ' + mnvr.name + ' on ' + curr_target.name + '\'s ' 
        + loc_name + '. ' 
        + ' For this attack, you will have a: ' + str(p_hit) +  '% chance to succeed.' + ' Your opponent will get a ' + str(mnvr.dodge_mod) + '% modifier to dodge. \n' + 
        'It will cost you ' + str(final_ap) + ' of your remaining ' + str(active_entity.fighter.ap) + ' AP to attack. \n'
        + ' Would you like to continue, or modify your choices?')

    active_entity.fighter.action = ['Accept', 'Restart']

    menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': active_entity.fighter.action, 'mode': False}

    if len(command) != 0:
        if command.get('Accept'):
            messages, combat_phase, active_entity, missed = perform_maneuver(active_entity, entities, final_to_hit, curr_target, combat_phase, game_map)
            active_entity.fighter.last_atk_ap = final_ap
            active_entity.fighter.acted = True
            active_entity.fighter.action.clear()
            active_entity.fighter.combat_choices.clear()
        if command.get('Restart'):
            #Reset vars
            active_entity.fighter.combat_choices.clear()
            combat_phase = CombatPhase.action
        
        menu_dict = dict()

    if missed:
        min_ap = curr_target.get_min_ap()
        if curr_target.fighter.ap >= min_ap and (active_entity.x, active_entity.y) in curr_target.fighter.aoc:
            curr_target.fighter.entities_opportunity_attacked.append(active_entity)
            curr_target.fighter.counter_attack.append(active_entity)
            if hasattr(curr_target.fighter, 'ai'):
                messages.append('You missed, allowing ' + curr_target.name + ' to counter-attack.')
            else:
                messages.append(curr_target.name + ' missed, giving you a chance to counter-attack.')
            active_entity = curr_target

    for message in messages:
        log.add_message(Message(message))

    if hasattr(active_entity.fighter, 'ai'):
        menu_dict = dict()

    return combat_phase, menu_dict, active_entity