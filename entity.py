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

