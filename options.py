
import enums
from components.ai import CombatAI

#UI Vars
screen_width = 180
screen_height = 90
status_panel_h = screen_height
status_panel_w = 30
status_panel_x = screen_width - status_panel_w
status_panel_y = 0

enemy_panel_h = screen_height
enemy_panel_w = 30
enemy_panel_x = 0
enemy_panel_y = 0

message_panel_h = 15
message_panel_w = screen_width - status_panel_w - enemy_panel_w
message_panel_y = screen_height - message_panel_h + 1
message_panel_x = enemy_panel_w

map_width = screen_width - status_panel_w - enemy_panel_w
map_height = screen_height - message_panel_h + 1
map_x = enemy_panel_w
map_y = 0

modal_w = map_width/4
modal_x = map_width/2 + modal_w/2
modal_y = map_height/2 - message_panel_h/2

panel_types = (0,1,2,3)
panel_colors = (('white','light_gray'), ('black','white'), ('black', 'yellow'), ('yellow', 'crimson'))

#Map setup
blocked = ((30,30),(30,31),(30,32),(30,33),(30,34),(30,35),(31,30),(32,30),(33,30),(34,30),(35,30))

#Debug
debug = True

#Base time units
fps = 30

#Player stat archetypes for testing
fat = [130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,400,130]
tank = [130,130,130,130,130,130,130,130,250,250,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,180,200,130]
fw = [130,130,130,130,130,130,130,130,150,150,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,50,50,130]
hw = [130,130,130,130,130,130,130,130,250,250,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,180,80,130]
hopeless_fat = [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,130,480,40]
hopeless = [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
midget = [130,130,130,130,130,130,130,130,250,250,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,30,80,130]
tallboy = [130,130,130,130,130,130,130,130,250,250,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,130,350,80,130]
hi_init = [130,130,130,130,130,130,430,130,250,250,130,130,130,430,130,130,130,130,130,130,130,130,130,130,130,130,350,80,130]
low_init = [130,130,130,130,130,130,30,130,150,150,130,130,130,30,130,130,130,130,130,130,130,130,130,130,130,130,50,50,130]

#Fighter specs
player_attr = tank
player_fighter = ['Player', player_attr, 4]
player_r_weapon = 'Steel Long Sword'
player_l_weapon = 'Unarmed'
player_rf_weapon = 'Unarmed'
player_lf_weapon = 'Unarmed'
player_weapons = {'r_wpn': player_r_weapon, 'l_wpn': player_l_weapon, 'rf_wpn': player_rf_weapon, 'lf_wpn': player_lf_weapon}

#Enemy specs
enemy_attr = low_init
enemy_fighter = ['Enemy', enemy_attr, 0, CombatAI]
enemy_r_weapon = 'Unarmed'
enemy_l_weapon = 'Unarmed'
enemy_rf_weapon = 'Unarmed'
enemy_lf_weapon = 'Unarmed'
enemy_weapons = {'r_wpn': enemy_r_weapon, 'l_wpn': enemy_l_weapon, 'rf_wpn': enemy_rf_weapon, 'lf_wpn': enemy_lf_weapon}

#Fighter and Weapons lists
fighters = [player_fighter, enemy_fighter]
weapons = {'Player': player_weapons, 'Enemy': enemy_weapons}

#Entity list
player = (60, 55, '@', 'white', 'Player', enums.EntityState.conscious, True, True)
enemy = (60, 60, '@', 'yellow', 'Enemy', enums.EntityState.conscious, False, True)
entities = [player, enemy]

#Key Dicts in order of key, command_verb
default_keys = {'q':('move','nw'), 'w':('move','n'), 'e':('move','ne'), 'd':('move','e'), 'c':('move','se'), 
                'x':('move','s'), 'z':('move','sw'),'a':('move','w'), 41: ('exit', None), '.':('spin','cw'), ',':('spin','ccw'),
                80: ('move','w'), 79:('move','e'),82:('move','n'),81:('move','s'),';':'strafe',95:('move','nw'), 
                96:('move','n'), 97:('move','ne'), 94:('move','e'), 91:('move','se'),90:('move','s'),
                89:('move','sw'),92:('move','w'),98:('spin','ccw'),'u':('stand',None),'p':('prone',None),'k':('kneel',None)}

key_maps = [default_keys]

#Gameplay options
show_rolls = True