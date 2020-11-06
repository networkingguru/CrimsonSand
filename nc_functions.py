import global_vars
import time
from copy import deepcopy
from enums import GameStates, MenuTypes
from components.circumstances import Circumstance
from components.ethnicities import Ethnicity, age_mods
from components.professions import Profession
from components.upbringing import get_valid_upbringings
from components.fighter import attr_name_dict, Skill
from utilities import inch_conv,roll_dice,make_bar
from chargen_functions import random_attr
from options import name_dict
from item_gen import weapon_generator, calc_weapon_stats



sex_attr_mods_m = {'Logic':5,'Wisdom':-5,'Comprehension':-5,'Communication':-5,'Mental Celerity':-5,'Willpower':5,'Steady State':30,'Power':30,'Manual Dexterity':-5,
                    'Pedal Dexterity':-10,'Balance':-5,'Swiftness':-10,'Flexibility':-10,'Stamina':5,'Dermatology':5,'Bone Structure':15,'Immune System':5, 'Shock Resistance':-10,
                    'Sight':15,'Hearing':-5,'Taste/Smell':-10,'Touch':-5,'Body Fat':-10}


def choose_circumstance(curr_actor, game_state, command) -> (dict, int, bool):
    clear = False
    menu_dict = {}
    menu_desc = {}
    skip = True

    if skip: #For debugging
        for c in Circumstance.getinstances():
            if c.name == 'Contracted Gladiator':
                menu_dict = {'type': MenuTypes.page, 'header': 'Choose your starting circumstances', 'options': [], 'mode': False, 'desc': {}}   
                curr_actor.circumstance = c
                curr_actor.creation_choices['circumstance'] = c.name
                game_state = GameStates.sex
                clear = True
                break

    elif len(command) != 0:
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
    skip = True
    
    if skip: #For debugging
        curr_actor.creation_choices['sex'] = 'Male'
        clear = True
        menu_dict = {'type': MenuTypes.page, 'header': 'Choose your sex', 'options': ['Male','Female'], 'mode': False, 'desc': {}} 
        if curr_actor.circumstance.c_creation:
            game_state = GameStates.ethnicity           
        else:
            game_state = GameStates.hire

    elif len(command) != 0:
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
            male_desc += a + ': ' + str(int(sex_attr_mods_m.get(a))) + '\n'

        menu_desc = {'Male': male_desc, 'Female': female_desc}

        menu_dict['desc'] = menu_desc


    return menu_dict, game_state, clear

def choose_ethnicity(curr_actor, game_state, command) -> (dict, int, bool):
    clear = False
    menu_dict = {}
    menu_desc = {}
    skip = True
    
    if skip: #For debugging
        for e in Ethnicity.getinstances():
            if e.name == 'Corrillian':
                menu_dict = {'type': MenuTypes.page, 'header': 'Choose your ethnicity', 'options': [], 'mode': False, 'desc': {}} 
                curr_actor.creation_choices['ethnicity'] = e.name
                game_state = GameStates.social
                clear = True
                break


    elif len(command) != 0:
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
                if list(e.attr_mods.keys())[-1] == a:
                    attr_txt += attr_name_dict.get(a) + ': ' + str(int(e.attr_mods.get(a)))
                else:
                    attr_txt += attr_name_dict.get(a) + ': ' + str(int(e.attr_mods.get(a))) + ', '
            culture_txt = 'Culture: ' + e.culture
            history_txt = 'History: ' + e.history

            menu_desc[e.name] = '_'*110 + '\n' + phys_txt + '\n' + '*'*110 + '\n' + age_txt + '\n' + '*'*110 + '\n' + attr_txt + '\n' + '*'*110 + '\n' + culture_txt + '\n' + '*'*110 + '\n' + history_txt


        menu_dict['desc'] = menu_desc


    return menu_dict, game_state, clear

def roll_social(curr_actor, game_state, command) -> (dict, int, bool):
    roll = 0
    standing = ''
    professions = set()
    clear = False
    skip = True
    
    if skip: #For debugging
        menu_dict = {'type': MenuTypes.roll, 'header': 'Roll for your family\'s social standing', 'options': ['Roll'], 'mode': False, 'desc': {'roll':roll,'standing':standing,'prof':professions}}
        curr_actor.creation_choices['social'] = 50
        game_state = GameStates.attributes
        curr_actor.temp_store = {}
        clear = True

    elif len(command) > 0:
        if command.get('Roll') or command.get('Re-roll'):
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
            
            professions = allowed_profs(curr_actor,roll)
                
            curr_actor.temp_store = {'type': MenuTypes.roll, 'header': 'Roll for your family\'s social standing', 'options': ['Re-roll','Accept Roll'], 'mode': False, 'desc': {'roll':roll,'standing':standing,'prof':professions}}


        elif command.get('Accept Roll') and curr_actor.temp_store.get('desc').get('roll') > 0:
            curr_actor.creation_choices['social'] = curr_actor.temp_store.get('desc').get('roll')
            menu_dict = {}
            game_state = GameStates.attributes
            curr_actor.temp_store = {}
            clear = True

    if len(curr_actor.temp_store) == 0:
        menu_dict = {'type': MenuTypes.roll, 'header': 'Roll for your family\'s social standing', 'options': ['Roll'], 'mode': False, 'desc': {'roll':roll,'standing':standing,'prof':professions}}
    else:
        menu_dict = curr_actor.temp_store 

    return menu_dict, game_state, clear

