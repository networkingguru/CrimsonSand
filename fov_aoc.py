
import math
import tcod as libtcodpy
from tcod import map
from enums import GameStates, EntityState



def fov_calc(radius, x, y, percent, start_angle) -> set:
    aoc = set()

    # calc range
    segment = (360/100)*percent
    # calculate endAngle 
    end_angle = segment + start_angle
    
    # Check whether polarradius is less 
    # then radius of circle or not and  
    # Angle is between startAngle and  
    # endAngle or not 
    w_hi = x + radius 
    w_lo = x - radius
    if w_lo < 0: w_lo = 0 

    h_hi = y + radius 
    h_lo = y - radius 
    if h_lo < 0: h_lo = 0 

    for w in range (w_lo, w_hi):
        for h in range (h_lo, h_hi):
            #Ignore initiator square
            if w == x and h == y:
                continue
            else:
                #determine distance between points
                dx = w - x
                dy = h - y

                angle = math.degrees(math.atan2(-dy, dx))

                #deal with boundary
                if angle < 0:
                    angle += 360
                #determine distance of w,h from x,y
                polarradius = math.sqrt((abs(w-x)) * (abs(w-x)) + (abs(y-h)) * (abs(y-h))) 
                if end_angle > 359:
                    overlap_end = end_angle - 360
                    if (angle <= overlap_end and polarradius < radius):
                        aoc.add((w,h))
                if (angle >= start_angle and angle <= end_angle 
                                    and polarradius < radius):
                    aoc.add((w,h))
    return aoc


def change_face(direction, x, y, range = 2, percent = 25) -> set:
    #direction as int, 0-7 starting with N and proceeding clockwise
    player_aoc = set()
    
    if direction == 7: #N
        player_aoc = fov_calc(range,x, y, percent, 45)
    elif direction == 0: #NE
        player_aoc = fov_calc(range,x, y, percent, 0)
    elif direction == 1: #E
        player_aoc = fov_calc(range,x, y, percent, 315)
    elif direction == 2: #SE
        player_aoc = fov_calc(range,x, y, percent, 270)
    elif direction == 3: #S
        player_aoc = fov_calc(range,x, y, percent, 225)
    elif direction == 4: #SW
        player_aoc = fov_calc(range,x, y, percent, 180)
    elif direction == 5: #W
        player_aoc = fov_calc(range,x, y, percent, 135)
    else: #NW
        player_aoc = fov_calc(range,x, y, percent, 90)
    
    return player_aoc

def aoc_check(entities, active_entity) -> list:
    targets = []
    for x, y in active_entity.fighter.aoc:
        for entity in entities:
            if entity == active_entity:
                continue
            elif entity.x == x and entity.y == y:
                if entity.state != entity.state.dead:
                    targets.append(entity)
    return targets


def modify_fov(entity, game_map) -> None:
    fov_area = change_face(entity.fighter.facing, entity.x, entity.y, int(round(entity.fighter.sit/3)), 50) #Contains truncated area based on facing
    entity.fighter.fov_visible.clear()
    for x in range(game_map.width):
        for y in range(game_map.height):
            visible = game_map.fov[x,y]

            wall = not game_map.walkable[x,y]
            #This truncates the FOV to the arc defined by direction
            if visible:
                temp_coords = (x,y)
                if temp_coords not in fov_area:
                    if x != entity.x or y != entity.y:
                        visible = False
            #Showing visible stuff and adding them to the exploration set
            if visible:
                if not (x,y) in entity.fighter.fov_explored: entity.fighter.fov_explored.add((x,y))
                if wall:
                    if not (x,y) in entity.fighter.fov_wall: entity.fighter.fov_wall.add((x,y))
                else:
                    if not (x,y) in entity.fighter.fov_visible: entity.fighter.fov_visible.add((x,y))
                
