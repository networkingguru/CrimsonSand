import math
from random import randint
import global_vars
import dill
from game_messages import Message

def roll_dice(dice, facing, explode = False) -> int:
    roll = 0
    if explode:
        i = 0
        while i < dice:
            current_roll = randint(1, facing)
            final_roll = current_roll
            while current_roll == facing:
                current_roll = randint(1, facing)
                final_roll += current_roll
            i += 1
            roll += final_roll
        return roll
    else:
        roll = randint(dice, (facing * dice))
        return roll

def inch_conv(inches, mode = 0) -> str or int:
    if mode == 0:
        #return inches and feet
        feet = int(inches / 12)
        remain = inches % 12
        total = str(feet) + '\'' + ' ' + str(remain) + '\"'
        return total
    elif mode == 1:
        #Return number of hexes
        feet = int(inches / 12)
        total = round(feet / 3)
        if feet >= 3 and feet % 12 != 0:
            total += 1
        if total < 1:
            total += 1
        return total
    elif mode == 2:
        #Return number of feet
        feet = int(inches / 12)
        return feet

def save_roll_un(score, modifiers) -> list: #Uncontested save
    roll = roll_dice(1, 100)
    result = ['',0]
    if roll == 1: result = ['cs', (score + modifiers) - roll]
    elif roll == 100: result = ['cf', 0]
    else: 
        if roll < (score + modifiers): result = ['s',  (score + modifiers) - roll]
        else: result = ['f', 0]
    return result

def save_roll_con(p1_score, p1_mods, p2_roll, p2_final_chance) -> (str, int, int): #Contested save
    result = 'f'
    p2_margin = p2_final_chance - p2_roll
    p1_result, p1_margin = save_roll_un(p1_score, p1_mods)
    if global_vars.debug: print('Attacker Margin: ' + str(p2_margin) + '\n' + 'Defender Margin: ' + str(p1_margin))
    if p1_result == 'cf': result = 'cf'
    elif p1_margin > p2_margin:
        result = 's'
    
    return result, p1_margin, p2_margin

def clamp(n, min_n, max_n = 2**10000) -> int:
    """Clamps a variable between a min and max"""
    if n < min_n:
        n = min_n
    elif n > max_n:
        n = max_n
    return n

def prune_list(source_list, to_remove, inverse = False, index = True) -> list: #If index true, source_list should be a list of index locations as ints
    if index:
            for i in to_remove:
                if inverse:
                    if not i in source_list:
                        source_list.remove(i)
                else:
                    if i in source_list:
                        source_list.remove(i)
    else:
        contents = []
        if inverse:
            for i in to_remove:
                contents.append(source_list[i])
            source_list = contents
        else:    
            for i in source_list:
                for n in to_remove:
                    if i == n:
                        source_list.remove(i)
    return source_list

def find_last_occurence(source, subject) -> object:
    if subject in source:
        #Find the last occurence of subject in list source and return it's index value
        return len(source) - source[::-1].index(subject) - 1
    else:
        if len(source)>0: return source[-1]
        else: return [1]

def entity_angle(reference, axis, relative = True) -> int:
    #Axis is active entity, reference is thing to get angle to
    dy = axis.y - reference.y
    dx = reference.x - axis.x
    radians = math.atan2(-dy, dx)
    degrees = math.degrees(radians)
    
    
    direction = axis.fighter.facing
    if direction == 0: #N
        angle_adj = 90
    elif direction == 1: #NE
        angle_adj = 45
    elif direction == 2: #E
        angle_adj = 0
    elif direction == 3: #SE
        angle_adj = 315
    elif direction == 4: #S
        angle_adj = 270
    elif direction == 5: #SW
        angle_adj = 225
    elif direction == 6: #W
        angle_adj = 180
    else: #NW
        angle_adj = 135

    #Deal with y axis being upside-down
    degrees -= 360
    degrees = abs(degrees)
    #Adjust if angle is supposed to be relative to facing
    if relative: degrees -= angle_adj
    #deal with boundary
    if degrees < 0:
        degrees += 360
    if degrees > 359:
        degrees -= 360
    
    #Return angle to ref from axis
    return degrees

def find_command(keymap, wanted_cmd) -> list:
    '''Function searches the keymap for the command and returns the key(s) associated with it. Reverse of dict.get'''
    keys = []
    wanted_cmd = {wanted_cmd[0]:wanted_cmd[1]}
    for key, command in keymap.items():
        if command == wanted_cmd:
            keys.append(key)
    return keys

def find_defense_probability(attack_prob, def_prob) -> int:
    '''Goal: Find approx probability for two numbers that may be over 100%'''
    defender_chance = int(0)

    #Determine chance of atk failing, min 1 max 99
    if attack_prob >= 100: 
        atk_fail = 1

    else: atk_fail = 100 - attack_prob

    diff = abs(def_prob - attack_prob)

    #If over 100% difference in scores, give chance as 99% or 1%
    if diff >= 100:
        if def_prob > attack_prob: defender_chance = 99
        else: defender_chance = 1
    else:
        #Handle cases where one or both numbers are over 100%
        if def_prob >= 100 or attack_prob >= 100:
            overage = int(0)
            for i in (def_prob, attack_prob):
                o = i - 100
                if o > 0 and o > overage:
                    overage = o
            def_prob -= overage
            attack_prob -= overage

        combined_prob = (def_prob/100)*(attack_prob/100)
        defender_chance = int((combined_prob*100) + atk_fail)
    
    return defender_chance

