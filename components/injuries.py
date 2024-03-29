from enums import FighterStance, EntityState
import weakref
from utilities import roll_dice

class Injury:
    def __init__(self):
        self.title = None #Use {} (str.format) to ID variables to be replaced at runtime {0}: Damage descriptor
        self.description = None #Use {} (str.format) to ID variables to be replaced at runtime {0}: Entity name {1}: Entity pronoun {2}: Loc name {3}: Damage descriptor
        self.damage_type = None #Acceptable damage types that can cause this injury. Set containing 'b', 's', 'p', or 't'
        self.severity = None #1-6
        self.layer = None #0,1,2 for skin, tissue, bone
        self.prerequisite = None #Reference to another injury that is required before getting this one
        self.locations = None #Set of allowed locations
        self.healable = True 
        self.duplicable = False
        self.max_dupes = 2
        self.pain_check = False 
        self.shock_check = False
        self.balance_check = False
        self.clarity_reduction = None #Positive int
        self.bleed_amount = None #Amount of blood loss
        self.bleed_duration = None #Duration of blood loss
        self.attr_name = None #Names of the attribute to modify. List
        self.attr_amount = None #Amounts to modify attribute. List
        self.loc_reduction = None #Additional amount to reduce the location hits by
        self.loc_max = None #Amount to reduce the location's max hits by. Scalar
        self.severed_locs = None  #locs to sever. set
        self.temp_phys_mod = None
        self.paralyzed_locs = None #set
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.pain_mv_mod = None #Positive int
        self.diseases = None #set of objects
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.mv_mod = None #Scalar
        self.gen_stance = None #Fighterstance
        self.state = None #EntityState

    def description_filler(self, recipient, location, descriptor) -> str:
        name = recipient.name
        if recipient.fighter.male: 
            pronoun1 = ' his '
            pronoun2 = ' him '
            pronoun3 = ' he '
        else: 
            pronoun1 = ' her '
            pronoun2 = ' her '
            pronoun3 = ' she '
        
        description = self.description.format(name, pronoun1, location, descriptor, pronoun2, pronoun3)
        return description

    def damage_descriptor(self, layer, dam_type) -> list:
        if layer == 0:
            if dam_type == 'b':
                descriptor_1 = 'bruised'
                descriptor_2 = 'split'
                descriptor_3 = 'ripped'
            elif dam_type == 's':
                descriptor_1 = 'scraped'
                descriptor_2 = 'gashed'
                descriptor_3 = 'sliced'
            elif dam_type == 'p':
                descriptor_1 = 'punctured'
                descriptor_2 = 'gouged'
                descriptor_3 = 'torn'
            else:
                descriptor_1 = 'scratched'
                descriptor_2 = 'shredded'
                descriptor_3 = 'flayed'
        elif layer == 1:
            if dam_type == 'b':
                descriptor_1 = 'bruised'
                descriptor_2 = 'ruptured'
                descriptor_3 = 'crushed'
            elif dam_type == 's':
                descriptor_1 = 'cut'
                descriptor_2 = 'gashed'
                descriptor_3 = 'cleaved'
            elif dam_type == 'p':
                descriptor_1 = 'punctured'
                descriptor_2 = 'gouged'
                descriptor_3 = 'impaled'
            else:
                descriptor_1 = 'ripped'
                descriptor_2 = 'flayed'
                descriptor_3 = 'shredded'
        else:
            if dam_type == 'b':
                descriptor_1 = 'cracked'
                descriptor_2 = 'shattered'
                descriptor_3 = 'crushed'
            elif dam_type == 's':
                descriptor_1 = 'cut'
                descriptor_2 = 'sliced'
                descriptor_3 = 'severed'
            elif dam_type == 'p':
                descriptor_1 = 'chipped'
                descriptor_2 = 'cracked'
                descriptor_3 = 'split'
            else:
                descriptor_1 = 'scratched'
                descriptor_2 = 'gouged'
                descriptor_3 = 'rent'
        return [descriptor_1, descriptor_2, descriptor_3]
                

class Light_Scraping(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Lightly '+ descriptors[0].capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0} has been lightly {3}. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.severity = 1
        self.locations = set(range(0,29))
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss

class Major_Scraping(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Heavily '+ descriptors[0].capitalize()
        self.prerequisite = Light_Scraping
        self.location = location
        self.recipient = recipient
        self.description = '{0} has been badly {3}. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['s','p','t', 'b'])
        self.severity = 2
        self.duplicable = True
        self.locations = set(range(0,29))
        self.bleed_amount = 20 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss

class Torn_Skin(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        if location == 0: 
            self.title = descriptors[1].capitalize() + ' Scalp'
            self.bleed_amount = 200 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss
        else: 
            self.title = descriptors[1].capitalize() + ' Skin'
            self.bleed_amount = 100 #Amount of blood loss
            self.bleed_duration = 5 #Duration of blood loss
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} has been {3} open and is bleeding. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[1])
        self.damage_type = set(['s','p','t','b'])
        self.severity = 3
        l = list(range(2,29))
        l.append(0)
        self.locations = set(l)

class Severe_Torn_Skin(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        if location == 0: 
            self.title = 'Severely ' + descriptors[1].capitalize() + ' Scalp'
            self.bleed_amount = 200 #Amount of blood loss
            self.bleed_duration = 20 #Duration of blood loss
        else: 
            self.title = 'Severely ' + descriptors[1].capitalize() + ' Skin'
            self.bleed_amount = 100 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} has been severely {3} open and is bleeding profusely. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[1])
        self.damage_type = set(['s','p','t','b'])
        self.severity = 4
        l = list(range(2,29))
        l.append(0)
        self.locations = set(l)

