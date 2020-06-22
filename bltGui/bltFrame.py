from bearlibterminal import terminal
from collections import namedtuple
from . import bltSkins
from . import bltInput
from .bltButton import bltButton
from .bltSlider import bltSlider
from math import ceil
import textwrap
import itertools

from . import bltColor as Color
from .bltControl import bltControl as Control
from types import *

Pos = namedtuple('Pos', 'x y')
mouse = bltInput.mouse



class bltFrame(Control):

    layer_index = 10

    def __init__(self, x, y, w ,h, title=None, frame=True, layer=None, text="", draggable=False, visible=True, skin=None, color_skin=None, font='', title_font = ''):
        Control.__init__(self, ['close', 'show'])
        self.pos = Pos(x, y)
        self.name = ''
        self.width = w
        self.height = h
        self.title = title
        self._wrapped_text = self.wrap_text(text)
        self._fulltext = text
        self._text_pages = []
        self.font = font
        self.title_font = title_font
        

        self.frame = frame
        if layer is None:
            self.layer = bltFrame.layer_index
            bltFrame.layer_index += 1
        else:
            self.layer = layer
        self.print_queue = []
        self.dragging = False
        self.click_x = None
        self.draggable = draggable
        self.visible = visible
        self.controls = []
        if skin:
            self.skin = dict(bltSkins.GLYPH_SKINS[skin])
        else:
            self.skin = dict(bltSkins.GLYPH_SKINS['SINGLE'])
        if color_skin:
            self.color_skin = dict(bltSkins.COLOR_SKINS[color_skin])
        else:
            self.color_skin = dict(bltSkins.COLOR_SKINS['DEFAULT'])
        self._dirty = True
        self.hover = False
        self.clicked = False
        self.resizing = False

    @property
    def full_text(self):
        return self._fulltext

    @property
    def text(self):
        return self._wrapped_text

    @text.setter
    def text(self, value):
        self._fulltext = value
        self._wrapped_text = self.wrap_text(value)


    @property
    def dirty(self):
        if self._dirty:
            return True
        for c in self.controls:
            if c.dirty:
                self.dirty = True
                return True
        return False

    @dirty.setter
    def dirty(self, value):
        self._dirty = value
        if value:
            for c in self.controls:
                c.dirty = True

    def get_dispatch(self, value):
        self.text = value
        self.dirty = True


    def clear(self):
        #print "Clearing Layer: {0}".format(self.layer)
        terminal.layer(self.layer)
        terminal.clear_area(self.pos.x, self.pos.y, self.width, self.height)

    def draw(self):
        if self.visible:
            #print "Drawing Frame: {0}, {1}".format(self.title, self.dirty)
            self.clear()
            self._draw_frame()
            #print self.controls
            for c in self.controls:
                if c.frame_element == True:
                    c.draw()
                elif c.y < self.height-2:
                    c.draw()
            self.dirty = False
        elif not self.visible:
            self.clear()

    def wrap_text(self, text):
        if isinstance(text, LambdaType):
            text = text()
        text = textwrap.dedent(text).strip()
        w = textwrap.TextWrapper(self.width - 2,break_long_words=False)
        t_list = [w.wrap(i) for i in text.split('\n') if i != '']

        t_list = list(itertools.chain.from_iterable(t_list))


        #text = textwrap.wrap(text, self.width - 2)

        return t_list


    def update(self):
        for c in self.controls:
            c.update()
        #self._test_mouse()
        if self.resizing:
            self._resize()

    def _draw_frame(self):
        if self.title:
            off = self.width - len(self.title)
            offset_x1 = off // 2
            offset_x2 = off - offset_x1
        else:
            offset_x1 = self.width
            offset_x2 = 0

        #print "Layer: {0}".format(self.layer)
        terminal.layer(self.layer)

        for x1 in range(self.width):
            for y1 in range(self.height):

                terminal.color(self.color_skin['BKCOLOR'])
                terminal.puts(x1 + self.pos.x, y1 + self.pos.y, self.skin['BACKGROUND'])
                terminal.color(self.color_skin['COLOR'])
                if self.frame:
                    # Colors
                    if (x1, y1) == (0, 0):
                        terminal.puts(x1 + self.pos.x, y1 + self.pos.y, self.skin['BOX_NW'])
                    elif (x1, y1) == (self.width - 1, 0):
                        terminal.puts(x1 + self.pos.x, y1 + self.pos.y, self.skin['BOX_NE'])
                    elif (x1, y1) == (0, self.height - 1):
                        terminal.puts(x1 + self.pos.x, y1 + self.pos.y, self.skin['BOX_SW'])
                    elif (x1, y1) == (self.width - 1, self.height - 1):
                        terminal.puts(x1 + self.pos.x, y1 + self.pos.y, self.skin['BOX_SE'])
                    elif x1 == self.width - 1:
                        terminal.puts(x1 + self.pos.x, y1 + self.pos.y, self.skin['BOX_E'])
                    elif x1 == 0:
                        terminal.puts(x1 + self.pos.x, y1 + self.pos.y, self.skin['BOX_W'])
                    elif y1 == self.height - 1 or (y1 == 0 and not self.title):
                        terminal.puts(x1 + self.pos.x, y1 + self.pos.y, self.skin['BOX_S'])
                    elif y1 == 0 and self.title and (
                            x1 < offset_x1 or x1 > self.width - offset_x2 - 1):  # + self.pos.x:
                        terminal.puts(x1 + self.pos.x, y1 + self.pos.y, self.skin['BOX_N'])

                # DEBUG
                #terminal.puts(self.pos.x + 1, self.pos.y + 1, "Layer: {0}".format(self.layer) )
                #terminal.puts(self.pos.x + 1, self.pos.y + 3, "Hover: {0}".format(self.hover))
                #terminal.puts(self.pos.x + 1, self.pos.y + 4, "Clicked on: {0}".format(self.clicked))
                #terminal.puts(self.pos.x + 1, self.pos.y + 5, ": {0}".format(self.layer))


        ''' DRAW TEXT'''

        if self.text:
            for i, line in enumerate(self.text):
                if i <= self.height - 3:
                    terminal.puts(self.pos.x + 1,
                                self.pos.y + 1 + i,
                                self.font + line
                                )
                else:
                    break

        terminal.puts(offset_x1 + self.pos.x, self.pos.y, self.title_font + self.title)

        for p in self.print_queue:
            text = textwrap.dedent(p[2]).strip()
            terminal.puts(p[0] + self.pos.x, p[1] + self.pos.y, self.font + textwrap.fill(text, self.width - 2))

    def _test_mouse(self):
        if mouse.hover_rect(self.pos.x, self.pos.y, self.width, self.height, layer=self.layer):
            self.hover = True
            if mouse.lbutton_pressed:
                self.clicked = True
                self.clear()
                self.layer = bltFrame.layer_index
                bltFrame.layer_index += 1
            else:
                self.clicked = False
            if mouse.clicked_rect(self.pos.x, self.pos.y, self.width, 1, layer=self.layer) and self.draggable:
                self.dragging = True
            else:
                if mouse.active_layer > self.layer:
                    self.dragging = False
            self.dirty = True
        else:
            if self.hover:
                self.hover = False
                self.dirty = True
            if self.clicked:
                self.clicked = False
                self.dirty = True

        #print "Layer: {0}, Mouse.ActiveLayer: {1}".format(self.layer, mouse.active_layer)

        '''
        if mouse.lbutton_pressed and self.pos.x <= mouse.cx <= self.pos.x + self.width and mouse.cy == self.pos.y:
            self.dragging = True
        '''
        if mouse.lbutton and self.dragging:
            if self.click_x is None:
                self.click_x = mouse.cx - self.pos.x
            self.clear()
            self.pos = Pos(mouse.cx - self.click_x, mouse.cy) # (width / 2)

            self.dragging = True
            self.dirty = True
        else:
            self.dragging = False
            self.click_x = None

    def _resize(self):
        if not mouse.lbutton:
            self.resizing = False
            return

        self.clear()
        new_width = mouse.cx - self.pos.x + 1
        new_height = mouse.cy - self.pos.y + 1

        if new_width != self.width or new_height != self.height:

            self.width = new_width
            if self.title:
                self.width = max(self.width, len(self.title) + 2)
            else:
                self.width = max(self.width, 4)
            self.height = new_height
            self.height = max(self.height, 3)

            for c in self.controls:
                c.resized()

            if self.text:
                self.text = self.full_text

            self.dirty = True

    def puts(self, x, y, text):
        self.print_queue.append((x, y, text))

    def clear_text(self):
        self.print_queue = []

    def show(self, visible=True):
        self.visible = visible

    def add_control(self, control):
        if type(control) is list:
            for c in control:
                self.controls.append(c)
        else:
            self.controls.append(control)


