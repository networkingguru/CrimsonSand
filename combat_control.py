
from combat_phases import (phase_init, phase_action, phase_weapon, phase_option, phase_location,  
    phase_option2, phase_confirm, phase_repeat, phase_defend, phase_disengage, phase_move, phase_maneuver, phase_feint, phase_stance, phase_guard, phase_grapple,
    phase_grapple_confirm, phase_grapple_defense)
from combat_functions import strafe_control, move_actor, update_targets, detect_enemies
from enums import CombatPhase, GameStates

def combat_controller(game_map, active_entity, entities, players, command, logs, combat_phase, game_state, order) -> (dict, int, int, object, list):

    if combat_phase == CombatPhase.explore:
        if isinstance(command, str):
            if command.get('strafe'): 
                message = strafe_control(active_entity)
                logs[2].add_message(message)
        elif len(command) != 0:
            if command.get('move') or command.get('spin'):
                move_actor(game_map, active_entity, entities, command, logs)
                combat_phase_new = detect_enemies(entities)
                #If phase changed, go into new phase
                if combat_phase != combat_phase_new:
                    combat_phase = combat_phase_new
                   
    if combat_phase == CombatPhase.init:
        combat_phase, order = phase_init(entities)
                
    elif combat_phase == CombatPhase.action:
        menu_dict, combat_phase, game_state, order = phase_action(active_entity, players, entities, order, command, logs, game_map)
        
    elif combat_phase == CombatPhase.weapon:
        combat_phase, menu_dict = phase_weapon(active_entity, command, logs, combat_phase)

    elif combat_phase == CombatPhase.option:
        combat_phase, menu_dict = phase_option(active_entity, command, logs, combat_phase)
        
    elif combat_phase == CombatPhase.location:
        combat_phase, menu_dict = phase_location(active_entity, command, logs, combat_phase)
        
    elif combat_phase == CombatPhase.option2:
        combat_phase, menu_dict = phase_option2(active_entity, command, logs, combat_phase)

    elif combat_phase == CombatPhase.confirm:
        combat_phase, menu_dict, active_entity = phase_confirm(active_entity, entities, command, logs, combat_phase)
    
    elif combat_phase == CombatPhase.defend:
        combat_phase, game_state, menu_dict, active_entity = phase_defend(active_entity, active_entity.fighter.attacker, entities, command, logs, combat_phase)

    elif combat_phase == CombatPhase.repeat:
        combat_phase, menu_dict = phase_repeat(active_entity, command, logs, combat_phase)
    
    elif combat_phase == CombatPhase.move:
        combat_phase, menu_dict, active_entity = phase_move(active_entity, entities, command, logs, combat_phase, game_map)

    elif combat_phase == CombatPhase.maneuver:
        combat_phase, menu_dict = phase_maneuver(active_entity, command, logs, combat_phase)

    elif combat_phase == CombatPhase.feint:
        combat_phase, menu_dict, active_entity = phase_feint(active_entity, command, logs, combat_phase)

    elif combat_phase == CombatPhase.stance:
        combat_phase, menu_dict = phase_stance(active_entity, command, logs, combat_phase)

    elif combat_phase == CombatPhase.guard:
        combat_phase, menu_dict = phase_guard(active_entity, command, logs, combat_phase)

    elif combat_phase == CombatPhase.grapple:
        combat_phase, menu_dict = phase_grapple(active_entity, command, logs, combat_phase)
    
    elif combat_phase == CombatPhase.grapple_defense:
        combat_phase, game_state, menu_dict, active_entity = phase_grapple_defense(active_entity, active_entity.fighter.curr_target, entities, command, logs, combat_phase, game_map)

    elif combat_phase == CombatPhase.grapple_confirm:
        combat_phase, menu_dict, active_entity = phase_grapple_confirm(active_entity, entities, command, logs, combat_phase, game_map)

    if combat_phase == CombatPhase.disengage:
        combat_phase, menu_dict, active_entity = phase_disengage(active_entity, entities, command, logs, combat_phase, game_map)

    if game_state == GameStates.default:
        menu_dict = dict()

    return menu_dict, combat_phase, game_state, active_entity, order
        





