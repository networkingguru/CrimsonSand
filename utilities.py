from random import randint

def roll_dice(dice, facing, explode = False):
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

def inch_conv(inches, mode = 0):
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

def save_roll_un(score, modifiers):
    roll = roll_dice(1, 100)
    result = ['',0]
    if roll == 1: result = ['cs', (score + modifiers) - roll]
    elif roll == 100: result = ['cf', 0]
    else: 
        if roll < (score + modifiers): result = ['s',  (score + modifiers) - roll]
        else: result = ['f', 0]
    return result

def save_roll_con(p1_score, p1_mods, p2_roll, p2_final_chance):
    result = 'f'
    p2_margin = p2_final_chance - p2_roll
    p1_result, p1_margin = save_roll_un(p1_score, p1_mods)
    if p1_result == 'cf': result = 'cf'
    elif p1_margin > p2_margin:
        result = 's'
    
    return result



def prune_list(source_list, to_remove, inverse = False, index = True): #If index true, source_list should be a list of index locations as ints
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



def find_last_occurence(source, subject):
    if subject in source:
        #Find the last occurence of subject in list source and return it's index value
        return len(source) - source[::-1].index(subject) - 1
    else:
        if len(source)>0: return source[-1]
        else: return [1]