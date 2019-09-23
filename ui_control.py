
import tcod as libtcodpy
import bearlibterminal.terminal as terminal
from tcod import event, console
import textwrap
import options
import global_vars
from enums import MenuTypes, GameStates, CombatPhase, EntityState
from game_messages import Message
from utilities import inch_conv


def gen_status_panel(player) -> list:
    entries = []
    
    entries.append(str('INTELLECT: \t' + str(round(player.fighter.get_attribute('int')))))
    entries.append(str('STRENGTH: \t' + str(round(player.fighter.get_attribute('str')))))
    entries.append(str('AGILITY: \t' + str(round(player.fighter.get_attribute('agi')))))
    entries.append(str('CONSTITUTION: \t' + str(round(player.fighter.get_attribute('con')))))
    entries.append(str('SENSES: \t' + str(round(player.fighter.get_attribute('sens')))))
    entries.append(str('APPEARANCE: \t' + str(round(player.fighter.get_attribute('appear')))))
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
    entries.append(str('Brawling: \t' + str(player.fighter.get_attribute('brawling')) + '%'))
    entries.append(str('Dodge: \t\t' + str(player.fighter.get_attribute('dodge')) + '%'))    
    entries.append(str('Deflect: \t' + str(player.fighter.get_attribute('deflect')) + '%'))
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


def render(entities, players, game_map, con_list, offset_list, type_list, dim_list, color_list, logs, menu_dict = dict(), modal_dialog = None) -> None:
    terminal.clear()
    map_con = con_list[0]
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
    
    if menu_dict != None:
        menu_type = menu_dict.get('type')
        menu_header = menu_dict.get('header')
        menu_options = menu_dict.get('options')
        hide_options = menu_dict.get('mode')
        
        if menu_type == MenuTypes.combat:
            if not hide_options:
                modal_dialog.options = menu_options
                modal_dialog.add_header(menu_header)
                modal_dialog.draw_window()
            else:
                modal_dialog.options = None
                modal_dialog.add_header(menu_header)
                modal_dialog.draw_window()

    terminal.refresh()
   




def create_terminal(w,h) -> bool:
    term = terminal.open()
    terminal.set('window: size='+str(w)+'x'+str(h)+', cellsize=10x10, title=Crimson Sands')
    #Fonts
    terminal.set("text font: fonts\\consolab.ttf, size=8x14")
    terminal.set("font: fonts\\DejaVuSansMono-Bold.ttf, size=10x10")
    terminal.set("big font: fonts\\consolab.ttf, size=10x16")
    
    terminal.composition(terminal.TK_OFF)
    terminal.refresh()
    return term

def blt_handle_keys(game_state, menu_dict) -> str or None:
    key = terminal.read()
    command = []

    if key == terminal.TK_CLOSE:
        exit()
    else:
        if game_state == GameStates.default:
            if not 88 < key < 99 and terminal.check(terminal.TK_CHAR):
                key = chr(terminal.state(terminal.TK_CHAR))
            keymap = options.key_maps[game_state.value - 1]
            command = keymap.get(key)
        if game_state == GameStates.menu:
            try:
                menu_type = menu_dict.get('type')
                menu_header = menu_dict.get('header')
                menu_options = menu_dict.get('options')
                hide_options = menu_dict.get('mode')
            except:
                print('Something is missing from the menu_dict')
            if hide_options:
                if not 88 < key < 99 and terminal.check(terminal.TK_CHAR):
                    key = chr(terminal.state(terminal.TK_CHAR))
                for item in menu_options:
                    if key == item:
                        keymap = options.key_maps[0]
                        command = keymap.get(key)
            else:
                if terminal.check(terminal.TK_CHAR):
                    key = ord(chr(terminal.state(terminal.TK_CHAR)))
                for option in menu_options:
                    opt_index = menu_options.index(option)
                    if opt_index < 26:
                        cp = ord('a') + opt_index
                    else:
                        cp = ord('0') + opt_index - 26
                    if cp == key:
                        command = {menu_options[opt_index]:menu_options[opt_index]}
                        pass
    
    return command


def blt_handle_global_input(game_state) -> str or int or None:
    
    command = []
    if terminal.has_input():
        key = terminal.read()
        if key == terminal.TK_CLOSE:
            exit(0)
        else:
            if not 88 < key < 99 and terminal.check(terminal.TK_CHAR):
                key = chr(terminal.state(terminal.TK_CHAR))
            keymap = options.key_maps[game_state.value - 1]
            command = keymap.get(key)
    return command
                
            


