import tcod as libtcodpy
import options
import time
from combat_control import GameControl
from ui_control import render_console, create_console

class Command():
    #Universal command class
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)




    


if __name__ == "__main__":
    libtcodpy.sys_set_fps(options.fps)
    con = create_console(options.screen_width, options.screen_height)
    
    i = 0
    while not libtcodpy.console_is_window_closed():
        render_console(con, options.screen_width, options.screen_height)
        #Establish ms timer, only execute block x times per second
        base_time = time.clock()
        tick = round(base_time - int(base_time), 1)
        if tick % .3 == 0:
            print(tick)
            i += 1
            print(i)


    
        
        

        
