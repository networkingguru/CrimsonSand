
import enums

#UI Vars
screen_width = 180
screen_height = 90

#Base time units
fps = 30

#Entity list
player = (50, 50, '@', enums.Colors.white, 'Player', enums.EntityState.conscious, True)
enemy = (60, 60, '@', enums.Colors.white, 'Enemy', enums.EntityState.conscious)
entities = [player, enemy]

#Key Dicts in order of key, command_verb
default_keys = {'q':('move','nw'), 'w':('move','n '), 'e':('move','ne'), 'd':('move',' e'), 'c':('move','se'), 
                'x':('move','s '), 'z':('move','sw'),'a':('move',' w'), 27: 'exit'}

key_maps = [default_keys]