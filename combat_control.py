import tcod as libtcodpy
import time
from entity import get_blocking_entities_at_location
from fov_aoc import modify_fov, change_face
from game_messages import Message

def combat_controller(game_map, active_entity, entities, command, logs) -> None:
    fov_recompute = False
    #Dict containing facing direction based on x,y offset
    facing_dict = {(-1,0):6,(-1,1):5,(-1,-1):7,(1,-1):1,(1,1):3,(1,0):2,(0,1):4,(0,-1):0}
    entity = entities[active_entity]
    #Name message logs
    message_log = logs[2]
    status_log = logs[0]
    enemy_log = logs[1]

    if command == 'exit':
        exit(0)
    if command[0] == 'move':
        direction = []
        direction.extend(command[1])
        y_mod = 0
        x_mod = 0
        for xy in direction:
            if xy == 'n':
                y_mod = -1
            if xy == 's':
                y_mod = 1
            if xy == 'w':
                x_mod = -1
            if xy == 'e':
                x_mod = 1
        fx, fy =entity.x + x_mod, entity.y + y_mod
        #Boundary and blocker checking
        if (game_map.width -1 >= fx and game_map.height -1 >= fy):
            if (game_map.walkable[fx, fy] and not (fx < 0  or fy < 0) 
                and get_blocking_entities_at_location(entities, fx, fy) is None):
                entity.mod_attribute('x', x_mod)
                entity.mod_attribute('y', y_mod)
                fov_recompute = True
                entity.fighter.facing = facing_dict.get((x_mod,y_mod))
                message = Message('You move ' + command[1], 'black')
                message_log.add_message(message)

        
    if command[0] == 'spin': 
        direction = command[1]
        if direction == 'ccw': entity.fighter.facing -= 1
        else: entity.fighter.facing += 1
        fov_recompute = True
        #Setting boundaries
        if entity.fighter.facing == 8: entity.fighter.facing = 0
        elif entity.fighter.facing == -1: entity.fighter.facing = 7
        #Change facing
        
    if command[0] == 'spin' or 'move':
        entity.fighter.update_aoc_facing()
        entity.fighter.aoc = change_face(entity.fighter.aoc_facing, entity.x, entity.y, entity.fighter.reach)

            

    if hasattr(entity, 'fighter') and fov_recompute == True:
        #t0 = time.time()
        
        fov_radius = int(round(entity.fighter.sit/5))
        game_map.compute_fov(entity.x, entity.y, fov_radius, True, libtcodpy.FOV_SHADOW)
        modify_fov(entity, game_map)

        # t1 = time.time()
        # total_time = t1 - t0
        # print(total_time)


