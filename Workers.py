
'''
    l o a d _ C o r p s ( )

    Loads a Corps from a script.

    load_Corps(CorpsClass, *args, ConfigFiles=[], **kwargs)

        CorpsClass is the class of the Corps to load.

        ConfigFiles is a list of Config file names.  See the Config Files entry below for a list of possible
            parameter entries in the Config File.  The Config files are processed in order - later entries for the
            same parameter override earlier ones.

        *args and **kwargs are regular parameters to the Corps class's __init__



    c r e a t e _ W o r k e r s ( )

    Factory function to create Workers.  Only the creation of Concs inside of a Corps by a Corps or another Conc
    are supported at this point.

    create_Workers(Mgr, WorkerClass, *args, LocType=LocType.Auto, LocVal=None, Num=1, **kwargs)

        Returns a list of Names of Workers.

        Mgr is the Manager of the Worker.  Caller should use self.my_Name() at this time.

        LocType

            LocType.EnvId
                Create Num Workers in caller-chosen Env

            LocType.Auto
                Create Num Workers in Corps Python-chosen Env

            LocType.PerEnv
                Create Num Workers in every Env

        LocVal
            Integer
                value >= 0
                For LocType=LocType.EnvId

            None
                For LocType=LocType.Auto or LocType.PerEnv

        Num:
            Number of Workers per Loc

        *args and **kwargs are regular parameters to Worker class's __init__

'''


'''
    Future Ideas:
    
        - create_Corps(Mgr, CorpsClass, *args, LocType=LocType.Auto, LocVal=None, Num=1, Ext=False, ConfigFiles=[], \
                                                                                                            **kwargs)

            - Full interface to create Cont Corps and Ext Corps

            - Extends create_workers api

            - Not implemented yet

            - Ext=False for Cont Corps, True for Ext Corps

            - ConfigFiles=List of Config file names

            - Loc=
                - Same ones as for create_worker
                - For Ext Corps EnvId is invalid
                - Extra Loc values:
                    - Host=name/ip
                    - Cluster=Name
                        - Name denotes a Conc or Corps?
                        - type of Auto Loc (that restricts it)
                  - Region=Name
                        - Name denotes a Conc or Corps?
                        - type of Auto Loc (that restricts it)

            - Num=
                - Same ones as for create_worker


        - delete_Workers()
            - Not implemented yet


        - linkto()
            - link an existing Ext Corps 
            - Not implemented yet
            - HostPort=(name/ip, port) or Dir=DirName
            - Support for ContCorps?


        - nameof()
            - Not implemented yet


        - unlink()
            - Not implemented yet

            - Support for ContCorps?
            - Means EnvIds is no longer a sequential 1-N
                - But can still iterate normally


        - dir_reg()
            - register a Dir
            - Not implemented yet


        - dir_find()
            - Not implemented yet


        - join()
            - Corps can request being part of this Corps

            - Not implemented yet


        - leave()
            - Corps can request leaving this Corps

            - Not implemented yet
'''



from inspect import stack, getmodule
from ConcAddr import ConcAddr
from Name import proxy, Name
from Env import EnvName    # EnvName dynamically genned by proxy()
from EnvGlobals import _ConcIdMgr, my_EnvId, _Addr2Conc, _EnvTable
from EnvAddrSpace import CORPSMGR_ENVID
from ConcIdMgr import ENVMGR_CONCID
from enum import IntEnum
from Conc import Conc
from Corps import Corps



def load_Corps(ConcClass, *args, **kwargs):
    ''' script-level support for loading top-level Corps '''

    assert issubclass(ConcClass, Corps) == True, f'{ConcClass.__name__} is not a Corps'

    frm = stack()[1]
    CallingModule = getmodule(frm[0])

    ConcClassInModule = getattr(CallingModule, ConcClass.__name__)

    ConfigFiles = 'ConfigFiles'
    if ConfigFiles not in kwargs:
        kwargs[ConfigFiles] = []

    NewConc = ConcClassInModule(*args, **kwargs)
    NewConcAddr = NewConc.ConcAddr

    ConcClassProxy = proxy(ConcClass, ConcClass.__name__+'Name', CallingModule)
    NewProxy = ConcClassProxy(NewConcAddr)
    NewName = Name(NewProxy, ConcClass.__name__, CallingModule.__name__)

    return NewName


