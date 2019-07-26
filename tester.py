import options
import time
from components import fighter, injuries, weapon
from entity import create_entity_list, fill_player_list, add_fighters, add_weapons
from utilities import itersubclasses
from combat_functions import filter_injuries, apply_injuries

entity_list = options.entities
entities = create_entity_list(entity_list)
fighters = options.fighters
add_fighters(entities, fighters)
weapons = options.weapons
add_weapons(entities, weapons)
inj_1 = injuries.Light_Scraping('Face',entities[0],'b')
inj_2 = injuries.Light_Scraping('Face',entities[0],'s')
entities[0].fighter.injuries.append(inj_1)
entities[0].fighter.injuries.append(inj_2)


""" for entity in entities:
    injury = injuries.Light_Scraping(0,entity)
    entity.fighter.injuries.append(injury)
    print(entity.name) """

# for cls in itersubclasses(injuries.Injury):
#     print(cls.__name__)
""" t0 = time.time()
classes = list(itersubclasses(injuries.Injury))

t1 = time.time()
iter_time = t1 - t0
print('Iteration time: ' + str(iter_time))

for cls in classes:
    a = cls('Face',entities[0],'b')
    if 'b' not in a.damage_type and a.severity >= 5 and a.layer == 2:
        print(cls.__name__)

t2 = time.time()
iter_time = t2 - t1
print('Sort time: ' + str(iter_time)) """

t0 = time.time()

valid = filter_injuries(injuries.Injury, 'Face', 'b', 4, 0, entities[0])
apply_injuries(valid, 'Face', entities[0], 'b')
test = entities[0].fighter.injuries

t1 = time.time()
iter_time = t1 - t0
print('Iteration time: ' + str(iter_time))

for t in test:
    print(t.title)