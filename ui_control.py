
import tcod as libtcodpy
import bearlibterminal.terminal as terminal
from tcod import event, console
import options
import global_vars
from enums import MenuTypes, GameStates, CombatPhase
from game_messages import Message
from utilities import inch_conv




colors = {'gray':libtcodpy.gray, 'dark_gray': libtcodpy.dark_gray, 'white':libtcodpy.white, 'black': libtcodpy.black, 'crimson': libtcodpy.crimson,
            'amber': libtcodpy.amber, 'dark_amber':libtcodpy.dark_amber, 'yellow':libtcodpy.yellow, 'light_gray': libtcodpy.light_gray,
            'darker_gray':libtcodpy.darker_gray, 'darker_amber': libtcodpy.darker_amber, 'green': libtcodpy.green, 'red': libtcodpy.red}


    

def create_root_console(w, h) -> object:
    con = libtcodpy.console_new(w, h)
    libtcodpy.console_set_custom_font('fonts\\cp437_8x8.png', libtcodpy.FONT_TYPE_GRAYSCALE | libtcodpy.FONT_LAYOUT_ASCII_INROW)
    libtcodpy.console_init_root(w, h, 'Combat Prototype', False, None, 'C')
    libtcodpy.console_set_default_background(con, libtcodpy.gray)
    libtcodpy.console_set_default_foreground(con, libtcodpy.black)
    return con

def create_console(w, h) -> object:

    con = console.Console(w,h,'F')    

    return con

def render_all(con_list, offset_list, type_list, dim_list, color_list, logs, entities, players, game_map, menu_dict = None) -> None:
    #con_list = [map_con, status_panel, enemy_panel, message_panel]
    map_con = con_list[0]

    for con in con_list:
        con.clear()
        idx = con_list.index(con)
        dim_x = dim_list[idx][0]
        dim_y = dim_list[idx][1]
        offset_x = offset_list[idx][0]
        offset_y = offset_list[idx][1]
        con_type = type_list[idx]
        fg_color = color_list[idx][0]
        bg_color = color_list[idx][1]
        if menu_dict != None:
            menu_type = menu_dict.get('type')
            menu_header = menu_dict.get('header')
            menu_options = menu_dict.get('options')
            hide_options = menu_dict.get('mode')
            
            if menu_type == MenuTypes.combat:
                menu(map_con, menu_header, menu_options, int(dim_list[0][0]/3), options.screen_width, options.screen_height, hide_options)
        if con_type == 0:
            render_console(con, entities, dim_x, dim_y, offset_x, offset_y, fg_color, bg_color, con_type, players, game_map)
        else:
            log = logs[con_type-1]
            render_console(con, entities, dim_x, dim_y, offset_x, offset_y, fg_color, bg_color, con_type, players, None, log)
        
    
    libtcodpy.console_flush()
   
