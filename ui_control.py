
import tcod as libtcodpy
import bearlibterminal.terminal as terminal
from tcod import event
import options

colors = {'gray':libtcodpy.gray, 'dark_gray': libtcodpy.dark_gray, 'white':libtcodpy.white, 'black': libtcodpy.black, 'crimson': libtcodpy.crimson,
            'amber': libtcodpy.amber, 'dark_amber':libtcodpy.dark_amber, 'yellow':libtcodpy.yellow}

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
    




def create_console(w, h):

    con = libtcodpy.console_new(w, h)
    libtcodpy.console_set_custom_font('fonts\\cp437_8x8.png', libtcodpy.FONT_TYPE_GRAYSCALE | libtcodpy.FONT_LAYOUT_ASCII_INROW)
    libtcodpy.console_init_root(w, h, 'Combat Prototype', False)
    return con

def render_all(con_list, entities, screen_width, screen_height):

    for con in con_list:
        con.clear()
        render_console(con, entities, screen_width, screen_height)

    
    libtcodpy.console_flush()
   
def render_console(con, entities, screen_width, screen_height, fg_color='white', bg_color='black', con_type=0):
    fg_color = colors.get(fg_color)
    bg_color = colors.get(bg_color)
    libtcodpy.console_set_default_background(con, bg_color)
    libtcodpy.console_set_default_foreground(con, fg_color)

    if con_type == 0:
        for entity in entities:
            ent_color = colors.get(entity.color)
            libtcodpy.console_put_char_ex(con, entity.x, entity.y, entity.char, ent_color,bg_color)

    libtcodpy.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

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



    