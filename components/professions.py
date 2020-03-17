from math import sqrt
from statistics import mean
from components.fighter import attr_name_dict

class Profession():
    def __init__(self, **kwargs):
        self.name = ''
        self.desc = ''
        self.entity = None
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.years = 0
        self.prereq_dict = {} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {}
        self.elect_sec_skills = {}
        self.title_list = [] #List of titles in order of level, beginning with 1 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        self.male_allowed = True
        self.female_allowed = True
        

        self.__dict__.update(kwargs)
        

    def calc_cost(self) -> None:
        prim_lvls = 0
        sec_lvls = 0
        for key in self.base_primary_dict:
            prim_lvls += self.base_primary_dict.get(key)
        for key in self.elect_primary_skills:
            cat = self.elect_primary_skills.get(key)
            prim_lvls += cat[1]
        for key in self.base_sec_dict:
            sec_lvls += self.base_sec_dict.get(key)
        for key in self.elect_sec_skills:
            cat = self.elect_sec_skills.get(key)
            sec_lvls += cat[1]

        self.cost = (prim_lvls*400) + (sec_lvls*50)

    def calc_lvl_cost(self) -> list:
        #Calc the XP cost for each level and return it
        #Excel A2^(SQRT(SQRT(C2+2)))/10 Where formula is in B2, A2 is cost, and C2 is level. Gentle log.
        i = 1
        level_costs = []
        while i<11:
            level_costs.append(self.cost**(sqrt(sqrt(i+2)))/10)
            i+=1
        
        return level_costs

    def calc_attr_mult(self,attributes) -> int:
        #Find all the prerteq attributes, figure out the amount the entity's attr exceeds it as a multiple, and cosolidate all of those into a single mult
        mult_list = []
        mult = 0
        for atr in self.prereq_dict:
            a = self.prereq_dict.get(atr)
            b = attributes.get(attr_name_dict.get(atr))
            mult_list.append(b/a)

        mult = mean(mult_list)

        return mult

    def calc_level(self, attributes, years) -> None:
        #Calc the effective level
        self.years = years
        level = 0
        attr_mult = self.calc_attr_mult(attributes)
        if self.entity.fighter is not None:
            lm = self.entity.fighter.lm
        else:
            lm = ((attributes.get(attr_name_dict.get('comp')) * 0.25) + (attributes.get(attr_name_dict.get('men'))  * 0.5) + (attributes.get(attr_name_dict.get('log'))  * 0.15) + (attributes.get(attr_name_dict.get('wis'))  * 0.05) + (attributes.get(attr_name_dict.get('mem'))  * 0.05)) / 100
        if lm + attr_mult >= 1:
            total_lm = sqrt(lm + attr_mult)
        else: total_lm = lm + attr_mult

        self.experience = 5000 * years * total_lm
        level_costs = self.calc_lvl_cost()
        for lvl in level_costs:
            if self.experience <= lvl:
                self.level = level_costs.index(lvl) + 1
                break
        
        if self.experience >= level_costs[9]: self.level = 10