def render_console(con, entities, width, height, dx=0, dy=0, fg_color='white', bg_color='black', con_type = 0, players = None, game_map = None, log = None) -> None:
    fg_color = colors.get(fg_color)
    bg_color = colors.get(bg_color)
    libtcodpy.console_set_default_background(con, bg_color)
    libtcodpy.console_set_default_foreground(con, fg_color)
    
    if con_type == 0: #Print map console
        
        for player in players:
            for y in range(game_map.height):
                for x in range(game_map.width):   
                    #Show if it's visible
                    if (x, y) in player.fighter.fov_visible:
                        con.bg[x][y] = colors.get('dark_amber')
                        if (x,y) in player.fighter.fov_wall:
                            con.bg[x][y] = colors.get('darker_gray')
                    #Not visible but explored
                    elif (x,y) in player.fighter.fov_explored:
                        if (x,y) in player.fighter.fov_wall:
                            con.bg[x][y] = colors.get('darker_gray')
                        else:
                            con.bg[x][y] = colors.get('darker_amber')
                    #Not explored                     
                    else:
                        con.bg[x][y] = colors.get('dark_gray')


        draw_entity(con, entities)

    elif con_type == 3: #Print messages to message console
        y = 1
        for message in log.messages:
            libtcodpy.console_set_default_foreground(con, colors.get(message.color))
            libtcodpy.console_print_ex(con, log.x, y, libtcodpy.BKGND_NONE, libtcodpy.LEFT, message.text)
            y += 1

    else: 
        if con_type == 1: entity = players[0]
        else:
            try:
                entity = players[0].fighter.targets[0]
            except:
                entity = None
                
        #Print paper dolls
        #libtcodpy.console_set_default_foreground(con, libtcodpy.white)
        libtcodpy.console_print_ex(con, log.x, 0, libtcodpy.BKGND_NONE, libtcodpy.LEFT, 'Hit Location')
        libtcodpy.console_print_ex(con, log.x+15, 0, libtcodpy.BKGND_NONE, libtcodpy.LEFT, 'DERM')
        libtcodpy.console_print_ex(con, log.x+20, 0, libtcodpy.BKGND_NONE, libtcodpy.LEFT, 'TIS')
        libtcodpy.console_print_ex(con, log.x+25, 0, libtcodpy.BKGND_NONE, libtcodpy.LEFT, 'BONE')
        if entity is not None:
            p_y = 1
            for hit_location in entity.fighter.locations:
                libtcodpy.console_print_ex(con, log.x, p_y, libtcodpy.BKGND_NONE, libtcodpy.LEFT, entity.fighter.name_location(p_y-1) + ':')
                libtcodpy.console_print_ex(con, log.x+15, p_y, libtcodpy.BKGND_NONE, libtcodpy.LEFT, str(hit_location[0]))
                libtcodpy.console_print_ex(con, log.x+20, p_y, libtcodpy.BKGND_NONE, libtcodpy.LEFT, str(hit_location[1]))
                libtcodpy.console_print_ex(con, log.x+25, p_y, libtcodpy.BKGND_NONE, libtcodpy.LEFT, str(hit_location[2]))
                p_y += 1

        if con_type == 1: #Print char con
            s_y = 50
            for message in log.messages:
                #libtcodpy.console_set_default_foreground(con, colors.get(message.color))
                libtcodpy.console_print_ex(con, log.x, s_y, libtcodpy.BKGND_NONE, libtcodpy.LEFT, message.text)
                s_y += 1

    libtcodpy.console_blit(con, 0, 0, width, height, 0, dx, dy)

def gen_status_panel(player) -> list:
    entries = []
    
    entries.append(str('INTELLECT: \t' + str(round(player.fighter.int))))
    entries.append(str('STRENGTH: \t' + str(round(player.fighter.str))))
    entries.append(str('AGILITY: \t' + str(round(player.fighter.agi))))
    entries.append(str('CONSTITUTION: \t' + str(round(player.fighter.con))))
    entries.append(str('SENSES: \t' + str(round(player.fighter.sens))))
    entries.append(str('APPEARANCE: \t' + str(round(player.fighter.appear))))
    entries.append(str('Height: \t' + inch_conv(player.fighter.height)))
    entries.append(str('Weight: \t' + str(round(player.fighter.weight)) + ' lbs'))
    entries.append(str('Reach: \t\t' + str(round(player.fighter.er)) + '"'))
    entries.append(str('Stamina: \t' + str(round(player.fighter.stamina))))
    entries.append(str('Stamina Regen: \t' + str(round(player.fighter.stamr)) + '/rd'))
    entries.append(str('Vitae: \t\t' + str(round(player.fighter.vitae)) + ' ml'))
    entries.append(str('Vitae Regen:\t' + str(round(player.fighter.vitr)) + ' ml/min'))
    entries.append(str('Move (walk): \t' + str(inch_conv(player.fighter.mv, 1)) + ' sq/rd'))
    entries.append(str('Move (jog): \t' + str(inch_conv(player.fighter.mv*1.5, 1)) + ' sq/rd'))
    entries.append(str('Move (run): \t' + str(inch_conv(player.fighter.mv*2, 1)) + ' sq/rd'))
    entries.append(str('Eff. Power: \t' + str(round(player.fighter.ep)) + ' PSI'))
    entries.append(str('Brawling: \t' + str(player.fighter.brawling) + '%'))
    entries.append(str('Dodge: \t\t' + str(player.fighter.dodge) + '%'))    
    entries.append(str('Deflect: \t' + str(player.fighter.deflect) + '%'))
    entries.append(str('AP: \t\t' + str(player.fighter.ap)))
    entries.append(str('Walk: \t\t' + str(player.fighter.walk_ap)) + ' AP/sq')
    entries.append(str('Jog: \t\t' + str(player.fighter.jog_ap)) + ' AP/sq')
    entries.append(str('Run: \t\t' + str(player.fighter.run_ap)) + ' AP/sq')
    return entries

