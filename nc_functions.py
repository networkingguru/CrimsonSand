from enums import GameStates, MenuTypes
from components.circumstances import Circumstance

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