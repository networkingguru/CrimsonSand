import math
from random import randint

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
        if feet/3 >= 1:
            if feet % 12 != 0:
                total += 1
        if total < 1:
            total += 1
        return total
    elif mode == 2:
        #Return number of feet
        feet = int(inches / 12)
        return feet

def save_roll_un(score, modifiers) -> list:
    roll = roll_dice(1, 100)
    result = ['',0]
    if roll == 1: result = ['cs', (score + modifiers) - roll]
    elif roll == 100: result = ['cf', 0]
    else: 
        if roll < (score + modifiers): result = ['s',  (score + modifiers) - roll]
        else: result = ['f', 0]
    return result

def save_roll_con(p1_score, p1_mods, p2_roll, p2_final_chance) -> str:
    result = 'f'
    p2_margin = p2_final_chance - p2_roll
    p1_result, p1_margin = save_roll_un(p1_score, p1_mods)
    if p1_result == 'cf': result = 'cf'
    elif p1_margin > p2_margin:
        result = 's'
    
    return result

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

def gen_status_panel(player) -> list:
    entries = []
    
    entries.append(str('INTELLECT: \t' + str(round(player.fighter.int))))
    entries.append(str('STRENGTH: \t' + str(round(player.fighter.str))))
    entries.append(str('AGILITY: \t' + str(round(player.fighter.agi))))
    entries.append(str('CONSTITUTION: \t' + str(round(player.fighter.con))))
    entries.append(str('SENSES: \t' + str(round(player.fighter.sens))))
    entries.append(str('APPEARANCE: \t' + str(round(player.fighter.appear))))
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
    entries.append(str('Eff. Power: \t' + str(round(player.fighter.ep)) + ' PSI'))
    entries.append(str('Brawling: \t' + str(player.fighter.brawling) + '%'))
    entries.append(str('Dodge: \t\t' + str(player.fighter.dodge) + '%'))    
    entries.append(str('Deflect: \t' + str(player.fighter.deflect) + '%'))
    entries.append(str('AP: \t\t' + str(player.fighter.ap)))
    entries.append(str('Walk: \t\t' + str(player.fighter.walk_ap)) + ' AP/sq')
    entries.append(str('Jog: \t\t' + str(player.fighter.jog_ap)) + ' AP/sq')
    entries.append(str('Run: \t\t' + str(player.fighter.run_ap)) + ' AP/sq')
    return entries


def entity_angle(reference, axis) -> int:
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
    
    degrees -= angle_adj
    #deal with boundary
    if degrees < 0:
        degrees += 360
    if degrees > 359:
        degrees -= 360
    
    return degrees