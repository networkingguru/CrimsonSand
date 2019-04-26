class Entity:

    def __init__(self, x, y, char, color, name, state, blocks = False, fighter = None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.state = state

        if self.fighter:
            self.fighter.owner = self


def create_entity_list(entity_list):
    entities = []
    for item in entity_list:
        entities.append(Entity(*item))

    return entities
