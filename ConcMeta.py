
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

        # store kwargs intended for Conc and delete them (to hide from end-developers in __init__())
        ConcAddr = 'ConcAddr'
        if ConcAddr in kwargs:
            obj.ConcAddr = kwargs[ConcAddr]
            del kwargs[ConcAddr]

        Mgr = 'Mgr'
        if Mgr in kwargs:
            obj.Mgr = kwargs[Mgr]
            del kwargs[Mgr]

        # store kwargs intended for Corps and delete them (to hide from end-developers in __init__())
        ConfigFiles = 'ConfigFiles'
        if ConfigFiles in kwargs:
            obj.ConfigFiles = kwargs[ConfigFiles]
            del kwargs[ConfigFiles]

        ConfigDicts = 'ConfigDicts'
        if ConfigDicts in kwargs:
            obj.ConfigDicts = kwargs[ConfigDicts]
            del kwargs[ConfigDicts]

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

