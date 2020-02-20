import weakref

class Circumstance():
    _instances = set()
    def __init__(self, **kwargs):
        self.name = ''
        self.desc = ''
        self.mgmt = False #Enable or disable mgmt mode
        self.c_creation = True #Enable or disable character creation
        self.slave = False #Enable or disable slavery mode
        self.fight_income_scalar = .2 #Adjust percentage income to fighter
        self.mgmt_income_scalar = .8 #Adjust owner income. Total of fight/mgmt scalars should = 1
        self.score_mult = 1 #Adjust score multiplier
        self.diff = 'Normal'

        self._instances.add(weakref.ref(self))

        self.__dict__.update(kwargs)

        self.update_desc()


    def update_desc(self):
        desc_add = ''
        if self.slave:
            desc_add += 'You will receive free training and equipment, but no income. '
        elif self.c_creation:
            desc_add += 'You will receive '+str(self.fight_income_scalar*100)+'%% of the purse for each fight you personally win. You will be responsible for purchasing your own equipment, training, and medical care. '
        if not self.c_creation:
            desc_add += 'Character creation will be disabled for this run. '
        if not self.mgmt:
            desc_add += 'Management mode will be disabled for this run. '
        else:
            desc_add += 'You will be responsible for hiring gladiators, providing training and medical facilities, and potentially subsidizing or providing equipment for your gladiators. You will receive '+str(self.mgmt_income_scalar*100)+'%% of the purse for each fight any of your gladiators win. '

        desc_add += '\nDifficulty: '+self.diff

        desc_add += '\nScore Multiplier: '+str(self.score_mult)

        self.desc += desc_add

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
        

slave_desc = 'You have been enslaved and forced to participate in the games. '
slave = Circumstance(name='Slave', desc=slave_desc, slave=True, fight_income_scalar=0, mgmt_income_scalar=1, score_mult=3, diff='Easy')

cont_glad_desc = 'You are a contracted gladiator to a gladiator company. '
cont_glad = Circumstance(name='Contracted Gladiator', desc=cont_glad_desc, score_mult=4)


