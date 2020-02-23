from enums import GameStates
from nc_functions import choose_circumstance, choose_sex, choose_ethnicity, roll_social

def nc_controller(curr_actor, entities, game_state, command) -> (dict, int, bool):
    clear = False
    menu_dict = {}
    if game_state == GameStates.circumstance:
        menu_dict, game_state, clear = choose_circumstance(curr_actor, game_state, command)
    elif game_state == GameStates.sex:
        menu_dict, game_state, clear = choose_sex(curr_actor, game_state, command)
    elif game_state == GameStates.ethnicity:
        menu_dict, game_state, clear = choose_ethnicity(curr_actor, game_state, command)
    elif game_state == GameStates.social:
        menu_dict, game_state, clear = roll_social(curr_actor, game_state, command)
    elif game_state == GameStates.attributes:
        pass
    elif game_state == GameStates.upbringing:
        pass
    elif game_state == GameStates.age:
        pass
    elif game_state == GameStates.profession:
        pass
    elif game_state == GameStates.shop:
        pass
    elif game_state == GameStates.equip:
        pass


    return menu_dict, game_state, clear