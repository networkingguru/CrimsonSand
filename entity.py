import math
from components.fighter import Fighter
from components import weapon

class Entity:

    def __init__(self, x, y, char, color, name, state, player = False, blocks = False, fighter = None, weapons = []):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.player = player
        self.blocks = blocks
        self.fighter = fighter
        self.state = state
        self.weapons = weapons

        if self.fighter:
            self.fighter.owner = self

    def mod_attribute(self, attribute, amount) -> None:
        value = int(getattr(self, attribute))
        if value + amount <= 0: setattr(self, attribute, 0)
        else: 
            value += int(amount)
            setattr(self, attribute, value)

    def add_fighter_component(self, fighter_attrs) -> None:
        attributes, facing, aoc, targets = fighter_attrs[0], fighter_attrs[1], fighter_attrs[2], fighter_attrs[3]
        if len(fighter_attrs) > 4: ai = fighter_attrs[4]
        self.fighter = Fighter(attributes, facing, aoc, targets, ai)

    def add_weapon_component(self, wpn) -> None:
        for w in weapon.weapon_master_list:
            new_wpn = w()
            if wpn == new_wpn.name:
                self.weapons.append(new_wpn)


def create_entity_list(entity_list) -> list:
    entities = []
    for item in entity_list:
        entities.append(Entity(*item))

    return entities

def fill_player_list(entities) -> list:
    players = []
    for entity in entities:
        if entity.player:
            players.append(entity)
    return players

def add_fighters(entities, fighter_list) -> None:
    for entity in entities:
        for fighter in fighter_list:
            if fighter[0] == entity.name:
                del fighter[0]
                entity.add_fighter_component(fighter)

def add_weapons(entities, weapon_dict) -> None:
    for entity in entities:
        if hasattr(entity, 'fighter'):
            wpns = weapon_dict.get(entity.name)
            for wpn in wpns:
                entity.add_weapon_component(wpn)

def entity_angle(reference, axis) -> int:
    dy = axis.y - reference.y
    dx = reference.x - axis.x
    radians = math.atan2(-dy, dx)
    degrees = math.degrees(radians)
    
    
    direction = axis.fighter.facing
    if direction == 0: #N
        angle_adj = 90
    elif direction == 1: #NE
        angle_adj = 45
    elif direction == 2: #E
        angle_adj = 0
    elif direction == 3: #SE
        angle_adj = 315
    elif direction == 4: #S
        angle_adj = 270
    elif direction == 5: #SW
        angle_adj = 225
    elif direction == 6: #W
        angle_adj = 180
    else: #NW
        angle_adj = 135

    #Deal with y axis being upside-down
    degrees -= 360
    degrees = abs(degrees)
    
    degrees -= angle_adj
    #deal with boundary
    if degrees < 0:
        degrees += 360
    if degrees > 359:
        degrees -= 360
    
    return degrees

def get_blocking_entities_at_location(entities, destination_x, destination_y) -> object or None:
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity
    return None