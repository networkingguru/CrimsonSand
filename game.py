import tcod as libtcodpy
from tcod import map
import options
import time
#import numpy as np
from combat_control import combat_controller
from ui_control import render_all, create_console, handle_keys, create_terminal, blt_handle_keys, create_root_console, render
from enums import GameStates
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from game_map import GameMap, array_gen, fill_map
from fov_aoc import initialize_fov, recompute_fov, modify_fov

 


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

    #term = create_terminal(options.screen_width, options.screen_height)

    con_list = [map_con, status_panel, enemy_panel, message_panel]
    offset_list = ((options.map_x,options.map_y),(options.status_panel_x,options.status_panel_y),(options.enemy_panel_x,options.enemy_panel_y),
                (options.message_panel_x,options.message_panel_y))
    type_list = (0,2,2,3)
    color_list = (('white','light_gray'), ('black','white'), ('black', 'yellow'), ('yellow', 'crimson'))


    #Entity init
    entity_list = options.entities
    entities = create_entity_list(entity_list)
    fighters = options.fighters
    add_fighters(entities, fighters)
    weapons = options.weapons
    add_weapons(entities, weapons)
    players = []
    players.extend(fill_player_list(entities))
    curr_actor = players[0]

    #Map/state init
    game_map = GameMap(options.map_width, options.map_height)
    fov_map = initialize_fov(game_map)
    game_state = GameStates.default

    new_map = map.Map(options.map_width, options.map_height, 'F')
    #blocked_array = array_gen(new_map, options.blocked)
    fill_map(new_map, options.blocked, options.blocked)



    #Initial computations
    fov_radius = int(round(curr_actor.fighter.sit/5))
    recompute_fov(fov_map, curr_actor.x, curr_actor.y, fov_radius)
    modify_fov(curr_actor, game_map, fov_map)
    

    while not libtcodpy.console_is_window_closed():

        render_all(con_list, offset_list, type_list, entities, players, dim_list, color_list, game_map)
        
        #command2 = blt_handle_keys(game_state)
        #Establish ms timer, only execute block x times per second
        base_time = time.perf_counter()
        tick = round(base_time - int(base_time), 1)
        if tick % .2 == 0:
            command = handle_keys(game_state)
            
            if command is not None:
                print(command)
                action = combat_controller(game_map, fov_map, 0, entities, command)


    
        
        

        