class Partial_Loss_Skin(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        if location == 0: 
            self.title = 'Scalp Paritally ' + descriptors[2].capitalize() + ' Off'
            self.bleed_amount = 1000 #Amount of blood loss
            self.bleed_duration = 40 #Duration of blood loss
            self.description = 'Part of {0}\'s {2} has been {3} off and is bleeding profusely, causing {0}\'s face to sag. '
            self.attr_name = ['fac', 'immune'] #Name of the attribute to modify
            self.attr_amount = [-10, -20] #Amount to modify attribute
        else: 
            self.title = 'Skin Paritally ' + descriptors[2].capitalize() + ' Off'
            self.bleed_amount = 500 #Amount of blood loss
            self.bleed_duration = 20 #Duration of blood loss
            self.description = 'Part of {0}\'s {2} skin has been {3} off and is bleeding profusely. '
            self.attr_name = ['immune'] #Name of the attribute to modify
            self.attr_amount = [-20] #Amount to modify attribute
        self.prerequisite = Severe_Torn_Skin
        self.location = location
        self.recipient = recipient
        self.description = self.description_filler(recipient, self.loc_name, descriptors[2])
        self.damage_type = set(['s','p','t','b'])
        self.severity = 5
        l = list(range(2,29))
        l.append(0)
        self.locations = set(l)
        self.loc_max = .5 #Amount to reduce the location's max hits by. Scalar

class Complete_Loss_Skin(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        if location == 0: 
            self.title = 'Scalp ' + descriptors[2].capitalize() + ' Off'
            self.bleed_amount = 1000 #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss
            self.description = '{0}\'s {2} has been {3} off and is bleeding profusely, causing {0}\'s face to sag severely, permanently disfiguring {4}. '
            self.attr_name = ['fac', 'immune'] #Name of the attribute to modify
            self.attr_amount = [-20, -30] #Amount to modify attribute
        else: 
            self.title = 'Skin ' + descriptors[2].capitalize() + ' Off'
            self.bleed_amount = 1000 #Amount of blood loss
            self.bleed_duration = 20 #Duration of blood loss
            self.description = 'Part of {0}\'s {2} skin has been {3} off and is bleeding profusely. '
            self.attr_name = ['immune'] #Name of the attribute to modify
            self.attr_amount = [-30] #Amount to modify attribute
        self.prerequisite = Partial_Loss_Skin
        self.location = location
        self.recipient = recipient
        self.description = self.description_filler(recipient, self.loc_name, descriptors[2])
        self.damage_type = set(['s','p','t','b'])
        self.severity = 6
        self.healable = False
        l = list(range(2,29))
        l.append(0)
        self.locations = set(l)
        self.loc_max = 0 #Amount to reduce the location's max hits by. Scalar

class Light_Disfigurement(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Light Disfigurement'
        self.location = location
        self.recipient = recipient
        self.description = '{0} has suffered a small facial wound that is disfiguring. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['s','p','t'])
        self.duplicable = True
        self.healable = False
        self.severity = 3
        self.locations = set([1])
        self.bleed_amount = 20 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss
        self.attr_name = ['fac'] #Name of the attribute to modify
        self.attr_amount = [-20] #Amount to modify attribute

class Mild_Disfigurement(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Mild Disfigurement'
        self.location = location
        self.recipient = recipient
        self.description = '{0} has suffered a large facial wound that is disfiguring. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['s','p','t'])
        self.duplicable = True
        self.healable = False
        self.prerequisite = Light_Disfigurement
        self.severity = 4
        self.locations = set([1])
        self.bleed_amount = 30 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss
        self.attr_name = ['fac'] #Name of the attribute to modify
        self.attr_amount = [-30] #Amount to modify attribute

class Broken_Nose(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Broken Nose'
        self.location = location
        self.recipient = recipient
        self.description = '{0} has suffered a broken nose. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['b'])
        self.duplicable = False
        self.healable = False
        self.severity = 4
        self.locations = set([1])
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss
        self.attr_name = ['fac','ts'] #Name of the attribute to modify
        self.attr_amount = [-10,-10] #Amount to modify attribute

class Smashed_Lip(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Smashed Lip'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s lip has been brutally split open. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['b'])
        self.duplicable = False
        
        self.severity = 3
        self.locations = set([1])
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss
        self.attr_name = ['fac'] #Name of the attribute to modify
        self.attr_amount = [-20] #Amount to modify attribute

class Closed_Eye(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Closed Eye'
        self.location = location
        self.recipient = recipient
        self.description = 'The skin around {0}\'s eye has been badly bruised, and has swollen shut. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['b'])
        self.duplicable = True
        
        self.severity = 4
        self.locations = set([1])
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss
        self.attr_name = ['fac','sit'] #Name of the attribute to modify
        self.attr_amount = [-10,-30] #Amount to modify attribute

class Crushed_Eye(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Crushed Eye'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s eye has been crushed, and {5} will never be able to see out of it again. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['b'])
        self.duplicable = True
        self.healable = False
        
        self.severity = 6
        self.locations = set([1])
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss
        self.attr_name = ['fac','sit'] #Name of the attribute to modify
        self.attr_amount = [-30,-60] #Amount to modify attribute

class Nose_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)

        self.title = 'Nose ' + descriptors[2].capitalize() + ' Off'
        self.bleed_amount = 100 #Amount of blood loss
        self.bleed_duration = 100 #Duration of blood loss
        self.description = '{0}\'s nose has been {3} off and is bleeding profusely, permanently disfiguring {4}. '
        self.attr_name = ['fac', 'ts'] #Name of the attribute to modify
        self.attr_amount = [-80, -20] #Amount to modify attribute
        self.location = location
        self.recipient = recipient
        self.description = self.description_filler(recipient, self.loc_name, descriptors[2])
        self.damage_type = set(['s','p','t'])
        self.severity = 6
        self.healable = False
        self.pain_check = True
        self.locations = set([1])
        self.loc_max = .8 #Amount to reduce the location's max hits by. Scalar

class Ear_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)

        self.title = 'Ear ' + descriptors[2].capitalize() + ' Off'
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss
        self.description = '{0}\'s ear has been {3} off, permanently disfiguring {4} and reducing {1} hearing. '
        self.attr_name = ['fac', 'hear'] #Name of the attribute to modify
        self.attr_amount = [-30, -50] #Amount to modify attribute
        self.location = location
        self.recipient = recipient
        self.description = self.description_filler(recipient, self.loc_name, descriptors[2])
        self.damage_type = set(['s','p','t'])
        self.severity = 6
        self.healable = False
        self.duplicable = True
        self.pain_check = True
        self.locations = set([1])
        self.loc_max = .8 #Amount to reduce the location's max hits by. Scalar

class Lip_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)

        self.title = 'Lip ' + descriptors[2].capitalize() + ' Off'
        self.bleed_amount = 30 #Amount of blood loss
        self.bleed_duration = 20 #Duration of blood loss
        self.description = '{0}\'s lip has been {3} off, permanently disfiguring {4}. '
        self.attr_name = ['fac'] #Name of the attribute to modify
        self.attr_amount = [-80] #Amount to modify attribute
        self.location = location
        self.recipient = recipient
        self.description = self.description_filler(recipient, self.loc_name, descriptors[2])
        self.damage_type = set(['s','p','t'])
        self.severity = 6
        self.healable = False
        self.duplicable = True
        self.pain_check = True
        self.locations = set([1])
        self.loc_max = .8 #Amount to reduce the location's max hits by. Scalar

class Eye_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Eye ' + descriptors[2].capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s eye has been ' + descriptors[2] + ', and {5} will never be able to see out of it again. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[2])
        self.damage_type = set(['s','p','t'])
        self.duplicable = True
        self.healable = False
        self.pain_check = True
        
        self.severity = 6
        self.locations = set([1])
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss
        self.attr_name = ['fac','sit'] #Name of the attribute to modify
        self.attr_amount = [-30,-60] #Amount to modify attribute

class Damaged_Facial_Muscles(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = 'Facial Muscle Damage'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s facial muscles have been damaged, resulting in a droop. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 4
        self.locations = set([1])
        self.attr_name = ['fac'] #Name of the attribute to modify
        self.attr_amount = [-10] #Amount to modify attribute

class Facial_Nerve_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = 'Facial Nerve Damage'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s facial nerves have been damaged, resulting in a permanent droop. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 5
        self.locations = set([1])
        self.attr_name = ['fac'] #Name of the attribute to modify
        self.attr_amount = [-10] #Amount to modify attribute

class Tongue_Cut_Out(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = 'Tongue Cut Out'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s tongue has been neatly severed, resulting in {4} being rendered mute. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 6
        self.locations = set([1])
        self.attr_name = ['fac'] #Name of the attribute to modify
        self.attr_amount = [-10] #Amount to modify attribute
        self.diseases = {'Mute'} #set of objects

class Light_Muscle_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Lightly '+ descriptors[0].capitalize() + ' ' + self.loc_name.capitalize() + ' Muscles'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} muscles have been lightly {3}. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 1
        l = list(range(2,11))
        l.extend(range(13,19))
        l.extend([21,22,25,26])
        self.locations = set(l)
        self.temp_phys_mod = -15
        if dam_type in ['s','p','t']:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss
        
class Moderate_Muscle_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = descriptors[1].capitalize() + ' ' + self.loc_name.capitalize() + ' Muscles'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} muscles have been {3}. This damage will restrict {1} movement. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[1])
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 2
        l = list(range(2,12))
        l.extend(range(13,19))
        l.extend([21,22,25,26])
        self.locations = set(l)
        self.temp_phys_mod = -30
        self.prerequisite = Light_Muscle_Damage
        
        if location in [3,4,5,6,7,8,13,14]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.05,-recipient.fighter.get_attribute('ss','max_val')*.05] #Amount to modify attribute
            if location % 2 == 0:
                self.atk_mod_l = -30
            else:
                self.atk_mod_r = -30
        elif location in [15,16]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.02,-recipient.fighter.get_attribute('ss','max_val')*.02] #Amount to modify attribute
            if location % 2 == 0:
                self.atk_mod_l = -30
            else:
                self.atk_mod_r = -30
        elif location in [21,22,25,26]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1] #Amount to modify attribute
            self.mv_mod = .6
            self.pain_mv_mod = 60

        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Heavy_Muscle_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = descriptors[2].capitalize() + ' ' + self.loc_name.capitalize() + ' Muscles'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} muscles have been {3}. Because of this, {5} can no longer move any affected limbs, and will likely never regain full strength. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[2])
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 3
        self.diseases = {'Withered Body Part'}
        self.prerequisite = Moderate_Muscle_Damage
        l = list(range(3,12))
        l.extend(range(13,19))
        l.extend([21,22,25,26])
        self.locations = set(l)
        self.temp_phys_mod = -40

        if location in [3,4,5,6,7,8]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1] #Amount to modify attribute
            if location % 2 == 0:
                self.paralyzed_locs = {8,12,16,20} #set
            else:
                self.paralyzed_locs = {7,11,15,19} #set
        elif location in [15,16]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1] #Amount to modify attribute
            if location == 15:
                self.paralyzed_locs = {15,19} #set
            else:
                self.paralyzed_locs = {16,20} #set
        elif location in [17,18,21,22]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25] #Amount to modify attribute
            if location == 21:
                self.paralyzed_locs = {21,25,27} #set
            else:
                self.paralyzed_locs = {22,26,28} #set
        elif location in [25,26]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25]  #Amount to modify attribute
            if location == 25:
                self.paralyzed_locs = {25,27} #set
            else:
                self.paralyzed_locs = {26,28} #set
        else:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25]  #Amount to modify attribute
            self.diseases = None
        if dam_type in ['s','p','t']:
            self.bleed_amount = 40 #Amount of blood loss
            self.bleed_duration = 3 #Duration of blood loss

