
import tcod as libtcodpy
import bearlibterminal.terminal as terminal
from tcod import event
import options

colors = {'gray':libtcodpy.gray, 'dark_gray': libtcodpy.dark_gray, 'white':libtcodpy.white, 'black': libtcodpy.black, 'crimson': libtcodpy.crimson,
            'amber': libtcodpy.amber, 'dark_amber':libtcodpy.dark_amber, 'yellow':libtcodpy.yellow}


    

def create_root_console(w, h):
    con = libtcodpy.console_new(w, h)
    libtcodpy.console_set_custom_font('fonts\\cp437_8x8.png', libtcodpy.FONT_TYPE_GRAYSCALE | libtcodpy.FONT_LAYOUT_ASCII_INROW)
    libtcodpy.console_init_root(w, h, 'Combat Prototype', False, None, 'F')
    libtcodpy.console_set_default_background(con, libtcodpy.gray)
    libtcodpy.console_set_default_foreground(con, libtcodpy.black)
    return con

def create_console(w, h):

    con = libtcodpy.console_new(w, h)

    return con

def render_all(con_list, offset_list, type_list, entities, dim_list, color_list):

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
        render_console(con, entities, dim_x, dim_y, offset_x, offset_y, fg_color, bg_color, con_type)

    
    libtcodpy.console_flush()
   
def render_console(con, entities, width, height, x=0, y=0, fg_color='white', bg_color='black', con_type=0):
    fg_color = colors.get(fg_color)
    bg_color = colors.get(bg_color)
    libtcodpy.console_set_default_background(con, bg_color)
    libtcodpy.console_set_default_foreground(con, fg_color)

    if con_type == 0:
        for entity in entities:
            ent_color = colors.get(entity.color)
            libtcodpy.console_put_char_ex(con, entity.x, entity.y, entity.char, ent_color,bg_color)

    libtcodpy.console_blit(con, 0, 0, width, height, 0, x, y)

def handle_keys(game_state):
    for evt in event.wait():
        if evt.type == "QUIT":
            exit()
        elif evt.type == "KEYDOWN":
            key = chr(evt.sym)
            if not key.isalnum():
                key = evt.sym
            keymap = options.key_maps[game_state.value - 1]
            command = keymap.get(key)
            return command
        else:
            return None



#Below for testing
def render(root_con, con_list, offset_list, type_list, entities, dim_list, color_list):
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
   




def create_terminal(w,h):
    term = terminal.open()
    terminal.set('window: size='+str(w)+'x'+str(h)+',title=Crimson Sands; font: fonts\\cp437_8x8.png, size=8x8, codepage=437')
    terminal.refresh()

    return term

def blt_handle_keys(game_state):
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