
'''
    Conc's Metaclass


    Remove's kwargs to Conc __init__ and stores them in the Conc.

    And generates Names (i.e. proxies) for the Conc.
'''



from inspect import stack, getmodule
from Name import proxy



class ConcMeta(type):
    def __call__(cls, *args, **kwargs):
        # create the instance of the Conc subclass
        obj = cls.__new__(cls, *args, **kwargs)

        # remove kwargs intended for Conc and Corps and store them
        ConcAddr = 'ConcAddr'
        if ConcAddr in kwargs:
            obj.ConcAddr = kwargs[ConcAddr]
            del kwargs[ConcAddr]

        ConfigFiles = 'ConfigFiles'
        if ConfigFiles in kwargs:
            obj.ConfigFiles = kwargs[ConfigFiles]
            del kwargs[ConfigFiles]

        # initialize the instance
        obj.__init__(*args, **kwargs)
        return obj


    def __init__(cls, name, bases, dct):
        super(ConcMeta, cls).__init__(name, bases, dct)

        #print(f'\nmetaclass init: {name} inherits from mro: {cls.mro()}\n')

        # generate a Name (i.e. a proxy) for the Conc subclass (except Name itself) in the calling module
        mro = cls.mro()
        if mro[0].__module__ != 'Name':
            frm = stack()[1]
            CallingModule = getmodule(frm[0])
            ClassProxy = proxy(cls, mro[0].__name__ + 'Name', CallingModule)

