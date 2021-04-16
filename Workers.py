
'''
    c r e a t e _ C o r p s ( )

    Creates a Corps.

    create_Corps(CorpsClass, *args, ConfigFiles=[], **kwargs)

        CorpsClass is the class of the Corps to load.

        ConfigFiles is a list of Config file names.  See the Config Files entry below for a list of possible
            parameter entries in the Config File.  The Config files are processed in order - later entries for the
            same parameter override earlier ones.

        *args and **kwargs are regular parameters to the Corps class's __init__



    c r e a t e _ C o n c s ( )

    Factory function to create Concs.

    create_Concs(ConcClass, *args, Mgr=None, LocType=LocType.Auto, LocVal=None, Num=1, **kwargs)

        Returns a list of Names of Concs.

        Mgr is the Manager of the Concs.  This an optional argument.

            Caller should use self.my_Name() and a Conc can access using self.my_Mgr().

        LocType

            LocType.EnvId
                Create Num Concs in caller-chosen Env

            LocType.Auto
                Create Num Concs in Corps Python-chosen Env

            LocType.PerEnv
                Create Num Concs in every Env

        LocVal
            Integer
                value >= 0
                For LocType=LocType.EnvId

            None
                For LocType=LocType.Auto or LocType.PerEnv

        Num:
            Number of Concs per Loc

        *args and **kwargs are regular parameters to Conc class's __init__

'''


