
import tcod as libtcodpy
import bearlibterminal.terminal as terminal
from tcod import event, console
import options





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

def render_all(con_list, offset_list, type_list, dim_list, color_list, logs, entities, players, game_map) -> None:

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

def handle_keys(game_state) -> str or None:
    for evt in event.wait():
        if evt.type == "QUIT":
            exit()
        elif evt.type == "KEYDOWN":
            try:
                key = chr(evt.sym)
                if not key.isalnum():
                    key = evt.scancode
                    #print(key)
            except:
                key = evt.scancode
                #print(key)
                
            keymap = options.key_maps[game_state.value - 1]
            if not evt.repeat:
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

                    

        
























#Below for testing
def render(root_con, con_list, offset_list, type_list, entities, dim_list, color_list) -> None:
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
        fg_color = colors.get(fg_color)
        bg_color = colors.get(bg_color)
        libtcodpy.console_set_default_background(con, bg_color)
        libtcodpy.console_set_default_foreground(con, fg_color)
        if con_type == 0:
            for entity in entities:
                ent_color = colors.get(entity.color)
                libtcodpy.console_put_char_ex(con, entity.x, entity.y, entity.char, ent_color,bg_color)

        libtcodpy.console_blit(con, 0, 0, dim_x, dim_y, 0, offset_x, offset_y)
    
    libtcodpy.console_flush()
   




def create_terminal(w,h) -> object:
    term = terminal.open()
    terminal.set('window: size='+str(w)+'x'+str(h)+',title=Crimson Sands; font: fonts\\cp437_8x8.png, size=8x8, codepage=437')
    terminal.refresh()

    return term

def blt_handle_keys(game_state) -> str or None:
    key = None
    if terminal.has_input():
        key = terminal.read()
        print(key)
        if key == terminal.TK_CLOSE:
            exit()
        else:
            key = terminal.get(key)
            print(key)
            keymap = options.key_maps[game_state.value - 1]
            command = keymap.get(key)
            return command
    else:
        return None