def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)
    Generator over all subclasses of a given class, in depth first order.
    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>> 
    >>> for cls in itersubclasses(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """
    
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None: _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError: # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub

def save_game() -> list:
    messages = []
    try:
        dill.dump_session(filename='game.pkl')
        messages.append(Message('Game saved'))
    except:
        messages.append(Message('There was an error saving the game. '))

    return messages

def load_game() -> list:
    messages = []
    try:
        dill.load_session (filename='game.pkl')
        messages.append(Message('Game loaded'))
    except:
        messages.append(Message('There was an error loading the game. '))

    return messages

def make_bar(value,max=200,min=0,reverse=False):
    if reverse:
        bars = (value - ((max - min)*-1))/50
    else:
        bars = (value / ((max - min)/50))/10

    if bars < 2:
        color = '[color=red]'
    elif bars < 4:
        color = '[color=yellow]'
    else:
        color = '[color=green]'

    bar = color

    if bars > 5:
        bar += '█████+'
    else:
        while bars > 0:
            if bars >= 1:
                bar += '█'
                bars -= 1
            elif bars < 1:
                bar += '▌'
                bars = 0

    return bar

def name_location(location) -> int or str:
        #THIS IS A DIRECT COPY OF THE METHOD IN THE FIGHTER CLASS. COPIED SO IT CAN BE USED OUTSIDE OF THE CLASS (FOR TESTING).

        #Method to convert loc names to numbers and vice versa
        loc_list = ['Scalp', 'Face', 'Neck', 'R Shoulder', 'L Shoulder', 'R Chest', 'L Chest', 'Up R Arm', 'Up L Arm', 'R Ribs', 'L Ribs', 
                    'R Elbow', 'L Elbow', 'R Abdomen', 'L Abdomen', 'R Forearm', 'L Forearm', 'R Hip', 'L Hip', 'R Hand', 'L Hand', 'R Thigh', 'L Thigh', 
                    'R Knee', 'L Knee', 'R Shin', 'L Shin', 'R Foot', 'L Foot']
        #Key for reference
        # 0 Scalp
        # 1 Face
        # 2 Neck
        # 3 R Shoulder
        # 4 L Shoulder
        # 5 R Chest
        # 6 L Chest
        # 7 Up R Arm
        # 8 Up L Arm
        # 9 R Ribs
        # 10 L Ribs
        # 11 R Elbow
        # 12 L Elbow
        # 13 R Abdomen
        # 14 L Abdomen
        # 15 R Forearm
        # 16 L Forearm
        # 17 R Hip
        # 18 L Hip
        # 19 R Hand
        # 20 L Hand
        # 21 R Thigh
        # 22 L Thigh
        # 23 R Knee
        # 24 L Knee
        # 25 R Shin
        # 26 L Shin
        # 27 R Foot
        # 28 L Foot


        #If given a number, return a name
        try:
            val = int(location)
            title = loc_list[location]
        #Otherwise, return a number
        except:
            title = loc_list.index(location)

        return title
    
def armor_log (entities, components):
    #Purpose: Write a log file in the project directory of random armors for debugging purposes
    #Requires following line to create components outside of function prior to calling: components = component_sort(entities[0])

    with open('armor_gen.txt','w') as armor_log:
        for cat in components:
            armor_log.write('Category: ' + cat + '\n')
            armor_log.write('\n')
            for a in components.get(cat):
                locs = ''
                for i, l in enumerate(a.covered_locs):
                    if i: 
                        locs += ', '
                    locs += name_location(l)

                armor_log.write('Name: ' + a.name + '\n')
                armor_log.write('Cost: ' + str(round(a.cost)) + '\n') 
                armor_log.write('Thickness: ' + str(round(a.thickness,2)) + ' inches'+ '\n')
                armor_log.write('Rigidity: ' + a.rigidity + '\n')
                armor_log.write('Covered Locations: ' + locs + '\n')
                armor_log.write('Area Covered: ' + str(round(a.main_area,1)) + ' square inches\n')
                armor_log.write('Weight: ' + str(round(a.weight,2)) + ' pounds \n')
                armor_log.write('Density: ' + str(round(a.density,2)) + '\n')
                armor_log.write('Quality: ' + a.quality + '\n')
                armor_log.write('B/S/P Deflect Maximums: ' + str(round(a.b_deflect_max)) + '/' + str(round(a.s_deflect_max)) + '/' + str(round(a.p_deflect_max)) + ' PSI' + '\n')
                armor_log.write('B/S/P Deflect Percentage: ' + str(round(a.b_deflect*100,2)) + '%/' + str(round(a.s_deflect*100,2)) + '%/' + str(round(a.p_deflect*100,2)) + '%' + '\n')
                armor_log.write('Hits: ' + str(round(a.hits)) + '\n')
                armor_log.write('Hits per Square Inch: ' + str(round(a.hits_sq_in)) + '\n')
                armor_log.write('B Soak: ' + str(round(a.b_soak*100)) + '%' + '\n')
                armor_log.write('Physical Modifier (base): ' + str(round(a.physical_mod)) + '\n')
                armor_log.write('Stamina Drain: ' + str(round(a.stam_drain)) + ' per round' + '\n')
                armor_log.write('\n')