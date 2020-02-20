import weakref
from components.circumstances import Circumstance

all_circumstances = []

for obj in Circumstance.getinstances():
    all_circumstances.append(obj.name)


class Upbringing():
    _instances = set()
    def __init__(self, **kwargs):
        self.name = ''
        self.desc = ''
        self.allowed_ethnicities = ['Barbarian','Corrillian','Stygian','Nomad','Eastern','Kebrini','Solomanian']
        self.min_social_standing = 0
        self.max_social_standing = 100
        self.allowed_prof = ['Fighter', 'Knight', 'Archer', 'Ranger', 'Mariner', 'Thief', 'Spy'] #List of the name of each allowed profession
        self.max_age = 40
        self.allowed_circumstances = all_circumstances #List of circumstance by name. 'all' is all inclusive
        self.attr_mods = {} #Dict of attribute mods in abbr:mod format (ex. 'ss':40)
        self.skill_mods = {} #Dict of skill mods in abbr:mod format
        self.free_skills = [] #list of free skills by name
        

        self._instances.add(weakref.ref(self))

        self.__dict__.update(kwargs)

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

attr_mods = {'ss':20,'pwr':10,'sta':30,'log':-20,'wis':-10,'cre':-10,'men':-10,'will':30,'fat':-30}

slave = Upbringing(name='Slave',desc='You have been a slave your entire life. Upon turning 16 your owner sold you to a gladiator company. ',
                    allowed_prof=[], max_age=16,allowed_circumstances=['Slave'],attr_mods=attr_mods)

attr_mods = {'ss':10,'sta':20,'log':-10,'men':-10,'will':10,'man':10,'immune':10}
allowed_ethnicities = ['Corrillian','Stygian','Kebrini','Solomanian']

farmhand = Upbringing(name='Farmhand',desc='You worked on a farm for most of your childhood, and are used to physical labor. ',
                    max_social_standing=25,attr_mods=attr_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'ss':-10,'pwr':-10,'log':-10,'men':20,'cre':10,'man':20,'immune':-10,'derm':-10,'bone':-10,'swift':20}
desc = 'You spent most of your childhood begging on the streets of a large city. You are quick and resourceful, but a bit malnourished. '
allowed_ethnicities = ['Corrillian','Stygian','Kebrini','Solomanian']

beggar = Upbringing(name='Beggar',desc=desc,max_social_standing=15,attr_mods=attr_mods)

desc = 'You had an average childhood for your village, and have no major advantages or drawbacks.'

normal = Upbringing(name='Normal',desc=desc,min_social_standing=20,max_social_standing=65)

attr_mods = {'log':-10,'cre':-20,'comp':-10,'comm':-10,'man':10,'bal':10,'swift':10}
free_skills = ['Deflect','Dodge','Brawling','Short Sword','Dagger','Mace','Spear']
skill_mods = {'spear':10,'dagger':15,'deflect':20}
desc = 'Your childhood was spent tagging along with your family from camp to camp. You have seen death aplenty and are no stranger to weaponry, though your social and mental skills are a bit lacking. '
allowed_ethnicities = ['Corrillian','Stygian']

military = Upbringing(name='Military Brat',desc=desc,max_social_standing=65,attr_mods=attr_mods,free_skills=free_skills,
                    skill_mods=skill_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'comp':-10,'comm':-10,'wis':-10,'man':20,'swift':20,'ss':-10,'bone':-10}
free_skills = ['Dodge','Brawling','Dagger']
skill_mods = {'dodge':10,'dagger':10}
desc = 'Your childhood was spent picking pockets and slitting purses. You are fast and good with a blade, but smaller than you might have been and uneducated.'
allowed_ethnicities = ['Corrillian','Stygian','Kebrini']

thief = Upbringing(name='Thief',desc=desc,max_social_standing=45,attr_mods=attr_mods,free_skills=free_skills,
                    skill_mods=skill_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'comp':-10,'comm':-10,'wis':-10,'log':-20,'pwr':30,'bone':20}
