from enums import WeaponTypes, FighterStance, EntityState
from utilities import itersubclasses, clamp
import global_vars



class Weapon:
    def __init__(self, name, skill, attack_mod, parry_mod, parry_ap, stamina, base_ap, damage_type, b_dam, s_dam, p_dam, t_dam, hands = 1, length = 0, weight = 0):
        self.name = name
        self.skill = skill
        self.attack_mod = attack_mod
        self.parry_mod = parry_mod
        self.stamina = stamina
        self.b_dam = b_dam
        self.s_dam = s_dam
        self.p_dam = p_dam
        self.t_dam = t_dam
        self.hands = hands
        self.length = length
        self.weight = weight
        self.damage_type = damage_type
        self.base_ap = base_ap


class Attack():
    def __init__(self, name, attack_mod, parry_mod, stamina, b_dam, s_dam, p_dam, t_dam, hands, damage_type, base_ap, 
        hand = True, length = 0, side_restrict = True, restricted_locs = [], allowed_angles_r = [0,1,2,3,4,5,6,7,8], allowed_angles_l = [0,1,2,3,4,5,6,7,8]):
        self.name = name
        self.attack_mod = attack_mod
        self.parry_mod = parry_mod
        self.stamina = stamina
        self.b_dam = b_dam
        self.s_dam = s_dam
        self.p_dam = p_dam
        self.t_dam = t_dam
        self.hands = hands
        self.damage_type = damage_type
        self.base_ap = base_ap
        self.hand = hand
        self.length = length
        self.side_restrict = side_restrict #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.restricted_locs = restricted_locs #Locations that can never be targeted with this attack (i.e. foot with uppercut)
        self.allowed_angles_r = allowed_angles_r #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)
        self.allowed_angles_l = allowed_angles_l #Angles that are allowed as an index of angles (0 = N-> S, 7 = NW -> SE, 8 = thrust) (i.e. N->S with an uppercut)

class Guard():
    def __init__(self, name, loc_hit_mods, hit_mod = 0, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = [], rh_default = False, lh_default = False):
        self.name = name
        self.loc_hit_mods = loc_hit_mods #A dict in 'location name':mod format with mods to hit chance based on location
        self.hit_mod = hit_mod
        self.dodge_mod = dodge_mod
        self.parry_mod = parry_mod
        self.req_locs = req_locs #A list of locs required to be funtional to use the guard
        self.auto_block = auto_block #A list of locations autoblocked
        self.rh_default = rh_default
        self.lh_default = lh_default

class Maneuver():
    def __init__(self):
        self.name = ''
        self.desc = ''
        self.skill = [] #List of skills that can use this maneuver
        self.loc_idx = None
        self.succeed_desc = ''
        self.fail_desc = ''
        self.aggressor = None #Used to indicate person controlling hold
        self.mnvr_mod = 0 #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = 0 
        self.reversal_mod = 0 
        self.dodgeable = True
        self.reversible = False
        self.counterable = False
        self.counters = [] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = False #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 0
        self.random_dam_loc = False
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 1
        self.locs_allowed = set() #Locs maneuver can target
        self.restricted_locs = []
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 0
        self.hand = True
        self.length = 0
        self.side_restrict = True #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = set() #LOcs immobilized on the aggressor
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = True #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = False #If inv moved, is defender thrown back? Forward if false.
        self.throw_force = 0 #Additional force (beyond gravity) imparted as damage in a throw
        self.agg_stance_pre = [FighterStance.standing, FighterStance.sitting, FighterStance.kneeling, FighterStance.prone] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing, FighterStance.sitting, FighterStance.kneeling, FighterStance.prone] #An 'or' list of stances necessary for the target of the maneuver
        
