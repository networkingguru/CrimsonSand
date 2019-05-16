
from combat_functions import move_actor, update_targets, detect_enemies, phase_init, phase_action, phase_weapon, phase_option, phase_location, phase_option2, phase_confirm, phase_repeat, phase_defend
from enums import CombatPhase, GameStates

def combat_controller(game_map, active_entity, entities, players, command, logs, combat_phase, game_state, order) -> (dict, int, int, object, list):


    if command == 'exit':
        exit(0)


    if combat_phase == CombatPhase.explore:
        try: 
            if command[0] == 'move' or 'spin':
                moved = move_actor(game_map, active_entity, entities, command, logs)
                if moved: 
                    combat_phase_new = detect_enemies(entities)
                    #If phase changed, go into new phase
                    if combat_phase != combat_phase_new:
                        combat_phase = combat_phase_new
        except: pass
                   
    if combat_phase == CombatPhase.init:
        combat_phase, order = phase_init(entities)
                
    if combat_phase == CombatPhase.action:
        menu_dict, combat_phase, game_state, order = phase_action(active_entity, players, entities, order, command, logs, game_map)
        
    if combat_phase == CombatPhase.weapon:
        combat_phase, menu_dict = phase_weapon(active_entity, command, logs, combat_phase)

    if combat_phase == CombatPhase.option:
        combat_phase, menu_dict = phase_option(active_entity, command, logs, combat_phase)
        
    if combat_phase == CombatPhase.location:
        combat_phase, menu_dict = phase_location(active_entity, command, logs, combat_phase)
        
    if combat_phase == CombatPhase.option2:
        combat_phase, menu_dict = phase_option2(active_entity, command, logs, combat_phase)

    if combat_phase == CombatPhase.confirm:
        combat_phase, menu_dict, active_entity = phase_confirm(active_entity, entities, command, logs, combat_phase)
    
    if combat_phase == CombatPhase.defend:
        combat_phase, game_state, menu_dict, active_entity = phase_defend(active_entity, active_entity.fighter.attacker, entities, command, logs, combat_phase)

    if combat_phase == CombatPhase.repeat:
        combat_phase, menu_dict = phase_repeat(active_entity, command, logs, combat_phase)
    
    elif combat_phase == CombatPhase.disengage:
        pass

    if game_state == GameStates.default:
        menu_dict = None

    return menu_dict, combat_phase, game_state, active_entity, order
        





