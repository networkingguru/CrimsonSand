from tcod import libtcodpy

def create_console(w, h):
    con = libtcodpy.console_new(w, h)
    libtcodpy.console_set_custom_font('fonts\\cp437_8x8.png', libtcodpy.FONT_TYPE_GRAYSCALE | libtcodpy.FONT_LAYOUT_ASCII_INROW)
    libtcodpy.console_init_root(w, h, 'Combat Prototype', False)
    return con

def render_console(con, screen_width, screen_height):

 
    libtcodpy.console_set_default_background(con, libtcodpy.dark_gray)
    libtcodpy.console_set_default_foreground(con, libtcodpy.white)
    libtcodpy.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
    libtcodpy.console_flush()
   