class Warrior(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Warrior'
        self.desc = 'Fighters are the typical rough-and-tumble grunts of the realm. Fighters come in many forms, from simple infantrymen, to hardened mercenaries, to gladiators. One thing all fighters have in common, however, is experience in dealing out damage, whether it is obtained through formal training or barroom brawls. To reflect the wide diversity available in this class, several primary and secondary skill choices are available as electives.'
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'men':80,'will':80,'ss':120,'pwr':120,'man':120,'ped':80,'bal':70,'swift':70,'sta':120,'sit':60} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Dodge':2,'Deflect':2,'Brawling':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {'Melee':[['Long Sword','Dagger','Short Sword','Great Sword','Small Axe','Large Axe','Staff','Mace','Flail','Large Hammer','Small Hammer','Spear','Polearm'],3],'Armor':[['Shield','Light Armor','Medium Armor','Heavy Armor'],3]} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {}
        self.elect_sec_skills = {}
        self.title_list = ['Recruit','Soldier','Warrior','Veteran','Shock Troop','Elite','Commander','General','Warlord','Lord','Hero'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        

        self.__dict__.update(kwargs)
        self.calc_cost()

class Knight(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Knight'
        self.desc = 'Knights are specialized soldiers specifically trained has heavy cavalry. Knights fight with a variety of weapons, though they are more limited at the outset than Fighters. However, knights gain Riding as a primary skill, which allows them to show considerably more prowess in the saddle than all but the most dedicated Fighters.  '
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':80,'mem':80,'wis':80,'comp':70,'comm':70,'men':120,'will':115,'ss':120,'pwr':90,'man':80,'bal':120,'flex':80,'bone':120,'sit':80} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Lance':2,'Heavy Armor':1,'Shield':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {'Melee':[['Long Sword','Dagger','Short Sword','Great Sword','Small Axe','Large Axe','Staff','Mace','Flail','Large Hammer','Small Hammer','Spear','Polearm'],2],'Armor':[['Shield','Light Armor','Medium Armor','Heavy Armor'],1]} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {}
        self.elect_sec_skills = {}
        self.title_list = ['Squire','Cavalry','Seasoned Cavalry','Veteran Cavalry','Minor Knight','Knight','Cavalier','Knight of the Land','Knight Commander','Lord','Hero'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        

        self.__dict__.update(kwargs)
        self.calc_cost()

class Archer(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Archer'
        self.desc = 'Archer’s are specialized soldiers trained (usually from a very young age) in the art of hitting a moving target from a considerable distance. Archers are one of only two professions capable of gaining Archery as a primary skill at creation. Archers are one of the few combat professions in which intellect is the most important ability, as they need to be able to calculate the effects of wind, distance, and speed in their heads quickly and easily. Due to this, archers are rare, but despite their usual lack of physical fortitude, they tend to be very, very dangerous.'
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':120,'mem':80,'comp':70,'men':120,'ss':100,'pwr':110,'sit':120} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Light Armor':1,'Short Sword':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Dagger':2}
        self.elect_sec_skills = {}
        self.title_list = ['Apprentice','Journeyman Archer','Archer','Seasoned Archer','Marksman','Sharpshooter','Sniper','Master Archer','Archery Commander','Lord','Legend'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        

        self.__dict__.update(kwargs)
        self.calc_cost()

class Mariner(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Mariner'
        self.desc = 'Mariners are the naval military forces in the realm, whether they be enlisted military, or privateer. Pirates, warship captains, and sea explorers all fall into this category. Mariners have a heavy emphasis on naval skills, and a lesser emphasis on combat skills. '
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':70,'wis':120,'comm':70,'men':120,'ss':120,'pwr':120,'man':80,'ped':120,'bal':80,'swift':70,'sit':90} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Dodge':1,'Brawling':1,'Dagger':1,'Short Sword':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {}
        self.elect_sec_skills = {'Combat':[['Long Sword','Dagger','Short Sword','Great Sword','Small Axe','Large Axe','Staff','Mace','Flail','Large Hammer','Small Hammer','Spear','Polearm','Light Armor'],6]}
        self.title_list = ['Apprentice','Journeyman Archer','Archer','Seasoned Archer','Marksman','Sharpshooter','Sniper','Master Archer','Archery Commander','Lord','Legend'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        

        self.__dict__.update(kwargs)
        self.calc_cost()

class Ranger(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Ranger'
        self.desc = 'Rangers are a highly specialized fighting force adept at wilderness survival and trained to handle situations without backup. All rangers receive a very strict and expansive training regimen designed to make them the most versatile troops imaginable. This means that the Ranger’s skill set is unusually deep and broad, but a beginning Ranger has zero opportunity for specialization. \nAll rangers are trained one of two different factions: The Antaran Combine, or the Corrillian Ranger’s Troop. \nThe Antaran Combine is a highly secretive society, all that is really left of the once proud nation of Antara, and little is known about their ways or goals. Occasionally, they will burst onto the scene in some dramatic way, usually in defense of some arcane relic, but for the most part, few citizens of any nation are aware of their existence.\nThe Corrillian Ranger’s Troop, on the other hand, is a small, elite fighting force trained primarily in reconnaissance and exploration techniques. No one is quite sure when the Troop was established, but the strong similarities between the Troop and the Combine lead many to speculate that the Troop’s founder was an outcast from the Combine. Regardless, the Troop’s missions and primary goals are always very secretive, the only thing that is known for certain is that Corrillian Rangers have the distinct honor of being some of the few individuals allowed to visit, and in some cases, live with the Elves at Sylvanestria.'
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':110,'mem':130,'wis':150,'comp':110,'comm':90,'cre':130,'men':110,'ss':100,'pwr':90,'man':120,'ped':120,'bal':100,'swift':120,'sta':130,'immune':110,'shock':110,'toxic':110,'sit':120,'hear':120,'ts':120} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Long Sword':2,'Dodge':2,'Light Armor':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Short Sword':1,'Dagger':1,'Spear':1,'Polearm':1,'Deflect':1,'Boxing':1,'Wrestling':1}
        self.elect_sec_skills = {}
        self.title_list = ['Runner','Scout','Tracker','Woodsman','Frontiersman','Recon','Strider','Stalker','Ranger','Ranger Knight','Master Ranger'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        

        self.__dict__.update(kwargs)
        self.calc_cost()

class Thief(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Thief'
        self.desc = 'Thieves are a catch-all profession that encompasses all skilled thieves, including pickpockets, charlatans, con-artists, professional gamblers, safecrackers, and “second-story” men. This profession does not include petty thieves with no skills to speak of, such as thugs, bandits, cutpurses, robbers, etc. For the most part, those criminals are basic fighters. True thieves tend to use their wits more than their fists, and this is reflected in the Thief profession. \nIn most cities, crime of any consequence is organized. In most cases, organized crime in the Realm is run similar to gangs on the low end of the scale, and can be as complex as mafia organizations in large cities. Also, organized crime will typically have more than one faction vying for control of a particular city. Therefore, it is important for the would-be thief to be streetwise and understand the boundaries and territory controlled in a given location, less they upset the wrong people.\nOf course, thieves are not always criminals in the strictest sense. Thieves may also be benevolent, only preying on political or obscenely rich figures and giving back to the people. They may also simply be people who have “flexible” morals, and are simply looking out for number one. However, one thing all thieves have in common is a knack for getting into, and out of, places they are not supposed to be.'
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':90,'mem':90,'wis':100,'comp':90,'comm':90,'cre':130,'men':120,'swift':120} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Dodge':1,'Light Armor':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {'Melee':[['Long Sword','Dagger','Short Sword','Great Sword','Small Axe','Large Axe','Staff','Mace','Flail','Large Hammer','Small Hammer','Spear','Polearm'],1]} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {}
        self.elect_sec_skills = {}
        self.title_list = ['Apprentice','Footpad','Robber','Burglar','Journeyman','Cutthroat','Thief','Hitman','Nightblade','Master Thief','Grandmaster'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        

        self.__dict__.update(kwargs)
        self.calc_cost()

class Spy(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Spy'
        self.desc = 'Spies, similar to thieves, are people centered around stealth and secrecy. However, spies steal something that is much less tangible, and in some cases, more valuable than Gold and Jewelry: Spies steal information. Spies include people in all imaginable fields. There are of course military and political spies. But there are also spies dedicated to a particular industry, as industrial espionage is alive and well in the Realm. In addition, sometimes spies are counter-espionage operatives. \nThere are no collective “spy companies” in the Realm, nor are there any training centers. Spies are typically just people who are very inquisitive, quick thinking, and are smart enough to realize that information is valuable. These people tend to learn the trade by trial and error, though, in this business, the penalties for failure tend to be pretty severe. For this reason, spies are a rare commodity.'
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':120,'mem':130,'wis':110,'comp':110,'comm':110,'cre':90,'men':120} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Dodge':1,'Light Armor':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {'Melee':[['Long Sword','Dagger','Short Sword','Great Sword','Small Axe','Large Axe','Staff','Mace','Flail','Large Hammer','Small Hammer','Spear','Polearm'],1]} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {}
        self.elect_sec_skills = {}
        self.title_list = ['Informant','Leak','Source','Mole','Plant','Operative','Agent','Mist','Shadow','Ghost','Unknown'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        

        self.__dict__.update(kwargs)
        self.calc_cost()

class DesertRanger(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Desert Ranger'
        self.desc = 'Desert Ranger is the only profession allowed for the Nomad race. This is both a blessing and a curse, as Desert Rangers are as adept at survival in the wilderness as standard Rangers. Additionally, Desert Rangers have the distinction of being masters of mounted archery.  However, Desert Rangers are a very specialized profession, and Nomads have no other choices. \nAll Desert Rangers are trained nearly from birth, so they do not have the skill restrictions normally imposed upon standard Rangers. However, their starting skill-set isn’t quite as diverse as a standard Ranger’s.'
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'wis':120,'men':120,'will':120,'ss':120,'pwr':110,'man':130,'ped':90,'bal':120,'swift':100,'sta':110,'sit':120} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Long Sword':1,'Dodge':1,'Light Armor':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Short Sword':1,'Dagger':1,'Deflect':1,'Boxing':1,'Wrestling':1}
        self.elect_sec_skills = {}
        self.title_list = ['Supplicant','Tribesman','Hunter','Hunting Chief','Scout','Warrior','War Chief','Elder Warrior','Tribal Chief','Khan','Great Khan'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        self.female_allowed = False

        self.__dict__.update(kwargs)
        self.calc_cost()

class DaishoSamurai(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Daisho Samurai'
        self.desc = 'Samurai are masters of a specific weapon. In Eastern society, those whom are deemed as potentially worthy are trained almost from birth in the art of the weapon. Worth, in this sense, is based on the parent’s skill level and what little potential can be recognized at an early age. As such, Samurai tend to come from a long line of other Samurai, but this is not necessarily always the case. \nMost Samurai are masters of the Katana and Wakizashi, and are known as Daisho Samurai. However, there are also No-Dachi Samurai, who are masters of the two-handed sword, and Yari Samurai, who are master of the Spear. \nRegardless of the choice of weapon, all Samurai are fearsome opponents, and may be the only people in the Realm who can correctly claim to have mastered their chosen weapon. '
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':110,'mem':110,'wis':110,'comp':100,'comm':100,'men':120,'will':130,'ss':90,'pwr':90,'man':130,'ped':110,'bal':110,'swift':110,'flex':110,'sta':110,'derm':90,'bone':90,'sit':90,'hear':90,'ts':90} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Long Sword':3,'Short Sword':2,'Dodge':2,'Heavy Armor':3,'Deflect':3,'Martial Arts':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Dagger':1}
        self.elect_sec_skills = {}
        self.title_list = ['Apprentice Bushi','Journeyman Bushi','Ronin','Bushi','Selu','Yuma Selu','Samurai','Sensei','Hanshi','Selai','Shogun'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        self.female_allowed = False

        self.__dict__.update(kwargs)
        self.calc_cost()

class NoDachiSamurai(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'No-Dachi Samurai'
        self.desc = 'Samurai are masters of a specific weapon. In Eastern society, those whom are deemed as potentially worthy are trained almost from birth in the art of the weapon. Worth, in this sense, is based on the parent’s skill level and what little potential can be recognized at an early age. As such, Samurai tend to come from a long line of other Samurai, but this is not necessarily always the case. \nMost Samurai are masters of the Katana and Wakizashi, and are known as Daisho Samurai. However, there are also No-Dachi Samurai, who are masters of the two-handed sword, and Yari Samurai, who are master of the Spear. \nRegardless of the choice of weapon, all Samurai are fearsome opponents, and may be the only people in the Realm who can correctly claim to have mastered their chosen weapon. '
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':110,'mem':110,'wis':110,'comp':100,'comm':100,'men':120,'will':130,'ss':90,'pwr':90,'man':130,'ped':110,'bal':110,'swift':110,'flex':110,'sta':110,'derm':90,'bone':90,'sit':90,'hear':90,'ts':90} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Great Sword':5,'Dodge':2,'Heavy Armor':3,'Deflect':3,'Martial Arts':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Dagger':1}
        self.elect_sec_skills = {}
        self.title_list = ['Apprentice Bushi','Journeyman Bushi','Ronin','Bushi','Selu','Yuma Selu','Samurai','Sensei','Hanshi','Selai','Shogun'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        self.female_allowed = False

        self.__dict__.update(kwargs)
        self.calc_cost()

class YariSamurai(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Yari Samurai'
        self.desc = 'Samurai are masters of a specific weapon. In Eastern society, those whom are deemed as potentially worthy are trained almost from birth in the art of the weapon. Worth, in this sense, is based on the parent’s skill level and what little potential can be recognized at an early age. As such, Samurai tend to come from a long line of other Samurai, but this is not necessarily always the case. \nMost Samurai are masters of the Katana and Wakizashi, and are known as Daisho Samurai. However, there are also No-Dachi Samurai, who are masters of the two-handed sword, and Yari Samurai, who are master of the Spear. \nRegardless of the choice of weapon, all Samurai are fearsome opponents, and may be the only people in the Realm who can correctly claim to have mastered their chosen weapon. '
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':110,'mem':110,'wis':110,'comp':100,'comm':100,'men':120,'will':130,'ss':90,'pwr':90,'man':130,'ped':110,'bal':110,'swift':110,'flex':110,'sta':110,'derm':90,'bone':90,'sit':90,'hear':90,'ts':90} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Spear':5,'Dodge':2,'Heavy Armor':3,'Deflect':3,'Martial Arts':1} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Dagger':1}
        self.elect_sec_skills = {}
        self.title_list = ['Apprentice Bushi','Journeyman Bushi','Ronin','Bushi','Selu','Yuma Selu','Samurai','Sensei','Hanshi','Selai','Shogun'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        self.female_allowed = False

        self.__dict__.update(kwargs)
        self.calc_cost()

class Ninja(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Ninja'
        self.desc = 'Ninja are highly trained assassins, spies, and reconnaissance agents. You can think of a Ninja as a Ranger, but with less wilderness skills, and in their place, spying skills. Ninja are trained from a very young age in the art of getting into, and out of, places where they aren’t supposed to be. They are highly skilled in stealth, evasion, acting, and self-defense. \nNinja are almost mythical figures in the Realm. Most believe them to be but a legend, like Solomon and Demons. But Ninja are real, and it is a testament to their skills that the only reference to them in the collective consciousness is that of a “ghost”.\nContrary to many stories, most Ninja have no magical ability. Like all characters, they can learn it if they so desire, but it is not a part of their general training. However, Ninja are so adept at avoiding detection that many come to believe that they can walk through walls and fly. \nLike Rangers, Ninja spend a large part of their lives in regimented training, so much, that in the beginning, all Ninja share the same skill-set. Also, like Rangers, Ninja are an Elite force, and are required to possess rather impressive physical and mental abilities.\nAlso like Rangers, Ninja are required to be members of the Ninja clan, known as Kage-Do (literally, the Way of the Shadow). This membership is for life, even after the Ninja has retired from active duty. The Ninja that attempts to leave the clan is forever hunted as a fugitive, and long indeed are the arms of Kage-Do.\nDue to the requirement that Ninja always be a member of Kage-Do, they will be required to carry out orders from time to time. \nUnlike most other Eastern professions, Ninja are not required to be Eastern. Ninja can be of Eastern, Stygian, Corrillian, or Solomanian stock, though any but Eastern is rare. A small number from each of these races are, however, actively trained from a very early age to be spies in the appropriate kingdom. '
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':110,'mem':110,'wis':110,'comp':110,'comm':120,'cre':130,'men':130,'will':130,'ss':110,'pwr':110,'man':120,'ped':120,'bal':115,'swift':110,'flex':110,'sta':110,'derm':110,'bone':110,'immune':110,'shock':110,'toxic':110,'sit':110,'hear':110,'ts':110,'touch':110} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Dagger':1,'Short Sword':2,'Dodge':2,'Deflect':1,'Light Armor':1,'Martial Arts':2} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Long Sword':1,'Small Axe':1,'Mace':1,'Small Hammer':1,'Spear':1,'Polearm':1}
        self.elect_sec_skills = {}
        self.title_list = ['Apprentice Jenin','Journeyman Jenin','Jenin','Apprentice Chunnin','Journeyman Chunnin','Chunnin','Apprentice Jounin','Journeyman Jounin','Jounin','Shinobi','Kage'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        self.female_allowed = False

        self.__dict__.update(kwargs)
        self.calc_cost()

class Geisha(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Geisha'
        self.desc = 'The Geisha are the ultimate Eastern Assassins and Spies. Geisha are always female, and are more practiced at fewer skills than the Ninja. Geisha have a smaller number of combat skills, but in general, are more practiced at the ones they have. Geisha also has a reduced set of non-combat skills, but are much more adept at those remaining. Like Ninja, Geisha lose all free skill points due to their lifelong training, and like Ninja, Geisha must be members of the Kage-Do.  '
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':130,'mem':110,'wis':130,'comp':110,'comm':130,'cre':150,'men':150,'will':130,'ss':80,'pwr':80,'man':150,'ped':110,'bal':110,'swift':110,'flex':110,'sta':110,'derm':110,'bone':110,'immune':110,'shock':110,'toxic':110,'sit':110,'hear':110,'ts':110,'touch':110,'fac':110,'shape':110} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Dagger':4,'Dodge':4,'Deflect':2,'Martial Arts':4} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Long Sword':1,'Short Sword':1,'Small Axe':1,'Spear':1,'Polearm':1}
        self.elect_sec_skills = {}
        self.title_list = ['Apprentice Jenin','Journeyman Jenin','Jenin','Apprentice Chunnin','Journeyman Chunnin','Chunnin','Apprentice Jounin','Journeyman Jounin','Jounin','Shinobi','Kage'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        self.male_allowed = False

        self.__dict__.update(kwargs)
        self.calc_cost()

class Sohei(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Sohei'
        self.desc = 'Sohei are the ultimate hand-to-hand fighting machines. They have devoted their lives to Hachiman, and similar to Paladins in other societies, Sohei are the protectors of the faith. Sohei, however, do not believe in using bladed weapons as an offensive or defensive mechanism. They believe that their faith is benefited by defeating opponents with their bare hands, so that their opponent may live to see the strength imparted by the wise Hachiman. Like Paladins, Sohei have a strict sense of honor, and must at all times uphold the honor of Hachiman. In addition, Sohei must live a life of poverty, humility, and destitution, and are almost Sadistic in their pursuit of this.'
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'wis':110,'will':130,'ss':80,'pwr':80,'man':110,'ped':110,'bal':110,'swift':110,'flex':110,'sta':110} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Dodge':5,'Deflect':2,'Martial Arts':5} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Staff':3}
        self.elect_sec_skills = {}
        self.title_list = ['Chiroi Obi','Kiroi Obi','Midori-iro Obi','Aoi Obi','Akai Obi','Tcha-iro Obi','Master of Winter','Master of Autumn','Master of Summer','Master of Spring','Grandmaster'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels

        self.__dict__.update(kwargs)
        self.calc_cost()

class Monk(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Sohei'
        self.desc = 'Monks live their lives in pursuit of enlightenment by pain, suffering, and enduring servitude to the God Hachiman. Like priests in other societies, monks are the primary vessels of the faith, but monks are also wise men, martial arts practitioners, and if necessary, defenders of the faith. Monks have but one pursuit, enlightenment. Mortal desires are things to be ignored, mortal pleasures are things to be avoided. Monks believe enlightenment, and holiness, come from deep reflection, a reflection that can only be fully understood through sacrifice. To this end, monks cannot keep mortal treasures. Monks cannot allow themselves to experience mortal pleasures. And above all, monks cannot give in to mortal weakness. Monks pursue enlightenment through purity, purity of mind, purity of body, and purity of spirit.'
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'wis':110,'will':110} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Dodge':2,'Deflect':2,'Martial Arts':3,'Staff':2} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {'Flail':1,'Mace':1}
        self.elect_sec_skills = {}
        self.title_list = ['Supplicant','Initiate','Brother','Disciple','Guide','Master','Master of Wind','Master of Earth','Master of Fire','Master of Water','Grandmaster of Flowers'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels

        self.__dict__.update(kwargs)
        self.calc_cost()

class DeathKnight(Profession):
    def __init__(self, entity, **kwargs):
        Profession.__init__(self)
        self.name = 'Death Knight'
        self.desc = 'Solomanian Death Knights are perhaps the most feared fighting force in all of the Realm. In recorded history, no other fighting force has ever been victorious against odds the likes that the Death Knights have endured.  The Death Knights owe their fearsome reputation to a combination of factors, the biggest of which is their training. Those who are chosen for the Death Knights are presented with a unique honor, and trained from an early age to be the best of the best. Failure is not an option in this regiment. To fail is to die. As a result, only 60% of those chosen for the Death Knight training, each of which is a genetic anomaly, actually make it through training. Death Knight training is considered complete at age 16. As a result of life long training, all Death Knights begin with an identical, narrow, yet exceptionally deep, set of skills. Few can best a Death Knight in hand-to-hand combat, a fact proven by one simple truth: Even the ultra-elite Samurai consider a battle with a Death Knight the ultimate test. To be a Death Knight is to be the best at what you do. And what you do is kill.'
        self.entity = entity
        self.level = 0
        self.experience = 0
        self.cost = 0
        self.prereq_dict = {'log':110,'mem':110,'wis':110,'comp':110,'comm':110,'cre':110,'men':110,'will':110,'ss':150,'pwr':150,'man':130,'ped':130,'bal':120,'swift':110,'flex':110,'sta':130,'derm':110,'bone':115,'immune':110,'shock':110,'toxic':110,'sit':110,'hear':110,'ts':110,'touch':110} #Dict with the prereq attributes in 'attr':score format
        self.base_primary_dict = {'Large Axe':4,'Long Sword':2,'Dagger':2,'Lance':4,'Dodge':1,'Deflect':2,'Heavy Armor':4} #Dict with the base primary skills in 'Skill Name':level format
        self.elect_primary_skills = {} #Dict with elective primarys in the following format: {'Skill cat':[[Skill Name, Skill Name],Levels]} ex:{'Melee':[['Long Sword','Dagger'],Levels],'Armor':[['Heavy Armor'],2]}
        self.base_sec_dict = {}
        self.elect_sec_skills = {}
        self.title_list = ['Private First Class','Corporal','Sergeant','Sergeant, First Class','Sergeant, Major','Death Knight','Death Knight, First Class','Death Knight, Major','Major','Colonel','General'] #List of titles in order of level, beginning with 0 and ending with 11
        self.primary_skills = {} #Dict of chosen skils and effective levels
        self.secondary_skills = {} #Dict of chosen skills and levels
        self.female_allowed = False

        self.__dict__.update(kwargs)
        self.calc_cost()




