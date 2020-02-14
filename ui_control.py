
import tcod as libtcodpy
import bearlibterminal.terminal as terminal
from tcod import event, console
import textwrap
import options
import global_vars
from math import ceil
from enums import MenuTypes, GameStates, CombatPhase, EntityState
from game_messages import Message
from utilities import inch_conv
from bltGui import bltFrame as Frame
import bltGui



def initialize():
    key = bltGui.bltInput.update()
    mouse = bltGui.bltInput.mouse


def render_frames(frame_list):
    for f in frame_list:

        f.draw()

def update(frame_list):
    frame_list.sort(key=lambda x: x.layer, reverse=True)
    for f in frame_list:
        f.update()


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


def render(entities, players, game_map, con_list, frame_list, offset_list, type_list, dim_list, color_list, logs, menu_dict, game_state) -> None:
    terminal.clear()
    if game_state in [GameStates.default, GameStates.menu]:
        render_combat(entities, players, game_map, con_list, frame_list, offset_list, type_list, dim_list, color_list, logs, menu_dict)
    elif game_state == GameStates.c_sheet:
        render_csheet(players)

    

    terminal.refresh()

def render_csheet(players) -> None:
    player = players[0]
    max_x = options.screen_width
    max_y = options.screen_height

    #Static headers for sheet
    name_h = 'Name: '
    prof_h = 'Profession: '
    eth_h = 'Ethnicity: '
    age_h = 'Age: '
    wt_h = 'Weight: '
    ht_h = 'Height: '
    gender_h = 'Gender: '
    hand_h = 'Dominant Hand: '
    stam_h = 'Stamina: '
    vitae_h = 'Vitae: '
    ap_h = 'AP: '
    init_h = 'Initiative: '
    wpnr_h = 'Weapon Reach: '
    ohr_h = 'Off-hand Reach: '
    kickr_h = 'Kick Reach: '

    #Len vars used for variable spacing
    name_len = 12+len(name_h)+len(player.name)
    prof_len = 12+name_len+len(prof_h)+len('Fighter') #Replace when professions implemented
    age_len = 12+len(age_h)+len(str(player.fighter.age))
    ht_len = 12+age_len+len(ht_h)+len(inch_conv(player.fighter.height))
    wt_len = 12+ht_len+len(wt_h)+len(str(player.fighter.weight))
    gender_len = 12+wt_len+len(gender_h)+len(('Male' if player.fighter.male else 'Female'))
    stam_len = 8+len(stam_h)+len(str(player.fighter.stamina) + '/' + str(player.fighter.max_stamina))
    vitae_len = 8+stam_len+len(vitae_h)+len(str(player.fighter.vitae) + '/' + str(player.fighter.max_vitae))
    ap_len = 8+vitae_len+len(ap_h)+len(str(player.fighter.ap) + '/' + str(player.fighter.max_ap))
    init_len = 8+ap_len+len(init_h)+len(str(int(player.fighter.init)))
    wpnr_len = 8+init_len+len(wpnr_h)+len(str(player.fighter.reach) + ' squares')
    ohr_len = 8+wpnr_len+len(ohr_h)+len(str(player.fighter.reach_oh) + ' squares')


    #General Attributes
    terminal.puts(2, 2, '[font=headi][color=white][bg_color=black]'+ name_h)
    terminal.puts(2+len(name_h), 2, '[font=head][color=white][bg_color=black]' + player.name)

    terminal.puts(name_len, 2, '[font=headi][color=white][bg_color=black]'+prof_h)
    terminal.puts(name_len+len(prof_h), 2, '[font=head][color=white][bg_color=black]' + 'Fighter')#Replace when professions implemented

    terminal.puts(prof_len, 2, '[font=headi][color=white][bg_color=black]'+eth_h)
    terminal.puts(prof_len+len(eth_h), 2, '[font=head][color=white][bg_color=black]' + 'Barbarian')#Replace when ethnicities implemented

    terminal.puts(2, 4, '[font=bodyi][color=white][bg_color=black]'+age_h)
    terminal.puts(2+len(age_h), 4, '[font=body][color=white][bg_color=black]' + str(player.fighter.age))

    terminal.puts(age_len, 4, '[font=bodyi][color=white][bg_color=black]'+ht_h)
    terminal.puts(age_len+len(ht_h), 4, '[font=body][color=white][bg_color=black]' + inch_conv(player.fighter.height))

    terminal.puts(ht_len, 4, '[font=bodyi][color=white][bg_color=black]'+wt_h)
    terminal.puts(ht_len+len(wt_h), 4, '[font=body][color=white][bg_color=black]' + str(player.fighter.weight))

    terminal.puts(wt_len, 4, '[font=bodyi][color=white][bg_color=black]'+gender_h)
    terminal.puts(wt_len+len(gender_h), 4, '[font=body][color=white][bg_color=black]' + ('Male' if player.fighter.male else 'Female'))

    terminal.puts(gender_len, 4, '[font=bodyi][color=white][bg_color=black]'+hand_h)
    terminal.puts(gender_len+len(hand_h), 4, '[font=body][color=white][bg_color=black]' + ('Right' if player.fighter.dom_hand == 'R' else ('Left' if player.fighter.dom_hand == 'L' else 'Ambidexterous')))

    #Primary Attributes

    #Header
    terminal.puts(2, 7, '[font=headi][color=white][bg_color=black]'+ 'Primary Attributes')
    terminal.puts(6+len('Primary Attributes'), 7, '[font=headi][color=white][bg_color=black]' + 'Secondary Attributes')

    y = 9

    #Parent Attributes
    for key, attr in player.fighter.parent_attr_dict.items():
        terminal.puts(2, y, '[font=headi][color=white][bg_color=black]'+ attr.name + ": ")
        terminal.puts(16, y, '[font=head][color=white][bg_color=black]' + str(attr.val))
        for k, a in player.fighter.attr_dict.items():
            #Child Attributes
            if a.parent_attr == attr.abr:
                terminal.puts(24, y, '[font=bodyi][color=white][bg_color=black]'+ a.name + ": ")
                terminal.puts(44, y, '[font=body][color=white][bg_color=black]' + str(a.val))
                y += 2

    #Skills

    #Header
    terminal.puts(50, 7, '[font=headi][color=white][bg_color=black]'+ 'Skill Name')
    terminal.puts(54+len('Skill Name'), 7, '[font=headi][color=white][bg_color=black]' + 'Level')
    terminal.puts(58+len('Skill Name')+len('Level'), 7, '[font=headi][color=white][bg_color=black]' + 'Rating')

    y = 9

    #Skill name, level and value
    for key, skill in player.fighter.skill_dict.items():
        terminal.puts(50, y, '[font=body][color=white][bg_color=black]'+ skill.name + ": ")
        terminal.puts(64, y, '[font=body][color=white][bg_color=black]' + str(skill.level))
        terminal.puts(73, y, '[font=body][color=white][bg_color=black]' + str(skill.rating))
        y +=2

    y = 7

    #Hit locations 
    terminal.puts(85, y, '[font=headi][color=white][bg_color=black]Hit Location')
    terminal.puts(105, y, '[font=headi][color=white][bg_color=black]Dermitology')
    terminal.puts(120, y, '[font=headi][color=white][bg_color=black]Tissue')
    terminal.puts(130, y, '[font=headi][color=white][bg_color=black]Bone')
    y += 2
    loc = 0
    for hit_location in player.fighter.locations:
            terminal.color('white')
            terminal.puts(85, y, '[font=body]'+player.fighter.name_location(loc) + ':')
            terminal.puts(105, y, '[font=body]'+str(hit_location[0]))
            terminal.puts(120, y, '[font=body]'+str(hit_location[1]))
            terminal.puts(130, y, '[font=body]'+str(hit_location[2]))
            y += 2
            loc += 1

    #Minor stats
    terminal.puts(2, 68, '[font=text][color=white][bg_color=black]'+stam_h)
    terminal.puts(2+len(stam_h), 68, '[font=text][color=white][bg_color=black]' + str(player.fighter.stamina) + '/' + str(player.fighter.max_stamina))

    terminal.puts(stam_len, 68, '[font=text][color=white][bg_color=black]'+vitae_h)
    terminal.puts(stam_len+len(vitae_h), 68, '[font=text][color=white][bg_color=black]' + str(player.fighter.vitae) + '/' + str(player.fighter.max_vitae))

    terminal.puts(vitae_len, 68, '[font=text][color=white][bg_color=black]'+ap_h)
    terminal.puts(vitae_len+len(ap_h), 68, '[font=text][color=white][bg_color=black]' + str(player.fighter.ap) + '/' + str(player.fighter.max_ap))

    terminal.puts(ap_len, 68, '[font=text][color=white][bg_color=black]'+init_h)
    terminal.puts(ap_len+len(init_h), 68, '[font=text][color=white][bg_color=black]' + str(int(player.fighter.init)))

    terminal.puts(init_len, 68, '[font=text][color=white][bg_color=black]'+wpnr_h)
    terminal.puts(init_len+len(wpnr_h), 68, '[font=text][color=white][bg_color=black]' + str(player.fighter.reach) + ' squares')

    terminal.puts(wpnr_len, 68, '[font=text][color=white][bg_color=black]'+ohr_h)
    terminal.puts(wpnr_len+len(ohr_h), 68, '[font=text][color=white][bg_color=black]' + str(player.fighter.reach_oh) + ' squares')

    terminal.puts(ohr_len, 68, '[font=text][color=white][bg_color=black]'+kickr_h)
    terminal.puts(ohr_len+len(kickr_h), 68, '[font=text][color=white][bg_color=black]' + str(player.fighter.reach_leg) + ' squares')