def fill_status_panel(player, log) -> None:
    log.messages.clear()
    #Fill out char stats
    entries = gen_status_panel(player)
    for entry in entries:
        log.add_message(Message(entry))

def handle_input(game_state, menu_dict = None) -> str or int or None:
    for evt in event.wait():
        if evt.type == "QUIT":
            exit(0)
        elif evt.type == "KEYDOWN" and not evt.repeat:
            try:
                key = chr(evt.sym)
                if not key.isalnum():
                    key = evt.scancode
                    if global_vars.debug: print(key)
            except:
                key = evt.scancode
                if global_vars.debug: print(key)
            if game_state == GameStates.default:
                keymap = options.key_maps[game_state.value - 1]
                command = keymap.get(key)
                return command
            if game_state == GameStates.menu:
                try:
                    menu_type = menu_dict.get('type')
                    menu_header = menu_dict.get('header')
                    menu_options = menu_dict.get('options')
                    hide_options = menu_dict.get('mode')
                except:
                    print('Something is missing from the menu_dict')
                if hide_options:
                    for item in menu_options:
                        index = evt.sym - ord(item)
                        if index >= 0 and not index > (len(menu_options)-1):
                            command = {menu_options[index]:menu_options[index]}
                            return command
                else:
                    index = evt.sym - ord('a')
                    if index >= 0 and not index > (len(menu_options)-1):
                        command = {menu_options[index]:menu_options[index]}
                        return command
        else:
            return None

def handle_global_input(combat_phase) -> str or int or None:
    if combat_phase != CombatPhase.explore:
        for evt in event.get():
            if evt.type == "QUIT":
                exit(0)
            elif evt.type == "KEYDOWN" and not evt.repeat:
                try:
                    key = chr(evt.sym)
                    if not key.isalnum():
                        key = evt.scancode
                        if global_vars.debug: print(key)
                except:
                    key = evt.scancode
                    if global_vars.debug: print(key)

                keymap = options.default_keys
                command = keymap.get(key)
                return command
                
            else:
                return None
    else:    
        for evt in event.wait():
            if evt.type == "QUIT":
                exit(0)
            elif evt.type == "KEYDOWN" and not evt.repeat:
                try:
                    key = chr(evt.sym)
                    if not key.isalnum():
                        key = evt.scancode
                        if global_vars.debug: print(key)
                except:
                    key = evt.scancode
                    if global_vars.debug: print(key)

                keymap = options.default_keys
                command = keymap.get(key)
                return command
                
            else:
                return None

def draw_entity(con, entities) -> None:
    
    players = set()
    enemies = set()
    players_aoc = set()
    players_visible = set()
    players_explored = set()
    for entity in entities:
        if entity.player:
            players.add(entity)
        else:
            enemies.add(entity)

    #Creating a set with all player AOC, explored, and visible values    
    for player in players:
        players_aoc = players_aoc|set(player.fighter.aoc)
        players_visible = players_visible|set(player.fighter.fov_visible)
        players_explored = players_explored|set(player.fighter.fov_explored)

    #Creating a set with all enemy AOC values
    enemies_aoc = set()
    for enemy in enemies:
        enemies_aoc = enemies_aoc|set(enemy.fighter.aoc)


    #Paint players AOC green
    for (x,y) in players_aoc:
        libtcodpy.console_set_char_background(con, x, y, colors.get('green'), 1)
    #Paint visible enemy AOC's red
    for (x,y) in enemies_aoc:
        if (x,y) in players_visible:
            #Paint overlapping enemy/player AOC's yellow
            if (x,y) in players_aoc:
                libtcodpy.console_set_char_background(con, x, y, colors.get('yellow'), 1)
            else:
                libtcodpy.console_set_char_background(con, x, y, colors.get('red'), 1)
    
    #Place players
    for player in players:
        libtcodpy.console_put_char_ex(con, player.x, player.y, player.char, colors.get(player.color), colors.get('dark_amber'))

    #PLace visible enemies
    for enemy in enemies:
        if (enemy.x, enemy.y) in players_visible:
            libtcodpy.console_put_char_ex(con, enemy.x, enemy.y, enemy.char, colors.get(enemy.color), colors.get('dark_amber'))
        elif (enemy.x, enemy.y) in players_explored:
            libtcodpy.console_put_char_ex(con, enemy.x, enemy.y, enemy.char, colors.get('darker_gray'), colors.get('darker_amber'))

