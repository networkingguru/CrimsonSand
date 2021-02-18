import global_vars
from math import sqrt
from random import uniform
from utilities import itersubclasses, clamp, roll_dice
from components.material import (m_steel, m_leather, m_wood, m_tissue, m_bone, m_adam, m_bleather, m_bronze, m_canvas, m_cloth, m_copper, m_gold, m_granite, m_hgold,
    m_hsteel, m_ssteel, m_hssteel, m_iron, m_hiron, m_mithril, m_silver, m_hide, m_xthide, material_dict)


quality_dict = {'Junk': .5, 'Very Poor': .3, 'Poor': .2, 'Below Average': .1, 'Average': 1, 'Above Average': 1.15, 'Fine': 1.3, 'Exceptional': 1.4, 'Masterwork': 1.5}

#Generator Function
def gen_armor(armor_component, **kwargs):
    #Modes: 
    #1. Entity: Given an entity and (optional) kwargs, generate armor components to fit entity
    #2. Comparision: Set comparison kwarg to True, and given (optional) kwargs, will generate identical armors with every combination of main_material and contruction for comparison
    #3. Random: If the other modes are not set, generate x completely random armors. Will use kwargs if given to fix certain attributes.


    #Set vars for kwargs
    amount = kwargs.get('amount')
    random = kwargs.get('random')
    main_material = kwargs.get('main_material')
    binder = kwargs.get('binder')
    construction = kwargs.get('construction')
    thickness = kwargs.get('thickness')
    ht_range = kwargs.get('ht_range')
    str_fat_range = kwargs.get('str_fat_range')
    accent_material = kwargs.get('accent_material')
    accent_amount = kwargs.get('accent_amount')
    const_obj = kwargs.get('const_obj')
    comparison = kwargs.get('comparison')
    entity = kwargs.get('entity')
    quality = kwargs.get('quality')
    cost = kwargs.get('cost')

    if amount == None:
        amount = 1
    if random == None:
        random = True
    if comparison == None:
        comparison = False

    #List of components
    components = []

    #Create dummy component
    a = armor_component()

    if entity is not None:
        ht_min = entity.fighter.height
        ht_max = ht_min + a.ht_range[1] - a.ht_range[0]
        sf_min  = entity.fighter.get_attribute('str') + entity.fighter.get_attribute('fat')
        sf_max = sf_min + a.str_fat_range[1] - a.str_fat_range[0]
        ht_range = (ht_min, ht_max)
        str_fat_range = (sf_min,sf_max)

        if thickness == None:
            thickness = .1
        if construction == None:
            for construct in a.allowed_constructions:
                c = construct()
                if binder not in c.allowed_binder_materials or binder == None:
                    binder = c.allowed_binder_materials[0]
                if main_material not in c.allowed_main_materials:
                    if construct != a.allowed_constructions[-1]:
                        continue
                    else:
                        main_material = c.allowed_main_materials[0]                    
                elif main_material == None:
                    main_material = c.allowed_main_materials[0]
                construction = construct
        else:
            c = construction()
            if binder not in c.allowed_binder_materials or binder == None:
                binder = c.allowed_binder_materials[0]
            if main_material not in c.allowed_main_materials or main_material == None:
                main_material = c.allowed_main_materials[0]

        const_obj = construction(main_material = main_material, binder_material = binder)

        c_kwargs = {'construction': const_obj, 'thickness': thickness, 'ht_range': ht_range, 'str_fat_range': str_fat_range, 'accent_amount': accent_amount, 'accent_material': accent_material, 'quality': quality}
        del_keys = []

        for key, value in c_kwargs.items():
            if value == None:
                del_keys.append(key)

        for key in del_keys:
            del c_kwargs[key]
        
        component = armor_component(**c_kwargs)
        components.append(component)

    
    
    elif comparison:
        if thickness == None:
            thickness = .1
        for construction in a.allowed_constructions:
            #Create dummy construction
            c = construction()
            for material in c.allowed_main_materials:
                if binder == None:
                    binder = c.allowed_binder_materials[0]
                
                const_obj = construction(main_material = material, binder_material = binder)

                component = armor_component(thickness = thickness, construction = const_obj)
                components.append(component)

                

    elif random:
        i=0
        while i < amount:
            c_kwargs = gen_random_armor(a, **kwargs)
            
            component = armor_component(**c_kwargs)

            while any(ele < 1000 for ele in [component.b_deflect,component.s_deflect_max,component.p_deflect_max,component.b_soak*20000]):
                if any(ele > 1000 for ele in [component.b_deflect,component.s_deflect_max,component.p_deflect_max,component.b_soak*20000]) and component.cost < cost:
                    break
                c_kwargs = gen_random_armor(a, **kwargs)
                component = armor_component(**c_kwargs)
                
            components.append(component)
            #Reset vars
            main_material = kwargs.get('main_material')
            binder = kwargs.get('binder')
            construction = kwargs.get('construction')
            thickness = kwargs.get('thickness')
            ht_range = kwargs.get('ht_range')
            str_fat_range = kwargs.get('str_fat_range')
            accent_material = kwargs.get('accent_material')
            accent_amount = kwargs.get('accent_amount')
            i += 1

    return components