def render_combat(entities, players, game_map, con_list, frame_list, offset_list, type_list, dim_list, color_list, logs, menu_dict) -> None:
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
            map_x, map_y = offset_x, offset_y
            map_dim_x, map_dim_y = dim_x, dim_y

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
        desc = menu_dict.get('desc')
        x_offset = int(map_x + round(map_dim_x / 3))
        y_offset = int(map_y + round(map_dim_y / 3))

        if menu_type == MenuTypes.combat:
            options = menu_options
            header = menu_header                 

            if len(frame_list) == 0:
                bltgui_menu(terminal, x_offset, y_offset, header, options, desc, frame_list, hide_options)
                initialize()

    if len(frame_list) != 0:
        render_frames(frame_list)


def create_terminal(w,h) -> bool:
    term = terminal.open()
    terminal.set('window: size='+str(w)+'x'+str(h)+', cellsize=10x10, title=Crimson Sands')
    terminal.set("input: filter={keyboard+, mouse+}")

    #Fonts
    terminal.set("text font: fonts\\consolab.ttf, size=8x14")
    terminal.set("big font: fonts\\consolab.ttf, size=12x16")
    terminal.set("font: fonts\\DejaVuSansMono-Bold.ttf, size=10x10")
    terminal.set("headi font: fonts\\DejaVuSansMono-BoldOblique.ttf, size=16")
    terminal.set("head font: fonts\\DejaVuSansMono-Bold.ttf, size=14")
    terminal.set("bodyi font: fonts\\DejaVuSansMono-BoldOblique.ttf, size=13")
    terminal.set("body font: fonts\\DejaVuSansMono-Bold.ttf, size=12")
    
    terminal.composition(terminal.TK_OFF)
    terminal.refresh()
    return term

