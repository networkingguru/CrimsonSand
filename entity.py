import math

class Entity:

    def __init__(self, x, y, char, color, name, state, player = False, blocks = False, fighter = None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.player = player
        self.blocks = blocks
        self.fighter = fighter
        self.state = state

        if self.fighter:
            self.fighter.owner = self

    def mod_attribute(self, attribute, amount):
        value = int(getattr(self, attribute))
        if value + amount <= 0: setattr(self, attribute, 0)
        else: 
            value += int(amount)
            setattr(self, attribute, value)


def create_entity_list(entity_list):
    entities = []
    for item in entity_list:
        entities.append(Entity(*item))

    return entities

def fill_player_list(entities):
    players = []
    for entity in entities:
        if entity.player:
            players.append(entity)
    return players

def entity_angle(reference, axis):
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