def gen_random_armor(a, **kwargs):
    main_material = kwargs.get('main_material')
    binder = kwargs.get('binder')
    construction = kwargs.get('construction')
    thickness = kwargs.get('thickness')
    ht_range = kwargs.get('ht_range')
    str_fat_range = kwargs.get('str_fat_range')
    accent_material = kwargs.get('accent_material')
    accent_amount = kwargs.get('accent_amount')
    const_obj = kwargs.get('const_obj')
    quality = kwargs.get('quality')

    if construction == None:
        if len(a.allowed_constructions) > 1:
            construction = a.allowed_constructions[(roll_dice(1,len(a.allowed_constructions)))-1]
        else:
            construction = a.allowed_constructions[0]

    #Create dummy construction
    c = construction()
    if main_material == None:
        if len(c.allowed_main_materials) > 1:
            main_material = c.allowed_main_materials[(roll_dice(1,len(c.allowed_main_materials)))-1]
        else:
            main_material = c.allowed_main_materials[0]
        
    if binder == None: 
        if len(c.allowed_binder_materials) > 1:
            binder = c.allowed_binder_materials[(roll_dice(1,len(c.allowed_binder_materials)))-1]
        else:
            binder = c.allowed_binder_materials[0]
    
    const_obj = construction(main_material = main_material, binder_material = binder)
    
    if thickness == None:
        thickness = round(uniform(const_obj.min_thickness, const_obj.max_thickness), 2)

    if ht_range == None:
        ht_min = roll_dice(1,60) + 30
        ht_max = ht_min + a.ht_range[1] - a.ht_range[0]
        ht_range = (ht_min, ht_max)

    if str_fat_range == None:
        sf_min = (roll_dice(10,6)*10)
        sf_max = sf_min + a.str_fat_range[1] - a.str_fat_range[0]
        str_fat_range = (sf_min,sf_max)

    if accent_amount == None:
        accent_amount = round(uniform(.01,.1),2)

    if quality == None:
        quals = list(quality_dict.keys())
        quality = quals[(roll_dice(1,len(quals)-1))]

    c_kwargs = {'construction': const_obj, 'thickness': thickness, 'ht_range': ht_range, 'str_fat_range': str_fat_range, 'accent_amount': accent_amount, 'accent_material': accent_material, 'quality': quality}
    del_keys = []

    for key, value in c_kwargs.items():
        if value == None:
            del_keys.append(key)

    for key in del_keys:
        del c_kwargs[key]           

    return c_kwargs

#Application Function
def apply_armor(entity):
    #Used to automatically apply a list of armors generated from a definition string in an entity
    worn_armor = entity.worn_armor
    armor_objects = []
    error_msg = ''

    for num in worn_armor:
        components = itersubclasses(Armor_Component)
        for component in components:
            if num.get('component') == component.__name__:
                construction = num.get('construction')
                constructions = itersubclasses(Armor_Construction)
                for const in constructions:
                    if construction == const.__name__:
                        num['construction'] = const
                        num['armor_component'] = component
                        num['main_material'] = material_dict.get(num.get('main_material'))
                        num['entity'] = entity
                        armor_objects.extend(gen_armor(**num))
                        
    
    
    t_armors = []
    l_armors = []
    h_armors = []
    a_armors = []
    o_armors = []
    ao_lists = [t_armors,l_armors,h_armors,a_armors,o_armors]
    
    for ao in armor_objects:
        ao_type = armor_classifier(ao)
        if ao_type == 't':
            t_armors.append(ao)
        elif ao_type == 'l':
            l_armors.append(ao)
        elif ao_type == 'h':
            h_armors.append(ao)
        elif ao_type == 'a':
            a_armors.append(ao)
        else:
            o_armors.append(ao)


    for ao_list in ao_lists:
        #Sort by rigidity
        flex_ao = []
        semi_ao = []
        rigid_ao = []
        for ao in ao_list:
            if ao.rigidity == 'flexible':
                flex_ao.append(ao)
            elif ao.rigidity == 'semi':
                semi_ao.append(ao)
            else:
                rigid_ao.append(ao)
    
        for l in [flex_ao, semi_ao, rigid_ao]:
            #Sort by weight
            l.sort(key=lambda ao: ao.weight)
            for ao in l:
                #Check if valid to place
                error_msg = determine_validity(ao, entity)
                if error_msg != '':
                    print (error_msg)
                else:
                    for loc in ao.covered_locs:
                        entity.loc_armor[loc].append(ao)

    apply_armor_mods(entity)

