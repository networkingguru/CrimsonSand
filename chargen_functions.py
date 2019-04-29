from utilities import roll_dice

def random_attr(method):
    #Roll a set of 29 random attributes using exploding dice and the three methods 29 2d100, 40 2d100 (take best), and 58 2d100 (take best)
    attributes = []
    if method == 1:
        while len(attributes) < 29:
            roll = roll_dice(2,100,True)
            attributes.append(roll)
        return attributes
    elif method == 2:
        while len(attributes) < 41:
            roll = roll_dice(2,100,True)
            attributes.append(roll)
        while len(attributes) > 29:
            attributes.remove(min(attributes))
        return attributes
    else:
        while len(attributes) < 59:
            roll = roll_dice(2,100,True)
            attributes.append(roll)
        while len(attributes) > 29:
            attributes.remove(min(attributes))
        return attributes

def height_curve(height_score, race_avg = 72):
    if height_score < 30:
        height = (race_avg*.3) + (height_score/150)*race_avg #22 - 36
    elif height_score < 50:
        height = (race_avg*.5) + ((height_score-29)/132)*race_avg #36 - 47
    elif height_score < 100:
        height = (race_avg*.66) + ((height_score-49)/258)*race_avg #48 - 62
    elif height_score < 160:
        height = (race_avg*.86) + ((height_score-99)/272)*race_avg #62 - 78
    elif height_score < 210:
        height = (race_avg*1.11) + ((height_score-159)/454)*race_avg #78 - 86
    elif height_score < 230:
        height = (race_avg*1.19) + ((height_score-209)/364)*race_avg #86 - 90
    elif height_score < 300:
        height = (race_avg*1.25) + ((height_score-229)/297)*race_avg #90 - 107
    else:
        height = (race_avg*1.5) + ((height_score-299)/910)*race_avg #107+ (400 = 115")
    
    return height