def roll_attr(curr_actor, game_state, command) -> (dict, int, bool):
    clear=False
    rolls = []
    menu_dict = {}
    skip = True
    
    if skip: #For debugging
        while len(rolls) < 29:
            rolls.append(200)
        curr_actor.creation_choices['rolls'] = rolls
        menu_dict = {'type': MenuTypes.attr, 'header': 'Roll for your base attributes', 'options': ['Roll'], 'mode': False, 'desc': {'rolls':rolls}}
        game_state = GameStates.attributes2
        curr_actor.temp_store = {}
        clear = True

    elif len(command) > 0:
        if command.get('Roll') or command.get('Re-roll'):
            rolls = sorted(random_attr(1),reverse=True) 
            
            curr_actor.temp_store = {'type': MenuTypes.attr, 'header': 'Roll for your base attributes', 'options': ['Re-roll','Accept'], 'mode': False, 'desc': {'rolls':rolls}}
                

        elif command.get('Accept'):
            curr_actor.creation_choices['rolls'] = curr_actor.temp_store.get('desc').get('rolls')
            menu_dict = {}
            game_state = GameStates.attributes2
            curr_actor.temp_store = {}
            clear = True


    if len(curr_actor.temp_store) == 0:
        menu_dict = {'type': MenuTypes.attr, 'header': 'Roll for your base attributes', 'options': ['Roll'], 'mode': False, 'desc': {'rolls':rolls}}
    else:
        menu_dict = curr_actor.temp_store 

    return menu_dict, game_state, clear

def assign_attr(curr_actor, game_state, command) -> (dict, int, bool):
    clear=False
    rolls = curr_actor.creation_choices.get('rolls')
    attributes = {'Logic':0,'Wisdom':0,'Memory':0,'Comprehension':0,'Communication':0,'Creativity':0,'Mental Celerity':0,'Willpower':0,'Steady State':0,'Power':0,'Manual Dexterity':0,
                    'Pedal Dexterity':0,'Balance':0,'Swiftness':0,'Flexibility':0,'Stamina':0,'Dermatology':0,'Bone Structure':0,'Immune System':0, 'Shock Resistance':0,'Toxic Resistance':0,
                    'Sight':0,'Hearing':0,'Taste/Smell':0,'Touch':0,'Facial Features':0,'Height':0,'Body Fat':0,'Shapeliness':0}
    attr_mods = determine_attr_mods(curr_actor) #Dict of dicts in format attr:{ethnicity:mod,sex:mod}
    ethnicity = curr_actor.creation_choices.get('ethnicity')
    professions = allowed_profs(curr_actor)
    skip = True

    
    if len(curr_actor.temp_store) == 0:
        curr_actor.temp_store = {'type': MenuTypes.attr2, 'header': 'Assign rolls to your attributes', 'options': ['Revert'], 'mode': False, 'desc': {'attributes':attributes,'index':0,'roll':0,'attr_mods':attr_mods,'professions':professions,'curr_actor':curr_actor}}

    i =  curr_actor.temp_store.get('desc').get('index')

    if skip:    #For debugging
        curr_actor.creation_choices['attributes'] = curr_actor.temp_store.get('desc').get('attributes')
        menu_dict = curr_actor.temp_store
        game_state = GameStates.upbringing
        curr_actor.temp_store = {}
        clear = True
        i = 0
        for key,value in curr_actor.creation_choices['attributes'].items():
            curr_actor.creation_choices['attributes'][key] = curr_actor.creation_choices['rolls'][i]
            i += 1

    elif len(command) > 0:
        if command.get('Accept'):
            curr_actor.creation_choices['attributes'] = curr_actor.temp_store.get('desc').get('attributes')
            menu_dict = {}
            game_state = GameStates.upbringing
            curr_actor.temp_store = {}
            clear = True
        elif command.get('Revert'):
            curr_actor.temp_store['desc']['attributes'] = attributes
            curr_actor.temp_store['desc']['index' ]= 0
            curr_actor.temp_store['options' ]= ['Revert']

        else:
            for key,value in curr_actor.temp_store['desc']['attributes'].items():
                if command.get(key):
                    attr_mod = 0
                    if attr_mods.get(key):
                        attr_mod = sum(attr_mods.get(key).values())
                    curr_actor.temp_store['desc']['attributes'][key] = rolls[i] + attr_mod
                    curr_actor.temp_store['desc']['index'] += 1
                    curr_actor.temp_store['options'].remove(key)
    else:
        if curr_actor.temp_store.get('desc').get('attributes'):
            attrs = curr_actor.temp_store.get('desc').get('attributes')
        else:
            attrs = attributes
        for key,value in attrs.items():
            if value == 0 and key not in curr_actor.temp_store.get('options'):
                curr_actor.temp_store['options'].append(key)
        if i == 29 and 'Accept' not in curr_actor.temp_store.get('options'):
            curr_actor.temp_store['options'].append('Accept')
        curr_actor.temp_store['desc']['roll'] = rolls[i] if i <= len(rolls) - 1 else 0
    menu_dict = curr_actor.temp_store 

    return menu_dict, game_state, clear

def choose_upbringing(curr_actor, game_state, command) -> (dict, int, bool):
    valid_upbringings = get_valid_upbringings(curr_actor, None)
    menu_dict = {'type': MenuTypes.page, 'header': 'Choose your childhood upbringing', 'options': [], 'mode': False, 'desc': {}}
    clear = False
    skip = True
    
    if skip: #For debugging
        for u in valid_upbringings:
            if u.name == 'Normal':
                curr_actor.creation_choices['upbringing'] = u.name 
                game_state = GameStates.age
                clear = True
                break


    elif len(command) > 0:
        for u in valid_upbringings:
            if command.get(u.name):
                curr_actor.creation_choices['upbringing'] = u.name 
                game_state = GameStates.age
                clear = True
                menu_dict = {}
                curr_actor.temp_store = {}

    else:
        for u in valid_upbringings:
            menu_dict['options'].append(u.name)
            attr_txt = 'Attribute modifiers: '
            skill_txt = 'Free Skills: '
            skill_mod_txt = 'Skill Modifiers: '
            if len(u.attr_mods) > 0:
                for a in u.attr_mods:
                    if list(u.attr_mods.keys())[-1] == a:
                        attr_txt += attr_name_dict.get(a) + ': ' + str(int(u.attr_mods.get(a)))
                    else:
                        attr_txt += attr_name_dict.get(a) + ': ' + str(int(u.attr_mods.get(a))) + ', '
            else:
                attr_txt += 'None'
            if len(u.free_skills) > 0:
                for s in u.free_skills:
                    if u.free_skills[-1] == s:
                        skill_txt += s
                    else:
                        skill_txt += s + ', '
            else:
                skill_txt += 'None'
            if len(u.skill_mods) > 0:
                for s in u.skill_mods:
                    if list(u.skill_mods.keys())[-1] == s:
                        skill_mod_txt += s.capitalize() + ': ' + str(int(u.skill_mods.get(s)))
                    else:
                        skill_mod_txt += s.capitalize() + ': ' + str(int(u.skill_mods.get(s))) + ', '
            else:
                skill_mod_txt += 'None'


            menu_dict['desc'][u.name] = u.desc + '\n' + attr_txt + '\n' + skill_txt + '\n' + skill_mod_txt


    return menu_dict, game_state, clear

