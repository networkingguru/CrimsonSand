
from combat_functions import move_actor, update_targets, detect_enemies, phase_init, phase_action
from enums import CombatPhase, GameStates

def combat_controller(game_map, active_entity, entities, players, command, logs, combat_phase, game_state, order) -> (dict, int, int, object, list):
    menu_dict = None

    if command == 'exit':
        exit(0)
    if combat_phase == CombatPhase.explore:
        if command[0] == 'move' or 'spin':
            moved = move_actor(game_map, active_entity, entities, players, command, logs)
            if moved: combat_phase = detect_enemies(entities)
    else:
        if combat_phase == CombatPhase.init:
            order = phase_init(entities)
            combat_phase = CombatPhase.action
                    
        elif combat_phase == CombatPhase.action:
            menu_dict, combat_phase, order = phase_action(active_entity, players, entities, order, command, logs, game_map)
            
        elif combat_phase == CombatPhase.weapon:
            pass

        elif combat_phase == CombatPhase.option:
            pass
            
        elif combat_phase == CombatPhase.location:
            pass
            
        elif combat_phase == CombatPhase.option2:
            pass

        elif combat_phase == CombatPhase.confirm:
            pass
        
        elif combat_phase == CombatPhase.repeat:
            pass
        
        elif combat_phase == CombatPhase.defend:
            pass

        elif combat_phase == CombatPhase.disengage:
            pass

    if menu_dict is not None:
        game_state = GameStates.menu

    return menu_dict, combat_phase, game_state, active_entity, order
        





