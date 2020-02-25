from enums import GameStates, MenuTypes
from components.circumstances import Circumstance
from components.ethnicities import Ethnicity
from components.professions import Profession
from components.upbringing import get_valid_upbringings
from utilities import inch_conv,roll_dice
from components.fighter import attr_name_dict
from chargen_functions import random_attr


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

def roll_social(curr_actor, game_state, command) -> (dict, int, bool):
    roll = 0
    standing = ''
    professions = set()
    u_profs = set()
    clear = False
    
    roll_button = {'text':'Roll Dice','command':'roll'}
    accept_button = {'text':'Accept Standing and Continue','command':'accept'}
    buttons = [roll_button,accept_button]

    if len(command) > 0:
        if command.get('roll'):
            roll = roll_dice(1,100)
            if roll <= 10:
                standing = 'Lower Lower Class'
            elif roll <= 20:
                standing = 'Middle Lower Class'
            elif roll <= 30:
                standing = 'Upper Lower Class'
            elif roll <= 45:
                standing = 'Lower Middle Class'    
            elif roll <= 60:
                standing = 'Middle Middle Class'  
            elif roll <= 75:
                standing = 'Upper Middle Class' 
            elif roll <= 85:
                standing = 'Lower Upper Class'     
            elif roll <= 95:
                standing = 'Middle Upper Class'
            else:
                standing = 'Upper Upper Class'  
            for e in Ethnicity.getinstances():
                if e.name == curr_actor.creation_choices.get('ethnicity'):
                    professions = set(e.allowed_prof)

            for u in get_valid_upbringings(curr_actor,roll):
                u_profs.update(u.allowed_prof)

            professions = professions.intersection(u_profs)

            for p in Profession.__subclasses__():
                prof = p(curr_actor)
                if prof.name in professions:
                    if prof.male_allowed == False and curr_actor.creation_choices.get('sex') == 'Male':
                        professions.discard(prof.name)
                    if prof.female_allowed == False and curr_actor.creation_choices.get('sex') == 'Female':
                        professions.discard(prof.name)
                
            curr_actor.temp_store = {'type': MenuTypes.roll, 'header': 'Roll for your family\'s social standing', 'options': ['Roll','Accept'], 'mode': False, 'desc': {'roll':roll,'standing':standing,'prof':professions,'buttons':buttons}}


        elif command.get('accept') and curr_actor.temp_store.get('desc').get('roll') > 0:
            curr_actor.creation_choices['social'] = curr_actor.temp_store.get('desc').get('roll')
            menu_dict = {}
            game_state = GameStates.attributes
            curr_actor.temp_store = {}
            clear = True

    if len(curr_actor.temp_store) == 0:
        menu_dict = {'type': MenuTypes.roll, 'header': 'Roll for your family\'s social standing', 'options': ['Roll','Accept'], 'mode': False, 'desc': {'roll':roll,'standing':standing,'prof':professions,'buttons':buttons}}
    else:
        menu_dict = curr_actor.temp_store 

    return menu_dict, game_state, clear

def roll_attr(curr_actor, game_state, command) -> (dict, int, bool):
    clear=False
    rolls = []
    menu_dict = {}
    assigned_slots = []
    roll_buttons = []
    attributes = {'Logic':0,'Wisdom':0,'Comprehension':0,'Communication':0,'Mental Celerity':0,'Willpower':0,'Steady State':0,'Power':0,'Manual Dexterity':0,
                    'Pedal Dexterity':0,'Balance':0,'Swiftness':0,'Flexibility':0,'Stamina':0,'Dermatology':0,'Bone Structure':0,'Immune System':0, 'Shock Resistance':0,
                    'Sight':0,'Hearing':0,'Taste/Smell':0,'Touch':0,'Body Fat':0}

    if len(command) > 0:
        if command.get('roll'):
            rolls = random_attr(1)
            i=0
            for r in rolls:
                roll_buttons.append({'slot':i,'roll':r,'selected':False})
                i+=1

            curr_actor.temp_store = {'type': MenuTypes.attr, 'header': 'Roll for your base attributes', 'options': ['Roll','Accept'], 'mode': False, 'desc': {'roll_buttons':roll_buttons,'assigned_slots':assigned_slots,'attributes':attributes}}

        elif command.get('slot'):
            roll_buttons = curr_actor.temp_store.get('desc').get('roll_buttons')
            for r in roll_buttons:
                if r.get('slot') != command.get('slot'):
                    r['selected'] = False
                else:
                    r['selected'] = True                  

        elif command.get('accept') and len(curr_actor.temp_store.get('attributes')) == len(curr_actor.temp_store.get('assigned_slots')):
            curr_actor.creation_choices['attributes'] = curr_actor.temp_store.get('desc').get('attributes')
            menu_dict = {}
            game_state = GameStates.upbringing
            curr_actor.temp_store = {}
            clear = True

        else:
            roll_buttons = curr_actor.temp_store.get('desc').get('roll_buttons')
            attributes = curr_actor.temp_store.get('desc').get('attributes')
            assigned_slots = curr_actor.temp_store.get('desc').get('assigned_slots')
            for a in attributes:
                if command.get(a):
                    for r in roll_buttons:
                        if r.get('selected') == True:
                            attributes[a] = r.get('roll')
                            assigned_slots.append(r.get('slot'))

    if len(curr_actor.temp_store) == 0:
        menu_dict = {'type': MenuTypes.attr, 'header': 'Roll for your base attributes', 'options': ['Roll','Accept'], 'mode': False, 'desc': {'roll_buttons':roll_buttons,'assigned_slots':assigned_slots,'attributes':attributes}}
    else:
        menu_dict = curr_actor.temp_store 

    return menu_dict, game_state, clear