def handle_input(active_entity, game_state, menu_dict, entities, combat_phase, game_map, order, frame_list) -> (dict, bool): 
    command = {}
    dirty = False
    hide_options = menu_dict.get('mode')

    

    
    if active_entity.player:
        #Below complexity is due to modal nature. if targets exist, block for input. 
        #Otherwise, see if a menu is present. If so, block for input, if not, refresh and get menu
        if game_state != GameStates.menu: command = blt_handle_global_input(game_state)
        else:
            if len(active_entity.fighter.targets) == 0 and len(menu_dict.get('options')) == 0: #This is to handle the case of moving with direction keys
                command = blt_handle_keys(game_state, menu_dict)
            else:
                if 'options' in menu_dict:
                    if len(frame_list) != 0:
                        
                        key = bltGui.bltInput.update()       
                        update(frame_list)

                        if key is not None:
                            if key == terminal.TK_CLOSE:
                                exit()
                            dirty = True
                            if not hide_options:
                                if key == 41:
                                    if 'Return' in menu_dict.get('options'):
                                        command = {'Return':'Return'}
                                    else:                                  
                                        command = {'esc':'esc'}
                                else:
                                    for frame in frame_list:
                                        for control in frame.controls:
                                            if isinstance(control, bltGui.bltListbox):
                                                if control.selected_index is not None:
                                                    item = control.return_item()
                                                    command = {item:item}
                            elif key < 128:
                                char = chr(key+93) #Needed because BLT returns a hex value for the scan code that is offset -93
                                if key in menu_dict.get('options'):
                                    command = blt_handle_keys(game_state, menu_dict, key)
                                elif char in menu_dict.get('options'):
                                    command = blt_handle_keys(game_state, menu_dict, char)
                                
                            


    elif not active_entity.player:
        command = active_entity.fighter.ai.ai_command(active_entity, entities, combat_phase, game_map, order)
        dirty = True

        if global_vars.debug: print(active_entity.name + ' actions: ', *active_entity.fighter.action, sep=', ')
        if global_vars.debug and isinstance(command, str): print(active_entity.name + ' command: ' + command)

    
        


    return command, dirty