def choose_age(curr_actor, game_state, command) -> (dict, int, bool):
    valid_upbringings = get_valid_upbringings(curr_actor, None)
    menu_dict = {'type': MenuTypes.num_page, 'header': 'Choose your age', 'options': ['Accept'], 'mode': False, 'desc': {}}
    clear = False
    eth_name = curr_actor.creation_choices.get('ethnicity')
    ethnicity = None
    skip = True

    for e in Ethnicity.getinstances():
        if e.name == eth_name:
            ethnicity = e
    if skip: #For debugging
        for _ in valid_upbringings:
            curr_actor.temp_store['Age'] = '35'
            curr_actor.creation_choices['age'] = '35' 
            game_state = GameStates.profession
            clear = True
            break

    elif len(command) > 0:
        if command.get('Age'):
            curr_actor.temp_store['Age'] = command.get('Age')
        elif command.get('Accept'):
            curr_actor.creation_choices['age'] = curr_actor.temp_store.get('Age')
            curr_actor.temp_store = {}
            game_state = GameStates.profession
            clear = True          

    else:
        if not curr_actor.temp_store.get('Age'):
            curr_actor.temp_store['Age'] = '16'

    mod_dict = age_mods(int(curr_actor.temp_store.get('Age')),ethnicity)

    mod_str = ''
    for key, value in mod_dict.items():
        if key is not list(mod_dict.keys())[-1]:
            mod_str += key + ': ' + str(value) + ', '
        else:
            mod_str += key + ': ' + str(value)

    menu_dict['desc']['age mods'] = mod_str
    menu_dict['desc']['age'] = curr_actor.temp_store.get('Age')

    return menu_dict, game_state, clear

def choose_profs(curr_actor, game_state, command) -> (dict, int, bool):
    menu_dict = {}
    clear = False
    years = int(curr_actor.creation_choices.get('age')) - 16
    skip = True
    

    #Add fighter component if missing
    if curr_actor.fighter is None:
        attrs = curr_actor.creation_choices.get('attributes')
        attr_mods = determine_attr_mods(curr_actor)

        for a,d in attr_mods.items():
                attrs[a] += sum(d.values())
        attr_dict = dict()
        for a,v in attrs.items():
            for k,n in attr_name_dict.items():
                if n == a:
                    abr = k
                    break
            attr_dict[k] = v
        f_attrs = [attr_dict,{},0]
        curr_actor.add_fighter_component(f_attrs)

    #Add ethnicity, SS, age, upbringing, sex to fighter
    if curr_actor.creation_choices.get('sex') != 'Male':
        curr_actor.fighter.male = False
    for u in get_valid_upbringings(curr_actor, None):
        if u.name == curr_actor.creation_choices.get('upbringing'):
            curr_actor.fighter.upbringing = u
    for e in Ethnicity.getinstances():
        if e.name == curr_actor.creation_choices.get('ethnicity'):
            curr_actor.fighter.ethnicity = e
    curr_actor.fighter.social = curr_actor.creation_choices.get('social')
    curr_actor.fighter.age = curr_actor.creation_choices.get('age')
    

    if not curr_actor.temp_store.get('valid_professions'):
        curr_actor.temp_store['valid_professions'] = prune_profs(curr_actor,allowed_profs(curr_actor))
    valid_professions = curr_actor.temp_store.get('valid_professions')
    
    if len(valid_professions) == 0 or skip:
        curr_actor.creation_choices['professions'] = {} 
        game_state = GameStates.name
        clear = True
        menu_dict = {}
        curr_actor.temp_store = {}

    elif len(command) > 0:
        if command.get('Accept'):
            add_profs(curr_actor)
            electives = False
            for p in curr_actor.fighter.professions:
                if len(p.elect_primary_skills) > 0:
                    electives = True
                if len(p.elect_sec_skills) > 0:
                    electives = True
            game_state = GameStates.name
            if electives:
                game_state = GameStates.skills
            clear = True
            menu_dict = {}
            curr_actor.temp_store = {}
        elif command.get('Revert'):
            curr_actor.creation_choices['professions'] = {} 
        else: 
            for p in valid_professions:
                if command.get(p.name):
                    if not curr_actor.creation_choices.get('professions').get(p.name):
                        curr_actor.creation_choices['professions'][p.name] = 0
                    curr_actor.creation_choices['professions'][p.name] += 1
                    curr_actor.temp_store['menu_dict'] = gen_profs_menu(curr_actor,valid_professions,years)
                    menu_dict = curr_actor.temp_store.get('menu_dict')


    else:
        if not curr_actor.temp_store.get('menu_dict'):
            curr_actor.temp_store['menu_dict'] = gen_profs_menu(curr_actor,valid_professions,years)
        menu_dict = curr_actor.temp_store.get('menu_dict')


    return menu_dict, game_state, clear

