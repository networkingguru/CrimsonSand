
import enums

#UI Vars
screen_width = 180
screen_height = 90
status_panel_h = screen_height
status_panel_w = 30
status_panel_x = screen_width - status_panel_w

enemy_panel_h = screen_height
enemy_panel_w = 30
enemy_panel_x = 0

message_panel_h = 15
message_panel_w = screen_width - status_panel_w
message_panel_y = screen_height - message_panel_h

map_width = screen_width - status_panel_w
map_height = screen_height - message_panel_h

#Base time units
fps = 30

#Entity list
player = (50, 50, '@', 'white', 'Player', enums.EntityState.conscious, True, True)
enemy = (60, 60, '@', 'yellow', 'Enemy', enums.EntityState.conscious, False, True)
entities = [player, enemy]

#Key Dicts in order of key, command_verb
default_keys = {'q':('move','nw'), 'w':('move','n '), 'e':('move','ne'), 'd':('move',' e'), 'c':('move','se'), 
                'x':('move','s '), 'z':('move','sw'),'a':('move',' w'), 27: 'exit'}

key_maps = [default_keys]