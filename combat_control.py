import tcod as libtcodpy
import time
from entity import get_blocking_entities_at_location
from fov_aoc import modify_fov, change_face
from game_messages import Message
from utilities import inch_conv

def combat_controller(game_map, active_entity, entities, players, command, logs) -> None:
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

        entries = gen_status_panel(players[0])
        status_log.messages.clear()
        for entry in entries:
            status_log.add_message(Message(entry))


def gen_status_panel(player) -> list:
    entries = []
    
    entries.append(str('INTELLECT: \t' + str(round(player.fighter.int))))
    entries.append(str('STRENGTH: \t' + str(round(player.fighter.str))))
    entries.append(str('AGILITY: \t' + str(round(player.fighter.agi))))
    entries.append(str('CONSTITUTION: \t' + str(round(player.fighter.con))))
    entries.append(str('SENSES: \t' + str(round(player.fighter.sens))))
    entries.append(str('APPEARANCE: \t' + str(round(player.fighter.appear))))
    entries.append(str('Height: \t' + inch_conv(player.fighter.height)))
    entries.append(str('Weight: \t' + str(round(player.fighter.weight)) + ' lbs'))
    entries.append(str('Reach: \t\t' + str(round(player.fighter.er)) + '"'))
    entries.append(str('Stamina: \t' + str(round(player.fighter.stamina))))
    entries.append(str('Stamina Regen: \t' + str(round(player.fighter.stamr)) + '/rd'))
    entries.append(str('Vitae: \t\t' + str(round(player.fighter.vitae)) + ' ml'))
    entries.append(str('Vitae Regen:\t' + str(round(player.fighter.vitr)) + ' ml/min'))
    entries.append(str('Move (walk): \t' + str(inch_conv(player.fighter.mv, 1)) + ' sq/rd'))
    entries.append(str('Move (jog): \t' + str(inch_conv(player.fighter.mv*1.5, 1)) + ' sq/rd'))
    entries.append(str('Move (run): \t' + str(inch_conv(player.fighter.mv*2, 1)) + ' sq/rd'))
    entries.append(str('Eff. Power: \t' + str(round(player.fighter.ep)) + ' PSI'))
    entries.append(str('Brawling: \t' + str(player.fighter.brawling) + '%'))
    entries.append(str('Dodge: \t\t' + str(player.fighter.dodge) + '%'))    
    entries.append(str('Deflect: \t' + str(player.fighter.deflect) + '%'))
    entries.append(str('AP: \t\t' + str(player.fighter.ap)))
    entries.append(str('Walk: \t\t' + str(player.fighter.walk_ap)) + ' AP/sq')
    entries.append(str('Jog: \t\t' + str(player.fighter.jog_ap)) + ' AP/sq')
    entries.append(str('Run: \t\t' + str(player.fighter.run_ap)) + ' AP/sq')
    return entries