def choose_skills(curr_actor, game_state, command) -> (dict, int, bool):
    menu_dict = {}
    clear = False
    skip = True

    


    if not curr_actor.creation_choices.get('skills'):
        curr_actor.creation_choices['skills'] = {} #Nested dict in the following format {skill:xp}
    
    if not curr_actor.temp_store.get('electives'):
        curr_actor.temp_store['electives'] = {} #Nested dict in following format {profession:{primary:{category:[[skill list],levels]}}}

    if len(curr_actor.creation_choices.get('skills')) == 0 and len(curr_actor.temp_store.get('electives')) == 0: 
        electives = curr_actor.temp_store.get('electives')
        for p in curr_actor.fighter.professions:
            if len(p.elect_primary_skills) > 0:
                electives[p.name] = {'primary':{}}
                electives[p.name]['primary'] = p.elect_primary_skills
            if len(p.elect_sec_skills) > 0:
                electives[p.name] = {'secondary':{}}
                electives[p.name]['secondary'] = p.elect_sec_skills
    if skip:
        game_state = GameStates.name
        clear = True
        curr_actor.temp_store = {}


    elif len(command) > 0:
        if command.get('Accept'):
            for k in curr_actor.creation_choices.get('skills'):
                skill = curr_actor.skill_dict.get(k)
                xp = curr_actor.creation_choices.get('skills').get(k)
                skill.experience += xp
                skill.set_level()
                skill.set_rating()
            game_state = GameStates.name
            clear = True
            menu_dict = {}
            curr_actor.temp_store = {}
        elif command.get('Revert'):
            curr_actor.temp_store['electives'] = {}
            curr_actor.creation_choices['skills'] = {} 
        else: 
            profs = list(curr_actor.temp_store.get('electives').keys())
            if not curr_actor.temp_store.get('picks'):
                gen_picks_dict(curr_actor)
            for prof in profs:
                for ps in curr_actor.temp_store.get('electives').get(prof):
                    for cat in curr_actor.temp_store.get('electives').get(prof).get(ps):
                        if list(command.keys())[0] in curr_actor.temp_store.get('electives').get(prof).get(ps).get(cat)[0]:
                            skill = list(command.keys())[0]
                            skl = curr_actor.fighter.skill_dict.get(skill)
                            xp = skl.experience
                            lvl = skl.level
                            if ps == 'primary' and curr_actor.temp_store.get('electives').get(prof).get(ps).get(cat)[1] > curr_actor.temp_store.get('picks').get(prof).get(ps).get(cat):  
                                if not curr_actor.creation_choices.get('skills'):
                                    curr_actor.creation_choices['skills'] = {}
                                if not curr_actor.creation_choices.get('skills').get(skill):
                                    curr_actor.creation_choices['skills'][skill] = 0
                                    for p in curr_actor.fighter.professions:
                                        if p.name == prof:
                                            add_lvl = p.level
                                            new_lvl = lvl
                                            while add_lvl > 0:
                                                new_lvl += 1
                                                xp += skl.cost * new_lvl
                                                add_lvl -= 1
                                else:
                                    xp += curr_actor.creation_choices.get('skills').get(skill)
                                    for sk in Skill.__subclasses__():
                                        s = sk(curr_actor)
                                        if s.name == skill:
                                            s.experience = xp
                                            s.set_level()
                                            xp += s.cost * (s.level + 1)
                                            break                       
                                
                                curr_actor.creation_choices['skills'][skill] += xp
                                curr_actor.temp_store['picks'][prof][ps][cat] += 1
                                break
                        elif cat == 'secondary' and curr_actor.temp_store.get('electives').get(prof).get(ps).get(cat)[1] > curr_actor.temp_store.get('picks').get(prof).get(ps).get(cat):
                            xp += skl.cost
                            curr_actor.creation_choices['skills'][skill] += xp
                            curr_actor.temp_store['picks'][prof][ps][cat] += 1
                            break

    else:
        menu_dict = gen_skill_menu(curr_actor)

    return menu_dict, game_state, clear

def choose_name(curr_actor, game_state, command) -> (dict, int, bool):
    menu_dict = {'type': MenuTypes.name_page, 'header': 'Choose your name', 'options': ['Random','Accept'], 'mode': False, 'desc': {}}
    clear = False
    lang_name = curr_actor.fighter.ethnicity.name_lang
    skip = True
    if curr_actor.fighter.male:
        sex = 'male'
    else:
        sex = 'female'
    names = name_dict.get(lang_name).get(sex) + name_dict.get(lang_name).get('unisex')

    if skip: #For debugging
        curr_actor.temp_store = {}
        curr_actor.creation_choices['name'] = 'Player'
        curr_actor.name = 'Player' 
        game_state = GameStates.shop_w
        clear = True


    elif len(command) > 0:
        if command.get('Name'):
            curr_actor.temp_store['name'] = command.get('Name')
        elif command.get('Accept'):
            curr_actor.creation_choices['name'] = curr_actor.temp_store.get('name')
            curr_actor.name = curr_actor.temp_store.get('name')
            curr_actor.temp_store = {}
            game_state = GameStates.shop_w
            clear = True
        elif command.get('Random'):
            idx = roll_dice(1,len(names)) - 1
            curr_actor.temp_store['name'] = names[idx]


    else:
        if not curr_actor.temp_store.get('name'):
            idx = roll_dice(1,len(names)) - 1
            curr_actor.temp_store['name'] = names[idx]

    menu_dict['desc']['name'] = curr_actor.temp_store.get('name')

    return menu_dict, game_state, clear

def buy_weapons(curr_actor, game_state, command) -> (dict, int, bool):
    menu_dict = {}
    clear = False
    skip = False

    if 'Category' not in curr_actor.temp_store:
        curr_actor.temp_store['Category'] = 0
    category = curr_actor.temp_store.get('Category')

    if skip:
        game_state = GameStates.shop_a
        clear = True
        curr_actor.temp_store = {}
    elif len(command) > 0:
        if command.get('Next Category'):
            category += 1
            if category >= (len(list(curr_actor.temp_store.get('weapons').keys()))-2):
                category = 0
            curr_actor.temp_store['Category'] = category

        elif command.get('Revert Purchases'):
            for w in curr_actor.fighter.weapons:
                curr_actor.fighter.money += int(w.cost)
            curr_actor.fighter.weapons.clear()
        elif command.get('Continue to Armor Store'):
            curr_actor.temp_store = {}
            game_state = GameStates.shop_a
            clear = True
        else:
            catname = list(curr_actor.temp_store.get('weapons'))[category]
            for w in curr_actor.temp_store.get('weapons').get(catname):
                if command.get(id(w)) and curr_actor.fighter.money >= w.cost:
                    curr_actor.fighter.weapons.append(w)
                    curr_actor.fighter.money -= int(w.cost)
                    break
    else:
        menu_dict = gen_wstore_menu(curr_actor,category)


    return menu_dict, game_state, clear