#Utility function for apply_armor
def armor_classifier(armor_component) -> str:
    #Sort by general type based on location
    torso_locs = [3,4,5,6,9,10,13,14]
    leg_locs = [17,18,21,22,23,24,25,26]
    head_locs = [0,1,2]
    arm_locs = [7,8,11,12,15,16]
    other_locs = [19,20,17,18,27,28]

    for loc in torso_locs:
        if loc in armor_component.covered_locs:
            return 't'
    for loc in leg_locs:
        if loc in armor_component.covered_locs:
            return 'l'
    for loc in head_locs:
        if loc in armor_component.covered_locs:
            return 'h'
    for loc in arm_locs:
        if loc in armor_component.covered_locs:
            return 'a'
    for loc in other_locs:
        if loc in armor_component.covered_locs:
            return 'o'

#Armor sorter for store
def component_sort() -> dict:
    components = itersubclasses(Armor_Component)
    categories = {'t':[],'l':[],'h':[],'a':[],'o':[]}

    for comp in components:
        #Dummy component
        c = gen_armor(comp)
        cat = armor_classifier(c[0])
        categories[cat].append(c[0])

    return categories


#Determine if armor can be applied to layer
def determine_validity(armor_component, entity):
    error_message = ''

    for loc in armor_component.covered_locs:
        if len(entity.loc_armor[loc]) >= 1:
            top_layer = entity.loc_armor[loc][-1]
        else:
            top_layer = None
        if top_layer is None:
            continue
        elif armor_component.rigidity == 'rigid' and top_layer.rigidity == 'rigid' or armor_component.rigidity == 'semi' and top_layer.rigidity in ['rigid','semi']:
            error_message = 'Cannot apply ' + armor_component.name + '. ' + top_layer.name + ' is already applied. '

        thickness = sum(layer.thickness for layer in entity.loc_armor[loc])

        if thickness + armor_component.thickness > 1:
            error_message += 'Cannot apply ' + armor_component.name + '. Total armor thickness at ' + entity.fighter.name_location(loc) + ' exceeds 1 inch. '

        if error_message != '': break

    return error_message

def apply_armor_mods(entity):
    armor_objects = []
    total_stam = 0
    l_mod = 0
    m_mod = 0
    h_mod = 0 

    la_skill = entity.fighter.get_attribute('l_armor')
    ma_skill = entity.fighter.get_attribute('m_armor')
    ha_skill = entity.fighter.get_attribute('h_armor')

    for loc in entity.loc_armor:
        for ao in loc:
            if ao in armor_objects: continue
            else: armor_objects.append(ao)

    for ao in armor_objects:
        total_stam += ao.stam_drain
        if ao.density < .1:
            l_mod += ao.physical_mod
        elif ao.density <= .2:
            m_mod += ao.physical_mod
        else:
            h_mod += ao.physical_mod
    
    l_mod = clamp(l_mod - la_skill, 0)
    m_mod = clamp(m_mod - ma_skill, 0)
    h_mod = clamp(h_mod - ha_skill, 0)

    entity.fighter.mod_attribute('stam_drain', total_stam)
    entity.fighter.mod_attribute('armor_mod', l_mod + m_mod + h_mod)


#Class Definitions
class Armor_Construction:
    def __init__(self, **kwargs):
        self.name = ''
        self.base_name = ''
        self.allowed_main_materials = [] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_steel #Primary material
        self.min_thickness = .001
        self.max_thickness = 1
        self.allowed_binder_materials = [] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 1 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.binder_name = ''
        self.desc = ''
        self.rigidity = 'rigid' #rigid, semi, or flexible
        self.density = 1 #Scalar to represent main material density, in terms of how much material vs binder/air is in the armor per inch of thickness. For example, steel chainmail is mostly holes, so it is much less dense than steel plate. Even plate is not 1, though, because the thickness is not uniform
        self.coverage = 1 #Scalar to represent how much area is covered by the main material. Plate would be 1, ring would be very low
        self.balance = 1 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1
        self.t_resist = 1
        self.construction_diff = 1 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        

    def set_name(self):
        if len(self.allowed_binder_materials) > 1:
            self.binder_name = ' with ' + self.binder_material.name + ' bindings '
        self.name = self.main_material.name + ' ' + self.base_name

