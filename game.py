import tcod as libtcodpy
from tcod import map
import options
import time
import global_vars
from combat_control import combat_controller
from combat_functions import change_actor
from ui_control import render_all, create_console, handle_input, handle_global_input, create_terminal, blt_handle_keys, create_root_console, render
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

    #Set debug from options
    global_vars.debug = options.debug

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
    combat_phase = CombatPhase.explore
    command = None
    event = None
    game_map = map.Map(options.map_width, options.map_height, 'F')
    fill_map(game_map, options.blocked, options.blocked)
    fov_transparency = array_gen(game_map, options.blocked)

    #Initial computations:
    #FOV and AOC comps
    for entity in entities:
        entity.fighter.update_aoc_facing()
        entity.fighter.aoc = change_face(entity.fighter.aoc_facing, entity.x, entity.y, entity.fighter.reach)
        fov_radius = int(round(entity.fighter.sit/5))
        game_map.compute_fov(entity.x, entity.y, fov_radius, True)
        modify_fov(entity, game_map)
        
    #Fill out initial char stats
    entries = gen_status_panel(players[0])
    for entry in entries:
        status_log.add_message(Message(entry))

    
    while not libtcodpy.console_is_window_closed():
        if global_vars.debug_time: t0 = time.time()

        render_all(con_list, offset_list, type_list, dim_list, color_list, logs, entities, players, game_map, menu_dict)
        #render(entities, players, game_map, con_list, offset_list, type_list, dim_list, color_list, logs)

        combat_phase, order, new_curr_actor = change_actor(order, entities, curr_actor, combat_phase, logs)
        if curr_actor != new_curr_actor:
            if global_vars.debug: print(curr_actor.name + ' ' + new_curr_actor.name)
            curr_actor = new_curr_actor

        event = handle_global_input(combat_phase)

        if event == 'exit': exit(1)
        elif combat_phase == CombatPhase.explore:
            command = event
        elif curr_actor.player:
            #Below complexity is due to modal nature. if targets exist, block for input. 
            #Otherwise, see if a menu is present. If so, block for input, if not, refresh and get menu
            if len(curr_actor.fighter.targets) == 0:
                command = handle_input(game_state, menu_dict)
            else:
                try:
                    if menu_dict.get('options'):
                        command = handle_input(game_state, menu_dict)
                except:
                    command = None
                    menu_dict, combat_phase, game_state, curr_actor, order = combat_controller(game_map, curr_actor, entities, players, command, logs, combat_phase, game_state, order)       
        elif not curr_actor.player:
            command = curr_actor.fighter.ai.ai_command(curr_actor, entities, combat_phase, game_map, order)

            if global_vars.debug: print(curr_actor.name + ' actions: ', *curr_actor.fighter.action, sep=', ')
            if global_vars.debug and isinstance(command, str): print(curr_actor.name + ' command: ' + command)

        if command is not None:
            menu_dict, combat_phase, game_state, curr_actor, order = combat_controller(game_map, curr_actor, entities, players, command, logs, combat_phase, game_state, order)
            if global_vars.debug: print('Phase: ' + str(combat_phase))



        if global_vars.debug_time: t1 = time.time()
        if global_vars.debug_time: total_time = t1 - t0
        if global_vars.debug_time: print('Refresh time: ' + str(total_time))
        
        

        