def blt_handle_keys(game_state, menu_dict, key = None) -> str or None:
    if key is None:
        key = terminal.read()
    command = {}
    menu_options = menu_dict.get('options')

    if key == terminal.TK_CLOSE:
        exit()
    else:
        if game_state != GameStates.menu:
            if not 88 < key < 99 and terminal.check(terminal.TK_CHAR):
                key = chr(terminal.state(terminal.TK_CHAR))
            keymap = options.key_maps[game_state.value - 1]
            command = keymap.get(key)
        elif key is not None and menu_options is not None:
            if key in menu_options:
                keymap = options.key_maps[0]
                command = keymap.get(key)

    
    return command


def blt_handle_global_input(game_state) -> str or int or None:
    
    command = {}
    if terminal.has_input():
        key = terminal.read()
        if key == terminal.TK_CLOSE:
            exit(0)
        else:
            if not 88 < key < 99 and terminal.check(terminal.TK_CHAR):
                key = chr(terminal.state(terminal.TK_CHAR))
            keymap = options.key_maps[0]
            if keymap.get(key) is not None:
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


def bltgui_menu(terminal, x_offset, y_offset, header, options, desc, frame_list, hide_options):
    items = []
    item_dict = {}
    
    if header is not None:
        i_width = len(header)+2
        header_h = 1
    if not hide_options:
        items = options
        i_width = max(30, len(max(items,key=len)) + 8)
        header_h = len(textwrap.wrap(header, i_width))+2
        list_frame = Frame(x_offset,y_offset,i_width,max(len(items)+header_h+2,8), "", text=header, frame=True, draggable=True, color_skin = 'GRAY', font = '[font=big]', title_font='[font=big]')
        list_frame.add_control(bltGui.bltResizeFrameButton(list_frame))
        list_box = bltGui.bltListbox(list_frame, 1, header_h+1, items, False, True)
        if desc is not None:
            item_dict = make_item_dict(options, desc)
            content_frame = bltGui.bltShowListFrame(i_width + x_offset, y_offset,25,20, "", frame=True, draggable=True, color_skin = 'GRAY', font = '[font=text]', title_font='[font=big]')
            content_frame.set_dict(item_dict)
            content_frame.add_control(bltGui.bltResizeFrameButton(content_frame))
            list_box.register('changed', content_frame)
        else:
            content_frame = None
    else:
        content_frame = None
        list_box = None
        list_frame = Frame(x_offset,y_offset,i_width,len(items)+header_h+2, "", text=header, frame=True, draggable=True, color_skin = 'GRAY', font = '[font=text]', title_font='[font=big]')
    

    if list_box is not None:    
        list_frame.add_control(list_box)
    
    frame_list.append(list_frame)

    if content_frame is not None:
        frame_list.append(content_frame)

def make_item_dict(options, desc) -> dict:
    item_dict = {}
    i = 0
    for option in options:
        for key in desc:
            if option == key:
                item_dict[i] = desc.get(key)
                i+=1

    
    return item_dict
        

class BLTWindow:
    def __init__(self, x, y, w, color, bg_color):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.header = None
        self.options = ['You are disabled and may not attack']

        self.h = 4
        self.bg_color = bg_color
        self.color = color
    def add_header(self, header):
        if header is not None:
            self.header = textwrap.wrap(header, self.w-2)
            self.h = len(self.header)
            if self.options is not None: 
                #Calc option length with text wrapping
                opt_len = 0
                for o in self.options:
                    opt_len += ceil(len(o)/(self.w-4))

                self.h = opt_len + 5
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
                wrapped_option = textwrap.wrap(option, self.w-4)
                if opt_index < 26:
                    letter_index = ord('a') + opt_index
                else:
                    letter_index = ord('0') + opt_index - 26
                terminal.layer(2)
                if len(wrapped_option) == 1:
                    text = '[font=big](' + chr(letter_index) + ') ' + option
                    terminal.printf(x+1, y+1+header_len+1+(self.options.index(option)), '[color=white]'+ text)
                else:
                    for o in wrapped_option:
                        if wrapped_option.index(o) == 0:
                            text = '[font=big](' + chr(letter_index) + ') ' + o
                            terminal.printf(x+1, y+1+header_len+1+(self.options.index(option)), '[color=white]'+ text)
                        else:
                            text = '[font=big]    ' + o
                            terminal.printf(x+1, y+1+header_len+1+(self.options.index(option)+wrapped_option.index(o)), '[color=white]'+ text)

                        
                        

