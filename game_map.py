
from tcod import map as tcod_map
import numpy as np
import options
from entity import get_blocking_entities_at_location
from utilities import find_command

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


def get_adjacent_cells(entity, entities, game_map, aoc_cells = True) -> list:
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
                if aoc_cells:
                    for opponent in combatants:
                        if hasattr(opponent, 'fighter'):
                            if (x,y) in opponent.fighter.aoc:
                                continue
                            else:
                                result.append([x,y])
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
        #Below complexity is necessary to find multiple keys in the dict and add them all, along with thier offsets, in correct order
        if x_offset == 1:
            if y_offset == 1:
                n_keys = find_command(options.default_keys, ('move','se'))
                keys += n_keys
                repeat = len(n_keys)
                i = 0
                while i < repeat:
                    offsets.append((x_offset, y_offset))
                    i += 1
            elif y_offset == 0:
                n_keys = find_command(options.default_keys, ('move','e'))
                keys += n_keys
                repeat = len(n_keys)
                i = 0
                while i < repeat:
                    offsets.append((x_offset, y_offset))
                    i += 1
            else:
                n_keys = find_command(options.default_keys, ('move','ne'))
                keys += n_keys
                repeat = len(n_keys)
                i = 0
                while i < repeat:
                    offsets.append((x_offset, y_offset))
                    i += 1
        elif x_offset == 0:
            if y_offset == 1:
                n_keys = find_command(options.default_keys, ('move','s'))
                keys += n_keys
                repeat = len(n_keys)
                i = 0
                while i < repeat:
                    offsets.append((x_offset, y_offset))
                    i += 1
            else:
                n_keys = find_command(options.default_keys, ('move','n'))
                keys += n_keys
                repeat = len(n_keys)
                i = 0
                while i < repeat:
                    offsets.append((x_offset, y_offset))
                    i += 1
        else:
            if y_offset == 1:
                n_keys = find_command(options.default_keys, ('move','sw'))
                keys += n_keys
                repeat = len(n_keys)
                i = 0
                while i < repeat:
                    offsets.append((x_offset, y_offset))
                    i += 1
            elif y_offset == 0:
                n_keys = find_command(options.default_keys, ('move','w'))
                keys += n_keys
                repeat = len(n_keys)
                i = 0
                while i < repeat:
                    offsets.append((x_offset, y_offset))
                    i += 1
            else:
                n_keys = find_command(options.default_keys, ('move','nw'))
                keys += n_keys
                repeat = len(n_keys)
                i = 0
                while i < repeat:
                    offsets.append((x_offset, y_offset))
                    i += 1

    #Add spin
    n_keys = find_command(options.default_keys, ('spin','ccw'))
    keys += n_keys
    repeat = len(n_keys)
    i = 0
    while i < repeat:
        offsets.append((x_offset, y_offset))
        i += 1
    n_keys = find_command(options.default_keys, ('spin','cw'))
    keys += n_keys
    repeat = len(n_keys)
    i = 0
    while i < repeat:
        offsets.append((x_offset, y_offset))
        i += 1
    #Add strafe
    keys += find_command(options.default_keys, 'strafe')
    offsets.append((0,0))
    return keys, offsets