import tcod as libtcodpy
from tcod import map
import options
import time
import global_vars
from combat_control import combat_controller
from combat_functions import change_actor
from ui_control import render_all, create_console, handle_keys, create_terminal, blt_handle_keys, create_root_console, render
from enums import GameStates, CombatPhase
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from game_map import GameMap, array_gen, fill_map
from fov_aoc import modify_fov, change_face
from game_messages import MessageLog, Message
from utilities import gen_status_panel
 


if __name__ == "__main__":
    libtcodpy.sys_set_fps(options.fps)

    #Console init
    con = create_root_console(options.screen_width, options.screen_height)
    dim_list = [(options.map_width, options.map_height), (options.status_panel_w, options.status_panel_h), 
                (options.enemy_panel_w, options.enemy_panel_h), (options.message_panel_w, options.message_panel_h)]
    map_con = create_console(dim_list[0][0], dim_list[0][1])
    status_panel = create_console(dim_list[1][0], dim_list[1][1])
    enemy_panel = create_console(dim_list[2][0], dim_list[2][1])
    message_panel = create_console(dim_list[3][0], dim_list[3][1])
    menu_dict = None

    #term = create_terminal(options.screen_width, options.screen_height)

    con_list = [map_con, status_panel, enemy_panel, message_panel]
    offset_list = ((options.map_x,options.map_y),(options.status_panel_x,options.status_panel_y),(options.enemy_panel_x,options.enemy_panel_y),
                (options.message_panel_x,options.message_panel_y))
    type_list = options.panel_types
    color_list = options.panel_colors

    #Message Log init
    message_log = MessageLog(1, options.message_panel_w-1, options.message_panel_h-2)
    status_log = MessageLog(1, options.status_panel_w-1, options.status_panel_h-2)
    enemy_log = MessageLog(1, options.enemy_panel_w-1, options.enemy_panel_h-2)
    logs = [status_log, enemy_log, message_log]



    #Entity init
    entity_list = options.entities
    entities = create_entity_list(entity_list)
    fighters = options.fighters
    add_fighters(entities, fighters)
    weapons = options.weapons
    add_weapons(entities, weapons)
    players = []
    players.extend(fill_player_list(entities))
    enemies = []
    enemies = set(entities) - set(players)
    
    #Global order vars; players get first move
    order = []
    order.extend(players)
    order.extend(enemies)
    curr_actor = order[0]
    round_num = global_vars.round_num


    #Map/state init
    game_state = GameStates.default
    #map_dict = None
    combat_phase = CombatPhase.explore

    game_map = map.Map(options.map_width, options.map_height, 'F')
    fill_map(game_map, options.blocked, options.blocked)
    fov_transparency = array_gen(game_map, options.blocked)

    #Initial computations:
    #FOV and AOC comps
    fov_radius = int(round(curr_actor.fighter.sit/5))
    game_map.compute_fov(curr_actor.x, curr_actor.y, fov_radius, True)
    modify_fov(curr_actor, game_map)
    for entity in entities:
        entity.fighter.update_aoc_facing
        entity.fighter.aoc = change_face(entity.fighter.aoc_facing, entity.x, entity.y, entity.fighter.reach)
    #Fill out initial char stats
    entries = gen_status_panel(players[0])
    for entry in entries:
        status_log.add_message(Message(entry))

    
    while not libtcodpy.console_is_window_closed():
        
        render_all(con_list, offset_list, type_list, dim_list, color_list, logs, entities, players, game_map, menu_dict)
        #render(entities, players, game_map, con_list, offset_list, type_list, dim_list, color_list, logs)

        command = handle_keys(game_state, menu_dict)

        combat_phase, order = change_actor(order, entities, combat_phase, logs)
        curr_actor = order[0]
        
        if combat_phase is not CombatPhase.explore:
            if hasattr(curr_actor.fighter, 'ai'):
                if command != 'exit':
                    command = curr_actor.fighter.ai.ai_command(curr_actor, entities, combat_phase)
            
        if command is not None:
            print(curr_actor)
            menu_dict, combat_phase, game_state, curr_actor, order = combat_controller(game_map, curr_actor, entities, players, command, logs, combat_phase, game_state, order)

    
        
        

        