def menu(con, header, options, width, screen_width, screen_height, hide_options = False):
    #if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcodpy.console_get_height_rect(con, 0, 0, width, screen_height, header)
    #header_height = int(round(len(header)/width))
    if not hide_options:
        height = len(options) + header_height
    else:
        height = header_height

    # create an off-screen console that represents the menu's window
    window = libtcodpy.console_new(width, height)

    # print the header, with auto-wrap
    libtcodpy.console_set_default_foreground(window, libtcodpy.white)
    libtcodpy.console_print_rect_ex(window, 0, 0, width, height, libtcodpy.BKGND_NONE, libtcodpy.LEFT, header)

    # print all the options
    if not hide_options:
        y = header_height
        letter_index = ord('a')
        for option_text in options:
            text = '(' + chr(letter_index) + ') ' + option_text
            libtcodpy.console_print_ex(window, 0, y, libtcodpy.BKGND_NONE, libtcodpy.LEFT, text)
            y += 1
            letter_index += 1

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    libtcodpy.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def combat_menu(con, header, options, menu_width, screen_width, screen_height, hide_options = False):
    #Show a menu with each option as a seperate key
    if len(options) == 0:
        options = ['You are disabled and may not attack']
    menu(con, header, options, menu_width, screen_width, screen_height, hide_options)
             

        
























#Below for testing
def render(entities, players, game_map, con_list, offset_list, type_list, dim_list, color_list,logs) -> None:
    terminal.clear()
    for con in con_list:
        idx = con_list.index(con)
        dim_x = dim_list[idx][0]
        dim_y = dim_list[idx][1]
        offset_x = offset_list[idx][0]
        offset_y = offset_list[idx][1]
        con_type = type_list[idx]
        
        if con_type == 0:
            render_map_con(entities, players, game_map, dim_x, dim_y, offset_x, offset_y)
        elif con_type == 3:
            log = logs[con_type-1]
            render_msg_con(offset_x, offset_y, log)
        else:
            log = logs[con_type-1]
            render_status_con(entities, players, game_map, dim_x, dim_y, con_type, log, offset_x, offset_y)
    terminal.refresh()
   




def create_terminal(w,h) -> bool:
    term = terminal.open()
    terminal.set('window: size='+str(w)+'x'+str(h)+', cellsize=auto, title=Crimson Sands; font: fonts\\DejaVuSansMono-Bold.ttf, size=8x8')
    terminal.composition(terminal.TK_OFF)
    terminal.refresh()
    return term

def blt_handle_keys(game_state) -> str or None:
    key = terminal.read()
    command = None
    #print(key)
    if key == terminal.TK_CLOSE:
        exit()
    else:
        if terminal.check(terminal.TK_CHAR):
            key = chr(terminal.state(terminal.TK_CHAR))
        #print(key)
        keymap = options.key_maps[game_state.value - 1]
        command = keymap.get(key)
    
    return command


def blt_handle_global_input(game_state) -> str or int or None:
    
    command = None
    if terminal.has_input():
        key = terminal.read()
        if key == terminal.TK_CLOSE:
            exit(0)
        else:
            if terminal.check(terminal.TK_CHAR):
                key = chr(terminal.state(terminal.TK_CHAR))
            keymap = options.key_maps[game_state.value - 1]
            command = keymap.get(key)
    return command
                
            


