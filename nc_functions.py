from enums import GameStates, MenuTypes
from components.circumstances import Circumstance
from components.ethnicities import Ethnicity
from utilities import inch_conv
from components.fighter import attr_name_dict

sex_attr_mods_m = {'Logic':5,'Wisdom':-5,'Comprehension':-5,'Communication':-5,'Mental Celerity':-5,'Willpower':5,'Steady State':30,'Power':30,'Manual Dexterity':-5,
                    'Pedal Dexterity':-10,'Balance':-5,'Swiftness':-10,'Flexibility':-10,'Stamina':5,'Dermatology':5,'Bone Structure':15,'Immune System':5, 'Shock Resistance':-10,
                    'Sight':15,'Hearing':-5,'Taste/Smell':-10,'Touch':-5,'Body Fat':-10}


def choose_circumstance(curr_actor, game_state, command) -> (dict, int, bool):
    clear = False
    menu_dict = {}
    menu_desc = {}

    if len(command) != 0:
        for c in Circumstance.getinstances():
            if command.get(c.name):
                curr_actor.circumstance = c
                curr_actor.creation_choices['circumstance'] = c.name
                game_state = GameStates.sex
                clear = True

    else:
        menu_dict = {'type': MenuTypes.page, 'header': 'Choose your starting circumstances', 'options': [], 'mode': False, 'desc': {}}   
        
        for c in Circumstance.getinstances():
            menu_dict['options'].append(c.name)
            menu_desc[c.name] = c.desc

        menu_dict['desc'] = menu_desc


    return menu_dict, game_state, clear

def choose_sex(curr_actor, game_state, command) -> (dict, int, bool):
    clear = False
    menu_dict = {}
    menu_desc = {}

    if len(command) != 0:
        if command.get('Male'):
            curr_actor.creation_choices['sex'] = 'Male'
        elif command.get('Female'):
            curr_actor.creation_choices['sex'] = 'Female'

        if curr_actor.creation_choices.get('sex'):
            clear = True
            if curr_actor.circumstance.c_creation:
                game_state = GameStates.ethnicity           
            else:
                game_state = GameStates.hire

    else:
        menu_dict = {'type': MenuTypes.page, 'header': 'Choose your sex', 'options': ['Male','Female'], 'mode': False, 'desc': {}} 

        male_desc = 'Attribute modifiers due to sex for males: \n'
        female_desc = 'Females are the baseline sex, and have no positive or negative attribute modifiers. '

        for a in sex_attr_mods_m:
            male_desc += a + ': ' + str(int(sex_attr_mods_m.get(a))) + '%\n'

        menu_desc = {'Male': male_desc, 'Female': female_desc}

        menu_dict['desc'] = menu_desc


    return menu_dict, game_state, clear

def choose_ethnicity(curr_actor, game_state, command) -> (dict, int, bool):
    clear = False
    menu_dict = {}
    menu_desc = {}

    if len(command) != 0:
        for e in Ethnicity.getinstances():
            if command.get(e.name):
                curr_actor.creation_choices['ethnicity'] = e.name
                game_state = GameStates.social
                clear = True

    else:
        menu_dict = {'type': MenuTypes.page, 'header': 'Choose your ethnicity', 'options': [], 'mode': False, 'desc': {}} 

        for e in Ethnicity.getinstances():
            menu_dict['options'].append(e.name)
            phys_txt = 'Physical Description: ' + e.phys_desc + '\nAverage Height: Males - ' + inch_conv(e.avg_ht_m) + ' Females - ' + inch_conv(e.avg_ht_f)
            age_txt = 'Age Ranges: Child: 0 - ' + str(e.age_ranges.get('Child')) + ' Young Adult: ' + str(e.age_ranges.get('Child')+1) + ' - ' + str(e.age_ranges.get('Young Adult')) + ' Adult: ' + str(e.age_ranges.get('Young Adult')+1) + ' - ' + str(e.age_ranges.get('Adult')) + ' Mature Adult: ' + str(e.age_ranges.get('Adult')+1) + ' - ' + str(e.age_ranges.get('Mature Adult')) + ' Elderly: ' + str(e.age_ranges.get('Mature Adult')+1) + '+'
            attr_txt = 'Attribute modifiers: '
            for a in e.attr_mods:
                attr_txt += attr_name_dict.get(a) + ': ' + str(int(e.attr_mods.get(a))) + '%, '
            culture_txt = 'Culture: ' + e.culture
            history_txt = 'History: ' + e.history

            menu_desc[e.name] = '_'*110 + '\n' + phys_txt + '\n' + '*'*110 + '\n' + age_txt + '\n' + '*'*110 + '\n' + attr_txt + '\n' + '*'*110 + '\n' + culture_txt + '\n' + '*'*110 + '\n' + history_txt


        menu_dict['desc'] = menu_desc


    return menu_dict, game_state, clear