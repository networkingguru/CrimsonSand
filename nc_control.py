from enums import GameStates
from nc_functions import choose_circumstance, choose_sex, choose_ethnicity, roll_social, roll_attr, assign_attr, choose_upbringing, choose_age, choose_profs, choose_skills

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
        menu_dict, game_state, clear = roll_attr(curr_actor, game_state, command)
    elif game_state == GameStates.attributes2:
        menu_dict, game_state, clear = assign_attr(curr_actor, game_state, command)
    elif game_state == GameStates.upbringing:
        menu_dict, game_state, clear = choose_upbringing(curr_actor, game_state, command)
    elif game_state == GameStates.age:
        menu_dict, game_state, clear = choose_age(curr_actor, game_state, command)
    elif game_state == GameStates.profession:
        menu_dict, game_state, clear = choose_profs(curr_actor, game_state, command)
    elif game_state == GameStates.skills:
        menu_dict, game_state, clear = choose_skills(curr_actor, game_state, command)
    elif game_state == GameStates.name:
        pass
    elif game_state == GameStates.shop_w:
        pass
    elif game_state == GameStates.shop_a:
        pass
    elif game_state == GameStates.equip:
        pass


    return menu_dict, game_state, clear