class Light_Nerve_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Lightly Damaged ' + self.loc_name.capitalize() + ' Nerves'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} nerves have been damaged, leading to a loss of feeling. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 4
        self.locations = set([7,8,15,16,19,20,21,22,25,26,27,28])
        self.attr_name = ['touch'] #Name of the attribute to modify
        self.attr_amount = [-10] #Amount to modify attribute
        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Moderate_Nerve_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Damaged ' + self.loc_name.capitalize() + ' Nerves'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} nerves have been badly damaged, leading to a severe loss of feeling and muscular strength. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 5
        self.locations = set([7,8,15,16,19,20,21,22,25,26,27,28])
        self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
        self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.2,-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1] #Amount to modify attribute
        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Paralysis(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        self.title = 'Paralysis'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} nerves have been destroyed, leading to paralysis. '
        self.description = self.description_filler(recipient, self.loc_name, descriptors[0])
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 6
        self.locations = set([7,8,15,16,19,20,21,22,25,26,27,28])

        if location in [7,8]:
            self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.3,-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1] #Amount to modify attribute
            if location == 7:
                self.paralyzed_locs = {7,11,15,19} #set
            else:
                self.paralyzed_locs = {8,12,16,20} #set
        elif location in [15,16]:
            self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.3,-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1] #Amount to modify attribute
            if location == 15:
                self.paralyzed_locs = {15,19} #set
            else:
                self.paralyzed_locs = {16,20} #set
        elif location in [21,22]:
            self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.15,-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25] #Amount to modify attribute
            if location == 21:
                self.paralyzed_locs = {21,25,27} #set
            else:
                self.paralyzed_locs = {22,26,28} #set
        elif location in [25,26]:
            self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.1,-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25] #Amount to modify attribute
            if location == 25:
                self.paralyzed_locs = {25,27} #set
            else:
                self.paralyzed_locs = {26,28} #set
        else:
            self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.3,-recipient.fighter.get_attribute('pwr','max_val')*.02,-recipient.fighter.get_attribute('ss','max_val')*.02] #Amount to modify attribute
        
        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Damaged_Artery(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = descriptor.capitalize() + ' Artery in ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} arteries have been {3}, leading to significant bleeding. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = True
        
        self.severity = 3
        self.locations = set([2,7,8,11,12,15,16,21,22,25,26])

        if location == 2:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        if location in [7,8,11,12]:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss
        elif location in [15,16]:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 50 #Duration of blood loss
        elif location in [21,22]:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss
        else:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss

class Heavily_Damaged_Artery(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Artery in ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} arteries have been {3}, leading to severe bleeding. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = True
        self.prerequisite = Damaged_Artery
        
        self.severity = 4
        self.locations = set([2,7,8,11,12,15,16,21,22,25,26])

        if location == 2:
            self.bleed_amount = 40 #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        if location in [7,8,11,12]:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 200 #Duration of blood loss
        elif location in [15,16]:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss
        elif location in [21,22]:
            self.bleed_amount = 40 #Amount of blood loss
            self.bleed_duration = 200 #Duration of blood loss
        else:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 200 #Duration of blood loss
            
class Destroyed_Artery(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' Artery in ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} arteries have been {3}, leading to severe bleeding. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        self.prerequisite = Heavily_Damaged_Artery
        
        self.severity = 5
        self.diseases = {'Gangrene'} #set of objects
        self.locations = set([2,7,8,11,12,15,16,21,22,25,26])
        vitae_dam = max(80, recipient.fighter.vitae*.04)

        if location == 2:
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 10000 #Duration of blood loss
        if location in [7,8,11,12]:
            self.bleed_amount = vitae_dam/2 #Amount of blood loss
            self.bleed_duration = 400 #Duration of blood loss
        elif location in [15,16]:
            self.bleed_amount = vitae_dam/2 #Amount of blood loss
            self.bleed_duration = 200 #Duration of blood loss
        elif location in [21,22]:
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 400 #Duration of blood loss
        else:
            self.bleed_amount = vitae_dam/2 #Amount of blood loss
            self.bleed_duration = 400 #Duration of blood loss

class Destroyed_Windpipe(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' Artery in ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 6
        self.locations = set([2])
        self.diseases = {'Mute'} #set of objects
        self.suffocation = (recipient.fighter.get_attribute('sta')/10)*12 #In rounds till death
        if dam_type in ['s','p','t']:
            self.healable = False
            vitae_dam = max(80, recipient.fighter.vitae*.1)
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 10000 #Duration of blood loss
            self.description = '{0}\'s windpipe has been {3}. In short order, {5} will choke to death on his own blood. '
        else:
            self.description = '{0}\'s windpipe has been {3}. Without medical aid, {5} will choke to death. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Lung_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Lung'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s lung has collapsed, and {5} begins gasping for breath. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([5,6,9,10])
        self.stam_drain = 50 #Amount per round
        self.stam_regin = .5 #Scalar
        if dam_type in ['s','p','t']:
            self.bleed_amount = 5 #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss

class Lung_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' Lung'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s lung has been {3}, and {5} begins gasping for breath. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        self.prerequisite = Lung_Damage
        
        self.severity = 6
        self.locations = set([5,6,9,10])
        self.stam_drain = 100 #Amount per round
        self.stam_regin = .5 #Scalar
        vitae_dam = recipient.fighter.max_vitae*.02
        self.bleed_amount = vitae_dam #Amount of blood loss
        self.bleed_duration = 1000 #Duration of blood loss

class Heart_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = 'Heart ' + descriptor
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s heart has been {3}, and {5} dies instantly. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 6
        self.locations = set([6])
        self.state = EntityState.dead

class Partial_Decapitation(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = 'Partially Decapitated'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} has been {3}, nearly decapitating {4}. Only the spinal column keeps {4} head attatched. Blood spurts rhythmically from the wound, causing death in moments. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 6
        self.locations = set([2])
        self.state = EntityState.dead

class Liver_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Liver'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s liver has been {3}. The pain is excruciating, and the wound bleeds heavily internally. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.description = '{0}\'s liver has been {3}. The pain is excruciating, and the wound bleeds heavily. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 20 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([9,10])
        self.diseases = ['Cirrhosis']
        self.pain_mv_mod = 50
        self.pain_check = True
            
class Pancreas_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Pancreas'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s pancreas has been {3}. The wound bleeds heavily internally. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.description = '{0}\'s pancreas has been {3}. The wound bleeds heavily. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 20 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([9,10])
        self.diseases = ['Pancreatitis']

class Gall_Bladder_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Gall Bladder'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s gall bladder has been {3}. The wound bleeds internally. '
            vitae_dam = recipient.fighter.max_vitae*.005
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.description = '{0}\'s gall bladder has been {3} and is bleeding. '
            vitae_dam = recipient.fighter.max_vitae*.005
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([9])

class Spleen_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Spleen'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s spleen has been {3}. The wound bleeds heavily internally. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.description = '{0}\'s spleen has been {3} and is bleeding heavily. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 200 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([10])
        self.attr_name = ['immune'] #Names of the attribute to modify. List
        self.attr_amount = [(recipient.fighter.get_attribute('immune')*.05)*-1] #Amounts to modify attribute. List

class Spleen_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' Spleen'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s spleen has been {3}. The wound bleeds heavily internally. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.description = '{0}\'s spleen has been {3} and is bleeding heavily. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 200 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        self.prerequisite = Spleen_Damage
        
        self.severity = 6
        self.locations = set([10])
        self.attr_name = ['immune'] #Names of the attribute to modify. List
        self.attr_amount = [(recipient.fighter.get_attribute('immune')*.05)*-1] #Amounts to modify attribute. List

class Stomach_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Stomach'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s stomach has been {3}. The wound bleeds heavily internally and is incredibly painful. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss
        else:
            self.description = '{0}\'s stomach has been {3}. The wound bleeds heavily, and is incredibly painful. '
            vitae_dam = recipient.fighter.max_vitae*.04
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 20 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([6,9])
        self.diseases = ['Stomach perforation']
        self.pain_mv_mod = 60

class Intestinal_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Intestines'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s intestines have been {3}. The wound bleeds internally and will not stop without treatment. '
            vitae_dam = recipient.fighter.max_vitae*.02
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.description = '{0}\'s intestines have been {3}. Blood seeps from the open wound, and the sight of {1} own intestines spilling out causes {4} a large degree of alarm. '
            vitae_dam = recipient.fighter.max_vitae*.02
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.shock_check = True
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 6
        self.locations = set([9,10,13,14])
        self.diseases = ['Intestinal perforation']
        self.pain_mv_mod = 80

class Kidney_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Kidney'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s kidney has been {3}. This causes blinding pain and internal bleeding.'
            self.bleed_amount = 5 #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.description = '{0}\'s kidney has been {3}. This causes blinding pain. '
            self.bleed_amount = 5 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.pain_check = True
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([9,10])
        self.pain_mv_mod = 10

class Kidney_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' Kidney'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s kidney has been {3}. This causes blinding pain and internal bleeding.'
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.description = '{0}\'s kidney has been {3}. This causes blinding pain. '
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 20 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.pain_check = True
        self.healable = False
        self.prerequisite = Kidney_Damage
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 6
        self.locations = set([9,10])
        self.pain_mv_mod = 10

class Reproductive_Organs_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        if recipient.fighter.male: organ = 'testicles'
        else: organ = 'ovaries'
        self.title = descriptor.capitalize() + ' ' + organ.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s '+ organ +' have been {3}. This causes blinding pain.'
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.pain_check = True
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([17,18])
        self.pain_mv_mod = 40

class Reproductive_Organs_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        if recipient.fighter.male: 
            organ = 'testicles'
            self.diseases = ['Castrated']
            result = 'castrated.'
        else: 
            organ = 'ovaries'
            self.diseases = ['Hysterectomy']
            result = 'rendered baren.'
        self.title = descriptor.capitalize() + ' ' + organ.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s '+ organ +' have been {3}. This causes blinding pain.' + '{0} has been ' + result
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.pain_check = True
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        self.prerequisite = Reproductive_Organs_Damaged
        
        self.severity = 6
        self.locations = set([17,18])
        self.pain_mv_mod = 80

class Bladder_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Bladder'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s bladder has been {3}, causing intense pain and internal bleeding.'
            self.bleed_amount = 5 #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss
        else:
            self.description = '{0}\'s bladder has been {3}. This causes intense pain and a continuous flow of urine and blood from the wound. '
            self.bleed_amount = 5 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.pain_check = True
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([17,18])
        self.pain_mv_mod = 40
        self.attr_name = ['immune'] #Names of the attribute to modify. List
        self.attr_amount = [(recipient.fighter.get_attribute('immune')*.1)*-1] #Amounts to modify attribute. List

class Bladder_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' Bladder'
        self.location = location
        self.recipient = recipient
        if dam_type == 'b':
            self.description = '{0}\'s bladder has been {3}, causing intense pain and internal bleeding.'
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.description = '{0}\'s bladder has been {3}. This causes intense pain and a continuous flow of urine and blood from the wound. '
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.pain_check = True
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        self.prerequisite = Bladder_Damage
        
        self.severity = 6
        self.locations = set([17,18])
        self.pain_mv_mod = 60
        self.attr_name = ['immune'] #Names of the attribute to modify. List
        self.attr_amount = [(recipient.fighter.get_attribute('immune')*.3)*-1] #Amounts to modify attribute. List
        self.diseases = ['Cystectomy']

class Light_Tendon_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize() + ' Tendons'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} tendons have been {3}. This damage will restrict {1} movement. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 2
        self.locations = set([11,12,19,20,23,24,27,28])
        self.temp_phys_mod = -20
        self.prerequisite = None

        if dam_type in ['s','p','t']:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Moderate_Tendon_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize() + ' Tendons'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} tendons have been {3}. This damage will restrict {1} movement and reduce {1} strength. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 3
        self.locations = set([11,12,19,20,23,24,27,28])
        self.temp_phys_mod = -30
        self.prerequisite = Light_Tendon_Damage

        if location in [11,12]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.05,-recipient.fighter.get_attribute('ss','max_val')*.05] #Amount to modify attribute
            if location % 2 == 0:
                self.atk_mod_l = -30
            else:
                self.atk_mod_r = -30
        elif location in [19,20]:
            if location % 2 == 0:
                self.atk_mod_l = -30
            else:
                self.atk_mod_r = -30
        else:
            self.pain_mv_mod = 20
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.15,-recipient.fighter.get_attribute('ss','max_val')*.15] #Amount to modify attribute

        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Heavy_Tendon_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 1
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize() + ' Tendons'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} tendons have been {3}. This damage will prevent {2} moving the affected limb until healed. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 4
        self.locations = set([11,12,19,20,23,24,27,28])
        self.temp_phys_mod = -40
        self.prerequisite = Moderate_Tendon_Damage

        if location in [11,12]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1] #Amount to modify attribute
            if location == 11:
                self.paralyzed_locs = {11,15,19} #set
            else:
                self.paralyzed_locs = {12,16,20} #set
        elif location in [19,20]:
            if location == 19:
                self.paralyzed_locs = {19} #set
            else:
                self.paralyzed_locs = {20} #set
        else:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25] #Amount to modify attribute
            self.pain_mv_mod = 40
            if location == 27:
                self.paralyzed_locs = {27} #set
            elif location == 28:
                self.paralyzed_locs = {28} #set
            elif location == 23:
                self.paralyzed_locs = {23,25,27} #set
            else:
                self.paralyzed_locs = {24,26,28} #set
        if dam_type in ['s','p','t']:
            self.bleed_amount = 40 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Finger_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = descriptor.capitalize() + ' Finger'
        self.location = location
        self.recipient = recipient
        self.description = 'One of {0}\'s fingers has been {3}. This damage makes it difficult for {4} to use the affected hand. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.max_dupes = 5
        
        self.severity = 1
        self.locations = set([19,20])

        if location % 2 == 0:
            self.atk_mod_l = -10
        else:
            self.atk_mod_r = -10

        if dam_type in ['s','p','t']:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Toe_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 0
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = descriptor.capitalize() + ' Toe'
        self.location = location
        self.recipient = recipient
        self.description = 'One of {0}\'s toes has been {3}. This damage makes moving painful for {4}. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.max_dupes = 5
        
        self.severity = 1
        self.locations = set([27,28])
        self.pain_mv_mod = 10

        if dam_type in ['s','p','t']:
            self.bleed_amount = 5 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Finger_Bone_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Finger'
        self.location = location
        self.recipient = recipient
        self.description = 'One of {0}\'s fingers has been {3}. This damage makes it impossible to use the finger, which makes it difficult for {4} to use the affected hand. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.max_dupes = 5
        self.prerequisite = Finger_Damaged
        
        self.severity = 3
        self.locations = set([19,20])
        
        if location % 2 == 0:
            self.atk_mod_l = -10
        else:
            self.atk_mod_r = -10

        if dam_type in ['s','p','t']:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Finger_Bone_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' Finger'
        self.location = location
        self.recipient = recipient
        self.description = 'One of {0}\'s fingers has been {3}. This damage makes it impossible to use the finger, which makes it difficult for {4} to use the affected hand. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.healable = False
        self.max_dupes = 5
        self.prerequisite = Finger_Bone_Damaged
        
        self.severity = 4
        self.locations = set([19,20])
        
        if location % 2 == 0:
            self.atk_mod_l = -20
        else:
            self.atk_mod_r = -20

        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 5 #Duration of blood loss

