import textwrap
from .bltButton import *
from bearlibterminal import terminal
from bltGui import bltSkins as Skins
from .bltControl import bltControl as Control


class bltListbox(Control):
    def __init__(self, owner, x, y, items, collapse=False, lock_focus = False, header = None, w = 15):
        Control.__init__(self, ['hover', 'changed'])
        self.owner = owner
        self.x = x
        self.y = y
        self.w = w
        self.header_h = 0
        self.items = items
        self.header = header
        self.frame_element = False
        self.dirty = True
        self.length = len(max(items, key=len))
        self.selected_index = None
        self.hover_index = -1
        self.hover = False
        self.lock_focus = lock_focus

        self.colors = Skins.COLOR_SKINS['GRAY']

        self.collapse = collapse
        if self.collapse:
            self.expanded = False
        else:
            self.expanded = True

    def apply_header(self):
        if self.header is not None:
            self.header = textwrap.wrap(self.header, self.w-2)
            self.header_h = len(self.header)

    def update(self):
        mouse = Input.mouse
        key = Input.key
        if self.owner:
            layer = self.owner.layer
            x = self.owner.pos.x
            y = self.owner.pos.y
        else:
            layer = terminal.state(terminal.TK_LAYER)
            x = 0
            y = 0
        
        if self.expanded:
            if self.hover or self.lock_focus:
                if key is not None and key not in range(128,141):
                    if key in [terminal.TK_UP, terminal.TK_DOWN, terminal.TK_ENTER, terminal.TK_KP_ENTER]:
                        if self.hover_index is not None:
                            if key == terminal.TK_UP:
                                if self.hover_index == 0:
                                    self.hover_index = len(self.items) - 1
                                else:
                                    self.hover_index -= 1
                            elif key in [terminal.TK_ENTER, terminal.TK_KP_ENTER]:
                                self.selected_index = self.hover_index
                                self.dispatch('changed', self.selected_index)
                            else:
                                if self.hover_index == len(self.items) - 1:
                                    self.hover_index = 0
                                else:
                                    self.hover_index += 1
                            self.dispatch('changed', self.hover_index)
                            self.dirty = True
                        else:
                            if key == terminal.TK_UP:
                                self.hover_index = 0
                            else:
                                self.hover_index = len(self.items) - 1
                            self.dispatch('changed', self.hover_index)
                            self.dirty = True
                    else:
                        for item in self.items:
                            item_index = self.items.index(item)
                            cp = 4 + item_index
                            if cp == key:
                                self.hover_index = item_index
                                self.selected_index = item_index
                                self.dispatch('changed', self.hover_index)
                                self.dispatch('changed', self.selected_index)
                                self.dirty = True
                                break


            if mouse.hover_rect(self.x + x, self.y + y, self.length + 1, len(self.items)):
                if mouse.hover_rect(self.x + x + self.length, self.y + y, 1, 1) and self.collapse:

                    self.hover = True
                    if mouse.lbutton_pressed:
                        self.expanded = False
                        self.dirty = True
                else:
                    self.hover = True
                    self.hover_index = mouse.cy - (self.y + self.owner.pos.y)
                    #DEBUG
                    # print("Mouse pos: " + str(mouse.cy))
                    # print("Control pos: " + str(self.y))
                    # print("Owner pos: " + str(self.owner.pos.y))
                    # print("Item index: " + str(self.hover_index))
                    self.dispatch('changed', self.hover_index)
                    if mouse.lbutton_pressed:
                        self.selected_index = mouse.cy - (self.y + self.owner.pos.y)
                        self.dispatch('changed', self.selected_index)
                        if self.collapse:
                            self.expanded = False
                    self.dirty = True
            else:
                if self.hover:
                    self.dirty = True
                self.hover = False
                self.pressed = False
                #self.hover_index = -1
        elif mouse.hover_rect(self.x + x + self.length, self.y + y, 1, 1) and self.collapse:
            self.hover = True
            if mouse.lbutton_pressed:
                self.expanded = True

        else:
            self.hover = False
            if self.collapse:
                self.expanded = False

    def draw(self):
        if self.expanded:
            if self.header is not None:
                color = self.colors['COLOR']
                bkcolor = self.colors['BKCOLOR']
                terminal.puts(self.x + self.owner.pos.x, self.y + self.owner.pos.y, "[c={0}] {2}".format(color, bkcolor, self.header))
            for i, item in enumerate(self.items):
                letter_index = ord('a') + i
                color = self.colors['COLOR']
                bkcolor = self.colors['BKCOLOR']
                if i == self.hover_index:
                    color = self.colors['HOVER']
                    bkcolor = self.colors['BKHOVER']
                if i == self.selected_index:
                    color = self.colors['SELECTED']
                    bkcolor = self.colors['BKSELECTED']

                if bkcolor is not None:
                    terminal.puts(self.x + self.owner.pos.x, self.y + self.owner.pos.y + i + self.header_h, "[c={0}]".format(bkcolor) + str("[U+2588]" * (self.length+5)))
                terminal.puts(self.x + self.owner.pos.x, self.y + self.owner.pos.y + i + self.header_h, "[c={0}] {3}) {2}".format(color, bkcolor, item, chr(letter_index)))

            if self.collapse:
                bkcolor = self.colors['SELECTED']
                terminal.puts(self.x + self.owner.pos.x + self.length, self.y + self.owner.pos.y,
                              "[c={0}]".format(bkcolor) + str("[U+2588]"))
                terminal.puts(self.x + self.owner.pos.x + self.length, self.y + self.owner.pos.y,
                              "[c={0}]".format(color) + str("[U+25BC]"))
            self.dirty = False
        if not self.expanded:

            color = self.colors['COLOR']
            bkcolor = self.colors['BKCOLOR']


            i = self.selected_index


            if bkcolor is not None:
                terminal.puts(self.x + self.owner.pos.x, self.y + self.owner.pos.y , "[c={0}]".format(bkcolor) + str("[U+2588]" * (self.length+5)))
            if self.selected_index is not None:
                item = self.items[i]
                terminal.puts(self.x + self.owner.pos.x, self.y + self.owner.pos.y, "[c={0}] {3}) {2}".format(color, bkcolor, item, chr(letter_index)))

            if self.collapse:
                bkcolor = self.colors['BKCOLOR']
                terminal.puts(self.x + self.owner.pos.x + self.length, self.y + self.owner.pos.y,
                              "[c={0}]".format(bkcolor) + str("[U+2588]"))
                terminal.puts(self.x + self.owner.pos.x + self.length, self.y + self.owner.pos.y,
                              "[c={0}]".format(color) + str("[U+25B2]"))

            self.dirty = False

    def return_item(self):
        item = self.items[self.selected_index]
        return item






