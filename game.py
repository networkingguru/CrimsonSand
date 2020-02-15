import tcod as libtcodpy
from tcod import map
import options
import time
import global_vars
from combat_control import combat_controller
from combat_functions import change_actor
from ui_control import create_terminal, handle_input, render, fill_status_panel, BLTWindow
from enums import GameStates, CombatPhase, EntityState, MenuTypes
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from components.armor import apply_armor
from game_map import array_gen, fill_map
from fov_aoc import modify_fov, change_face
from game_messages import MessageLog, Message
from utilities import save_game, load_game


 


if __name__ == "__main__":
    libtcodpy.sys_set_fps(options.fps)

    #Console init
    dim_list = [(options.map_width, options.map_height), (options.status_panel_w, options.status_panel_h), 
                (options.enemy_panel_w, options.enemy_panel_h), (options.message_panel_w, options.message_panel_h)]

    menu_desc = {'New Game':'Start a new game', 'Load Game': 'Load the game from disk','Quit Game':'Exit the game'}
    menu_dict = {'type': MenuTypes.combat, 'header': 'Main Menu', 'options': ['New Game', 'Load Game','Quit Game'], 'mode': False, 'desc': menu_desc}

    term = create_terminal(options.screen_width, options.screen_height)

    con_list = ['map_con', 'status_panel', 'enemy_panel', 'message_panel']
    offset_list = ((options.map_x,options.map_y),(options.status_panel_x,options.status_panel_y),(options.enemy_panel_x,options.enemy_panel_y),
                (options.message_panel_x,options.message_panel_y))
    type_list = options.panel_types
    color_list = options.panel_colors

    frame_list = []

    leave = False
    dirty = True
    clear = False

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
    enemies = list(set(entities) - set(players))
    players[0].worn_armor = options.player_armor
    enemies[0].worn_armor = options.enemy_no_armor
    for e in entities:
        apply_armor(e)
    fill_status_panel(players[0], status_log)
    
    #Global order vars; players get first move
    order = []
    order.extend(players)
    order.extend(enemies)
    curr_actor = order[0]
    round_num = global_vars.round_num
    global_vars.turn_order = list(order)


    #Map/state init
    game_state = GameStates.main_menu
    combat_phase = CombatPhase.explore
    command = []
    event = []
    game_map = map.Map(options.map_width, options.map_height, 'F')
    fill_map(game_map, options.blocked, options.blocked)
    fov_transparency = array_gen(game_map, options.blocked)

    #Initial computations:
    #FOV and AOC comps
    for entity in entities:
        entity.fighter.update_aoc_facing()
        entity.fighter.aoc = change_face(entity.fighter.aoc_facing, entity.x, entity.y, entity.fighter.reach)
        fov_radius = int(round(entity.fighter.get_attribute('sit')/5))
        game_map.compute_fov(entity.x, entity.y, fov_radius, True)
        modify_fov(entity, game_map)

    #Begin main loop
    while not leave:
        if global_vars.debug_time: t0 = time.time()
        if game_state == GameStates.quit: 
            leave = True

        if dirty: render(entities, players, game_map, con_list, frame_list, offset_list, type_list, dim_list, color_list, logs, menu_dict, game_state)
        old_menu = menu_dict
        combat_phase, game_state, order, new_curr_actor = change_actor(order, entities, curr_actor, combat_phase, game_state, logs)
        if curr_actor != new_curr_actor:
            if global_vars.debug: print(curr_actor.name + ' ' + new_curr_actor.name)
            curr_actor = new_curr_actor

        elif curr_actor.state == EntityState.dead:
            combat_phase, game_state, order, new_curr_actor = change_actor(order, entities, curr_actor, combat_phase, game_state, logs)

        command, dirty = handle_input(curr_actor, game_state, menu_dict, entities, combat_phase, game_map, order, frame_list)
        
        if game_state not in [GameStates.main_menu]:
            menu_dict, combat_phase, game_state, curr_actor, order, clear = combat_controller(game_map, curr_actor, entities, players, command, logs, combat_phase, game_state, order)

        if old_menu != menu_dict: 
            dirty = True
            frame_list.clear()

        if clear: command = dict()
            
        if len(command) != 0:
            dirty = True
            if command.get('esc'): 
                if game_state in [GameStates.c_sheet] or combat_phase == CombatPhase.pause:
                    game_state = GameStates.default
                else:
                    combat_phase = CombatPhase.pause
            if command.get('Save Game'):
                messages = save_game()
                for msg in messages:
                    logs[2].add_message(msg)
            if command.get('Load Game'):
                messages = load_game()
                for msg in messages:
                    logs[2].add_message(msg)

            
            fill_status_panel(players[0], status_log)
            command = {}
            frame_list.clear()
            if global_vars.debug: print('Phase: ' + str(combat_phase))



        if global_vars.debug_time: t1 = time.time()
        if global_vars.debug_time: total_time = t1 - t0
        if global_vars.debug_time: print('Refresh time: ' + str(total_time))
        
        

        