def render_map_con(entities, players, game_map, width, height, ox=0, oy=0) -> None:

    for player in players:
        for y in range(game_map.height):
            for x in range(game_map.width):   
                #Show if it's visible
                if (x,y) in player.fighter.fov_visible:
                    terminal.color('light amber')
                    terminal.put(x+ox, y+oy, 0x2588)
                    if (x,y) in player.fighter.fov_wall:
                        terminal.color('dark gray')
                        terminal.put(x+ox, y+oy, 0x2588)
                #Not visible but explored
                elif (x,y) in player.fighter.fov_explored:
                    if (x,y) in player.fighter.fov_wall:
                        terminal.color('darker gray')
                        terminal.put(x+ox, y+oy, 0x2588)
                    else:
                        terminal.color('darker amber')
                        terminal.put(x+ox, y+oy, 0x2588)
                #Not explored                     
                else:
                    terminal.color('dark gray')
                    terminal.put(x+ox, y+oy, 0x2588)


    print_entities(entities, ox, oy)

def render_status_con(entities, players, game_map, width, height, con_type, log, ox=0, oy=0):
    if con_type == 1: entity = players[0]
    else:
        try:
            entity = players[0].fighter.targets[0]
        except:
            entity = None
           
    #Print paper dolls
    terminal.puts(ox, oy, '[color=white][bg_color=black]Hit Location')
    terminal.puts(ox+15, oy, '[color=white][bg_color=black]DERM')
    terminal.puts(ox+20, oy, '[color=white][bg_color=black]TIS')
    terminal.puts(ox+25, oy, '[color=white][bg_color=black]BONE')

    if entity is not None:
        p_y = 1
        for hit_location in entity.fighter.locations:
            terminal.color('white')
            terminal.puts(ox, oy+p_y, entity.fighter.name_location(p_y-1) + ':')
            terminal.puts(ox+15, oy+p_y, str(hit_location[0]))
            terminal.puts(ox+20, oy+p_y, str(hit_location[1]))
            terminal.puts(ox+25, oy+p_y, str(hit_location[2]))
            p_y += 1

    if con_type == 1: #Print char con
        s_y = 50
        for message in log.messages:
            terminal.puts(ox, oy+s_y, message.text)
            s_y += 1

def render_msg_con(ox, oy, log):
    y = 1
    for message in log.messages:
        terminal.puts(ox, oy+y, message.text)
        y += 1

def print_entities(entities, ox, oy) -> None:
    
    players = set()
    enemies = set()
    players_aoc = set()
    players_visible = set()
    players_explored = set()
    for entity in entities:
        if entity.player:
            players.add(entity)
        else:
            enemies.add(entity)

    #Creating a set with all player AOC, explored, and visible values    
    for player in players:
        players_aoc = players_aoc|set(player.fighter.aoc)
        players_visible = players_visible|set(player.fighter.fov_visible)
        players_explored = players_explored|set(player.fighter.fov_explored)

    #Creating a set with all enemy AOC values
    enemies_aoc = set()
    for enemy in enemies:
        enemies_aoc = enemies_aoc|set(enemy.fighter.aoc)


    #Paint players AOC green
    for (x,y) in players_aoc:
        terminal.color('green')
        terminal.put(x+ox, y+oy, 0x2588)
    #Paint visible enemy AOC's red
    for (x,y) in enemies_aoc:
        if (x,y) in players_visible:
            #Paint overlapping enemy/player AOC's yellow
            if (x,y) in players_aoc:
                terminal.color('yellow')
                terminal.put(x+ox, y+oy, 0x2588)
            else:
                terminal.color('red')
                terminal.put(x+ox, y+oy, 0x2588)

    
    #Place players
    for player in players:
        terminal.puts(player.x+ox, player.y+oy, '[bk_color=dark amber][color='+player.color+']'+player.char+'[/color][/bk_color]')

    #PLace visible enemies
    for enemy in enemies:
        if (enemy.x, enemy.y) in players_visible:
            terminal.puts(enemy.x+ox, enemy.y+oy, '[bk_color=dark amber][color='+enemy.color+']'+enemy.char+'[/color][/bk_color]')
        elif (enemy.x, enemy.y) in players_explored:
            terminal.puts(enemy.x+ox, enemy.y+oy, '[bk_color=darker amber][color=darker gray]'+enemy.char+'[/color][/bk_color]')