def render_map_con(entities, players, game_map, width, height, ox=0, oy=0) -> None:
    terminal.layer(0)
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
    terminal.puts(ox, oy, '[font=text][color=white][bg_color=black]Hit Location')
    terminal.puts(ox+15, oy, '[font=text][color=white][bg_color=black]DERM')
    terminal.puts(ox+20, oy, '[font=text][color=white][bg_color=black]TIS')
    terminal.puts(ox+25, oy, '[font=text][color=white][bg_color=black]BONE')

    if entity is not None:
        p_y = 1
        for hit_location in entity.fighter.locations:
            terminal.color('white')
            terminal.puts(ox, oy+p_y, '[font=text]'+entity.fighter.name_location(p_y-1) + ':')
            terminal.puts(ox+15, oy+p_y, '[font=text]'+str(hit_location[0]))
            terminal.puts(ox+20, oy+p_y, '[font=text]'+str(hit_location[1]))
            terminal.puts(ox+25, oy+p_y, '[font=text]'+str(hit_location[2]))
            p_y += 1

    if con_type == 1: #Print char con
        s_y = 50
        for message in log.messages:
            terminal.puts(ox, oy+s_y, '[font=text]'+message.text)
            s_y += 1

def render_msg_con(ox, oy, log):
    y = 1
    for message in log.messages:
        terminal.puts(ox, oy+y, '[font=text]'+message.text)
        y += 1

def print_entities(entities, ox, oy) -> None:
    
    players = set()
    enemies = set()
    corpses = set()
    players_aoc = set()
    players_visible = set()
    players_explored = set()
    for entity in entities:
        if entity.state == EntityState.dead:
            corpses.add(entity)
        elif entity.player:
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
        if (x,y) in players_visible:
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

    #Place visible corpses
    for corpse in corpses:
        if (corpse.x, corpse.y) in players_visible:
            terminal.puts(corpse.x+ox, corpse.y+oy, '[bk_color=dark amber][color='+corpse.color+']'+corpse.char+'[/color][/bk_color]')
        elif (corpse.x, corpse.y) in players_explored:
            terminal.puts(corpse.x+ox, corpse.y+oy, '[bk_color=darker amber][color=darker gray]'+corpse.char+'[/color][/bk_color]')



        

class BLTWindow:
    def __init__(self, x, y, w, color, bg_color):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.header = None
        self.options = ['You are disabled and may not attack']
        self.h = len(self.options) + 3
        self.bg_color = bg_color
        self.color = color
    def add_header(self, header):
        if header is not None:
            self.header = textwrap.wrap(header, self.w-2)
            self.h = len(self.header)
            if self.options is not None: 
                self.h += len(self.options)+3
            else: self.h += 3
    def draw_window(self):

        x = self.x
        y = self.y
        w = self.w
        h = self.h
        header_len = 0

        #Draw border
        for dx in range(x, x+w):
            for dy in range(y, y+h):
                terminal.layer(1)
                terminal.color('darker gray')
                terminal.put(dx, dy, 0x2593)
                if dx == x and dy == y:
                    terminal.puts(dx, dy,'[color='+self.color+']'+'╔')
                elif dx == x+w-1 and dy == y+h-1:
                    terminal.puts(dx, dy,'[color='+self.color+']'+'╝')
                elif dx == x and dy == y+h-1:
                    terminal.puts(dx, dy,'[color='+self.color+']'+'╚')
                elif dx == x+w-1 and dy == y:
                    terminal.puts(dx, dy,'[color='+self.color+']'+'╗')
                elif dx == x or dx == x+w-1:
                    terminal.puts(dx, dy,'[color='+self.color+']'+'║')
                elif dy == y or dy == (y+h-1):
                    terminal.puts(dx, dy,'[color='+self.color+']'+'═')

        if self.header is not None:
            header_len = len(self.header)
            for h in self.header:
                terminal.layer(2)
                terminal.printf(x+1, y+1+(self.header.index(h)), '[color=white][font=big]'+h)
            terminal.print_(x+1, y+1+header_len, '\n')
        if self.options is not None:
            

            letter_index = ord('a')

            for option in self.options:
                opt_index = self.options.index(option)
                if opt_index < 26:
                    letter_index = ord('a') + opt_index
                else:
                    letter_index = ord('0') + opt_index - 26
                terminal.layer(2)
                text = '[font=big](' + chr(letter_index) + ') ' + option
                terminal.printf(x+1, y+1+header_len+1+(self.options.index(option)), '[color=white]'+ text)
