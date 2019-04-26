import tcod as libtcodpy
import options
import time
from combat_control import combat_controller
from ui_control import render_all, create_console, handle_keys
from enums import GameStates
from entity import create_entity_list

 


if __name__ == "__main__":
    libtcodpy.sys_set_fps(options.fps)
    con = create_console(options.screen_width, options.screen_height)
    con_list = [con]
    entity_list = options.entities
    
    

    game_state = GameStates.default

    while not libtcodpy.console_is_window_closed():

        entities = create_entity_list(entity_list)

        render_all(con_list, entities, options.screen_width, options.screen_height)



        #Establish ms timer, only execute block x times per second
        base_time = time.clock()
        tick = round(base_time - int(base_time), 1)
        if tick % .2 == 0:
            command = handle_keys(game_state)
            if command is not None:
                print(command)
                action = combat_controller(None, entities, command)


    
        
        

        
