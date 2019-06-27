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
    def __init__(self, name, attack_mod, parry_mod, stamina, b_dam, s_dam, p_dam, t_dam, hands, damage_type, base_ap, atk_type, 
        hand = True, dom_hand = True, length = 0, side_restrict = True):
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
        self.atk_type = atk_type
        self.hand = hand
        self.dom_hand = dom_hand
        self.length = length
        self.side_restrict = side_restrict #Determines if the attack can only hit one side of the enemy (i.e. hook from R hand only hitting left side)


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
        self.punch = Attack('Punch', 0, 40, 1, .5, 0, 0, 0, 1, 'B', 20, WeaponTypes.thrust_and_slash)
        self.kick = Attack('Kick', -20, 0, 2, .75, 0, 0, 0, 0, 'B', 30, WeaponTypes.thrust_and_slash, False)
        self.base_attacks = [self.punch, self.kick]
        self.attacks = []


weapon_master_list = [Unarmed]