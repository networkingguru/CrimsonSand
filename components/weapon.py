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
        self.punch = Attack('Punch', 0, 40, 1, .5, 0, 0, 0, 1, 'B', 20,)
        self.kick = Attack('Kick', -20, 0, 2, .75, 0, 0, 0, 0, 'B', 30, False)
        self.jab = Attack("Jab/Cross", 0, 0, 1, .5, 0, 0, 0, 1, 'B', 10, True, 0, True, [0], [8], [8])
        self.haymaker = Attack("Haymaker", -20, +20, 3, .7, 0, 0, 0, 1, 'B', 25, True, 0, True, [27,28], [2,3,4], [5,6,7])
        self.base_attacks = [self.jab, self.haymaker]
        self.attacks = []


weapon_master_list = [Unarmed]