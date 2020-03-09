from bearlibterminal import terminal
from . import bltSkins
from . import bltInput
from .bltControl import bltControl as Control
mouse = bltInput.mouse


class bltTextBox(Control):
    def __init__(self, owner, x, y, text="", length=4, color='white', bkcolor='black', frame=None, skin='SINGLE'):
        Control.__init__(self, ['active', 'changed'])
        self.owner = owner
        self.x = x
        self.y = y
        self.text = text
        self.length = length
        self.color = color
        self.bkcolor = bkcolor
        self.skin = bltSkins.GLYPH_SKINS[skin]
        self.active = False
        self.dirty = True
        self.frame_element = False

    def draw(self):
        if self.dirty:
            if self.owner:
                layer = self.owner.layer
                x = self.owner.pos.x
                y = self.owner.pos.y
            else:
                layer = terminal.state(terminal.TK_LAYER)
                x = 0
                y = 0

            terminal.color(self.bkcolor)
            terminal.puts(self.x + 1 + x, self.y + y, self.skin['BACKGROUND'] * self.length)
            terminal.color(self.color)

            if self.active:

                self.active = False

            terminal.color(self.bkcolor)
            terminal.puts(self.x + 1 + x, self.y + y, self.skin['BACKGROUND'] * self.length)
            terminal.color(self.color)
            #print self.text
            terminal.puts(self.x + x + 1, self.y + y, self.text[:self.length])
            self.dirty = False

    def update(self):
        if self.owner:
            layer = self.owner.layer
            x = self.owner.pos.x
            y = self.owner.pos.y
        else:
            layer = terminal.state(terminal.TK_LAYER)
            x = 0
            y = 0

        if mouse.clicked_rect(self.x + x, self.y + y, self.length, 1):
            terminal.layer(layer)
            terminal.color('white')
            terminal.puts(self.x + 1 + x, self.y + y, self.skin['BACKGROUND'] * self.length)
            terminal.color('black')
            terminal.refresh()
            result, text = terminal.read_str(self.x + x + 1, self.y + y, self.text, self.length)
            terminal.refresh()
            self.text = text



            self.active = True
            self.dirty = True

class bltNumericBox(Control):
    def __init__(self, owner, x, y, text="", length=4, color='white', bkcolor='black', frame=None, skin='SINGLE',min_val=0,max_val=100):
        Control.__init__(self, ['active', 'changed'])
        self.owner = owner
        self.x = x
        self.y = y
        self.text = text
        self.length = length
        self.color = color
        self.bkcolor = bkcolor
        self.skin = bltSkins.GLYPH_SKINS[skin]
        self.min_val = min_val
        self.max_val = max_val
        self.error = None
        self.active = False
        self.dirty = True
        self.frame_element = False

    def draw(self):
        if self.dirty:
            if self.owner:
                layer = self.owner.layer
                x = self.owner.pos.x
                y = self.owner.pos.y
            else:
                layer = terminal.state(terminal.TK_LAYER)
                x = 0
                y = 0

            terminal.color(self.bkcolor)
            terminal.puts(self.x + 1 + x, self.y + y, self.skin['BACKGROUND'] * self.length)
            terminal.color(self.color)

            if self.active:

                self.active = False

            terminal.color(self.bkcolor)
            terminal.puts(self.x + 1 + x, self.y + y, self.skin['BACKGROUND'] * self.length)
            terminal.color(self.color)
            #print self.text
            terminal.puts(self.x + x + 1, self.y + y, self.text[:self.length])
            self.dirty = False

    def update(self):
        if self.owner:
            layer = self.owner.layer
            x = self.owner.pos.x
            y = self.owner.pos.y
        else:
            layer = terminal.state(terminal.TK_LAYER)
            x = 0
            y = 0

        if mouse.clicked_rect(self.x + x, self.y + y, self.length, 1):
            terminal.layer(layer)
            terminal.color('white')
            terminal.puts(self.x + 1 + x, self.y + y, self.skin['BACKGROUND'] * self.length)
            terminal.color('black')
            terminal.refresh()
            result, text = terminal.read_str(self.x + x + 1, self.y + y, self.text, self.length)
            terminal.refresh()
            if text.isnumeric() and (self.min_val <= int(text) <= self.max_val):
                self.text = str(text)
                self.error = None
            else:
                self.error = 'Text must be numeric and between ' + str(self.min_val) + ' and ' + str(self.max_val) + '.'


            self.active = True
            self.dirty = True