def confirm_weapon(curr_actor, game_state, command) -> (dict, int, bool):
    menu_dict = {'type': MenuTypes.confirm_page, 'header': 'Confirm your purchase', 'options': ['Confirm', 'Abort'], 'mode': False, 'desc': {}}
    clear = False
    skip = False
    w = curr_actor.temp_store.get('purchase')

    if len(command) != 0 or skip:
        if skip or command.get('Confirm'):
            curr_actor.fighter.money -= w.cost
            curr_actor.fighter.weapons.append(w)
            
        curr_actor.temp_store['purchase'] = None
        game_state = GameStates.shop_w
        clear = True
    else:
        menu_dict['desc']['text'] = 'You have decided to purchase ' + w.name + ' for ' + str(int(w.cost)) + ' gold. This will leave you with ' + str(int(curr_actor.fighter.money - w.cost)) + ' gold. \n'
        menu_dict['desc']['text'] += 'Is this OK? '

    return menu_dict, game_state, clear

def gen_picks_dict(curr_actor):
    picks = curr_actor.temp_store['picks'] = {} #Nested dict for holding picks. Format is {profession:{primary:{category:picks}}}
    electives = curr_actor.temp_store.get('electives')

    for prof in electives:
        picks[prof] = {}
        for sk_type in electives.get(prof):
            picks[prof][sk_type] = {}
            for cat in electives.get(prof).get(sk_type):
                picks[prof][sk_type][cat] = 0

def gen_skill_menu(curr_actor) -> dict:
    menu_dict = {'type': MenuTypes.page, 'header': 'Choose your elective skills', 'options': [], 'mode': False, 'desc': {}}
    chosen_skills = curr_actor.creation_choices.get('skills')
    electives = curr_actor.temp_store.get('electives')
    picks = curr_actor.temp_store.get('picks')

    if len(chosen_skills) > 0:
        menu_dict['options'].append('Revert')
    if len(electives) == 0:
        menu_dict['options'].append('Accept')
    else:
        prof = sk_type = cat = None
        prof, sk_type, cat = set_electives(curr_actor)


        if prof is not None:
            levels = electives.get(prof).get(sk_type).get(cat)[1]
            for skill in electives.get(prof).get(sk_type).get(cat)[0]:
                skl = curr_actor.fighter.skill_dict.get(skill)
                desc = 'Profession: ' + prof + '\n' + 'Category: ' + cat + '\n' + 'Skill Type: ' + sk_type + '\n' + 'Picks Remaining: ' + str(levels) + '\n' + 'Skill \t\t Level \t\t Rating \n' + '===== \t\t ===== \t\t ======\n'

                for p in curr_actor.fighter.professions:
                    if p.name == prof:
                        profession = p

                for sk in Skill.__subclasses__():
                    s = sk(curr_actor)
                    if s.name == skill:
                        l = skl.level+profession.level
                        xp = 0
                        while l > 0:
                            xp += l * s.cost
                            l -= 1
                        s.experience = xp
                        s.set_level()
                        s.set_rating()
                        x = len(skl.name)
                        if len(skl.name) < 7:
                            desc += skl.name + ' \t\t ' + str(s.level) + ' \t\t ' + str(s.rating) + '\n'
                        else:
                            desc += skl.name + ' \t ' + str(s.level) + ' \t\t ' + str(s.rating) + '\n'

                for k,v in curr_actor.fighter.skill_dict.items():
                    if k != skill:
                        if len(k) < 7:
                            desc += v.name + ' \t\t ' + str(v.level) + ' \t\t ' + str(v.rating) + '\n'
                        else:
                            desc += v.name + ' \t ' + str(v.level) + ' \t\t ' + str(v.rating) + '\n'


                menu_dict['options'].append(skill)
                menu_dict['desc'][skill] = desc



    return menu_dict

def set_electives(curr_actor) -> (str,str,str):
    electives = curr_actor.temp_store.get('electives')
    picks = curr_actor.temp_store.get('picks')
    profs = list(curr_actor.temp_store.get('electives').keys())
    for prof in profs:
            for sk_type in electives.get(prof):
                for cat in electives.get(prof).get(sk_type):
                    if not curr_actor.temp_store.get('picks'):
                        return prof, sk_type, cat
                    elif electives.get(prof).get(sk_type).get(cat)[1] > picks.get(prof).get(sk_type).get(cat):
                        return prof, sk_type, cat