free_skills = ['Dodge','Brawling','Mace']
skill_mods = {'brawling':20}
desc = 'You have always been bigger than normal, so you gravitated towards pushing people around. You are strong and good with your fists, but your understanding of other aspects of life is a bit lacking.'
allowed_ethnicities = ['Corrillian','Stygian','Kebrini']

thug = Upbringing(name='Thug',desc=desc,max_social_standing=35,attr_mods=attr_mods,free_skills=free_skills,
                    skill_mods=skill_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'comp':10,'comm':30,'wis':-10,'log':20,'men':30}
desc = 'You\'ve always been sharper than the average person, and as a child, you learned to use your wits and the gift of gab to weasel your way into, and out of, all kinds of situations.'
allowed_ethnicities = ['Corrillian','Stygian','Kebrini']

conman = Upbringing(name='Con Artist',desc=desc,max_social_standing=55,attr_mods=attr_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'pwr':10,'bone':10,'man':10,'sta':10,'fat':10,'swift':-10,'hear':-20}
free_skills = ['Small Hammer']
desc = 'You grew up apprenticing to be a blacksmith. You are good with a hammer, and have no aversion to hard work. But all that noise has not been kind to your hearing.'
allowed_ethnicities = ['Corrillian','Stygian','Kebrini']

blacksmith = Upbringing(name='Apprentice Smith',desc=desc,max_social_standing=45,attr_mods=attr_mods,free_skills=free_skills,
                    allowed_ethnicities=allowed_ethnicities)

attr_mods = {'man':10,'ss':10,'will':10,'bal':10,'flex':-10,'comp':-10,'comm':-10,'mem':-10}
desc = 'Most of your childhood was spent on fishing boats hauling nets and baiting traps. You are decent with your hands and patient, but have some gaps intellectually.'
allowed_ethnicities = ['Corrillian','Stygian']

fisherman = Upbringing(name='Fisherman',desc=desc,max_social_standing=45,attr_mods=attr_mods,
                    allowed_ethnicities=allowed_ethnicities)

attr_mods = {'comp':10,'comm':10,'wis':-10,'log':10,'mem':10,'immune':-10,'shock':-10,'toxic':-10,'will':-20,'sta':-20,'man':10,'ped':10,'flex':10,'bal':10,'ss':-20,'pwr':-10}
free_skills = ['Dodge','Deflect','Wrestling','Boxing','Long Sword']
desc = 'As a child, your every desire was provided for due to your high social standing and doting parents. You got the best of educations, and are very well rounded, but are a stranger to adversity.'
allowed_ethnicities = ['Corrillian','Stygian','Kebrini']

spoiled = Upbringing(name='Spoiled Brat',desc=desc,min_social_standing=65,attr_mods=attr_mods,free_skills=free_skills,
                    allowed_ethnicities=allowed_ethnicities)

attr_mods = {'comp':20,'comm':20,'log':10,'mem':20,'sta':-20,'ss':-10}
desc = 'As a child, your parents groomed you to take over the family empire. You had personal tutors and are very learned. However, you have very little experience with physical labor.'
allowed_ethnicities = ['Corrillian','Stygian','Kebrini']

groomed = Upbringing(name='Groomed for Leadership',desc=desc,min_social_standing=65,attr_mods=attr_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'wis':20,'hear':10,'sit':10,'will':10,'comp':-20,'comm':-20}
desc = 'You spent your childhood in the wilderness, hunting and tracking. You have excellent judgement and senses, but poor communication skills.'
allowed_ethnicities = ['Corrillian','Stygian','Barbarian']

woodsman = Upbringing(name='Woodsman',desc=desc,max_social_standing=45,attr_mods=attr_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'pwr':30,'will':10,'sta':-20,'immune':-10}
desc = 'You spent your childhood mining. The constant breaking of rock has made you immensely strong, but the inhalation of dust has scarred your lungs.'
allowed_ethnicities = ['Corrillian','Stygian']

