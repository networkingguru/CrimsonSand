from enums import GameStates, MenuTypes
from components.circumstances import Circumstance

def choose_circumstance(curr_actor, game_state, command) -> (dict, int, bool):
    clear = False
    menu_dict = {}
    menu_desc = {}

    if len(command) != 0:
        for c in Circumstance.getinstances():
            if command.get(c.name):
                curr_actor.circumstance = c
                game_state = GameStates.sex
                clear = True

    else:
        menu_dict = {'type': MenuTypes.page, 'header': 'Choose your starting circumstances', 'options': [], 'mode': False, 'desc': {}}   
        
        for c in Circumstance.getinstances():
            menu_dict['options'].append(c.name)
            menu_desc[c.name] = c.desc

        menu_dict['desc'] = menu_desc


    return menu_dict, game_state, clear