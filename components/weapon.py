from enums import WeaponTypes



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
        self.damage_type = 'B'
        self.base_ap = 0
        #self, name, attack_mod, parry_mod, stamina, b_dam, s_dam, p_dam, t_dam, hands, damage_type, base_ap, 
        #hand = True, length = 0, side_restrict = True, restricted_locs = [], restricted_angles = []
        self.jab = Attack("Jab/Cross", 0, 0, 1, .5, 0, 0, 0, 1, 'B', 10, True, 0, True, [0], [8], [8])
        self.haymaker = Attack("Haymaker", -20, +20, 3, .7, 0, 0, 0, 1, 'B', 25, True, 0, True, [27,28], [2,3,4], [5,6,7])
        self.hook = Attack("Hook", -10, +10, 2, .6, 0, 0, 0, 1, 'B', 20, True, 0, True, [27,28], [2,3,4], [5,6,7])
        self.uppercut = Attack("Uppercut", -20, 0, 2, .6, 0, 0, 0, 1, 'B', 20, True, 0, True, [2,3,4,7,8,11,12,15,16,19,20,21,22,23,24,25,26,27,28], [3,4], [5,4])
        self.hammerfist = Attack("Hammer Fist", 0, -20, 1, .4, 0, 0, 0, 1, 'B', 10, True, 0, True, [2,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28], [7,0,1], [7,0,1])
        self.elbow = Attack("Elbow Strike", -20, -20, 1, .6, 0, 0, 0, 1, 'B', 10, True, -14, True, [], [0,1,2,3], [0,7,6,5])
        self.frontkick = Attack("Front Kick", -10, +10, 2, .6, 0, 0, 0, 1, 'B', 15, False, 0, False, [0,27,28], [8], [8])
        self.roundhousekick = Attack("Roundhouse Kick", +10, +20, 5, .8, 0, 0, 0, 1, 'B', 30, False, 0, False, [0,27,28], [2,3], [5,6])
        self.sidekick = Attack("Side Kick", -20, +10, 3, .7, 0, 0, 0, 1, 'B', 20, False, 0, False, [0,27,28], [8], [8])
        self.stomp = Attack("Stomp", +20, 0, 1, .4, 0, 0, 0, 1, 'B', 10, False, 0, False, [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26], [0], [0])
        self.knee = Attack("Knee Strike", -30, -10, 1, .4, 0, 0, 0, 1, 'B', 15, False, -18, False, [0,2,27,28], [3,4], [4,5])
        self.base_attacks = [self.jab, self.haymaker, self.hook, self.uppercut, self.hammerfist, self.elbow, self.frontkick, self.roundhousekick, self.sidekick, self.stomp, self.knee]
        self.attacks = []


weapon_master_list = [Unarmed]