class Toe_Bone_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Toe'
        self.location = location
        self.recipient = recipient
        self.description = 'One of {0}\'s toes has been {3}. This damage makes it very painful to move. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.max_dupes = 5
        self.prerequisite = Toe_Damaged
        
        self.severity = 3
        self.locations = set([27,28])
        self.pain_mv_mod = 10

        if dam_type in ['s','p','t']:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Toe_Bone_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' Toe'
        self.location = location
        self.recipient = recipient
        self.description = 'One of {0}\'s toes has been {3}, making moving extremely painful and affecting {4} balance. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.healable = False
        self.max_dupes = 5
        self.prerequisite = Toe_Bone_Damaged
        
        self.severity = 4
        self.locations = set([27,28])
        self.pain_mv_mod = 20
        self.attr_name = ['bal'] #Names of the attribute to modify. List
        self.attr_amount = [-2] #Amounts to modify attribute. List

        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 5 #Duration of blood loss

class Metacarpals_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Metacarpals'
        self.location = location
        self.recipient = recipient
        self.description = 'The central bones of the hand have been {3}, which makes it difficult for {0} to use the affected hand. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([19,20])
        
        if location % 2 == 0:
            self.atk_mod_l = -30
        else:
            self.atk_mod_r = -30

        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss

class Hand_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        if dam_type in ['s','p']:
            self.description = '{0}\'s ' + self.loc_name + ' has been {3}. Arterial blood spurts from the stump in long jets. '
        else:
            self.description = '{0}\'s ' + self.loc_name +' has been {3}. Blood pours from the crevases of the mangled appendage. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        self.pain_check = True
        
        self.severity = 6
        self.locations = set([19,20])
        
        self.paralyzed_locs = set([location])
        self.severed_locs = set([location])

        if dam_type in ['s','p']:
            self.bleed_amount = 25 #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
        else:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss

