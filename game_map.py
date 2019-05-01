
from tcod import map as tcod_map
import numpy as np
import options

def array_gen(game_map, blocked) -> np.array:
    blocked_tiles = np.full((game_map.width, game_map.height), True, order='F')
    for (x,y) in blocked:
        blocked_tiles[x,y] = False
    return blocked_tiles

def fill_map(game_map, s_blocked, mv_blocked):
    game_map.transparent[:] = True
    game_map.walkable[:] = True
    for (x,y) in s_blocked:
        game_map.transparent[x,y] = False
    for (x,y) in mv_blocked:
        game_map.walkable[x,y] = False


class Tile:
    """
    A tile on a map. It may or may not be blocked, and may or may not block sight.
    """
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]

        tiles[50][22].blocked = True
        tiles[50][22].block_sight = True
        tiles[51][22].blocked = True
        tiles[51][22].block_sight = True
        tiles[52][22].blocked = True
        tiles[52][22].block_sight = True

        return tiles

def get_adjacent_cells(entity, entities, game_map):
    result = []
    if entity in entities: entities.remove(entity)
    for x,y in [(entity.x+i,entity.y+j) for i in (-1,0,1) for j in (-1,0,1) if i != 0 or j != 0]:
        if game_map.tiles[x][y]:
            if game_map.tiles[x][y].blocked:
                continue
            #If not blocked, check for entities. 
            else:
                if entity.get_blocking_entities_at_location(entities, x, y) is None:
                    #If nothing blocking square, see if square is in any enemies AOC
                    for entity in entities:
                        if hasattr(entity, 'fighter'):
                            if [x,y] in entity.fighter.aoc:
                                continue
                            else:
                                result.append([x,y])
                        else:
                            result.append([x,y])
    return result

def cells_to_keys(cells, entity):
    keys = []
    offsets = []
    for cell in cells:
        x,y = cell
        x_offset = x - entity.x
        y_offset = y - entity.y
        offsets.append((x_offset, y_offset))
        if x_offset == 1:
            if y_offset == 1:
                keys.append('c')
            elif y_offset == 0:
                keys.append('d')
            else:
                keys.append('e')
        elif x_offset == 0:
            if y_offset == 1:
                keys.append('x')
            else:
                keys.append('w')
        else:
            if y_offset == 1:
                keys.append('z')
            elif y_offset == 0:
                keys.append('a')
            else:
                keys.append('q')
    return keys, offsets