'''
    Future Ideas:
    
        - create_Corps()

            - Ext=True
                - False for Cont Corps, True for Ext Corps

            - Tag=TagName
                - default 'None'

            - Mgr=Name
                - default is auto chosen as creating Corps
                
            - Loc=
                LocType.Auto LocVal=None
                    -default
                                
                LocType.Host LocVal=name/ip
                
                LocType.Cluster LocVal=ClusterName
                    - Name denotes a Conc or Corps?
                    - type of Auto Loc (that restricts it)
                    
                LocType.Region LocVal=RegionName
                    - Name denotes a Conc or Corps?
                    - type of Auto Loc (that restricts it)


        - delete_Workers()
            - Not implemented yet


        - linkto()
            - link (i.e. become Mgr of) an existing Ext Corps 
            - Not implemented yet
            - HostPort=(name/ip, port) or Dir=DirName
            

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
from ConcAddr import ConcAddr, ExtAddr
from Name import proxy, Name
from Env import EnvName    # EnvName dynamically genned by proxy()
from EnvGlobals import _ConcIdMgr, my_EnvId, _Addr2Conc, _EnvTable, my_Port, my_Ip, my_EnvStatus
from EnvAddrSpace import CORPSMGR_ENVID
from ConcIdMgr import ENVMGR_CONCID, CORPS_CONCID
from enum import IntEnum
from Conc import Conc
from Corps import Corps
from sys import exc_info
from Exceptions import AsyncExecutionError
from traceback import format_exception
from importlib import import_module
from multiprocessing import Process, Queue
from CorpsStatus import MajorStatus



class LocType(IntEnum):
    # Conc or Func
    EnvId = 0
    PerEnv = 1

    # Conc, Func, or Corps
    Auto = 2

    # Corps
    Host = 3
    Cluster = 4
    Region = 5

##############################

#  Managed vs unmanaged in Api  ?????

###############################
def create_Corps(CorpsClass, *args, Mgr=None, Tag="No Name", Ext=True, ConfigFiles=[], \
                                                                        LocType=LocType.Auto, LocVal=None, **kwargs):
    ''' create an ExtCorps from a script or an ExtCorps or ContCorps from calling Corps '''

    assert issubclass(CorpsClass, Corps) == True, f'{CorpsClass.__name__} is not a type of Corps'

    frm = stack()[1]
    CallingModule = getmodule(frm[0])

    # Store kwargs for new Corps (will be processed by ConcMeta)
    kwargs['Tag'] = Tag
    kwargs['Ext'] = Ext
    kwargs['ConfigFiles'] = ConfigFiles

    # Create ExtCorps on this Host from a Script caller (Ext must be True)
    # Mgr stays None for ExtCorps w/ no Mgr
    EnvStatus = my_EnvStatus()
    if EnvStatus == MajorStatus.Running:
        print(f'create_Corps "{Tag}"  E n v S t a t u s: {MajorStatus.Running.name} == {EnvStatus.name}?')
        return

    elif EnvStatus == MajorStatus.Nonexistent:
        print(f'create_Corps "{Tag}"  E n v S t a t u s: {MajorStatus.Nonexistent.name} == {EnvStatus.name}?')

        WorkerQueue = Queue()

        NewCorpsProcess = Process(target=__other_process_create_Corps__, \
                              args=(CallingModule.__name__, CorpsClass.__name__, WorkerQueue, *args), kwargs=kwargs)
        NewCorpsProcess.start()

        NewCorpsData = WorkerQueue.get()
        NewCorpsIp = NewCorpsData[0]
        NewCorpsPort = NewCorpsData[1]


    NewConcAddr = ExtAddr(CORPSMGR_ENVID, CORPS_CONCID, CORPSMGR_ENVID, NewCorpsIp, NewCorpsPort)

    ConcClassProxy = proxy(CorpsClass, CorpsClass.__name__+'Name', CallingModule)
    NewProxy = ConcClassProxy(NewConcAddr)
    NewName = Name(NewProxy, CorpsClass.__name__, CallingModule.__name__)

    return NewName


def __other_process_create_Corps__(CallingModule, CorpsClass, WorkerQueue, *args, **kwargs):
    '''
        Create a Corps in a new process

        CallingModule and ConcClass are text names
    '''

    # Find the CorpsClass object
    TheCallingModule = import_module(CallingModule)
    ConcClassInModule = getattr(TheCallingModule, CorpsClass)

    # Create the Corps
    NewConc = ConcClassInModule(*args, **kwargs)

    # Return data to calling process
    WorkerQueue.put([my_Ip(), my_Port()])
    return True


def __create_local_Conc__(Mgr, CallingModule, ConcClass, *args, **kwargs):
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


def __create_remote_Conc__(Mgr, RemoteEnvId, CallingModule, ConcClass, *args, **kwargs):
    ''' low-level support for Conc creation in another Env '''

    ConcId = _ConcIdMgr.new()
    NewConcAddr = ConcAddr(my_EnvId(), ConcId, RemoteEnvId)

    ConcClassProxy = proxy(ConcClass, ConcClass.__name__+'Name', CallingModule)
    NewProxy = ConcClassProxy(NewConcAddr)
    NewName = Name(NewProxy, ConcClass.__name__, CallingModule.__name__)

    # create proxy for remote Env
    EnvConcAddr = ConcAddr(CORPSMGR_ENVID, ENVMGR_CONCID, RemoteEnvId)
    RemoteEnv = EnvName(EnvConcAddr)

    # request object creation in remote Env
    kwargs['ConcAddr'] = NewConcAddr
    FutRes = RemoteEnv.rem2loc_create_Conc(NewConcAddr, CallingModule.__name__, ConcClass.__name__, *args, **kwargs)

    try:
        Ret = FutRes.Ret

    except:
        ei = exc_info()
        ftb = format_exception(ei[0], ei[1], ei[2])
        raise AsyncExecutionError(ei[0].__name__, ei[1], ''.join(ftb))

    return NewName


def create_Concs(ConcClass, *args, Mgr=None, LocType=LocType.Auto, LocVal=None, Num=1, **kwargs):
    ''' Create Concs '''

    assert issubclass(ConcClass, Conc) == True, f'{ConcClass.__name__} is not a valid Conc class'

    frm = stack()[1]
    CallingModule = getmodule(frm[0])

    if Num < 1:
        return None

    if LocVal != None and LocVal > _EnvTable.num_Envs():
        raise IndexError(f'EnvId {LocVal} does not exist')

    TheWorkers = []

    if LocType == LocType.EnvId:
        for w in range(Num):
            if LocVal == my_EnvId():
                TheWorkers.append(__create_local_Conc__(Mgr, CallingModule, ConcClass, *args, **kwargs))

            else:
                TheWorkers.append(__create_remote_Conc__(Mgr, LocVal, CallingModule, ConcClass, *args, **kwargs))


    elif LocType == LocType.Auto:
        if LocVal != None:
            raise ValueError(f'LocType Auto must have LocVal None')

        for w in range(Num):
            AutoLoc = _EnvTable.next_AutoEnvId()

            if AutoLoc == my_EnvId():
                TheWorkers.append(__create_local_Conc__(Mgr, CallingModule, ConcClass, *args, **kwargs))

            else:
                TheWorkers.append(__create_remote_Conc__(Mgr, AutoLoc, CallingModule, ConcClass, *args, **kwargs))


    elif LocType == LocType.PerEnv:
        if LocVal != None:
            raise ValueError(f'LocType PerEnv must have LocVal None')

        for w in range(Num):
            NumEnvs = _EnvTable.num_Envs()
            for Loc in range(NumEnvs):
                if Loc == my_EnvId():
                    TheWorkers.append(__create_local_Conc__(Mgr, CallingModule, ConcClass, *args, **kwargs))

                else:
                    TheWorkers.append(__create_remote_Conc__(Mgr, Loc, CallingModule, ConcClass, *args, **kwargs))

    else:
        raise NotImplementedError(f'LocType {LocType} not supported')


    return TheWorkers


