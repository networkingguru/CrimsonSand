round_num = 1
turn_order = [] #Used to keep track of who has the last action. Needed due to interupt possibilities.
arm_locs = set([7,8,11,12,15,16,19,20]) #Set containing numbers for all arm locations to make code more readable in various places
r_arm_locs = set([7,11,15,19])
l_arm_locs = set([8,12,16,20])
leg_locs = set(range(21,29))
debug = True
debug_time = False