class Armor_Component:
    def __init__(self, **kwargs):
        self.base_name = ''
        self.ht_range = () #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = () #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [] #List of Armor_Constructions that may be used
        self.construction = None
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1 #Scalar for base construction time
        self.covered_locs = [] #List of locations protected
        self.shape = '' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.desc = ''
        self.quality = 'Average'
        self.single_side = True #Used to differentiate between items that are R/L vs those that cover both
        #Dynamic attributes below
        self.name = ''
        self.main_area = 0
        self.weight = 0
        self.cost = 0
        self.thickness = 0 #Thickness in inches
        self.rigidity = '' #Set from construction
        self.b_deflect_max = 0 #PSI at which damage is no longer deflected
        self.s_deflect_max = 0 #PSI at which damage is no longer deflected
        self.p_deflect_max = 0 #PSI at which damage is no longer deflected
        self.t_deflect_max = 0 #PSI at which damage is no longer deflected
        self.b_deflect = 0 #% to deflect
        self.s_deflect = 0 #% to deflect
        self.p_deflect = 0 #% to deflect
        self.t_deflect = 0 #% to deflect
        self.hits = 0 #Overall structural hits
        self.max_hits = 0
        self.hits_sq_in = 0 #Hits required to breach one sq inch
        self.b_soak = 0 #Amount of force absorbed by padding. Percentage/Scalar
        self.physical_mod = 0 #Modifier to all physical actions due to armor. Reducable with armor skill
        self.stam_drain = 0 #Amount of stamina drained per round when wearing the armor
        self.density = 0 #Used to determine classification (light, medium, heavy)

        self.__dict__.update(kwargs)
        


    def set_dynamic_attributes(self):
        #Set thickness if it is not already set
        if self.thickness == 0:
            self.thickness = (self.construction.min_thickness + self.construction.max_thickness)/2
            if self.construction.main_material in [m_canvas,m_cloth, m_bone, m_wood]:
                self.thickness *= 10
            elif self.construction.main_material in [m_hide, m_xthide, m_leather, m_bleather]:
                self.thickness *= 5
          
        #Location circ calcs
        avg_ht = (self.ht_range[0] + self.ht_range[1] / 2)
        waist = avg_ht * (.3 + (self.str_fat_range[1]/1000)) 
        shoulder = waist * 1.6
        arm = waist * .45
        leg = waist * .7
        head = avg_ht * .3

        #Find surface area
        location_ratios = (1, .9, .87, .82, .82, .8, .8, .7, .7, .72, .72, .63, .63, .6, .6, .55, .55, .53, .53, .49, .49, .4, .4, .29, .29, .2, .2, .04, .04)
        min_ht = avg_ht
        max_ht = 0
        #Determine widest hit location
        if any(elem in [3,4,5,6,9,10] for elem in self.covered_locs):
            circ = shoulder
        elif any(elem in [13,14,17,18] for elem in self.covered_locs):
            circ = waist
        elif any(elem in [2,7,8,11,12,15,16,19,20] for elem in self.covered_locs):
            circ = arm
        elif any(elem in range(21,29) for elem in self.covered_locs):
            circ = leg
        else:
            circ = head

        if self.shape == 'h_cyl':
                circ /= 2

        #Find height 
        for loc in self.covered_locs:
            loc_ht = location_ratios[loc]*avg_ht
            if loc_ht > max_ht: max_ht = loc_ht
            if loc_ht < min_ht: min_ht = loc_ht

        height = max_ht - min_ht

        #Handle armor with single hit loc and therefore no height
        if height == 0:
            #Handle helmets
            if self.covered_locs[0] == 0:
                height = location_ratios[0]*avg_ht - location_ratios[1]*avg_ht
            else:
                min_ht = location_ratios[self.covered_locs[0]]*avg_ht
                max_ht = location_ratios[(self.covered_locs[0] - 1)]*avg_ht
            
                height = max_ht - min_ht

        self.main_area = circ * height

        construction_vol = self.thickness * self.main_area * self.construction.coverage
        construction_wt = construction_vol * (self.construction.density * (self.construction.main_material.density * .03))
        binder_wt = (self.construction.binder_amount * construction_vol) * (self.construction.binder_material.density * .03)
        accent_wt = (self.accent_amount * construction_vol) * (self.accent_material.density * .03)

        self.weight = construction_wt + binder_wt + accent_wt

        construction_cost = construction_vol * self.construction.main_material.cost * self.construction.construction_diff 
        binder_cost = construction_vol * self.construction.binder_amount * self.construction.binder_material.cost
        accent_cost = construction_vol * self.accent_amount * self.accent_material.cost

        self.cost = (construction_cost + binder_cost + accent_cost) * self.assembly_diff * quality_dict.get(self.quality)

        self.rigidity = self.construction.rigidity

        if self.rigidity == 'rigid':
            self.b_deflect = .2
            self.s_deflect = .5
            self.p_deflect = .8
            self.t_deflect = 1
            self.physical_mod = ((self.weight / 2) * self.construction.balance)*2
        elif self.rigidity == 'semi':
            self.b_deflect = .1
            self.s_deflect = .35
            self.p_deflect = .5
            self.t_deflect = .5
            self.physical_mod = (self.weight * self.construction.balance)*2
        else:
            self.b_deflect = .05
            self.s_deflect = .1
            self.p_deflect = .1
            self.t_deflect = .3
            self.physical_mod = ((self.weight * 2) * self.construction.balance)*2

        for i in [self.b_deflect, self.s_deflect, self.p_deflect, self.t_deflect]:
            i *= quality_dict.get(self.quality)

        self.b_deflect *= self.construction.b_resist
        self.p_deflect *= self.construction.p_resist
        self.s_deflect *= self.construction.s_resist
        self.t_deflect *= self.construction.t_resist
        
        #Hits calc is attempting to model shear stress
        self.hits = (self.construction.main_material.hardness * 15000) * self.thickness * self.construction.density * self.construction.coverage * construction_vol * self.construction.main_material.toughness * ((self.construction.main_material.elasticity)/2) 
        self.hits_sq_in = self.hits / self.main_area

        deflect_max = (sqrt(self.construction.main_material.hardness))/8 * self.hits_sq_in

        self.b_deflect_max = deflect_max * 5
        self.s_deflect_max = deflect_max
        self.p_deflect_max = deflect_max
        self.t_deflect_max = deflect_max * 25

        self.b_soak = round(.045/self.construction.main_material.hardness * self.thickness, 3)

        qual = ''

        if self.quality != 'Average':
            qual = self.quality + ' '

        self.name = qual + self.construction.name + ' ' + self.base_name + self.construction.binder_name

        self.stam_drain = self.physical_mod / self.weight

        self.max_hits = self.hits

        self.density = self.weight / (self.main_area/100)

