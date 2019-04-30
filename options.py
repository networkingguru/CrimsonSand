
import enums

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

#Fighter specs
player_attr = tank
player_fighter = ['Player', player_attr, 0, [], [], None]
player_r_weapon = 'Unarmed'
player_f_weapon = 'Unarmed'
player_weapons = [player_r_weapon, player_f_weapon]

enemy_attr = tallboy
enemy_fighter = ['Enemy', enemy_attr, 0, [], [], None]
enemy_r_weapon = 'Unarmed'
enemy_f_weapon = 'Unarmed'
enemy_weapons = [enemy_r_weapon, enemy_f_weapon]

#Fighter and Weapons lists
fighters = [player_fighter, enemy_fighter]
weapons = {'Player': player_weapons, 'Enemy': enemy_weapons}

#Entity list
player = (50, 50, '@', 'white', 'Player', enums.EntityState.conscious, True, True)
enemy = (60, 60, '@', 'yellow', 'Enemy', enums.EntityState.conscious, False, True)
entities = [player, enemy]

#Key Dicts in order of key, command_verb
default_keys = {'q':('move','nw'), 'w':('move','n '), 'e':('move','ne'), 'd':('move',' e'), 'c':('move','se'), 
                'x':('move','s '), 'z':('move','sw'),'a':('move',' w'), 27: 'exit'}

key_maps = [default_keys]