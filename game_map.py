
from tcod import map as tcod_map
import numpy as np
import options
from entity import get_blocking_entities_at_location

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


def get_adjacent_cells(entity, entities, game_map) -> list:
    result = []
    combatants = entities.copy()
    if entity in combatants: combatants.remove(entity)
    for x,y in [(entity.x+i,entity.y+j) for i in (-1,0,1) for j in (-1,0,1) if i != 0 or j != 0]:
        if not game_map.walkable[x][y]:
            continue
        #If not blocked, check for entities. 
        else:
            if get_blocking_entities_at_location(combatants, x, y) is None:
                #If nothing blocking square, see if square is in any enemies AOC
                for opponent in combatants:
                    if hasattr(opponent, 'fighter'):
                        if (x,y) in opponent.fighter.aoc:
                            continue
                        else:
                            result.append([x,y])
                    else:
                        result.append([x,y])
    return result

def cells_to_keys(cells, entity) -> (list, list):
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