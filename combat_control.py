import tcod as libtcodpy

def combat_controller(game_map, originator, entities, command):


        if command == 'exit':
            exit(0)
        elif command[0] == 'move':
            entity = entities[originator]
            direction = []
            direction.extend(command[1])
            y, x = direction
            if y == 'n':
                entity.mod_attribute('y', -1)
            if y == 's':
                entity.mod_attribute('y', 1)
            if x == 'w':
                entity.mod_attribute('x', -1)
            if x == 'e':
                entity.mod_attribute('x', 1)
            return None

