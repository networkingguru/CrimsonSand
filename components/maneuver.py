from enums import WeaponTypes, FighterStance, EntityState
from utilities import itersubclasses, clamp
import global_vars

class Maneuver():
    def __init__(self):
        self.name = ''
        self.desc = ''
        self.skill = [] #List of skills that can use this maneuver
        self.loc_idx = None
        self.succeed_desc = ''
        self.fail_desc = ''
        self.aggressor = None #Used to indicate person controlling hold
        self.target = None 
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
        self.max_dist = 1 #Max distance maneuver can be performed from. Scalar
        self.min_dist = 0 #Min distance maneuver can be performed from. Scalar

class Headbutt(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Head Butt'
        self.desc = 'Head butt ' + target.name
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
        self.desc = 'Rush forward and attept to tackle ' + target.name
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' tackles ' + target.name + ', forcing both to the ground. '
        self.fail_desc = aggressor.name + ' attempts to tackle ' + target.name + ', but fails. ' + ('He ' if target.fighter.male else 'She ') + 'falls to the ground. '
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
        self.max_dist = 1 #Max distance maneuver can be performed from. Scalar
        self.min_dist = .5 #Min distance maneuver can be performed from. Scalar

class Push(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Push'
        self.desc = 'Shove ' + target.name
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' pushes ' + target.name + ', forcing ' + ('him ' if target.fighter.male else 'her ') + 'back. '
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
        self.desc = 'Attempt to hook ' + target.name + '\'s leg and trip ' + ('him' if target.fighter.male else 'her')
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
        self.locs_allowed = set(range(23,29)) #Locs maneuver can target
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
        self.max_dist = .5 #Max distance maneuver can be performed from. Scalar
        self.min_dist = 0 #Min distance maneuver can be performed from. Scalar

class Bearhug(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Bear Hug'
        self.desc = 'Place ' + target.name + ' in a Bear Hug'
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' grabs ' + target.name + ' in a bear hug, pinning ' + ('his ' if target.fighter.male else 'her ') + 'arms and squeezing. '
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
        self.max_dist = .5 #Max distance maneuver can be performed from. Scalar
        self.min_dist = 0 #Min distance maneuver can be performed from. Scalar

class Collar_Tie(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Collar Tie'
        self.desc = 'Grab ' + target.name + ' by the head or neck and place ' + ('him ' if target.fighter.male else 'her ') + 'in a head lock. '
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' grabs ' + target.name + ' in a collar tie, gaining control of ' + ('his ' if target.fighter.male else 'her ') + 'head and preventing movement. '
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
        self.max_dist = .5 #Max distance maneuver can be performed from. Scalar
        self.min_dist = 0 #Min distance maneuver can be performed from. Scalar

class Limb_Capture(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Limb Capture'
        self.desc = 'Grab one of ' + target.name + '\'s limbs and gain control of it. '
        self.skill = ['brawling','wrestling','martial_arts']
        self.succeed_desc = aggressor.name + ' grabs ' + target.name + '\'s' + loc_name + ', immobilizing it. ' 
        self.fail_desc = aggressor.name + ' attempts to grab ' + target.name + '\'s' + loc_name + ', but' + ('he ' if target.fighter.male else 'she ') + 'fails. '
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
        self.desc = 'Execute a wind choke, cutting off ' + target.name + '\'s air flow'
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' converts the collar tie on ' + target.name + ' to a wind choke, slowly suffocating ' + ('him.' if target.fighter.male else 'her.')
        self.fail_desc = aggressor.name + ' attempts to convert the collar tie on ' + target.name + ' to a wind choke in order to suffocate' + ('him ' if target.fighter.male else 'her ') + ', but fails. '
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
        self.desc = 'Grab ' + target.name + '\'s neck with both hands and strangle ' + ('him' if target.fighter.male else 'her')
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' grabs ' + target.name + ' by the throat and begins to throttle ' + ('him.' if target.fighter.male else 'her.')
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
        self.desc = 'Force ' + target.name + '\'s joint to painfully compress the muscles'
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' places ' + target.name + '\'s' + loc_name + 'in a compression lock, compressing ' + ('his ' if target.fighter.male else 'her ') + 'muscles and causing intense pain.'
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
        self.desc = 'Execute a blood choke, cutting off blood flow to ' + target.name + '\'s brain'
        self.skill = ['martial_arts']
        self.succeed_desc = aggressor.name + ' places ' + target.name + ' in a blood choke, cutting off blood flow to ' + ('his ' if target.fighter.male else 'her ') + 'head.'
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
        self.desc = 'Attempt to cause direct damage to ' +target.name + '\'s joint'
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' places ' + target.name + '\'s' + loc_name + 'in a joint lock, inflicting terrible damage to ' + ('him' if target.fighter.male else 'her') + '.'
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
        self.desc = 'Twist ' + target.name + '\'s neck, damaging ' + ('his' if target.fighter.male else 'her') + ' spine'
        self.skill = ['martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' begins violently twisting ' + target.name + '\'s' + loc_name + ', inflicting terrible damage to ' + ('his' if target.fighter.male else 'her') + ' spine.'
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
        self.desc = 'Trip ' + target.name + ' while simultaneously pushing ' + ('him' if target.fighter.male else 'her')
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
        self.locs_allowed = set(range(23,29)) #Locs maneuver can target
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
        self.max_dist = .5 #Max distance maneuver can be performed from. Scalar
        self.min_dist = 0 #Min distance maneuver can be performed from. Scalar

class Sacrifice_Throw(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Sacrifice Throw'
        self.desc = 'Lift and throw both yourself and ' + target.name + ', landing on top of ' + ('him' if target.fighter.male else 'her')
        self.skill = ['brawling','wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' lifts ' + target.name + ' off the ground and bodily throws ' + ('him' if target.fighter.male else 'her') + ', landing on top of '  + ('him.' if target.fighter.male else 'her.')
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
        self.desc = 'Using your hip, throw ' + target.name + ' to the ground'
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' lifts ' + target.name + ' off the ground and bodily throws ' + ('him' if target.fighter.male else 'her') + ', using '  + ('his ' if target.fighter.male else 'her ') + 'hip as a fulcrum. '
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
        self.desc = 'Throw ' + target.name + ' over your shoulder'
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' lifts ' + target.name + ' off the ground and bodily throws ' + ('him' if target.fighter.male else 'her') + ', using '  + ('his ' if target.fighter.male else 'her ') + 'shoulder and back as a fulcrum. '
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
        self.desc = 'Perform a single-leg takedown'
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' darts quickly in, grabbing ' + target.name + '\'s' + loc_name + ', and jerking it out from under ' + ('him.' if target.fighter.male else 'her.') 
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
        self.max_dist = 1 #Max distance maneuver can be performed from. Scalar
        self.min_dist = .5 #Min distance maneuver can be performed from. Scalar

class Double_Leg_Takedown(Maneuver):
    def __init__(self, aggressor, target, loc_name):
        Maneuver.__init__(self)
        self.name = 'Double Leg Takedown'
        self.desc = 'Perform a double-leg takedown'
        self.skill = ['wrestling','martial_arts']
        self.loc_idx = target.fighter.name_location(loc_name)
        self.succeed_desc = aggressor.name + ' darts quickly in, grabbing ' + target.name + '\'s legs, and jerking them out from under ' + ('him.' if target.fighter.male else 'her.') 
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
        self.max_dist = 1 #Max distance maneuver can be performed from. Scalar
        self.min_dist = .5 #Min distance maneuver can be performed from. Scalar