def __create_local_Conc(Mgr, CallingModule, ConcClass, *args, **kwargs):
    ''' low-level support for Conc creation in this Env '''

    ConcId = _ConcIdMgr.new()
    NewConcAddr = ConcAddr(my_EnvId(), ConcId, my_EnvId())

    ConcClassProxy = proxy(ConcClass, ConcClass.__name__+'Name', CallingModule)
    NewProxy = ConcClassProxy(NewConcAddr)
    NewName = Name(NewProxy, ConcClass.__name__, CallingModule.__name__)

    ConcClassInModule = getattr(CallingModule, ConcClass.__name__)

    kwargs['ConcAddr'] = NewConcAddr
    NewConc = ConcClassInModule(*args, **kwargs)
    
    _Addr2Conc.register(NewConc, NewConcAddr)

    return NewName


def __create_remote_Conc(Mgr, RemoteEnvId, CallingModule, ConcClass, *args, **kwargs):
    ''' low-level support for Conc creation in another Env '''

    ConcId = _ConcIdMgr.new()
    NewConcAddr = ConcAddr(my_EnvId(), ConcId, RemoteEnvId)

    ConcClassProxy = proxy(ConcClass, ConcClass.__name__+'Name', CallingModule)
    NewProxy = ConcClassProxy(NewConcAddr)
    NewName = Name(NewProxy, ConcClass.__name__, CallingModule.__name__)

    # create proxy for remote Env
    EnvConcAddr = ConcAddr(CORPSMGR_ENVID, ENVMGR_CONCID, RemoteEnvId)
    RemoteEnv = EnvName(EnvConcAddr)

    # call rem2loc_create_Conc
    kwargs['ConcAddr'] = NewConcAddr
    FutRes = RemoteEnv.rem2loc_create_Conc(NewConcAddr, CallingModule.__name__, ConcClass.__name__, *args, **kwargs)
    Ret = FutRes.Ret

    return NewName


class LocType(IntEnum):
    EnvId = 0
    Auto = 1
    PerEnv = 2


def __create_Workers__(Mgr, LocType, LocVal, Num, CallingModule, ConcClass, *args, **kwargs):
    ''' Internal create Workers '''

    from ConfigGlobals import NumEnvs

    assert issubclass(ConcClass, Conc) == True, f'{ConcClass.__name__} is not a valid Worker class'
    assert issubclass(ConcClass, Corps) == False, f'{ConcClass.__name__} is not a valid Worker class yet'

    if Num < 1:
        return None

    if LocVal != None and LocVal > NumEnvs:
        raise IndexError(f'EnvId {LocVal} does not exist')

    TheWorkers = []

    if LocType == LocType.EnvId:
        for w in range(Num):
            if LocVal == my_EnvId():
                TheWorkers.append(__create_local_Conc(Mgr, CallingModule, ConcClass, *args, **kwargs))

            else:
                TheWorkers.append(__create_remote_Conc(Mgr, LocVal, CallingModule, ConcClass, *args, **kwargs))


    elif LocType == LocType.Auto:
        if LocVal != None:
            raise ValueError(f'LocType Auto must have LocVal None')

        for w in range(Num):
            AutoLoc = _EnvTable.next_EnvId()

            if AutoLoc == my_EnvId():
                TheWorkers.append(__create_local_Conc(Mgr, CallingModule, ConcClass, *args, **kwargs))

            else:
                TheWorkers.append(__create_remote_Conc(Mgr, AutoLoc, CallingModule, ConcClass, *args, **kwargs))


    elif LocType == LocType.PerEnv:
        if LocVal != None:
            raise ValueError(f'LocType PerEnv must have LocVal None')

        for w in range(Num):
            for Loc in range(NumEnvs):
                if Loc == my_EnvId():
                    TheWorkers.append(__create_local_Conc(Mgr, CallingModule, ConcClass, *args, **kwargs))

                else:
                    TheWorkers.append(__create_remote_Conc(Mgr, Loc, CallingModule, ConcClass, *args, **kwargs))

    else:
        raise NotImplementedError(f'LocType {LocType} not supported')


    return TheWorkers



def create_Workers(Mgr, ConcClass, *args, LocType=LocType.Auto, LocVal=None, Num=1, **kwargs):
    '''
        External interface for creating Workers

        Identifies the calling module the Worker class defined in or imported to and calls
        the internal create Workers function
    '''
    '''    
        better formulation of CallingModule?:
            caller = inspect.currentframe().f_back
            print(f"f in {__name__}: called from module", caller.f_globals['__name__'])
    '''
    frm = stack()[1]
    CallingModule = getmodule(frm[0])

    return __create_Workers__(Mgr, LocType, LocVal, Num, CallingModule, ConcClass, *args, **kwargs)