class bltModalFrame(bltFrame):
    def __init__(self, *args, **kwargs):
        bltFrame.__init__(self, *args, **kwargs)

        #self.background = bltFrame(0, 0, 80, 24, bkcolor=Color("200,255,255,255"))
        self.add_control(bltButton(self, 2, 2, "1", function=bltButton.close))
        self.add_control(bltButton(self, 4, 2, "2", function=bltButton.close))

    '''
    def draw(self):
        while True:
            #self.background.draw()
            bltFrame.draw(self)
            for c in self.controls:
                c.draw()
    '''


class bltShowListFrame(bltFrame):
    def __init__(self, *args, **kwargs):
        bltFrame.__init__(self, *args, **kwargs)
        self.item_dict = {}


    def set_dict(self, item_dict):
        self.item_dict = item_dict

    def get_dispatch(self, value):
        for key in self.item_dict:
            if key == value:
                self.text = self.item_dict.get(key)

        if len(self.controls) > 0:
            for c in self.controls:
                if isinstance(c,bltSlider):
                    if len(self._wrapped_text) < self.height - 2:
                        c.visible = False
                    else:
                        c.visible = True
                        c.max_val = ceil(len(self._wrapped_text)/self.height)
                        c.value_per_cell =  c.max_val / c.width
                        self.paginate()
                        
        self.dirty = True

    def paginate(self):
        pages = []
        n = 0
        page = []
        for l in self._wrapped_text:
            if n < self.height - 2:
                page.append(l)
                n+=1
            else:
                pages.append(page)
                page = []
                n = 0

        if len(page) > 0:
            pages.append(page)

        self._text_pages = pages

    def change_page(self,page=0):
       
        self._wrapped_text = self._text_pages[page-1]






