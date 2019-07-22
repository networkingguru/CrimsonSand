import options
from components import fighter, injuries, weapon
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons

entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)
weapons = options.weapons
add_weapons(entities, weapons)



for entity in entities:
    injury = injuries.Light_Scraping(0,entity)
    entity.fighter.injuries.append(injury)
    print(entity.name)

