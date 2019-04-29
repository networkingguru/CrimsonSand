import tcod as libtcodpy
import options
import time
from combat_control import combat_controller
from ui_control import render_all, create_console, handle_keys, create_terminal, blt_handle_keys
from enums import GameStates
from entity import create_entity_list, fill_player_list
from game_map import GameMap

 


if __name__ == "__main__":
    libtcodpy.sys_set_fps(options.fps)
    con = create_console(options.screen_width, options.screen_height)
    term = create_terminal(options.screen_width, options.screen_height)
    con_list = [con]
    entity_list = options.entities
    entities = create_entity_list(entity_list)
    players = []
    players.append(fill_player_list(entities))
    curr_actor = players[0]
    game_map = GameMap(options.map_width, options.map_height)

    game_state = GameStates.default

    while not libtcodpy.console_is_window_closed():

        render_all(con_list, entities, options.screen_width, options.screen_height)
        command2 = blt_handle_keys(game_state)
        #Establish ms timer, only execute block x times per second
        base_time = time.clock()
        tick = round(base_time - int(base_time), 1)
        if tick % .2 == 0:
            command = handle_keys(game_state)
            
            if command is not None:
                print(command)
                action = combat_controller(game_map, 0, entities, command)


    
        
        

        
