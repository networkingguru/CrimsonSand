import tcod as libtcodpy
from entity import get_blocking_entities_at_location
from fov_aoc import recompute_fov, modify_fov

def combat_controller(game_map, fov_map, active_entity, entities, command) -> None:


        if command == 'exit':
            exit(0)
        elif command[0] == 'move':
            entity = entities[active_entity]
            direction = []
            direction.extend(command[1])
            y, x = direction
            y_mod = 0
            x_mod = 0
            if y == 'n':
                y_mod = -1
            if y == 's':
                y_mod = 1
            if x == 'w':
                x_mod = -1
            if x == 'e':
                x_mod = 1
            fx, fy =entity.x + x_mod, entity.y + y_mod
            #Boundary and blocker checking
            if (game_map.width -1 >= fx and game_map.height -1 >= fy):
                if (not game_map.tiles[fx][fy].blocked and not (fx < 0  or fy < 0) 
                    and get_blocking_entities_at_location(entities, fx, fy) is None):
                    entity.mod_attribute('x', x_mod)
                    entity.mod_attribute('y', y_mod)
            if hasattr(entity, 'fighter'):
                fov_radius = int(round(entity.fighter.sit/5))
                #fov_map = recompute_fov(fov_map, entity.x, entity.y, fov_radius)
                modify_fov(entity, game_map, fov_map)
                

            