def gen_wstore_menu(curr_actor,category) -> dict:
    menu_dict = {'type': MenuTypes.store_page, 'header': 'Purchase Weapons', 'options': {}, 'mode': False, 'desc': {}, 'to_hit_best': -100, 'to_hit_worst': 100,
                'parry_best': -100, 'parry_worst': 100, 'damage_best': 0, 'damage_worst': 10000}
    purchased_weapons = curr_actor.fighter.weapons
    categories = ['sword','dagger','staff','spear','axe','mace','hammer','pick','polearm']
    active_cat = categories[category]
    sword_desc = ('Swords are weapons that can do slashing, piercing, or bludgeoning damage. Slashing and piercing damage are done with the blade, giving them the advantage of length, while bludgeoning damage is done with the pommel, requiring close quarters. Swords come in nine varieties, based on length and blade design. There are short, medium, and long swords, and single-edged, double-edged, '  
                'and curved single-edged swords. Swords tend to be fast, versatile weapons that are devastatingly powerful vs. unarmored opponents, but tend to be ineffective vs. metal armor. Slashing/piercing damage is converted to bludgeoning damage for any damage that does not peirce the armor, and is spread out over a 3-4 hit location area. For unarmored opponents or armor piercing attacks, '  
                'slashing/piercing damage must go through each layer (skin/tissue/bone) one at a time, but can sever or run through, passing additional damage to a new location. In the case of slashing damage, this can sever limbs or even split an enemy in two. ')
    dagger_desc = ('Daggers are short weapons that can do slashing, piercing, or bludgeoning damage. Slashing and piercing damage are done with the blade, while bludgeoning damage is done with the pommel. As short weapons, all daggers require close quarters. ' 
                'Daggers are extremely fast, versatile weapons that are deadly vs. unarmored opponents, but tend to be ineffective vs. metal armor. Slashing/piercing damage is converted to bludgeoning damage for any damage that does not peirce the armor, and is spread out over a 3-4 hit location area. ')
    staff_desc = ('Staves are long wooden poles, sometimes shod with metal at the ends, with a grip around the center. While not incredibly powerful, staves are very defensive, with the basic guards providing ample protection. Additionally, wood is not easily cut by a blade, making staves excellent defenders vs. swords and other slashing weapons. Finally, staves inflict '  
                'bludgeoning damage, which damages all three hit layers (skin, tissue, and bone) simultaneously. If a location is removed of all hits, bludgeoning damage will pass through to the next location in the path. Bludgeoning damage is incredibly effective vs. flexible and semi flexible armor, and can even destroy rigid armor like plate. ')
    spear_desc = ('Spears are long wooden poles with a sharp point. Spears can perform both piercing (stab) and bludgeoning (shaft strike) damage, making spears a slightly more versatile version of staves. Spears share staff guards, so they are very good defensively. Piercing damage is very good at defeating armor, but suffers from deflection penalties. However, spears '  
                'also have the advantage of length, giving you the ability to engage the enemy from a great distance. Bludgeoning damage is incredibly effective vs. flexible and semi flexible armor, and can even destroy rigid armor like plate. ')
    axe_desc = ('Axes are weapons that can do slashing, piercing (Horn Thrust), or bludgeoning (Axe Hammer) damage, but they are not terribly effective at any of these roles. Axes do have the advantage, however, of being easy to manufacture, making them cheap weapons of destruction. '  
                'They also tend to be fast weapons that are powerful vs. unarmored opponents. Slashing/piercing damage is converted to bludgeoning damage for any damage that does not peirce the armor, and is spread out over a 3-4 hit location area. For unarmored opponents or armor piercing attacks, '  
                'slashing/piercing damage must go through each layer (skin/tissue/bone) one at a time, but can sever or run through, passing additional damage to a new location. In the case of slashing damage, this can sever limbs or even split an enemy in two. ')
    mace_desc = ('Maces are glorified clubs, with a wooden or metal shaft connected to a head that may be a ball, a spiked ball, or an advanced fluted surface. Maces inflict '  
                'intense bludgeoning damage, which damages all three hit layers (skin, tissue, and bone) simultaneously. If a location is removed of all hits, bludgeoning damage will pass through to the next location in the path. Bludgeoning damage is incredibly effective vs. flexible and semi flexible armor, and can even destroy rigid armor like plate. ')
    hammer_desc = ('Hammers are tools turned to war, with a wooden or metal shaft connected to a solid head with a flat striking surface. Hammers inflict '  
                'bludgeoning damage, which damages all three hit layers (skin, tissue, and bone) simultaneously. If a location is removed of all hits, bludgeoning damage will pass through to the next location in the path. Bludgeoning damage is incredibly effective vs. flexible and semi flexible armor, and can even destroy rigid armor like plate. ')
    pick_desc = ('Picks are tools turned to war, with a wooden or metal shaft connected to a solid head with a pointed striking surface. Picks inflict '  
                'piercing damage, but they aren\'t sharp in the traditional sense. Picks peirce armor very well due to the energy behind their attacks, but are cumbersome to use, and offer little in the way of defensive guards. ')
    pole_desc = ('Polearms are large, two-handed weapons that can often do slashing and piercing damage, and somtimes bludgeoning as well. Polearms also benefit from the stave guards, making them good defensive weapons, and long lengths, making the engagement range high. '  
                'They tend to be slow weapons, but due to the previously mentioned advantages, are often victorious despite this. ')
    cat_desc = [sword_desc,dagger_desc,staff_desc,spear_desc,axe_desc,mace_desc,hammer_desc,pick_desc,pole_desc]

    #combat_dict = {'total er': tot_er, 'psi': psi,'to hit': to_hit, 
    #                'to parry': to_parry, 'final ap': final_ap, 'parry ap': parry_ap}

    if not curr_actor.temp_store.get('weapons'):
        curr_actor.temp_store['weapons'] = {'sword':[],'dagger':[],'staff':[],'spear':[],'axe':[],'mace':[],'flail':[],'hammer':[],'lance':[],'pick':[],'polearm':[]}
    
    weapon_dict = curr_actor.temp_store.get('weapons')

    for w_type in weapon_dict.keys():
        if len(weapon_dict.get(w_type)) == 0:
            weapon_dict[w_type] = weapon_generator(w_type,23,max_cost=curr_actor.fighter.money)

    if not curr_actor.temp_store.get('combat_stats'):
        combat_stats = curr_actor.temp_store['combat_stats'] = {}

    combat_stats = curr_actor.temp_store.get('combat_stats')

    for w_type in weapon_dict.keys():
        for w in weapon_dict.get(w_type):
            if not combat_stats.get(id(w)):
                combat_stats[id(w)] = calc_weapon_stats(curr_actor,w)
            if combat_stats.get(id(w)).get('psi') > menu_dict.get('damage_best'): menu_dict['damage_best'] = combat_stats.get(id(w)).get('psi')
            if combat_stats.get(id(w)).get('psi') < menu_dict.get('damage_worst'): menu_dict['damage_worst'] = combat_stats.get(id(w)).get('psi')
            if combat_stats.get(id(w)).get('to hit') > menu_dict.get('to_hit_best'): menu_dict['to_hit_best'] = combat_stats.get(id(w)).get('to hit')
            if combat_stats.get(id(w)).get('to hit') < menu_dict.get('to_hit_worst'): menu_dict['to_hit_worst'] = combat_stats.get(id(w)).get('to hit')
            if combat_stats.get(id(w)).get('to parry') > menu_dict.get('parry_best'): menu_dict['parry_best'] = combat_stats.get(id(w)).get('to parry')
            if combat_stats.get(id(w)).get('to parry') < menu_dict.get('parry_worst'): menu_dict['parry_worst'] = combat_stats.get(id(w)).get('to parry')
    
    

    #Item details: Name Price  Weight  Length  To-hit  Parry   Damage  Hands   ER  AP/Attack  AP/Parry
    for w in weapon_dict.get(active_cat):
        if w not in curr_actor.fighter.weapons:
            cs_er = str(int(combat_stats.get(id(w)).get('total er')))
            cs_ap = str(int(combat_stats.get(id(w)).get('final ap')))
            cs_pap =str(int(combat_stats.get(id(w)).get('parry ap')))
            hands = ','.join(map(str,w.hands))
            menu_item = w.name
            item_stats = {'cost':str(int(w.cost)),'weight':str(int(w.weight)),'length':inch_conv(w.length),'to_hit':combat_stats.get(id(w)).get('to hit'),
                        'parry':combat_stats.get(id(w)).get('to parry'),'damage':combat_stats.get(id(w)).get('psi'),'hands':hands,'er':cs_er, 
                        'ap':cs_ap,'pap':cs_pap}


            menu_dict['options'][menu_item] = id(w)
            menu_dict['desc'][id(w)] = item_stats

    menu_dict['options']['Next Category'] = 'Next Category'
    menu_dict['options']['Revert Purchases'] = 'Revert Purchases'
    menu_dict['options']['Continue to Armor Store'] = 'Continue to Armor Store'
    menu_dict['category'] = active_cat.capitalize()
    menu_dict['money'] = curr_actor.fighter.money
    menu_dict['cat_desc'] = cat_desc[category]

    w_purchases = []
    for w in curr_actor.fighter.weapons:
        w_purchases.append(w.name)
    menu_dict['w_purchases'] = ', '.join(w_purchases)


    return menu_dict