miner = Upbringing(name='Miner',desc=desc,max_social_standing=50,attr_mods=attr_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'log':-10,'men':-10,'cre':-10,'mem':-10,'comp':-10,'swift':10,'pwr':10}
free_skills = ['Dodge','Brawling','Mace']
skill_mods = {'dodge':10,'brawling':10}
desc = 'As the child of a warrior, you spent your childhood learning the ways of tribal battle. You are swift, strong, and know how to fight, but unused to intense thought.'
allowed_ethnicities = ['Barbarian']

warrior = Upbringing(name='Warrior\'s Child',desc=desc,max_social_standing=70,attr_mods=attr_mods,free_skills=free_skills,
                    skill_mods=skill_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'mem':-10,'comp':-10,'will':-10,'swift':10,'pwr':10}
free_skills = ['Deflect','Brawling','Long Sword']
desc = 'As the child of a tribal elder, you spent your childhood learning how to lead men in battle. You are swift, strong, and know how to fight, but impatient and somwhat uneducated.'
allowed_ethnicities = ['Barbarian']

elder = Upbringing(name='Elder\'s Child',desc=desc,min_social_standing=71,max_social_standing=95,attr_mods=attr_mods,free_skills=free_skills,
                    allowed_ethnicities=allowed_ethnicities)

attr_mods = {'will':-20,'swift':10,'pwr':10}
free_skills = ['Dodge','Deflect','Brawling','Great Sword']
desc = 'As the child of a chieftan, you have been groomed to lead the tribe. You are better educated than other barbarians, and familiar with heavy weapons, but have had your spirit broken by your father.'
allowed_ethnicities = ['Barbarian']

chieftan = Upbringing(name='Chieftan\'s Child',desc=desc,min_social_standing=96,attr_mods=attr_mods,free_skills=free_skills,
                    allowed_ethnicities=allowed_ethnicities)

attr_mods = {'ss':10,'sta':20,'log':-10,'men':-10,'will':10,'man':10,'immune':10}
allowed_ethnicities = ['Eastern']
allowed_prof = []

