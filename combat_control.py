import tcod as libtcodpy

class GameControl():
    def __init__(self, game_map, entities, command):
        self.game_map = game_map
        self.entities = entities
        self.command = command