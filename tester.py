import options
from components import fighter, injuries, weapon
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from utilities import itersubclasses

entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)
weapons = options.weapons
add_weapons(entities, weapons)



""" for entity in entities:
    injury = injuries.Light_Scraping(0,entity)
    entity.fighter.injuries.append(injury)
    print(entity.name) """

# for cls in itersubclasses(injuries.Injury):
#     print(cls.__name__)

classes = list(itersubclasses(injuries.Injury))

for cls in classes:
    a = cls('Face',entities[0],'b')
    if 'b' not in a.damage_type:
        print(cls.__name__)