class Unarmed(Weapon):
    def __init__(self):
        super()
        self.name = 'Unarmed'
        self.skill = 'brawling'
        self.attack_mod = 0
        self.parry_mod = 0
        self.parry_ap = 10
        self.stamina = 0
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 1
        self.length = 0
        self.weight = 0
        self.damage_type = 'b'
        self.base_ap = 0
        #Attacks below
        #self, name, attack_mod, parry_mod, stamina, b_dam, s_dam, p_dam, t_dam, hands, damage_type, base_ap, 
        #hand = True, length = 0, side_restrict = True, restricted_locs = [], restricted_angles = []
        self.jab = Attack("Jab/Cross", 0, 0, 1, .5, 0, 0, 0, 1, 'b', 10, True, 0, True, [0], [8], [8])
        self.haymaker = Attack("Haymaker", -20, +20, 3, .7, 0, 0, 0, 1, 'b', 25, True, 0, True, [27,28], [2,3,4], [5,6,7])
        self.hook = Attack("Hook", -10, +10, 2, .6, 0, 0, 0, 1, 'b', 20, True, 0, True, [27,28], [2,3,4], [5,6,7])
        self.uppercut = Attack("Uppercut", -20, 0, 2, .6, 0, 0, 0, 1, 'b', 20, True, 0, True, [2,3,4,7,8,11,12,15,16,19,20,21,22,23,24,25,26,27,28], [3,4], [5,4])
        self.hammerfist = Attack("Hammer Fist", 0, -20, 1, .4, 0, 0, 0, 1, 'b', 10, True, 0, True, [2,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28], [7,0,1], [7,0,1])
        self.elbow = Attack("Elbow Strike", -20, -20, 1, .6, 0, 0, 0, 1, 'b', 10, True, -14, True, [], [0,1,2,3], [0,7,6,5])
        self.frontkick = Attack("Front Kick", -10, +10, 2, .6, 0, 0, 0, 1, 'b', 15, False, 0, False, [0,27,28], [8], [8])
        self.roundhousekick = Attack("Roundhouse Kick", +10, +20, 5, .8, 0, 0, 0, 1, 'b', 30, False, 0, False, [0,27,28], [2,3], [5,6])
        self.sidekick = Attack("Side Kick", -20, +10, 3, .7, 0, 0, 0, 1, 'b', 20, False, 0, False, [0,27,28], [8], [8])
        self.stomp = Attack("Stomp", +20, 0, 1, .4, 0, 0, 0, 1, 'b', 10, False, 0, False, [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26], [0], [0])
        self.knee = Attack("Knee Strike", -30, -10, 1, .4, 0, 0, 0, 1, 'b', 15, False, -18, False, [0,2,27,28], [3,4], [4,5])
        self.base_attacks = [self.jab, self.haymaker, self.hook, self.uppercut, self.hammerfist, self.elbow, self.frontkick, self.roundhousekick, self.sidekick, self.stomp, self.knee]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.conventional = Guard('Conventional', {'Face': -10, 'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': 20}, 0, 0, 0, [7,8,11,12,15,16], [9,10], 
                                True)
        self.southpaw = Guard('Southpaw', {'Face': -10, 'Neck': -40, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': 20}, 0, 0, 0, [7,8,11,12,15,16],[9,10], 
                                False, True)
        self.high = Guard('High', {'Scalp': -20, 'Face': -30, 'Neck': -60, 'R Chest': -40, 'L Chest': -40, 'R Ribs': -20, 'L Ribs': -20, 'R Elbow': 20, 'L Elbow': 20, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20}, -10, -20, 20, [7,8,11,12,15,16], [0,1,2,5,6])
        self.low = Guard('Low', {'Scalp': 20, 'Face': -10, 'Neck': -80, 'R Chest': -80, 'L Chest': -80, 'R Ribs': -80, 'L Ribs': -80, 'R Forearm': 20, 
                                'L Forearm': 20, 'R Hand': 20, 'L Hand': 20, 'R Abdomen': -60, 'L Abdomen': -60}, -20, -10, 20, [7,8,11,12,15,16], [2,5,6,9,10,13,14])
        self.half = Guard('Half', {'Neck': -10, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'R Ribs': -60, 
                                'R Elbow': -60, 'R Forearm': -60, 'R Hand': -60}, 20, 20, 0, [7,11,15], [9])
        self.guards = [self.conventional, self.southpaw, self.high, self.low, self.half]
        self.base_maneuvers = [Headbutt, Tackle, Push, Trip, Bearhug, Collar_Tie, Strangle_Hold, Reap, Sacrifice_Throw]
        self.maneuvers = []                        

class Long_Sword_Steel(Weapon):
    def __init__(self):
        super()
        self.name = 'Steel Long Sword'
        self.skill = 'long_sword'
        self.attack_mod = -20
        self.parry_mod = 30
        self.parry_ap = 10
        self.parry_mult = 3
        self.parry_threshold = 3000
        self.parry_durability = 30000
        self.stamina = 0
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 1
        self.length = 47
        self.weight = 2.8
        self.min_str_1h = 75
        self.damage_type = 's'
        self.base_ap = 0
        #Attacks below
        #self, name, attack_mod, parry_mod, stamina, b_dam, s_dam, p_dam, t_dam, hands, damage_type, base_ap, 
        #hand = True, length = 0, side_restrict = True, restricted_locs = [], allowed_angles_r = [], allowed_angles_l = []
        self.slash = Attack("Slash", -20, 20, 6, 0, 25, 0, 0, 1, 's', 30, True, 47, False, [], [0,1,2,3,4,5,6,7], [0,1,2,3,4,5,6,7])
        self.stab = Attack("Stab", -10, -10, 3, 0, 0, 100, 0, 1, 'p', 20, True, 47, False, [0], [8], [8])
        self.pommel = Attack("Pommel Strike", 0, -10, 3, 1, 0, 0, 0, 1, 'b', 20, True, 0, True, [], [0,8], [0,8])
        self.base_attacks = [self.slash, self.stab, self.pommel]
        self.attacks = []
        #Guards below
        #self, name, loc_hit_mods, dodge_mod = 0, parry_mod = 0, req_locs = [], auto_block = []
        self.ox_r = Guard('Hanging, Right-handed', {'Neck': -60, 'R Shoulder': -80, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': 20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -60, 
                                'R Shin': -80, 'R Foot': -80, 'L Knee': 30, 'L Shin': 20, 'R Hip': -80, 'L Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20])
        self.ox_l = Guard('Hanging, Left-handed', {'Neck': -60, 'L Shoulder': -80, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': 20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -60, 
                                'L Shin': -80, 'L Foot': -80, 'R Knee': 30, 'R Shin': 20, 'L Hip': -80, 'R Hip': -20}, 0, 0, 20, [7,8,11,12,15,16,19,20], [19,20])
        self.plow_r = Guard('Middle, Right-handed', {'Neck': -20, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -60, 'Up R Arm': -60, 'Up L Arm': 20, 'R Ribs': -60, 
                                'L Ribs': -20, 'R Elbow': -60, 'L Elbow': 20, 'R Forearm': -60, 'L Forearm': 20, 'R Hand': -60, 'L Hand': -60, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': -40, 'R Abdomen': -80, 'R Hip': -80, 'L Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [4,6,8,10,12,14,16,19,20], True)
        self.plow_l = Guard('Middle, Left-handed', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'R Ribs': -20, 'L Elbow': -60, 'R Elbow': 20, 'L Forearm': -60, 'R Forearm': 20, 'L Hand': -60, 'R Hand': -60, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -80, 'L Hip': -80, 'R Hip': -40}, 10, 20, 0, [7,8,11,12,15,16,19,20], 
                                [3,5,7,9,11,13,15,19,20], False, True)
        self.low = Guard('Low', {'Neck': -20, 'L Shoulder': -60, 'R Shoulder': 20, 'L Chest': -60, 'Up L Arm': -60, 'Up R Arm': 20, 'L Ribs': -60, 
                                'L Elbow': -40, 'R Elbow': 20, 'L Forearm': -20, 'R Forearm': 20, 'L Thigh': -60, 'L Knee': -80, 
                                'L Shin': -100, 'L Foot': -100, 'R Knee': 30, 'R Shin': 20, 'R Abdomen': -40, 'L Abdomen': -20, 'L Hip': -80, 'R Hip': -40}, 0, 30, -10, [7,8,11,12,15,16,19,20], 
                                [23,24,25,26,27,28])
        self.high = Guard('High', {'Neck': -40, 'R Shoulder': -60, 'L Shoulder': 20, 'R Chest': -20, 'L Chest': 20, 'Up R Arm': -20, 'Up L Arm': 40, 'R Ribs': -20, 
                                'L Ribs': 20, 'L Elbow': 40, 'R Forearm': -20, 'L Forearm': 20, 'R Hand': -20, 'L Hand': -20, 'R Thigh': -60, 'R Knee': -80, 
                                'R Shin': -100, 'R Foot': -100, 'L Knee': 30, 'L Shin': 20, 'L Abdomen': 20, 'R Abdomen': -20, 'R Hip': -80, 'L Hip': -20}, 20, 10, 10, [7,8,11,12,15,16,19,20], 
                                [0,1])
        self.guards = [self.ox_l, self.ox_r, self.plow_l, self.plow_r, self.low, self.high]
        self.base_maneuvers = []
        self.maneuvers = [] 

class Headbutt(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Head Butt'
        self.desc = ''
        self.skill = ['brawling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' headbutts ' + target.name
        self.fail_desc = aggressor.name + ' attempts to headbutt ' + target.name + ', but fails'
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = -30 #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = -10
        self.escape_mod = 0 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = False
        self.counters = [] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.stamina = 1
        self.b_dam = .7
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 1
        self.locs_allowed = set([0,1,2,3,4]) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = False
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = set() #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails

class Tackle(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Tackle'
        self.desc = ''
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' tackles ' + target.name + ', forcing both to the ground. '
        self.fail_desc = aggressor.name + ' attempts to tackle ' + target.name + ', but fails. ' + ('He ' if aggressor.fighter.male else 'She ') + 'falls to the ground. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = 20 #Mod to initial roll
        self.counter_mod = -10 #Mod to counter
        self.dodge_mod = -10
        self.escape_mod = 0 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = True
        self.counters = [Trip, Push, Hip_Throw, Shoulder_Throw, Reap, Sacrifice_Throw] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.stamina = 5
        self.random_dam_loc = True
        self.b_dam = .4
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = set(range(0-27)) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 40
        self.hand = True
        self.length = aggressor.fighter.height
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = set() #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = FighterStance.prone #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = FighterStance.prone #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = FighterStance.prone #Stance the aggressor is in if the maneuver fails
        self.agg_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the target of the maneuver

class Push(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Push'
        self.desc = ''
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' pushes ' + target.name + ', forcing ' + ('him ' if aggressor.fighter.male else 'her ') + 'back. '
        self.fail_desc = aggressor.name + ' attempts to push ' + target.name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = 40 #Mod to initial roll
        self.counter_mod = -20 #Mod to counter
        self.dodge_mod = -20
        self.escape_mod = 0 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = True
        self.counters = [Hip_Throw, Shoulder_Throw, Sacrifice_Throw, Limb_Capture] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.stamina = 2
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = set(range(1-11)) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = set() #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = ((10-self.loc_idx)*-10) - (aggressor.fighter.pwr - 100)
        self.pain_check = False 
        self.balance_check = True
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = True #Used to block movement
        self.inv_move = True #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.
        self.agg_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the target of the maneuver

class Trip(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Trip'
        self.desc = ''
        self.skill = ['brawling','wrestling','martial_arts']
        self.succeed_desc = aggressor.name + ' trips ' + target.name + '. '
        self.fail_desc = aggressor.name + ' attempts to trip ' + target.name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = -20 #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = -10
        self.escape_mod = 0 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = True
        self.counters = [Hip_Throw, Shoulder_Throw, Sacrifice_Throw, Headbutt, Collar_Tie] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.stamina = 1
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 0
        self.locs_allowed = set(range(23-29)) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = False
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = set() #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = -40 
        self.pain_check = False 
        self.balance_check = True
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = True #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.
        self.agg_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the target of the maneuver

class Bearhug(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Bear Hug'
        self.desc = ''
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' grabs ' + target.name + ' in a bear hug, pinning ' + ('him ' if aggressor.fighter.male else 'her ') + 'arms and squeezing. '
        self.fail_desc = aggressor.name + ' attempts to grab ' + target.name + ' in a bear hug, but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = 10 #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = 0 
        self.reversal_mod = 30 
        self.reversible = True
        self.counterable = False
        self.counters = [] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = True
        self.stamina = 6
        
        damage_scalar = .2 * (aggressor.fighter.ss/target.fighter.ss)

        self.b_dam = clamp(damage_scalar, 0, 1)
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = set([5,6,9,10,13,14]) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()

        self.loc_idx = target.fighter.name_location(loc_name)
        
        if  4 < self.loc_idx:
            self.immobilized_locs.update([3,4,7,8])
        if 12 < self.loc_idx:
            self.immobilized_locs.update([11,12,15,16])
        
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = 100*damage_scalar #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = False
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = target.fighter.pwr #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = False #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = False #If inv moved, is defender thrown back? Forward if false.

class Collar_Tie(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Collar Tie'
        self.desc = ''
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' grabs ' + target.name + ' in a collar tie, gaining control of ' + ('his ' if aggressor.fighter.male else 'her ') + 'head and preventing movement. '
        self.fail_desc = aggressor.name + ' attempts to grab ' + target.name + ' in a collar tie, but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold

        skill_mod = aggressor.fighter.best_unarmed_skill - target.fighter.best_unarmed_skill

        self.mnvr_mod = 20 + skill_mod #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = 20
        self.escape_mod = 0 + (-1*skill_mod) 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = True
        self.counters = [Limb_Capture, Shoulder_Throw] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = True #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 1
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = set([1,2]) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set([0,1,2])
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = target.fighter.best_unarmed_skill #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = False #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.

class Limb_Capture(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Limb Capture'
        self.desc = ''
        self.skill = ['brawling','wrestling','martial_arts']
        self.succeed_desc = aggressor.name + ' grabs ' + target.name + '\'s' + loc_name + ', immobilizing it. ' 
        self.fail_desc = aggressor.name + ' attempts to grab ' + target.name + '\'s' + loc_name + ', but' + ('he ' if aggressor.fighter.male else 'she ') + 'fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        
        self.loc_idx = target.fighter.name_location(loc_name)
        pwr_mod = aggressor.fighter.pwr - target.fighter.pwr
        self.immobilized_locs = set()
        self.agg_immob_locs = set()
        if self.loc_idx in global_vars.leg_locs:
            pwr_mod -= 30
            self.dodge_mod = -10
            self.reversible = False
            self.atk_mod_r = -20
            self.atk_mod_l = -20
            if self.loc_idx % 2 == 0:
                for i in global_vars.leg_locs:
                    if i % 2 == 0:
                        self.immobilized_locs.add(i)
                        self.agg_immob_locs.add(20)
            else:
                for i in global_vars.leg_locs:
                    if i % 2 != 0:
                        self.immobilized_locs.add(i)
                        self.agg_immob_locs.add(19)
        else:
            self.dodge_mod = 40
            self.reversible = True
            if self.loc_idx % 2 == 0:
                for i in global_vars.arm_locs:
                    if i % 2 == 0:
                        self.immobilized_locs.add(i)
                        self.agg_immob_locs.add(20)
                        
            else:
                for i in global_vars.arm_locs:
                    if i % 2 != 0:
                        self.immobilized_locs.add(i)
                        self.agg_immob_locs.add(19)

        self.mnvr_mod = pwr_mod #Mod to initial roll
        self.counter_mod = pwr_mod*-1 #Mod to counter
        self.escape_mod = 0 
        self.reversal_mod = 0 
        self.counterable = False
        self.counters = [] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = True #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 1
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 1
        self.locs_allowed = global_vars.leg_locs|global_vars.arm_locs #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 5
        self.hand = True
        self.length = 0
        self.side_restrict = True #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = target.fighter.best_grappling_skill #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = False #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.

class Wind_Choke(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Wind Choke'
        self.desc = ''
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' converts the collar tie on ' + target.name + ' to a wind choke, slowly suffocating ' + ('him.' if aggressor.fighter.male else 'her.')
        self.fail_desc = aggressor.name + ' attempts to convert the collar tie on ' + target.name + ' to a wind choke in order to suffocate' + ('him ' if aggressor.fighter.male else 'her ') + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold

        skill_mod = aggressor.fighter.best_grappling_skill - target.fighter.best_grappling_skill

        self.mnvr_mod = skill_mod #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = 0 + (-1*skill_mod) 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = True
        self.dodgeable = False
        self.counters = [Limb_Capture, Shoulder_Throw] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = True #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 5
        self.b_dam = .2
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = set([2]) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [Collar_Tie] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set([0,1,2])
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = (target.fighter.sta/10)*6 #In rounds till death
        self.stam_drain = 55 #Amount per round
        self.stam_regin = 0 #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = target.fighter.best_unarmed_skill #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = False #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.

class Strangle_Hold(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Strangle Hold'
        self.desc = ''
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' grabs ' + target.name + ' by the throat and begins to throttle ' + ('him.' if aggressor.fighter.male else 'her.')
        self.fail_desc = aggressor.name + ' attempts to grab ' + target.name + ' by the throat, but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = 20 #Mod to initial roll
        self.counter_mod = 20 #Mod to counter
        self.dodge_mod = 10
        self.escape_mod = 30 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = True
        self.counters = [Limb_Capture, Push, Trip, Reap, Shoulder_Throw, Hip_Throw] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = True #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 3
        self.b_dam = .1
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = set([2]) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set([0,1,2])
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = (target.fighter.sta/10)*15 #In rounds till death
        self.stam_drain = 30 #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = target.fighter.best_unarmed_skill #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = False #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.

class Compression_Lock(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Compression Lock'
        self.desc = ''
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' places ' + target.name + '\'s' + loc_name + 'in a compression lock, compressing ' + ('his ' if aggressor.fighter.male else 'her ') + 'muscles and causing intense pain.'
        self.fail_desc = aggressor.name + ' attempts to place a compression lock on ' + target.name + '\'s' + loc_name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = -20 #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = -20 
        self.reversal_mod = -40 
        self.reversible = True
        self.counterable = False
        self.dodgeable = False
        self.counters = [] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = True #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 5
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = global_vars.arm_locs|global_vars.leg_locs #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [Limb_Capture] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        
        self.immobilized_locs = set()
        self.agg_immob_locs = global_vars.arm_locs
        if self.loc_idx in global_vars.leg_locs:
            self.reversible = False
            self.atk_mod_r = -20
            self.atk_mod_l = -20
            self.mnvr_mod = -30 #Mod to initial roll
            if self.loc_idx % 2 == 0:
                for i in global_vars.leg_locs:
                    if i % 2 == 0:
                        self.immobilized_locs.add(i)
            else:
                for i in global_vars.leg_locs:
                    if i % 2 != 0:
                        self.immobilized_locs.add(i)
        else:
            if self.loc_idx % 2 == 0:
                for i in global_vars.arm_locs:
                    if i % 2 == 0:
                        self.immobilized_locs.add(i)         
            else:
                for i in global_vars.arm_locs:
                    if i % 2 != 0:
                        self.immobilized_locs.add(i)

        self.stability_mod = 0 
        self.pain_check = True 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = (aggressor.fighter.best_grappling_skill - target.fighter.will)*-1
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = target.fighter.best_grappling_skill #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = False #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.

class Blood_Choke(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Blood Choke'
        self.desc = ''
        self.skill = ['martial_arts']
        self.succeed_desc = aggressor.name + ' places ' + target.name + ' in a blood choke, cutting off blood flow to ' + ('his ' if aggressor.fighter.male else 'her ') + 'head.'
        self.fail_desc = aggressor.name + ' attempts to execute a blood choke on ' + target.name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = -20 #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = 30 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = True
        self.dodgeable = False
        self.counters = [Limb_Capture, Shoulder_Throw] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = True #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 3
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = set([2]) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [Collar_Tie] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set([0,1,2])
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = (target.fighter.sta/10)*5 #In rounds till death
        self.stam_drain = 55 #Amount per round
        self.stam_regin = 0 #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = target.fighter.best_grappling_skill #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = False #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.

class Joint_Lock(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Joint Lock'
        self.desc = ''
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' places ' + target.name + '\'s' + loc_name + 'in a joint lock, inflicting terrible damage to ' + ('him' if aggressor.fighter.male else 'her') + '.'
        self.fail_desc = aggressor.name + ' attempts to place a joint lock on ' + target.name + '\'s' + loc_name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = -30 #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = -20 
        self.reversal_mod = -60 
        self.reversible = True
        self.counterable = False
        self.dodgeable = False
        self.counters = [] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = True #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 5
        self.b_dam = .8
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = global_vars.arm_locs|global_vars.leg_locs #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [Limb_Capture] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        
        self.immobilized_locs = set()
        self.agg_immob_locs = global_vars.arm_locs
        if self.loc_idx in global_vars.leg_locs:
            self.reversible = False
            self.atk_mod_r = -20
            self.atk_mod_l = -20
            self.mnvr_mod = -40 #Mod to initial roll
            if self.loc_idx % 2 == 0:
                for i in global_vars.leg_locs:
                    if i % 2 == 0:
                        self.immobilized_locs.add(i)
            else:
                for i in global_vars.leg_locs:
                    if i % 2 != 0:
                        self.immobilized_locs.add(i)
        else:
            if self.loc_idx % 2 == 0:
                for i in global_vars.arm_locs:
                    if i % 2 == 0:
                        self.immobilized_locs.add(i)         
            else:
                for i in global_vars.arm_locs:
                    if i % 2 != 0:
                        self.immobilized_locs.add(i)

        self.stability_mod = 0 
        self.pain_check = True 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = (aggressor.fighter.best_grappling_skill - target.fighter.will)*-1
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = target.fighter.best_grappling_skill #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = False #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.

class Neck_Crank(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Neck Crank'
        self.desc = ''
        self.skill = ['martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' begins violently twisting ' + target.name + '\'s' + loc_name + ', inflicting terrible damage to ' + ('his' if aggressor.fighter.male else 'her') + ' spine.'
        self.fail_desc = aggressor.name + ' attempts to twist ' + target.name + '\'s' + loc_name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        skill_mod = aggressor.fighter.best_grappling_skill - target.fighter.best_grappling_skill

        self.mnvr_mod = -20 + skill_mod #Mod to initial roll
        self.counter_mod = 0 + (-1*skill_mod) #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = -20 + (-1*skill_mod) 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = True
        self.dodgeable = False
        self.counters = [Limb_Capture, Shoulder_Throw] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = True #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 5
        self.b_dam = .8
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = set([2]) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [Neck_Crank] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set([0,1,2])
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = target.fighter.best_unarmed_skill #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = False #Used to block movement
        self.inv_move = False #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.

class Reap(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Reap'
        self.desc = ''
        self.skill = ['brawling','wrestling','martial_arts']
        self.succeed_desc = aggressor.name + ' trips ' + target.name + ' while pushing him forcefully. '
        self.fail_desc = aggressor.name + ' attempts to trip ' + target.name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = -30 #Mod to initial roll
        self.counter_mod = 0 #Mod to counter
        self.dodge_mod = -10
        self.escape_mod = 0 
        self.reversal_mod = 0 
        self.reversible = False
        self.counterable = True
        self.counters = [Hip_Throw, Shoulder_Throw, Sacrifice_Throw, Headbutt, Collar_Tie] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.stamina = 3
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 0
        self.locs_allowed = set(range(23-29)) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 10
        self.hand = False
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = set() #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = -60 - (aggressor.fighter.pwr/5)
        self.pain_check = False 
        self.balance_check = True
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = None #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = True #Used to block movement
        self.inv_move = True #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.
        self.agg_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the target of the maneuver

class Sacrifice_Throw(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Sacrifice Throw'
        self.desc = ''
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' lifts ' + target.name + ' off the ground and bodily throws ' + ('him' if aggressor.fighter.male else 'her') + ', landing on top of '  + ('him.' if aggressor.fighter.male else 'her.')
        self.fail_desc = aggressor.name + ' attempts to throw ' + target.name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = aggressor.fighter.pwr - (target.fighter.weight/2) #Mod to initial roll
        self.counter_mod = -20 #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = 0 
        self.reversal_mod = 0
        self.dodgeable = False 
        self.reversible = False
        self.counterable = True
        self.counters = [Trip] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.stamina = 7
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = set(range(1-11)) #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [Bearhug, Collar_Tie, Limb_Capture] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 30
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = FighterStance.prone #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = FighterStance.prone #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = True #Used to block movement
        self.inv_move = True #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = False #If inv moved, is defender thrown back? Forward if false.
        self.throw_force = (aggressor.fighter.ep*.1) + aggressor.fighter.weight #Additional force (beyond gravity) imparted as damage in a throw
        self.agg_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the target of the maneuver

class Hip_Throw(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Hip Throw'
        self.desc = ''
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' lifts ' + target.name + ' off the ground and bodily throws ' + ('him' if aggressor.fighter.male else 'her') + ', using '  + ('his ' if aggressor.fighter.male else 'her ') + 'hip as a fulcrum. '
        self.fail_desc = aggressor.name + ' attempts to throw ' + target.name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = aggressor.fighter.pwr - (target.fighter.weight/4) #Mod to initial roll
        self.counter_mod = -20 #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = 0 
        self.reversal_mod = 0
        self.dodgeable = False 
        self.reversible = False
        self.counterable = True
        self.counters = [Trip, Reap] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.stamina = 3
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 1
        self.locs_allowed = global_vars.arm_locs #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [Limb_Capture] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 20
        self.hand = True
        self.length = 0
        self.side_restrict = True #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = FighterStance.prone #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = True #Used to block movement
        self.inv_move = True #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = False #If inv moved, is defender thrown back? Forward if false.
        self.throw_force = aggressor.fighter.ep*.2  #Additional force (beyond gravity) imparted as damage in a throw
        self.agg_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the target of the maneuver

class Shoulder_Throw(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Shoulder Throw'
        self.desc = ''
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' lifts ' + target.name + ' off the ground and bodily throws ' + ('him' if aggressor.fighter.male else 'her') + ', using '  + ('his ' if aggressor.fighter.male else 'her ') + 'shoulder and back as a fulcrum. '
        self.fail_desc = aggressor.name + ' attempts to throw ' + target.name + ', but fails. '
        self.aggressor = aggressor #Used to indicate person controlling hold
        self.mnvr_mod = aggressor.fighter.pwr - (target.fighter.weight/3) #Mod to initial roll
        self.counter_mod = -20 #Mod to counter
        self.dodge_mod = 0
        self.escape_mod = 0 
        self.reversal_mod = 0
        self.dodgeable = False 
        self.reversible = False
        self.counterable = True
        self.counters = [Trip, Reap] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.stamina = 5
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = global_vars.arm_locs #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [Limb_Capture] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 20
        self.hand = True
        self.length = 0
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor (i.e. both arms in a bear hug)
        self.stability_mod = 0
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = FighterStance.prone #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = None #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = True #Used to block movement
        self.inv_move = True #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = False #If inv moved, is defender thrown back? Forward if false.
        self.throw_force = aggressor.fighter.ep*.3  #Additional force (beyond gravity) imparted as damage in a throw
        self.agg_stance_pre = [FighterStance.standing, FighterStance.kneeling, FighterStance.sitting] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the target of the maneuver

class Single_Leg_Takedown(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Single Leg Takedown'
        self.desc = ''
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' darts quickly in, grabbing ' + target.name + '\'s' + loc_name + ', and jerking it out from under ' + ('him.' if aggressor.fighter.male else 'her.') 
        self.fail_desc = aggressor.name + ' attempts to take down ' + target.name + ', but fails, ending up in a kneeling position. '
        self.aggressor = aggressor #Used to indicate person controlling hold

        skill_mod = aggressor.fighter.best_grappling_skill - target.fighter.best_grappling_skill

        self.mnvr_mod = skill_mod/2 #Mod to initial roll
        self.counter_mod = -30 #Mod to counter
        self.dodge_mod = -1*skill_mod
        self.escape_mod = 0 
        self.reversal_mod = 0 
        self.dodgeable = True
        self.reversible = False
        self.counterable = True
        self.counters = [Collar_Tie] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = False #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 4
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = global_vars.leg_locs #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 20
        self.hand = True
        self.length = aggressor.fighter.mv / 720 #Add how far aggressor can move in .25 seconds to length allowed
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = FighterStance.prone #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = None #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = FighterStance.kneeling #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = True #Used to block movement
        self.inv_move = True #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.
        self.throw_force = 0 #Additional force (beyond gravity) imparted as damage in a throw
        self.agg_stance_pre = [FighterStance.standing, FighterStance.kneeling] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the target of the maneuver

class Double_Leg_Takedown(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Double Leg Takedown'
        self.desc = ''
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' darts quickly in, grabbing ' + target.name + '\'s legs, and jerking them out from under ' + ('him.' if aggressor.fighter.male else 'her.') 
        self.fail_desc = aggressor.name + ' attempts to take down ' + target.name + ', but fails, ending up in a kneeling position. '
        self.aggressor = aggressor #Used to indicate person controlling hold

        skill_mod = aggressor.fighter.best_grappling_skill - target.fighter.best_grappling_skill

        self.mnvr_mod = -20 - skill_mod/4 #Mod to initial roll
        self.counter_mod = -1*(skill_mod/2) #Mod to counter
        self.dodge_mod = -1*(skill_mod/2)
        self.escape_mod = 0 
        self.reversal_mod = 0 
        self.dodgeable = True
        self.reversible = False
        self.counterable = True
        self.counters = [Collar_Tie] #List of maneuvers that can be used to counter this one. 'Or' list.
        self.continuous = False #If True, hold can be held continuously without additional rolls, but still use AP/Sta
        self.stamina = 5
        self.b_dam = 0
        self.s_dam = 0
        self.p_dam = 0
        self.t_dam = 0
        self.hands = 2
        self.locs_allowed = global_vars.leg_locs #Locs maneuver can target
        self.restricted_locs = list(set(range(29)).difference(self.locs_allowed)) #Added because reachable_locs needs it 
        self.prereq = [] #Maneuvers required to be in place before this one can be used. Meant to be an 'or' list
        self.base_ap = 20
        self.hand = True
        self.length = aggressor.fighter.mv / 720 #Add how far aggressor can move in .25 seconds to length allowed
        self.side_restrict = False #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)
        self.immobilized_locs = set()
        self.agg_immob_locs = global_vars.arm_locs #LOcs immobilized on the aggressor
        self.stability_mod = 0 
        self.pain_check = False 
        self.balance_check = False
        self.clarity_reduction = None 
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.state = None #EntityState
        self.escape_uses_skill = True
        self.escape_skill = None #Skill used to escape/reverse.
        self.escape_attr = None #Attr used to escape (i.e. Bear hug) 
        self.stance = FighterStance.prone #Stance the defender is in if the manuever succeeds
        self.agg_suc_stance = FighterStance.kneeling #Stance the aggressor is in if the maneuver succeeds
        self.agg_fail_stance = FighterStance.kneeling #Stance the aggressor is in if the maneuver fails
        self.mv_scalar = 1 #Used to reduce movement as long as the hold is maintained
        self.can_move = True #Used to block movement
        self.inv_move = True #Used to trigger an involuntary move (such as in a push or throw)
        self.inv_move_back = True #If inv moved, is defender thrown back? Forward if false.
        self.throw_force = 0 #Additional force (beyond gravity) imparted as damage in a throw
        self.agg_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the aggressor of the maneuver
        self.target_stance_pre = [FighterStance.standing] #An 'or' list of stances necessary for the target of the maneuver

