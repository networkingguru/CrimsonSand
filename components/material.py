


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
        self.p_ratio = .5 #Poisson's ratio. Non-scaled, use actual values
        self.normality = 1 #Scalar. How rare the material is. 1 = Iron, very common. Gold is 4 million times rarer than Iron, but probably it will be ~.01 in game
        self.cost = 1 #Scalar. Raw cost of the material (taking into account refining costs). 1 = Wood, cheap $0.23/lb. 10 = Copper, $2.50/lb. 82,000 = Pure Gold
        self.craft_diff = 1 #Scalar. Difficulty of crafting. 1 = 1 day of crafting per lb of finished material. Cost of 1 day of a craftsman = 5 
        # For metals, hardness modifies it. Hardened Steel takes 5 days to craft 1 pound of weaponry. 
        self.density = 1 #Scalar. Relative density per cubic inch. 1 = Wood, .03 lb/in3. Copper = .32, Silver = .38, Gold = .7, Iron = .28, Bronze = .3, Steel = .28

        self.__dict__.update(kwargs)
        self.set_dynamic_attr()
    
    def set_dynamic_attr(self):                   
        if self.craft_diff == 0:
            self.craft_diff = .078 * self.hardness
            self.craft_diff = round(self.craft_diff, 2)


m_cloth = Material(name='Cloth', hardness=.2, elasticity=.3, toughness=6, normality=2, cost=12, density=.01, p_ratio = .5, craft_diff = 1)
m_canvas = Material(name='Canvas', hardness=.3, elasticity=.5, toughness=9, normality=1.5, cost=15, density=.015, p_ratio = .48, craft_diff = 1)
m_leather = Material(name='Leather', hardness=.4, elasticity=.5, toughness=8, normality=2, cost=14, density=.1, p_ratio = .47, craft_diff = .3)
m_bleather = Material(name='Boiled Leather', hardness=.8, elasticity=.9, toughness=6, normality=1, cost=18, density=.15, p_ratio = .45, craft_diff = .4)
m_hide = Material(name='Hide', hardness=.6, elasticity=.8, toughness=8, normality=2, cost=10, density=.05, p_ratio = .2, craft_diff = .1)
m_xthide = Material(name='Exotic Thick Hide', hardness=.7, elasticity=.9, toughness=8, normality=.5, cost=20, density=.08, p_ratio = .47, craft_diff = .4)
m_wood = Material(name='Wood', hardness=1, elasticity=1, toughness=1, normality=2, cost=1, density=1, p_ratio = .47, craft_diff = .1)
m_bone = Material(name='Bone', hardness=1.3, elasticity=1.8, toughness=1.2, normality=2, cost=5, density=.8, p_ratio = .4, craft_diff = .2)
m_tissue = Material(name='Tissue', hardness=.1, elasticity=.01, toughness=3, normality=2, cost=1, density=1, p_ratio = .46, craft_diff = 1)
m_copper = Material(name='Copper', hardness=12, elasticity=10, toughness=7, normality=.2, cost=10, density=11, p_ratio = .33, craft_diff = 0)
m_bronze = Material(name='Bronze', hardness=26, elasticity=12, toughness=6, normality=.1, cost=12, density=10, p_ratio = .3, craft_diff = 0)
m_iron = Material(name='Iron', hardness=35, elasticity=21, toughness=2, normality=1, cost=2, density=9, p_ratio = .26, craft_diff = 0)
m_hiron = Material(name='Hardened Iron', hardness=43, elasticity=21, toughness=1.5, normality=.9, cost=5, density=9, p_ratio = .21, craft_diff = 0)
m_steel = Material(name='Steel', hardness=57, elasticity=20, toughness=.5, normality=.7, cost=15, density=9, p_ratio = .3, craft_diff = 0)
m_hsteel = Material(name='Hardened Steel', hardness=64, elasticity=20, toughness=.5, normality=.6, cost=20, density=9, p_ratio = .27, craft_diff = 0)
m_ssteel = Material(name='Stygian Steel', hardness=71, elasticity=20, toughness=.4, normality=.2, cost=25, density=9, p_ratio = .27, craft_diff = 0)
m_hssteel = Material(name='Hardened Stygian Steel', hardness=86, elasticity=20, toughness=.4, normality=.1, cost=35, density=9, p_ratio = .27, craft_diff = 0)
m_mithril = Material(name='Mithril', hardness=100, elasticity=18, toughness=.8, normality=.1, cost=80, density=6, p_ratio = .2, craft_diff = 0) #Ultra materials are always hardened
m_adam = Material(name='Adamantine', hardness=150, elasticity=22, toughness=1, normality=.001, cost=160, density=10, p_ratio = .15, craft_diff = 0) #Ultra materials are always hardened
m_gold = Material(name='Gold', hardness=10, elasticity=8, toughness=10, normality=.001, cost=82000, density=23, p_ratio = .42, craft_diff = 0) 
m_hgold = Material(name='Half-Gold', hardness=11, elasticity=9, toughness=8, normality=.01, cost=40000, density=16, p_ratio = .44, craft_diff = 0) #Roughly 14K gold
m_silver = Material(name='Silver', hardness=10, elasticity=8, toughness=10, normality=.07, cost=1000, density=13, p_ratio = .4, craft_dif = 0) 
m_granite = Material(name='Granite', hardness=7, elasticity=5, toughness=.1, normality=3, cost=1, density=3, p_ratio = .2, craft_diff = 0) 
m_obsidian = Material(name='Obsidian', hardness=30, elasticity=25, toughness=.01, normality=.5, cost=15, density=2, p_ratio = .3, craft_diff = 0) 



master_material_list = Material._allMaterials
material_dict = {}

for m in master_material_list:
    material_dict[m.name] = m