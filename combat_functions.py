import tcod as libtcodpy
import time
import global_vars
from enums import CombatPhase, MenuTypes, EntityState, GameStates
from entity import get_blocking_entities_at_location
from fov_aoc import modify_fov, change_face, aoc_check
from game_messages import Message
from utilities import inch_conv, gen_status_panel, roll_dice

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
    status_log = logs[0]
    enemy_log = logs[1]


    
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

def phase_init(entities) -> list:
    fighters = []
    for entity in entities:
        if hasattr(entity, 'fighter'):
            fighters.append(entity)
    

    #Sort the entities by initiative
    if len(entities) > 1:    
        order = turn_order(entities)
    else:
        order = entities

    return order

def phase_action(curr_actor, players, entities, order, command, logs, game_map) -> (dict,int,list):
    combat_phase = CombatPhase.action
    game_state = GameStates.default
    combat_menu_header = None
    menu_dict = None
    messages = []
    log = logs[2]
    status_log = logs[0]  
    #Check and see if anyone can still act
    remaining_fighters = 0
    for entity in order:
        inactive_fighters = [entity.fighter.end_turn, entity.state == EntityState.unconscious]
        if not any (inactive_fighters): 
            if entity.fighter.ap != 0: remaining_fighters += 1
    
    if remaining_fighters == 0: 
        log.add_message(Message('The round has ended. '))
        combat_phase = CombatPhase.init
        global_vars.round_num  += 1
        return menu_dict, combat_phase, game_state, order
    
    
    if curr_actor.fighter.end_turn:
        order.remove(curr_actor)

    if hasattr(curr_actor.fighter, 'ai'):
        #messages, attacker, combat_phase = order[0].fighter.ai.take_turn(order[0], initiator, messages, combat_phase)
        #combat_menu_header = '' 
        pass
    
    else:
        #Check and see if player has a target in zoc
        if len(curr_actor.fighter.targets) == 0:
            if curr_actor.fighter.ap >= curr_actor.fighter.walk_ap:
                if command[0] == 'move' or 'spin':
                    moved = move_actor(game_map, curr_actor, entities, players, command, logs)
                    if moved: 
                        curr_actor.fighter.mod_attribute('ap', -curr_actor.fighter.walk_ap)
                        entries = gen_status_panel(players[0])
                        status_log.messages.clear()
                        for entry in entries:
                            status_log.add_message(Message(entry))
                        if len(curr_actor.fighter.targets) != 0:
                            phase_action(curr_actor,players,entities,order,command,logs,game_map)
            else:
                curr_actor.fighter.end_turn = True
                combat_phase = CombatPhase.action
        else:    
            game_state = GameStates.menu
            #CHeck to see if player can afford to attack
            wpn_ap = []
            for wpn in curr_actor.weapons:
                for atk in wpn.attacks:
                    cs = curr_actor.determine_combat_stats(wpn, atk)
                    wpn_ap.append(cs.get('final ap'))
            min_ap = min(wpn_ap)
            if curr_actor.fighter.ap >= min_ap: 
                curr_actor.fighter.action = ['Engage', 'Disengage', 'Wait', 'End Turn']
            elif curr_actor.fighter.ap > 0:
                curr_actor.fighter.action = ['Wait', 'End Turn']
            else:
                curr_actor.fighter.end_turn = True
                combat_phase = CombatPhase.action
                menu_dict = None
                game_state = GameStates.default
                return menu_dict, combat_phase, game_state, order

            combat_menu_header = 'What do you wish to do?'

            try:
                if command.get('Wait'):
                    messages.append('You decide to wait for your opponents to act')
                    order.append(order.pop(0))
                    combat_phase = CombatPhase.action                  
                elif command.get('Engage'):
                    messages.append('You decide to attack')
                    combat_phase = CombatPhase.weapon
                elif command.get('Disengage'):
                    messages.append('You decide to disengage from ' + curr_actor.fighter.targets[0].name)
                    combat_phase = CombatPhase.disengage
                elif command.get('End Turn'):
                    messages.append('You decide to end your turn')
                    curr_actor.fighter.end_turn = True
                    order.append(order.pop(0))
                    combat_phase = CombatPhase.action
            except:
                pass


            menu_dict = {'type': MenuTypes.combat, 'header': combat_menu_header, 'options': curr_actor.fighter.action, 'mode': False}

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




