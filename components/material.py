


class Material():
    _allMaterials = []
    def __init__(self, **kwargs):
        #Below is to create a list of instances of this class
        self._allMaterials.append(self)

        self.name = None
        #Goal: Hardness and elasticity set the hits for the material, toughness then scales them up or down. 
        self.hardness = 1 #Scalar. 1 = ~7 Brinell, roughly very hard wood. Copper 85, Bronze 180, Iron 300, Steel 400-600
        self.elasticity = 1 #Scalar. Basically resistance to deformation. 1 = Wood, average modulus of elasticity ~10 GPa. Bone 18, Gold 79, Copper 100, Bronze 120, Iron 210, Steel 200
        self.toughness = 1 #Scalar. Resistance to breaking when deformed. 1 = Wood, very non-brittle. 10 = Gold, very malliable. .5 = Steel, somewhat brittle. 0.1 = stone
        self.normality = 1 #Scalar. How rare the material is. 1 = Iron, very common. Gold is 4 million times rarer than Iron, but probably it will be ~.01 in game
        self.cost = 1 #Scalar. Raw cost of the material (taking into account refining costs). 1 = Wood, cheap $0.23/lb. 10 = Copper, $2.50/lb. 82,000 = Pure Gold
        self.craft_diff = 1 #Scalar. Difficulty of crafting. 
        for key in self.__dict__:
            for k in kwargs:
                if k == key:
                    self.__dict__.update(kwargs)
        self.set_dynamic_attr()
    
    def set_dynamic_attr(self):
        self.craft_diff = self.elasticity/self.toughness


m_cloth = Material(name='Cloth', hardness=.1, elasticity=.2, toughness=8, normality=2, cost=12)
m_canvas = Material(name='Canvas', hardness=.15, elasticity=.5, toughness=9, normality=1.5, cost=15)
m_leather = Material(name='Leather', hardness=.3, elasticity=.6, toughness=8, normality=2, cost=14)
m_bleather = Material(name='Boiled Leather', hardness=.5, elasticity=.8, toughness=6, normality=1, cost=18)
m_hide = Material(name='Hide', hardness=.3, elasticity=.8, toughness=8, normality=2, cost=10)
m_xthide = Material(name='Exotic Thick Hide', hardness=.5, elasticity=.9, toughness=8, normality=.5, cost=20)
m_wood = Material(name='Wood', hardness=1, elasticity=1, toughness=1, normality=2, cost=1)
m_bone = Material(name='Bone', hardness=1, elasticity=1.8, toughness=.7, normality=2, cost=5)
m_copper = Material(name='Copper', hardness=12, elasticity=10, toughness=7, normality=.2, cost=10)
m_bronze = Material(name='Bronze', hardness=26, elasticity=12, toughness=6, normality=.1, cost=12)
m_iron = Material(name='Iron', hardness=35, elasticity=21, toughness=2, normality=1, cost=2)
m_hiron = Material(name='Hardened Iron', hardness=43, elasticity=21, toughness=1.5, normality=.9, cost=5)
m_steel = Material(name='Steel', hardness=57, elasticity=20, toughness=.5, normality=.7, cost=15)
m_hsteel = Material(name='Hardened Steel', hardness=64, elasticity=20, toughness=.5, normality=.6, cost=20)
m_ssteel = Material(name='Stygian Steel', hardness=71, elasticity=20, toughness=.4, normality=.2, cost=25)
m_hssteel = Material(name='Hardened Stygian Steel', hardness=86, elasticity=20, toughness=.4, normality=.1, cost=35)
m_mithril = Material(name='Mithril', hardness=100, elasticity=18, toughness=.8, normality=.1, cost=80) #Ultra materials are always hardened
m_adam = Material(name='Adamantine', hardness=150, elasticity=22, toughness=1, normality=.001, cost=160) #Ultra materials are always hardened
m_gold = Material(name='Gold', hardness=10, elasticity=8, toughness=10, normality=.001, cost=82000) 
m_hgold = Material(name='Half-Gold', hardness=11, elasticity=9, toughness=8, normality=.01, cost=40000) #Roughly 14K gold
m_silver = Material(name='Silver', hardness=10, elasticity=8, toughness=10, normality=.07, cost=1000) 
m_granite = Material(name='Granite', hardness=7, elasticity=5, toughness=.1, normality=3, cost=1) 
m_obsidian = Material(name='Obsidian', hardness=30, elasticity=25, toughness=.01, normality=.5, cost=15) 



master_material_list = Material._allMaterials
