from enums import FighterStance
import weakref

class Injury:
    _instances = set()
    def __init__(self):
        self._instances.add(weakref.ref(self))
        self.title = None
        self.description = None #Use {} (str.format) to ID variables to be replaced at runtime {0}: Entity name {1}: Entity pronoun {2}: Loc name
        self.damage_type = None #set with 'b', 's', 'p', or 't'
        self.severity = None #1-6
        self.locations = None #Set of allowed locations
        self.healable = True #bool
        self.pain_check = False #All check args should be bool
        self.shock_check = False
        self.balance_check = False
        self.clarity_reduction = None
        self.bleed_amount = None #Amount of blood loss
        self.bleed_duration = None #Duration of blood loss
        self.attr_name = None #Name of the attribute to modify
        self.attr_amount = None #Amount to modify attribute
        self.loc_reduction = None #Additional amount to reduce the location hits by
        self.loc_max = None #Amount to reduce the location's max hits by. Scalar
        self.severed_locs = None  #locs to sever. List
        self.temp_phys_mod = None
        self.paralyzed_locs = None #list
        self.suffocation = None #In rounds till death
        self.stam_drain = None #Amount per round
        self.stam_regin = None #Scalar
        self.pain_mv_mod = None
        self.diseases = None #List of objects
        self.atk_mod_r = None
        self.atk_mod_l = None
        self.mv_mod = None #Scalar
        self.gen_stance = None #Fighterstance

    def getinstances(self, cls):
        '''Goal: get a list of instances based on this class'''
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    def description_filler(self, recipient, location) -> str:
        name = recipient.name
        if recipient.fighter.male: pronoun = ' his '
        else: pronoun = ' her '
        loc_name = recipient.fighter.name_location(location)
        description = self.description.format(name, pronoun, loc_name)
        return description


class Light_Scraping(Injury):
    def __init__(self, location, recipient):
        super()
        self.title = 'Light Scraping'
        self.location = location
        self.recipient = recipient
        self.description = '{0} has been lightly scraped and lacerated. '
        self.description = self.description_filler(recipient, location)
        self.damage_type = set(['s','p','t'])
        self.severity = 1
        self.locations = set(range(0,30))
        self.bleed_amount = 10 #Amount of blood loss
        self.bleed_duration = 1 #Duration of blood loss
