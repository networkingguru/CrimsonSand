import tcod as libtcodpy

def combat_controller(game_map, originator, entities, command):


        if command == 'exit':
            exit(0)
        elif command[0] == 'move':
            entity = entities[originator]
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
            #Boundary checking
            if (len(game_map) >= fx and len(game_map[fx]) >= fy) and not game_map.tiles[fx][fy].blocked and not (fx < 0  or fy < 0):
                entity.mod_attribute('x', x_mod)
                entity.mod_attribute('y', y_mod)