class Metatarsals_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Metatarsals'
        self.location = location
        self.recipient = recipient
        self.description = 'The central bones of the foot have been {3}, which makes it very difficult for {0} to walk. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 5
        self.locations = set([27,28])
        self.pain_mv_mod = 50
        self.mv_mod = .6

        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss

class Foot_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        if dam_type in ['s','p']:
            self.description = '{0}\'s ' + self.loc_name + ' has been {3}. Blood drips from the stump. '
        else:
            self.description = '{0}\'s ' + self.loc_name +' has been {3}. Blood pours from the crevases of the mangled appendage. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 6
        self.locations = set([27,28])
        
        self.paralyzed_locs = set([location])
        self.severed_locs = set([location])
        self.balance_check = True
        self.pain_check = True
        self.attr_name = ['bal'] #Names of the attribute to modify. List
        self.attr_amount = [(recipient.fighter.get_attribute('bal')*.6)*-1] #Amounts to modify attribute. List

        if dam_type in ['s','p']:
            self.bleed_amount = 15 #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss
        else:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 50 #Duration of blood loss

class Light_Concussion(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = 'Light Concussion'
        self.location = location
        self.recipient = recipient
        self.description = 'The blow to {0}\'s ' + self.loc_name + ' has mildly concussed {4}, making {4} a little dizzy and disoriented. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 2
        self.locations = set([0,1])
        self.shock_check = True
        self.balance_check = True
        self.clarity_reduction = 10 #Positive int

        if dam_type in ['s','p','t']:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Moderate_Concussion(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = 'Moderate Concussion'
        self.location = location
        self.recipient = recipient
        self.description = 'The blow to {0}\'s ' + self.loc_name + ' has concussed {4}, making {4} dizzy and disoriented. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.prerequisite = Light_Concussion
        
        self.severity = 3
        self.locations = set([0,1])
        self.shock_check = True
        self.balance_check = True
        self.clarity_reduction = 20 #Positive int

        if dam_type in ['s','p','t']:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Severe_Concussion(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = 'Severe Concussion'
        self.location = location
        self.recipient = recipient
        self.description = 'The blow to {0}\'s ' + self.loc_name + ' has severely concussed {4}, making {4} extremely dizzy and disoriented. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.prerequisite = Moderate_Concussion
        
        self.severity = 4
        self.locations = set([0,1])
        self.shock_check = True
        self.balance_check = True
        self.clarity_reduction = 40 #Positive int

        if dam_type in ['s','p','t']:
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Brain_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = 'Brain Damage'
        self.location = location
        self.recipient = recipient
        self.description = 'The blow to {0}\'s ' + self.loc_name + ' has caused something to rupture deep inside {4} brain, leading to an instantanious coma and brain damage. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 5
        self.locations = set([0,1])
        self.state = EntityState.unconscious
        self.gen_stance = FighterStance.prone
        roll = roll_dice(1,100)
        if roll <= 30: 
            self.description + str('If ' + ('he ' if recipient.fighter.male else 'she ') + 'survives, ' +
                ('he ' if recipient.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
            self.attr_name = ['log','wis'] #Names of the attribute to modify. List
            self.attr_amount = [-40,-40] #Amounts to modify attribute. List
        elif roll <= 60:
            self.description + str('If ' + ('he ' if recipient.fighter.male else 'she ') + 'survives, ' +
                ('he ' if recipient.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
            self.attr_name = ['log','wis','mem','comp','con','cre','men'] #Names of the attribute to modify. List
            self.attr_amount = [-10,-10,-10,-10,-10,-10,-10] #Amounts to modify attribute. List
        elif roll <= 70:
            self.description + str('If ' + ('he ' if recipient.fighter.male else 'she ') + 'survives, ' +
                ('he ' if recipient.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
            self.attr_name = ['sit'] #Names of the attribute to modify. List
            self.attr_amount = [-recipient.fighter.get_attribute('sit','max_val')] #Amounts to modify attribute. List
            self.diseases = ['Blind']
        elif roll <= 80:
            self.description + str('If ' + ('he ' if recipient.fighter.male else 'she ') + 'survives, ' +
                ('he ' if recipient.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
            self.attr_name = ['hear'] #Names of the attribute to modify. List
            self.attr_amount = [-recipient.fighter.get_attribute('hear','max_val')] #Amounts to modify attribute. List
            self.diseases = ['Deaf']
        elif roll <= 90:
            self.description + str('If ' + ('he ' if recipient.fighter.male else 'she ') + 'survives, ' +
                ('he ' if recipient.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
            self.attr_name = ['ts'] #Names of the attribute to modify. List
            self.attr_amount = [-recipient.fighter.get_attribute('ts','max_val')] #Amounts to modify attribute. List
            self.diseases = ['Ageusia']
        elif roll <= 95:
            self.description + str('If ' + ('he ' if recipient.fighter.male else 'she ') + 'survives, ' +
                ('he ' if recipient.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
            self.diseases = ['Epilepsy']
        elif roll <= 97:
            self.description + str('If ' + ('he ' if recipient.fighter.male else 'she ') + 'survives, ' +
                ('he ' if recipient.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
            loc_roll = roll_dice(1,4)
            if loc_roll == 1: 
                self.paralyzed_locs = set([7, 11, 15, 19])
                self.attr_name = ['ss','pwr'] #Names of the attribute to modify. List
                self.attr_amount = [-recipient.fighter.get_attribute('ss','max_val')*.1,-recipient.fighter.get_attribute('pwr','max_val')*.1] #Amounts to modify attribute. List
            if loc_roll == 2: 
                self.paralyzed_locs = set([8, 12, 16, 20])
                self.attr_name = ['ss','pwr'] #Names of the attribute to modify. List
                self.attr_amount = [recipient.fighter.get_attribute('ss')*.1,recipient.fighter.get_attribute('pwr')*.1] #Amounts to modify attribute. List
            if loc_roll == 3: 
                self.paralyzed_locs = set([21, 23, 25, 27])
                self.attr_name = ['ss','pwr'] #Names of the attribute to modify. List
                self.attr_amount = [-recipient.fighter.get_attribute('ss','max_val')*.25,-recipient.fighter.get_attribute('pwr','max_val')*.25] #Amounts to modify attribute. List
                self.mv_mod = .4
            if loc_roll == 4: 
                self.paralyzed_locs = set([22, 24, 26, 28])
                self.attr_name = ['ss','pwr'] #Names of the attribute to modify. List
                self.attr_amount = [-recipient.fighter.get_attribute('ss','max_val')*.25,-recipient.fighter.get_attribute('pwr','max_val')*.25] #Amounts to modify attribute. List
                self.mv_mod = .4
        elif roll == 98:
            #Below randomly paralizes 2 limbs
            self.description + str('If ' + ('he ' if recipient.fighter.male else 'she ') + 'survives, ' +
                ('he ' if recipient.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
            i = 0
            limbs = [[7, 11, 15, 19], [8, 12, 16, 20], [21, 23, 25, 27], [22, 24, 26, 28]]
            p_limbs = []
            mult = 0
            m_mod = 1
            while i < 2:
                loc_roll = roll_dice(1,len(limbs))-1
                p_limbs.extend(limbs.pop(loc_roll))
                i += 1
            self.paralyzed_locs = set(p_limbs)
            if 21 in self.paralyzed_locs:
                mult += .25
                m_mod -= .4
            if 22 in self.paralyzed_locs:
                mult += .25
                m_mod -= .4
            if 7 in self.paralyzed_locs:
                mult += .1
            if 8 in self.paralyzed_locs:
                mult += .1

            self.attr_name = ['ss','pwr'] #Names of the attribute to modify. List
            self.attr_amount = [-recipient.fighter.get_attribute('ss','max_val')*mult,-recipient.fighter.get_attribute('pwr','max_val')*mult] #Amounts to modify attribute. List
            if m_mod < 1: self.mv_mod = m_mod

        elif roll == 99:
            self.description + str('If ' + ('he ' if recipient.fighter.male else 'she ') + 'survives, ' +
                ('he ' if recipient.fighter.male else 'she ') + 'will be permanently debilitated in some way. ')
            self.diseases = ['Quadriplegic']
            self.paralyzed_locs = set([7, 11, 15, 19, 8, 12, 16, 20, 21, 23, 25, 27, 22, 24, 26, 28])
            self.mv_mod = 0
        else: 
            self.description + str(recipient.name + 'begins doing the dead man\'s shuffle, foam and blood bubbling from ' + 
                ('his ' if recipient.fighter.male else 'her ') + 'lips, and eyes wandering in alternate directions. ' +
                ('He ' if recipient.fighter.male else 'She ') + 'is dead in moments. ')
            self.state = EntityState.dead

class Spinal_Paralysis(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = 'Paralysis'
        self.location = location
        self.recipient = recipient       
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 6
        self.locations = set([2,5,6,9,10,13,14,17,18])
        
        if location == 2:
            self.description = '{0}\'s spine has been {3} at the neck, leading to complete paralysis. '
            self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val'),-recipient.fighter.get_attribute('pwr','max_val'),-recipient.fighter.get_attribute('ss','max_val')] #Amount to modify attribute
            self.paralyzed_locs = {range(3,29)} #set
            self.diseases = ['Quadriplegic']
            self.mv_mod = 0
        elif location in [5,6]:
            self.description = '{0}\'s spine has been {3} at the chest, leading to paralysis from the chest down. '
            self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.6,-recipient.fighter.get_attribute('pwr','max_val')*.8,-recipient.fighter.get_attribute('ss','max_val')*.8] #Amount to modify attribute
            l=[]
            l.extend(range(21,29))
            l.extend([9,10,13,14,17,18])
            self.paralyzed_locs = set(l) #set
            self.mv_mod = 0
        else:
            self.description = '{0}\'s spine has been {3}, leading to paralysis from the {2} down. '
            self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.4,-recipient.fighter.get_attribute('pwr','max_val')*.6,-recipient.fighter.get_attribute('ss','max_val')*.6] #Amount to modify attribute
            l=[]
            l.extend(range(21,29))
            if location <13:
                l.extend([13,14,17,18])
            elif location <17:
                l.extend([17,18])
            self.paralyzed_locs = set(l) #set
            self.mv_mod = 0
        
        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Tooth_Damage(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = 'Tooth Damage'
        self.location = location
        self.recipient = recipient
        self.description = 'The blow to {0}\'s ' + self.loc_name + ' has broken several teeth, causing pain and bleeding. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        
        self.severity = 2
        self.locations = set([1])
        self.pain_check = True
        self.diseases = ['Missing Teeth']

        
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 25 #Duration of blood loss

class Damaged_Eye_Socket(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = 'Shattered Eye Socket'
        self.location = location
        self.recipient = recipient
        self.description = 'The blow to {0}\'s ' + self.loc_name + ' has shattered {1} eye socket, causing intense pain and disrupting {1} vision. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.healable = False
        
        self.severity = 4
        self.locations = set([1])
        self.pain_check = True
        self.attr_name = ['sit','fac']
        self.attr_amount = [-recipient.fighter.get_attribute('sit','max_val')*.2,-10]
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 5 #Duration of blood loss

class Damaged_Cheekbone(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Cheekbone'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s cheekbone has been {3}, causing intense pain and disrupting {1} vision. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.healable = False
        
        self.severity = 4
        self.locations = set([1])
        self.pain_check = True
        self.attr_name = ['sit','fac']
        self.attr_amount = [-recipient.fighter.get_attribute('sit','max_val')*.1,-20]

class Damaged_Jawbone(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' Jaw'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s jaw has been {3}, causing excruciating pain. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 5
        self.locations = set([1])
        self.pain_check = True
        self.attr_name = ['fac']
        self.attr_amount = [-20]

class Severed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.damage_type = set(['s'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 6
        self.locations = set([0,1,2,7,8,11,12,15,16,21,22,23,24,25,26])
        self.pain_check = True
        self.shock_check = True
        self.description = '{0}\'s {2} has been {3}, causing excruciating pain and intense shock. '
        
        vitae_dam = max(80, recipient.fighter.vitae*.04)
        if location in [0,1,2]:
            self.state = EntityState.dead
            if location == 0:
                self.description = 'The top of {0}\'s head has been sliced off by the blow, spraying blood and brains. A moment later, {5} wobbles unsteadily, arms twitching spasmodically, and then falls in a heap. '
            elif location == 1:
                self.description = 'The blow cleanly splits {0}\'s head in a red spray. Staring blankly, eyes pointed in two different directions, {5} crumples like a rag doll. '
            else:
                self.description = 'Cleaving through {0}\'s {2}, the blow sends {1} head toppling one way while {1} body falls the other. '
        elif location in [7,8,11,12,25,26]:
            self.bleed_amount = vitae_dam/2 #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
            if location in [7,8]:
                self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
                self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.3,-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1] #Amount to modify attribute
                if location == 7:
                    self.paralyzed_locs = {7,11,15,19} #set
                    self.severed_locs = {7,11,15,19} #set
                else:
                    self.paralyzed_locs = {8,12,16,20} #set
                    self.severed_locs = {8,12,16,20} #set
            elif location in [25,26]:
                self.balance_check = True
                self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
                self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.1,-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25] #Amount to modify attribute
                if location == 25:
                    self.paralyzed_locs = {25,27} #set
                    self.severed_locs = {25,27} #set
                else:
                    self.paralyzed_locs = {26,28} #set
                    self.severed_locs = {26,28} #set
            else:
                self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
                self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.15,-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1] #Amount to modify attribute
                if location == 11:
                    self.paralyzed_locs = {11,15,19} #set
                    self.severed_locs = {11,15,19} #set
                else:
                    self.paralyzed_locs = {12,16,20} #set
                    self.severed_locs = {12,16,20} #set
        elif location in [15,16]:
            self.bleed_amount = vitae_dam/2 #Amount of blood loss
            self.bleed_duration = 400 #Duration of blood loss
            if location == 15:
                self.paralyzed_locs = {15,19} #set
                self.severed_locs = {15,19} #set
            else:
                self.paralyzed_locs = {16,20} #set
                self.severed_locs = {16,20} #set
        else:
            self.balance_check = True
            self.attr_name = ['touch','pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('touch','max_val')*.15,-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25] #Amount to modify attribute
            self.bleed_amount = vitae_dam #Amount of blood loss
            self.bleed_duration = 1000 #Duration of blood loss
            if location == 21:
                self.paralyzed_locs = {21,23,25,27} #set
                self.severed_locs = {21,23,25,27} #set
            elif location == 22:
                self.paralyzed_locs = {22,24,26,28} #set
                self.severed_locs = {22,24,26,28} #set
            elif location == 23:
                self.paralyzed_locs = {23,25,27} #set
                self.severed_locs = {23,25,27} #set
            elif location == 24:
                self.paralyzed_locs = {24,26,28} #set
                self.severed_locs = {24,26,28} #set

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Brain_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        if dam_type == 'b':
            self.title = descriptor.capitalize() + ' Skull'
        else:
            self.title = 'Impaled Skull'
        self.location = location
        self.recipient = recipient
        self.damage_type = set(['b','p'])
        self.duplicable = False
        self.healable = False
        
        self.severity = 6
        self.locations = set([0,1])
        
        self.state = EntityState.dead
        if location == 0:
            if dam_type == 'b':
                self.description = 'The top of {0}\'s head has been crushed with a wet crunch, spraying blood and brains. The body drops in a lifeless heap. '
            else:
                self.description = 'The tip of the weapon peirces {0}\'s skull with a sharp pop, sliding through brain to stop on the bone at the far side. The body slides off the weapon, now covered in gore. '
        else:
            if dam_type == 'b':
                self.description = '{0} lets out a pitiful moan as {1} face is crushed by the blow. Bits of bone puncture {1} his eyes as others invade deeper. The body drops to the ground, limbs curling unnaturally as it soils itself. '
            else:
                self.description = 'As the tip peirces {0}\'s eye, {5} screams, only for the scream to be cut off abruptly as the tip sinks deeper. As it falls, the body slides off and collapses in a heap. '
        

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Vertebra_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = 'Vertebra ' + descriptor.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = 'The blow to {0}\'s ' + self.loc_name + ' seems to have {3} a verterba, causing some pain when moving. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.max_dupes = 2
        
        self.severity = 2
        self.locations = set([2,5,6,9,10,13,14,17,18])
        self.pain_mv_mod = 10

        if dam_type in ['s','p','t']:
            self.bleed_amount = 30 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Vertebra_Heavily_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = 'Vertebra ' + descriptor.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = 'The blow to {0}\'s ' + self.loc_name + ' seems to have {3} a verterba, causing extreme pain at all times. '
        self.description = self.description_filler(recipient, self.loc_name, descriptor)
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = True
        self.healable = False
        self.max_dupes = 2
        self.prerequisite = Vertebra_Damaged
        
        self.severity = 5
        self.locations = set([2,5,6,9,10,13,14,17,18])
        self.pain_mv_mod = 30

        if dam_type in ['s','p','t']:
            self.bleed_amount = 40 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

class Bone_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize() + ' Bone'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} bone has been {3}. '
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        
        self.severity = 4
        self.locations = set([3,4,7,8,11,12,15,16,17,18,21,22,23,24,25,26])
        
        if location in [3,4,7,8,11,12,15,16]:
            self.description + str('This makes it painful for {4} to move {1} arm. ')
            if location % 2 == 0:
                self.atk_mod_l = -10
            else:
                self.atk_mod_r = -10
        else:
            self.description + str('This makes movement painful. ')
            self.pain_mv_mod = 10

        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Bone_Heavily_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize() + ' Bone'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} bone has been {3}. '
        self.damage_type = set(['b'])
        self.duplicable = False
        self.prerequisite = Bone_Damaged
        
        self.severity = 5
        self.pain_check = True
        self.locations = set([3,4,7,8,11,12,15,16,17,18,21,22,23,24,25,26])
        
        if location in [3,4,7,8]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1]  #Amount to modify attribute
            self.description + str('Jagged chunks of bone pierce the skin, causing intense pain, and rendering {1} arm unsusable until healed. ')
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss
            if location % 2 == 0:
                self.paralyzed_locs = {4,8,12,16,20}
            else:
                self.paralyzed_locs = {3,7,11,15,19}
        elif location in [11,12,15,16]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1]  #Amount to modify attribute
            self.description + str('Jagged chunks of bone peirce the skin, causing intense pain, and rendering {1} arm unsusable until healed. ')
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss
            if location % 2 == 0:
                self.paralyzed_locs = {12,16,20}
            else:
                self.paralyzed_locs = {11,15,19}
        else:
            self.description + str('Jagged chunks of bone peirce the skin, causing intense pain. The leg immmediately unloads, bending in an unnatural direction. ')
            self.bleed_amount = 30 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss
            self.mv_mod = .4
            self.balance_check = True
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25]  #Amount to modify attribute
            if location % 2 == 0:
                self.paralyzed_locs = {18,22,24,26,28}
            else:
                self.paralyzed_locs = {17,21,23,25,27}

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Bone_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize() + ' Bone'
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} bone has been {3}, pulverized into too many peices to ever heal properly. Blood seeps from mangled arteries continuously, and the pain is constant and intense. '
        self.damage_type = set(['b'])
        self.duplicable = False
        self.healable = False
        self.prerequisite = Bone_Heavily_Damaged
        
        self.severity = 6
        self.pain_check = True
        self.shock_check = True
        self.pain_mv_mod = 40
        self.loc_max = .2 #Amount to reduce the location's max hits by. Scalar
        self.locations = set([3,4,7,8,11,12,15,16,17,18,21,22,23,24,25,26])
        
        if location in [3,4,7,8]:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 100 #Duration of blood loss
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1]  #Amount to modify attribute
            if location % 2 == 0:
                self.paralyzed_locs = {4,8,12,16,20}
            else:
                self.paralyzed_locs = {3,7,11,15,19}
        elif location in [11,12,15,16]:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.1,-recipient.fighter.get_attribute('ss','max_val')*.1]  #Amount to modify attribute
            self.bleed_amount = 10 #Amount of blood loss
            self.bleed_duration = 50 #Duration of blood loss
            if location % 2 == 0:
                self.paralyzed_locs = {12,16,20}
            else:
                self.paralyzed_locs = {11,15,19}
        else:
            self.attr_name = ['pwr','ss'] #Name of the attribute to modify
            self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.25,-recipient.fighter.get_attribute('ss','max_val')*.25]  #Amount to modify attribute
            self.bleed_amount = 30 #Amount of blood loss
            self.bleed_duration = 200 #Duration of blood loss
            self.mv_mod = .4
            self.balance_check = True
            if location % 2 == 0:
                self.paralyzed_locs = {18,22,24,26,28}
            else:
                self.paralyzed_locs = {17,21,23,25,27}

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Ribs_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} have been {3}. This makes breathing and moving very painful. '
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.pain_check = True
        
        self.severity = 4
        self.locations = set([9,10])
        self.pain_mv_mod = 20
        self.stam_regin = .8 #Scalar

        if dam_type in ['s','p','t']:
            self.bleed_amount = 20 #Amount of blood loss
            self.bleed_duration = 1 #Duration of blood loss

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Ribs_Heavily_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[1]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} have been {3}, and jagged ends are poking through {1} flesh. This makes breathing and moving excruciating, and taking deep breaths is nearly impossible. '
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.pain_check = True
        self.prerequisite = Ribs_Damaged
        
        self.severity = 5
        self.locations = set([9,10])
        self.pain_mv_mod = 60
        self.stam_regin = .6 #Scalar

        if dam_type in ['s','p','t']:
            self.bleed_amount = 30 #Amount of blood loss
            self.bleed_duration = 5 #Duration of blood loss

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Ribs_Destroyed(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[2]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = '{0}\'s {2} have been {3}, and are just a collection of loose, bleeding bones in {1} body cavity that will never heal correctly. Just breathing is excruciatingly painful. Internal bleeding is severe, and will likely kill {4} if medical attention is not recieved.'
        self.damage_type = set(['b'])
        self.duplicable = False
        self.pain_check = True
        self.healable = False
        self.shock_check = True
        self.loc_max = .2 #Amount to reduce the location's max hits by. Scalar
        self.prerequisite = Ribs_Heavily_Damaged
        
        self.severity = 6
        self.locations = set([9,10])
        self.pain_mv_mod = 80
        self.stam_regin = .65 #Scalar
        self.bleed_amount = 30 #Amount of blood loss
        self.bleed_duration = 150 #Duration of blood loss

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Pelvis_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = 'A sharp crack and stab of pain seems to indicate that {0}\'s {2} has been {3}. This makes moving very painful. '
        self.damage_type = set(['s','p','t','b'])
        self.duplicable = False
        self.pain_check = True
        
        self.severity = 4
        self.locations = set([17,18])
        self.pain_mv_mod = 30

        if dam_type in ['s','p','t']:
            self.bleed_amount = 30 #Amount of blood loss
            self.bleed_duration = 10 #Duration of blood loss
            self.description + str('The wound also bleeds heavily. ')

        self.description = self.description_filler(recipient, self.loc_name, descriptor)

class Pelvis_Heavily_Damaged(Injury):
    def __init__(self, location, recipient, dam_type):
        Injury.__init__(self)
        self.layer = 2
        self.loc_name = recipient.fighter.name_location(location)
        descriptors = self.damage_descriptor(self.layer, dam_type)
        descriptor = descriptors[0]
        self.title = descriptor.capitalize() + ' ' + self.loc_name.capitalize()
        self.location = location
        self.recipient = recipient
        self.description = 'An intense, radiant pain and the immediate loss of support for both legs signals that {0}\'s {2} has been {3}. Walking is impossible, and the pelvis is unlikely to heal cleanly. '
        self.damage_type = set(['b'])
        self.duplicable = False
        self.pain_check = True
        self.shock_check = True
        self.gen_stance = FighterStance.prone
        self.severity = 6
        self.locations = set([17,18])
        self.pain_mv_mod = 90
        self.paralyzed_locs = set([21,22,23,24,25,26])
        self.diseases = ['Shattered Pelvis']
        self.attr_name = ['pwr','ss'] #Name of the attribute to modify
        self.attr_amount = [-recipient.fighter.get_attribute('pwr','max_val')*.6,-recipient.fighter.get_attribute('ss','max_val')*.6]  #Amount to modify attribute

        self.description = self.description_filler(recipient, self.loc_name, descriptor)