def add_profs(curr_actor) -> None:
    prof_dict, skill_dict = determine_ranks(curr_actor)
    for p in Profession.__subclasses__():
        prof = p(curr_actor)
        if curr_actor.creation_choices.get('professions').get(prof.name):
            prof.level = prof_dict.get(prof.name)
            prof.years = curr_actor.creation_choices.get('professions').get(prof.name)
            curr_actor.fighter.professions.add(prof)
    for s in skill_dict:
        for sk in Skill.__subclasses__():
            skl = sk(curr_actor)
            if skl.name == s:
                curr_actor.fighter.skill_dict[skl.name].experience = skill_dict.get(s)
                curr_actor.fighter.skill_dict[skl.name].set_level()
                curr_actor.fighter.skill_dict[skl.name].set_rating()

def gen_profs_menu(curr_actor,valid_professions,years) -> dict:
    valid_profs_list = []
    menu_dict = {'type': MenuTypes.page, 'header': 'Choose your past professions', 'options': ['Revert','Accept'], 'mode': False, 'desc': {}}

    for p in valid_professions:
        valid_profs_list.append(p.name)

    valid_profs_list.sort()
    if not curr_actor.creation_choices.get('professions'):
        curr_actor.creation_choices['professions'] = {}
    if len(curr_actor.creation_choices.get('professions')) > 0:
        for _,value in curr_actor.creation_choices.get('professions').items():
            years -= value

    if years > 0:
        menu_dict['options'].extend(valid_profs_list)
        for p_str in valid_profs_list:
            for p in valid_professions:
                if p.name == p_str:
                    prim_desc = 'Primary Skills(' + p.name + '): ' 
                    prim_elect_desc = 'Primary Elective Skills(' + p.name + '): '
                    sec_desc = 'Secondary Skills(' + p.name + '): '
                    sec_elect_desc = 'Secondary Elective Skills(' + p.name + '): '
                    
                    prof_dict, skill_dict = determine_ranks(curr_actor,p)
                    prof_str, skill_str = convert_ranks(curr_actor,prof_dict,skill_dict)
                    

                    for key,value in p.base_primary_dict.items():
                        if list(p.base_primary_dict.keys())[-1] == key:
                            prim_desc += key + ': ' + str(value)
                        else:
                            prim_desc += key + ': ' + str(value) + ', '
                    if len(p.elect_primary_skills) > 0:
                        for key,value in p.elect_primary_skills.items():
                            if list(p.elect_primary_skills.keys())[-1] == key:
                                prim_elect_desc += key + ': ' + str(value)
                            else:
                                prim_elect_desc += key + ': ' + str(value) + ', '
                    else:
                        prim_elect_desc += 'None'
                    if len(p.base_sec_dict) > 0:
                        for key,value in p.base_sec_dict.items():
                            if list(p.base_sec_dict.keys())[-1] == key:
                                sec_desc += key + ': ' + str(value)
                            else:
                                sec_desc += key + ': ' + str(value) + ', '
                    else:
                        sec_desc += 'None'
                    if len(p.elect_sec_skills) > 0:
                        for key,value in p.elect_sec_skills.items():
                            if list(p.elect_sec_skills.keys())[-1] == key:
                                sec_elect_desc += key + ': ' + str(value)
                            else:
                                sec_elect_desc += key + ': ' + str(value) + ', '
                    else:
                        sec_elect_desc += 'None'
                    menu_dict['desc'][p.name] = 'Years of training remaining: ' + str(years) + '\n' + prim_desc + '\n' + sec_desc + '\n' + prim_elect_desc + '\n' + sec_elect_desc + '\n' + prof_str + '\n' + skill_str
    return menu_dict