#Constructions

class Hide(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = ''        
        self.allowed_binder_materials = [m_leather] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 0 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .05
        self.max_thickness = .2
        self.desc = 'Minimally processed animal hide'
        self.allowed_main_materials = [m_hide, m_xthide] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_hide #Primary material
        self.rigidity = 'flexible' #rigid, semi, or flexible
        self.density = 1 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = 1 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = 1 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1
        self.t_resist = 1
        self.construction_diff = .1 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.set_name()

class Leather(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = ''
        self.allowed_binder_materials = [m_leather] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 0 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .1
        self.max_thickness = .5
        self.desc = 'Treated animal hide'
        self.allowed_main_materials = [m_leather, m_bleather] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_leather #Primary material
        self.rigidity = 'flexible' #rigid, semi, or flexible
        self.density = 1 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = 1 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = 1 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1
        self.t_resist = 1
        self.construction_diff = .3 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.set_name()

class Padded(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = ''
        self.allowed_binder_materials = [m_leather] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 0 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .05
        self.max_thickness = 1
        self.allowed_main_materials = [m_cloth, m_canvas] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_cloth #Primary material
        self.rigidity = 'flexible' #rigid, semi, or flexible
        self.density = 1 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = 1 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = 1 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1
        self.t_resist = 1
        self.construction_diff = .2 #Scalar for difficulty of construction     

        self.__dict__.update(kwargs)
        self.desc = 'Padded ' + self.main_material.name.lower()

        self.set_name()   

class Chain(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = 'Chainmail'
        self.allowed_binder_materials = [m_leather] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 0 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .1
        self.max_thickness = .25
        self.allowed_main_materials = [m_copper, m_bronze, m_iron, m_hiron, m_steel, m_hsteel, m_ssteel, m_hsteel, m_mithril, m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_hiron #Primary material
        self.rigidity = 'flexible' #rigid, semi, or flexible
        self.density = .2 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = .6 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = 1.2 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = .7
        self.t_resist = 1
        self.construction_diff = 1 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.desc = 'Small, densely packed interlocking ' + self.main_material.name.lower() + ' rings'
        self.set_name()

class Ring(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = 'Ringmail'
        self.allowed_binder_materials = [m_leather, m_cloth, m_canvas] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 1.2 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .1
        self.max_thickness = .25
        self.allowed_main_materials = [m_copper, m_bronze, m_iron, m_hiron, m_steel, m_hsteel, m_ssteel, m_hsteel, m_mithril, m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_hiron #Primary material
        self.rigidity = 'flexible' #rigid, semi, or flexible
        self.density = .05 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = .4 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = 1 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = .3
        self.t_resist = .5
        self.construction_diff = .5 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.desc = 'Large ' + self.main_material.name.lower() + ' rings sewn onto a ' + self.binder_material.name.lower() + ' surface'
        self.set_name()
        
class Splint(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = 'Splintmail'
        self.allowed_binder_materials = [m_leather, m_cloth, m_canvas] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 1.3 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .05
        self.max_thickness = .25
        self.allowed_main_materials = [m_copper, m_bronze, m_iron, m_hiron, m_steel, m_hsteel, m_ssteel, m_hsteel, m_mithril, m_adam, m_wood, m_bone] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_hiron #Primary material
        self.rigidity = 'semi' #rigid, semi, or flexible
        self.density = .4 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = .8 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = 1 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1.1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = .8
        self.t_resist = 1
        self.construction_diff = .8 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.desc = 'Large, long ' + self.main_material.name.lower() + ' segments sewn onto a ' + self.binder_material.name.lower() + ' backing'
        self.set_name()

class Scale(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = 'Scalemail'
        self.allowed_binder_materials = [m_leather, m_cloth, m_canvas] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 1.1 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .03
        self.max_thickness = .2
        self.allowed_main_materials = [m_leather, m_bleather, m_copper, m_bronze, m_iron, m_hiron, m_steel, m_hsteel, m_ssteel, m_hsteel, m_mithril, m_adam, m_wood, m_bone] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_hiron #Primary material
        self.rigidity = 'semi' #rigid, semi, or flexible
        self.density = .3 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = .9 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = 1.1 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1.2
        self.t_resist = 1
        self.construction_diff = 2 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.desc = 'Small ' + self.main_material.name.lower() + ' scales arranged in rows and attached to each other and a ' + self.binder_material.name.lower() + ' backing'
        self.set_name()

class Lamellar(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = 'Lamellar'
        self.allowed_binder_materials = [m_leather] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 0 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .03
        self.max_thickness = .25
        self.desc = 'Small plates arranged in rows and attached to each other with a high amount of overlap'
        self.allowed_main_materials = [m_leather, m_bleather, m_copper, m_bronze, m_iron, m_hiron, m_steel, m_hsteel, m_ssteel, m_hsteel, m_mithril, m_adam, m_wood, m_bone] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_hiron #Primary material
        self.rigidity = 'semi' #rigid, semi, or flexible
        self.density = .1 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = .85 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = 1.2 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1.4
        self.t_resist = 1
        self.construction_diff = 2 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.desc = 'Small ' + self.main_material.name.lower() + ' plates arranged in rows and attached to each other with a high amount of overlap'
        self.set_name()

class Brigandine(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = 'Brigandine'
        self.allowed_binder_materials = [m_leather, m_cloth, m_canvas] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = 2 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .05
        self.max_thickness = .25
        self.desc = 'Irregular plates arranged to suit anatomy sandwitched between layers of dense cloth'
        self.allowed_main_materials = [m_bronze, m_iron, m_hiron, m_steel, m_hsteel, m_ssteel, m_hsteel, m_mithril, m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_hiron #Primary material
        self.rigidity = 'semi' #rigid, semi, or flexible
        self.density = .05 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = .95 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = 1 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1.4
        self.t_resist = 1
        self.construction_diff = 2.2 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.desc = 'Irregular ' + self.main_material.name.lower() + ' plates arranged to suit anatomy sandwitched between layers of  ' + self.binder_material.name.lower() 
        self.set_name()

class Plate(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = 'Plate'
        self.allowed_binder_materials = [m_leather] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = .3 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .03
        self.max_thickness = .15
        self.allowed_main_materials = [m_bleather, m_wood, m_bronze, m_iron, m_hiron, m_steel, m_hsteel, m_ssteel, m_hssteel, m_mithril, m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_hiron #Primary material
        self.rigidity = 'rigid' #rigid, semi, or flexible
        self.density = .1 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = 1 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = .8 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1
        self.t_resist = 1
        self.construction_diff = 3 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.desc = 'Interlocking and overlapping ' + self.main_material.name.lower() + ' plates configured to conform to anatomy with minimal gaps'
        self.set_name()

class Double_Plate(Armor_Construction):
    def __init__(self, **kwargs):
        Armor_Construction.__init__(self)
        self.base_name = 'Double-walled Plate'
        self.allowed_binder_materials = [m_leather] #List of allowed materials for binder components
        self.binder_material = m_leather #Material that holds the armor together
        self.binder_amount = .4 #Scalar. 1 = 1:1 ratio of binder to main volume
        self.min_thickness = .04
        self.max_thickness = .2
        self.allowed_main_materials = [m_steel, m_hsteel, m_ssteel, m_hssteel, m_mithril, m_adam] # List of materials applicable for the main surface. Young's modulus prevents copper and bronze swords longer than 24", for example
        self.main_material = m_hsteel #Primary material
        self.rigidity = 'rigid' #rigid, semi, or flexible
        self.density = .15 #Scalar to represent material density. For example, steel chainmail is less dense than steel plate
        self.coverage = 1 #Scalar to represent how much area is coverd by the main material. Plate would be 1, ring would be very low
        self.balance = .9 #Scalar to represent impact on overall balance. Used to apply negative modifiers for moving an attacking due to poor weight distribution.
        self.b_resist = 1.1 #Scalar to modify damage resistance
        self.s_resist = 1
        self.p_resist = 1.3
        self.t_resist = 1
        self.construction_diff = 8 #Scalar for difficulty of construction

        self.__dict__.update(kwargs)
        self.desc = 'Interlocking and overlapping ' + self.main_material.name.lower() + ' plates that include an inner and outer wall with an airgap in between'
        self.set_name()

#Components
class Coif(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Coif'
        self.ht_range = (36,84) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (0,600) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Chain,Ring,Hide,Leather,Padded] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .8 #Scalar for base construction time
        self.covered_locs = [0,2] #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = 'Armor hood made from ' + self.construction.main_material.name.lower() + ' that covers the top of the head and the neck'
        self.set_dynamic_attributes()

class Helm(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Helm'
        self.ht_range = (36,84) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (150,500) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Hide,Leather,Padded,Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .5 #Scalar for base construction time
        self.covered_locs = [0] #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = 'An open helmet made from ' + self.construction.main_material.name.lower() + ' that covers the top of the head'
        self.set_dynamic_attributes()

class Closed_Helm(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Closed Helm'
        self.ht_range = (48,84) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (200,450) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1 #Scalar for base construction time
        self.covered_locs = [0,1] #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = 'A closed helmet made from ' + self.construction.main_material.name.lower() + ' that covers the top of the head and face'
        self.set_dynamic_attributes()

class Bevor(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Bevor'
        self.ht_range = (54,78) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (200,400) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1 #Scalar for base construction time
        self.covered_locs = [1,2] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = 'A heavy ' + self.construction.main_material.name.lower() + ' covering for the neck and lower face'
        self.set_dynamic_attributes()

class Gorget(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Gorget'
        self.ht_range = (40,84) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (150,450) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Leather,Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .5 #Scalar for base construction time
        self.covered_locs = [2] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = 'A simple ' + self.construction.main_material.name.lower() + ' covering for the neck'
        self.set_dynamic_attributes()

class Hauberk(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Hauberk'
        self.ht_range = (66,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,400) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Leather,Hide,Padded,Chain,Ring,Lamellar,Brigandine] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 2.5 #Scalar for base construction time
        self.covered_locs = range(3,17) #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = 'A coat of ' + self.construction.name.lower() + ' armor that protects most of the upper body'
        self.set_dynamic_attributes()

class Curiass(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Curiass'
        self.ht_range = (60,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (200,450) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Leather,Scale,Splint,Lamellar,Brigandine,Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .5 #Scalar for base construction time
        self.covered_locs = [3,4,5,6,9,10,13,14] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = 'A sleeveless breastplate of ' + self.construction.name.lower() + ' armor that protects the upper body'
        self.set_dynamic_attributes()

class Pixane(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Pixane'
        self.ht_range = (40,84) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (150,450) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Leather,Padded,Chain] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .5 #Scalar for base construction time
        self.covered_locs = [3,4,5,6] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = 'A long segment of ' + self.construction.name.lower() + ' armor that protects the neck and upper chest'
        self.set_dynamic_attributes()

class Culet(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Culet'
        self.ht_range = (50,78) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,400) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Hide,Leather,Chain,Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1 #Scalar for base construction time
        self.covered_locs = [17,18] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = 'A covering of ' + self.construction.name.lower() + ' armor that protects the hips'
        self.set_dynamic_attributes()

class Couter(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Couter'
        self.ht_range = (36,84) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (150,500) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1 #Scalar for base construction time
        self.covered_locs = [11,12] #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'A covering of ' + self.construction.name.lower() + ' armor that protects the elbows'
        self.set_dynamic_attributes()

class Spaulder(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Spaulder'
        self.ht_range = (50,78) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (200,350) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1 #Scalar for base construction time
        self.covered_locs = [3,4] #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'A section of ' + self.construction.name.lower() + ' armor that protects the shoulders'
        self.set_dynamic_attributes()

class Pauldron(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Pauldron'
        self.ht_range = (66,78) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (200,300) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1.5 #Scalar for base construction time
        self.covered_locs = range(3,9) #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'A complex section of ' + self.construction.name.lower() + ' armor that protects the shoulders, chest, and upper arms'
        self.set_dynamic_attributes()

class Brassart(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Brassart'
        self.ht_range = (66,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (200,300) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .3 #Scalar for base construction time
        self.covered_locs = [7,8] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'A simple cylinder of ' + self.construction.name.lower() + ' armor that protects the upper arm'
        self.set_dynamic_attributes()

class Vambrace(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Vambrace'
        self.ht_range = (66,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (200,300) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Leather,Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .3 #Scalar for base construction time
        self.covered_locs = [15,16] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'A simple cylinder of ' + self.construction.name.lower() + ' armor that protects the lower arm'
        self.set_dynamic_attributes()

class Gauntlet(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Gauntlet'
        self.ht_range = (66,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (150,450) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Leather,Scale,Brigandine,Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 3 #Scalar for base construction time
        self.covered_locs = [19,20] #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'A complex construction using ' + self.construction.name.lower() + ' armor to protect the hand and fingers'
        self.set_dynamic_attributes()

class Chauses(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Chauses'
        self.ht_range = (60,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,400) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Padded,Leather,Chain,Scale,Lamellar,Brigandine] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1.5 #Scalar for base construction time
        self.covered_locs = range(21,27) #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'
        self.single_side = False #Used to differentiate between items that are R/L vs those that cover both

        self.__dict__.update(kwargs)
        self.desc = self.construction.name + ' armor to protect the legs'
        self.set_dynamic_attributes()

class Polyen(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Polyen'
        self.ht_range = (66,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,350) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1.5 #Scalar for base construction time
        self.covered_locs = [23,24] #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'A complex construction using ' + self.construction.name.lower() + ' armor to protect the knees'
        self.set_dynamic_attributes()

class Greave(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Greave'
        self.ht_range = (60,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,450) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .3 #Scalar for base construction time
        self.covered_locs = [25,26] #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'A half-cylinder of ' + self.construction.name.lower() + ' armor to protect lower legs'
        self.set_dynamic_attributes()

class Cuisse(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Cuisse'
        self.ht_range = (60,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,350) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Plate,Double_Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .7 #Scalar for base construction time
        self.covered_locs = [21,22] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'An articulated cylinder of ' + self.construction.name.lower() + ' armor to protect upper legs'
        self.set_dynamic_attributes()

class Sabaton(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Sabaton'
        self.ht_range = (66,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,450) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Chain,Plate] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1.5 #Scalar for base construction time
        self.covered_locs = [27,28] #List of locations protected
        self.shape = 'h_cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = self.construction.name + ' armor in a complex arrangement to cover the top of the foot'
        self.set_dynamic_attributes()

class Boot(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Boot'
        self.ht_range = (66,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,450) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Leather] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1 #Scalar for base construction time
        self.covered_locs = [27,28] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.desc = 'A sturdy boot reinforced for combat'
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.set_dynamic_attributes()

class Jerkin(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Jerkin'
        self.ht_range = (54,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,450) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Padded,Leather] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = 1 #Scalar for base construction time
        self.covered_locs = [3,4,5,6,9,10,13,14] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'A vest made of ' + self.construction.main_material.name.lower() + ' to protect the torso'
        self.set_dynamic_attributes()

class Breeches(Armor_Component):
    def __init__(self, **kwargs):
        Armor_Component.__init__(self)
        self.base_name = 'Breeches'
        self.ht_range = (60,72) #Tuple containing min and max ht supported by the armor 
        self.str_fat_range = (250,350) #Tuple containing min and max str/fat combination supported by the armor (girth)
        self.allowed_constructions = [Padded,Leather] #List of Armor_Constructions that may be used
        self.construction = self.allowed_constructions[0]()
        self.accent_material = m_steel #Material used for decorations
        self.accent_amount = 0 #Scalar. 1 = 1:1 ratio of accent to main volume
        self.assembly_diff = .5 #Scalar for base construction time
        self.covered_locs = [17,18,21,22,23,24,25,26] #List of locations protected
        self.shape = 'cyl' #Used to approximate area. Valid shapes: cyl, h_cyl
        self.quality = 'Average'

        self.__dict__.update(kwargs)
        self.desc = 'Pants made of ' + self.construction.main_material.name.lower() + ' to protect the lower body'
        self.set_dynamic_attributes()