e_farmhand = Upbringing(name='Farmhand',desc='You worked on a farm for most of your childhood, and are used to physical labor. ',
                    max_social_standing=15,attr_mods=attr_mods,allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

desc = 'You had an average childhood for your village, and have no major advantages or drawbacks.'
allowed_ethnicities = ['Eastern']
allowed_prof = []

e_normal = Upbringing(name='Normal',desc=desc,max_social_standing=15,allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

attr_mods = {'comp':-10,'comm':-10,'wis':-10,'man':20,'swift':20,'ss':-10,'bone':-10}
free_skills = ['Dodge','Brawling','Dagger']
skill_mods = {'dodge':10,'dagger':10}
desc = 'Your childhood was spent picking pockets and slitting purses. You are fast and good with a blade, but smaller than you might have been and uneducated.'
allowed_ethnicities = ['Eastern']
allowed_prof = []

e_thief = Upbringing(name='Thief',desc=desc,max_social_standing=15,attr_mods=attr_mods,free_skills=free_skills,
                    skill_mods=skill_mods,allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

attr_mods = {'comp':-10,'comm':-10,'wis':-10,'log':-20,'pwr':30,'bone':20}
free_skills = ['Dodge','Brawling','Mace']
skill_mods = {'brawling':20}
desc = 'You have always been bigger than normal, so you gravitated towards pushing people around. You are strong and good with your fists, but your understanding of other aspects of life is a bit lacking.'
allowed_ethnicities = ['Eastern']
allowed_prof = []

e_thug = Upbringing(name='Thug',desc=desc,max_social_standing=15,attr_mods=attr_mods,free_skills=free_skills,
                    skill_mods=skill_mods,allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

attr_mods = {'comp':10,'comm':30,'wis':-10,'log':20,'men':30}
desc = 'You\'ve always been sharper than the average person, and as a child, you learned to use your wits and the gift of gab to weasel your way into, and out of, all kinds of situations.'
allowed_ethnicities = ['Eastern']
allowed_prof = []

e_conman = Upbringing(name='Con Artist',desc=desc,max_social_standing=5,attr_mods=attr_mods,allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

attr_mods = {'pwr':10,'bone':10,'man':10,'sta':10,'fat':10,'swift':-10,'hear':-20}
free_skills = ['Small Hammer']
desc = 'You grew up apprenticing to be a blacksmith. You are good with a hammer, and have no aversion to hard work. But all that noise has not been kind to your hearing.'
allowed_ethnicities = ['Eastern']
allowed_prof = []

e_blacksmith = Upbringing(name='Apprentice Smith',desc=desc,max_social_standing=15,attr_mods=attr_mods,free_skills=free_skills,
                    allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

attr_mods = {'man':10,'ss':10,'will':10,'bal':10,'flex':-10,'comp':-10,'comm':-10,'mem':-10}
desc = 'Most of your childhood was spent on fishing boats hauling nets and baiting traps. You are decent with your hands and patient, but have some gaps intellectually.'
allowed_ethnicities = ['Eastern']
allowed_prof = []

e_fisherman = Upbringing(name='Fisherman',desc=desc,max_social_standing=15,attr_mods=attr_mods,
                    allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

desc = 'Your childhood was spent training intensely to become a conscripted warrior. '
allowed_ethnicities = ['Eastern']
allowed_prof = ['Fighter']

e_warrior = Upbringing(name='Training',desc=desc,min_social_standing=16,max_social_standing=20,
                    allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

desc = 'Your childhood was spent training intensely to become a monk. '
allowed_ethnicities = ['Eastern']
allowed_prof = ['Monk']

monk = Upbringing(name='Training',desc=desc,min_social_standing=21,max_social_standing=35,
                    allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

desc = 'Your childhood was spent training intensely to become a warrior monk. '
allowed_ethnicities = ['Eastern']
allowed_prof = ['Sohei']

sohei = Upbringing(name='Training',desc=desc,min_social_standing=36,max_social_standing=45,
                    allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

desc = 'Your childhood was spent training intensely to become a Samurai. '
allowed_ethnicities = ['Eastern']
allowed_prof = ['Daisho Samurai', 'No-Dachi Samurai', 'Yari Samurai']

samurai = Upbringing(name='Training',desc=desc,min_social_standing=46,max_social_standing=55,
                    allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

desc = 'Your childhood was spent training intensely to become a hidden assassin and operative. '
allowed_ethnicities = ['Eastern']
allowed_prof = ['Ninja','Geisha']

ninja = Upbringing(name='Training',desc=desc,min_social_standing=56,max_social_standing=85,
                    allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

desc = 'Your childhood was spent training intensely in secret to become a hidden assassin and operative for the Eastern empire. You never knew your parents, and other of your ethinicity are a mystery to you. '
allowed_ethnicities = ['Corrillian','Stygian','Solomanian']
allowed_prof = ['Ninja']

f_ninja = Upbringing(name='Kidnapped and trained',desc=desc,
                    allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

desc = 'As a member of the ruling caste outside of the succession, you spent your childhood in brutal training, as you have your pick of professions. You are representative of the pinnacle of Eastern Empire training. '
allowed_ethnicities = ['Eastern']
allowed_prof = ['Ninja','Geisha','Fighter','Daisho Samurai', 'No-Dachi Samurai', 'Yari Samurai','Monk','Sohei']
attr_mods = {'wis':10,'men':10,'man':10,'swift':20,'ped':10,'flex':10,'sta':20,'will':20}

ruling = Upbringing(name='Ruling Caste Training',desc=desc,min_social_standing=86,attr_mods=attr_mods,
                    allowed_ethnicities=allowed_ethnicities,allowed_prof=allowed_prof)

attr_mods = {'pwr':10,'bone':10,'man':10,'sta':10,'fat':10,'swift':-10,'hear':-20}
free_skills = ['Small Hammer']
desc = 'You grew up apprenticing to be a blacksmith. You are good with a hammer, and have no aversion to hard work. But all that noise has not been kind to your hearing.'
allowed_ethnicities = ['Solomanian']

s_blacksmith = Upbringing(name='Apprentice Smith',desc=desc,max_social_standing=20,attr_mods=attr_mods,free_skills=free_skills,
                    allowed_ethnicities=allowed_ethnicities)

attr_mods = {'man':10,'ss':10,'will':10,'bal':10,'flex':-10,'comp':-10,'comm':-10,'mem':-10}
desc = 'Most of your childhood was spent on fishing boats hauling nets and baiting traps. You are decent with your hands and patient, but have some gaps intellectually.'
allowed_ethnicities = ['Solomanian']

s_fisherman = Upbringing(name='Fisherman',desc=desc,max_social_standing=20,attr_mods=attr_mods,
                    allowed_ethnicities=allowed_ethnicities)

attr_mods = {'pwr':30,'will':10,'sta':-20,'immune':-10}
desc = 'You spent your childhood mining. The constant breaking of rock has made you immensely strong, but the inhalation of dust has scarred your lungs.'
allowed_ethnicities = ['Solomanian']

s_miner = Upbringing(name='Miner',desc=desc,max_social_standing=20,attr_mods=attr_mods,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'man':10,'bal':10,'sta':10}
free_skills = ['Long Sword','Dagger','Mace','Spear']
desc = 'Your childhood was spent training to become a member of the Solomanian Infantry. You are skilled with basic weaponry and tactics.'
allowed_ethnicities = ['Solomanian']
allowed_prof = ['Fighter']

s_fighter = Upbringing(name='Training',desc=desc,min_social_standing=21, max_social_standing=55,attr_mods=attr_mods,free_skills=free_skills,
                    allowed_prof=allowed_prof,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'wis':10,'men':10,'ped':10,'bal':20,'ss':10,'pwr':10}
desc = 'Your childhood was spent training to become a member of the Solomanian Navy. You can handle the choppiest seas.'
allowed_ethnicities = ['Solomanian']
allowed_prof = ['Mariner']

s_mariner = Upbringing(name='Training',desc=desc,min_social_standing=56, max_social_standing=75,attr_mods=attr_mods,
                    allowed_prof=allowed_prof,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'man':10,'ped':10,'ss':20,'pwr':20,'sta':10}
free_skills = ['Mace','Spear','Short Sword']
desc = 'Your childhood was spent training to become a Solomanian Death Knight. Your prerquisite attributes have all been enchanced, and you have been trained in a variety of secondary weapons.'
allowed_ethnicities = ['Solomanian']
allowed_prof = ['Death Knight']

s_knight = Upbringing(name='Training',desc=desc,min_social_standing=76, max_social_standing=95,attr_mods=attr_mods,free_skills=free_skills,
                    allowed_prof=allowed_prof,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'man':10,'ped':10,'ss':20,'pwr':20,'sta':10,'wis':10,'men':10,'bal':10}
desc = 'As a member of the Solomanian aristocracy, your childhood was spent training to be an advanced spcimen of your culture, capable of excelling at any role. You have no specific skills, but you are highly trained in body and mind.'
allowed_ethnicities = ['Solomanian']
allowed_prof = ['Death Knight','Fighter','Mariner']

s_noble = Upbringing(name='Advanced Training',desc=desc,min_social_standing=96, attr_mods=attr_mods,
                    allowed_prof=allowed_prof,allowed_ethnicities=allowed_ethnicities)

attr_mods = {'man':20,'will':10,'wis':10,'men':10,'bal':10}
desc = 'Your childhood was spent with your tribe on the steppes, learning to ride, shoot, hunt and raid. You have no specific skills, but are crafty and very good with your hands.'
allowed_ethnicities = ['Nomad']
allowed_prof = ['Desert Ranger']

nomad = Upbringing(name='Nomad',desc=desc, attr_mods=attr_mods,
                    allowed_prof=allowed_prof,allowed_ethnicities=allowed_ethnicities)