def allowed_profs(curr_actor, roll=0) -> set:
    #Goal: Return a set of valid profs based on social standing, ethnicity, and upbringing
    professions = set()
    u_profs = set()

    if curr_actor.creation_choices.get('social'):
        roll = curr_actor.creation_choices.get('social')

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

    return professions

def prune_profs(curr_actor, professions) -> set:
    #Goal: Prune a set of professions based on attribute prerequisites
    invalid_profs = set()
    prof_objects = set()
    for prof in professions:
        for pr in Profession.__subclasses__():
            p = pr(curr_actor)
            if p.name == prof:
                for key,value in p.prereq_dict.items():
                    if curr_actor.fighter.get_attribute(key) < value:
                        invalid_profs.add(p.name)
    professions -= invalid_profs
    for prof in professions:
        for pr in Profession.__subclasses__():
            p = pr(curr_actor)
            if p.name == prof:
                prof_objects.add(p)

    return prof_objects

def determine_ranks(curr_actor, selected_prof=None) -> (dict, dict):
    #Goal: Return two dicts with profession and level and skill and xp based on profession choices and upbringing/ethnicity
    py_dict = deepcopy(curr_actor.creation_choices.get('professions'))
    prof_dict = {}
    skill_dict = {}
    primary_skills = {}
    secondary_skills = {}
    attrs = curr_actor.creation_choices.get('attributes')
    attr_mods = determine_attr_mods(curr_actor)
    upbringing = curr_actor.fighter.upbringing
    ethnicity = curr_actor.fighter.ethnicity

    for a,d in attr_mods.items():
        attrs[a] += sum(d.values())

    #Add year from selected profession, if present
    if selected_prof is not None:
        if not py_dict.get(selected_prof.name):
            py_dict[selected_prof.name] = 0
        py_dict[selected_prof.name] += 1

    #Determine profession ranks
    for prof_str,years in py_dict.items():
        for pr in Profession.__subclasses__():
            p = pr(curr_actor)
            if prof_str == p.name:
                p.calc_level(attrs,years)
                prof_dict[p.name] = p.level

    #Determine skill levels, taking into account primary/secondary skills as well as free skills
    for s in upbringing.free_skills:
        for sk in Skill.__subclasses__():
            skl = sk(curr_actor)
            if skl.name == s:
                secondary_skills[s] = skl.cost
    for s in ethnicity.free_skills:
        for sk in Skill.__subclasses__():
            skl = sk(curr_actor)
            if skl.name == s:
                secondary_skills[s] += skl.cost
    for p in prof_dict:
        level = prof_dict.get(p)
        for pr in Profession.__subclasses__():
            pro = pr(curr_actor)
            if pro.name == p:
                prof = pro
        for ps,l in prof.base_primary_dict.items():
            for sk in Skill.__subclasses__():
                skl = sk(curr_actor)
                if skl.name == ps:
                    lvl = level-1 + l
                    xp = 0
                    while lvl > 0:
                        xp += lvl * skl.cost
                        lvl -= 1
            if not primary_skills.get(ps):
                primary_skills[ps] = 0
            primary_skills[ps] += xp
            if secondary_skills.get(ps):
                primary_skills[ps] += secondary_skills.get(ps)
                del secondary_skills[ps]
        for ps,l in prof.base_sec_dict.items():
            for sk in Skill.__subclasses__():
                skl = sk(curr_actor)
                if skl.name == ps:
                    xp = 0
                    while l > 0:
                        xp += l * skl.cost
                        l -= 1
            if primary_skills.get(ps):
                primary_skills[ps] += xp
            else:
                if not secondary_skills.get(ps):
                    secondary_skills[ps] = 0
                secondary_skills[ps] += xp

    skill_dict = {**primary_skills,**secondary_skills}

    return prof_dict, skill_dict

def convert_ranks(curr_actor, prof_dict, skill_dict) -> (str,str):
    prof_str = 'Professions and ranks based on selection: '
    skill_str = 'Skills and levels based on selection: '

    if len(prof_dict) == 0:
        prof_str + 'None'
    else:
        for p,y in prof_dict.items():
            for pr in Profession.__subclasses__():
                prof = pr(curr_actor)
                if prof.name == p:
                    prof_str += p + ': ' + prof.title_list[y-1]
                    if list(prof_dict.keys())[-1] != p:
                        prof_str += ', '
    if len(skill_dict) == 0:
        skill_str + 'None'
    else:
        for s,x in skill_dict.items():
            for sk in Skill.__subclasses__():
                skl = sk(curr_actor,x)
                if skl.name == s:
                    skl.set_level()
                    skill_str += s + ': ' + str(skl.level)
                    if list(skill_dict.keys())[-1] != s:
                        skill_str += ', '

    return prof_str, skill_str


def determine_attr_mods(curr_actor) -> dict:
    #Goal: Get all attribute mods based on sex and ethnicity and return them in a dict of dicts
    attr_mods = {} #Dict of dicts in format attr:{ethnicity:mod,sex:mod}
    ethnicity = curr_actor.creation_choices.get('ethnicity')
    for u in get_valid_upbringings(curr_actor, None):
        if u.name == curr_actor.creation_choices.get('upbringing'):
            upbringing = u

    if curr_actor.creation_choices.get('sex') == 'Male':
        for key,value in sex_attr_mods_m.items():
            attr_mods[key] = {}
            attr_mods[key]['sex'] = value

    for e in Ethnicity.getinstances():
        if e.name == ethnicity:
            for key,value in e.attr_mods.items():
                a_name = attr_name_dict.get(key)
                if not attr_mods.get(a_name):
                    attr_mods[a_name] = {}
                attr_mods[a_name]['ethnicity'] = value

    for key,value in u.attr_mods.items():
        a_name = attr_name_dict.get(key)
        if not attr_mods.get(a_name):
            attr_mods[a_name] = {}
        attr_mods[a_name]['upbringing'] = value
    
    return attr_mods