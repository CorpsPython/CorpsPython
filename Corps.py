'''
    A Corps is a large-grained Worker.  It is fronted by a Conc with the Corps' Api, so all Conc methods also apply
    to Corps.  Note that some may be overridden; their updated description appears here.


    _ _ i n i t _ _ ( )

    A Corps subclass's __init__() should call:
        super().__init__()


    c l e a n u p ( )

    When exit() is called on a Corps its cleanup() will automatically be called.  Should be overridden if the Corps
    has resources such as files to flush, database transactions to commit, etc.  Can call exit() on any of its
    Workers, including Corps, whether managed or unmanaged.


    e x i t ( )

    Should *not* be overridden by subclasses.  Can be called explicitly to cleanup and exit. Will be called automat-
    icaLLy if its Mgr Corps exits.  Best practice is for the Mgr Corps to make the call so it can ensure all existing
    references to the exiting Corps are negated.  Calls cleanup(), which should be overridden if the Corps has resources
    such as files to flush, database transactions to commit, etc.


    m y _ M g r ( )

    Returns an ExtName for the Mgr Corps (the Corp that created this instance), if any.  If the Corps is unmanaged it
    returns None.


    m y _ E x t N a m e ( )

    Returns a new ExtName of the Corps instance.  Used to return the instance ExtName or to pass the instance ExtName
    as a method or function argument to another Corps.

    Do not use my_Name(), inherited from conc, for that purpose.  Instead my_Name() should be used for Workers within
    the instance's logical address space, such as Concs and Funcs.

    Any Corps, including ContCorps, will not recognize the return from my_Name() passed to it as it is not within
    its own logical address space.

'''

'''
    Corps and CorpsMgr Concs


    Instantiate and cooperate with Envs to establish the run-time environment for a Corps
'''



from Conc import Conc
from ConcAddr import ConcAddr, ExtAddr, ConcAddr_to_ExtAddr
from EnvRecord import EnvRecord, XferEnvRecord, CorpsEnvRecord, XferCorpsEnvRecord
from Env import Env, EnvName    # EnvName is dynamically genned by proxy()
from EnvGlobals import TheThread, NullConcAddr, _ConcIdMgr, _Addr2Conc, DefaultEnvRecord, _EnvTable,  my_Ip, my_Port, \
    DefaultCorpsEnvRecord, _ExtCorpsEnvTable, _ContCorpsEnvTable, my_CorpsTag
from os import getpid, kill
from multiprocessing import Process, Queue
from EnvAddrSpace import MIN_ENVID, MIN_ENVID_plus_1, MAX_ENVID, CORPSMGR_ENVID
from ConcIdMgr import ENVMGR_CONCID, CORPSMGR_CONCID, CORPS_CONCID
from signal import SIGTERM
from logging import info
from CorpsStatus import MajorStatus, MinorStatus
import Workers
import time
from sys import exc_info
from Name import proxy, Name
from importlib import import_module



def EnvIdGen(MinEnvId, MaxEnvId):
    ''' Generator for EnvIds given a range of EnvIds '''
    for EnvId in range(MaxEnvId - MinEnvId + 1):
        yield EnvId + MinEnvId


def EnvNameGen(MinEnvId, MaxEnvId):
    ''' Generator for EnvMgr Names, given a range of EnvIds '''
    for EnvId in range(MaxEnvId - MinEnvId + 1):
        yield EnvName(ConcAddr(CORPSMGR_ENVID, ENVMGR_CONCID, EnvId + MinEnvId))


class CorpsMgr(Conc):
    def __init__(self, ConfigFiles):
        ''' Init a Corps, including all of its initial Envs (except its own - Corps Conc has already booted Env 0). '''

        # Import the Config data here to make sure we get the version loaded by EnvMgr
        from ConfigGlobals import NumEnvs
        assert NumEnvs < MAX_ENVID-MIN_ENVID+1, f'Number of Envs must be less than {MAX_ENVID-MIN_ENVID+1}'

        # Self-initialize
        ConcId = _ConcIdMgr.new()
        assert ConcId == CORPSMGR_CONCID, f'CorpsMgr has ConcId {ConcId} and not {CORPSMGR_CONCID}'

        self.ConcAddr = ConcAddr(CORPSMGR_ENVID, ConcId, CORPSMGR_ENVID)
        super().__init__()
        self.MajorStatus = MajorStatus.Booting

        # Make sure thread-local data knows the Conc it's assigned to
        TheThread.TheConcAddr = self.ConcAddr

        # Make sure we can be found
        _Addr2Conc.register(self, self.ConcAddr)

        # todo: make tuple into a named tuple or a data class?
        # Build a list of Envs' list of EnvRecord specs with indexes: 0: LocEnvId, 1: IpAddr, 2: Port
        # Ours first, the other Envs as we receive them off the Queue
        XferEnvRecords = []
        OurEnvRecord = _EnvTable.get(CORPSMGR_ENVID)
        OurXferEnvRecord = XferEnvRecord(CORPSMGR_ENVID, OurEnvRecord.IpAddr, OurEnvRecord.Port)
        XferEnvRecords.append(OurXferEnvRecord)

        # Boot all other Envs in this Corps and get their EnvRecord Spec
        # ...Everything is on this Host
        #from time import perf_counter
        EnvIds = EnvIdGen(MIN_ENVID_plus_1, NumEnvs-1)
        #tot_t = 0
        for NewEnvId in EnvIds:
            #t1 = perf_counter()
            CorpsMgrQueue = Queue()
            NewEnv = Process(target=Env, args=(NewEnvId, my_CorpsTag(), CorpsMgrQueue, ConfigFiles))

            NewEnv.start()

            NewXferEnvRecord = CorpsMgrQueue.get()
            #t2 = perf_counter()
            #tot_t += (t2 - t1)
            #print(f'CorpsMgr init Env {NewEnvId} in {t2-t1} seconds')

            assert NewXferEnvRecord.LocEnvId == NewEnvId, \
                                f'CorpsMgr __init__ returned Envid {NewXferEnvRecord.LocEnvId} vs expected {NewEnvId}'
            XferEnvRecords.append(NewXferEnvRecord)

            # Create an EnvRecord and add to our EnvTable
            NewEnvRecord = EnvRecord(DefaultEnvRecord.MsgHdlrFactory, DefaultEnvRecord.NetwFactory, \
                                                                        NewXferEnvRecord.IpAddr, NewXferEnvRecord.Port)
            _EnvTable.register(NewEnvId, NewEnvRecord)

        #print(f'CorpsMgr {self.ConcAddr} init: queue get {NumEnvs-1} Env processes in {tot_t} seconds')

        info(f'{self} EnvTable:\n{_EnvTable}')

        # Send EnvRecordSpecs to all Envs except ours
        EnvNames = EnvNameGen(MIN_ENVID_plus_1, NumEnvs-1)
        FutRets = []
        for RemoteEnv in EnvNames:
            FutRets.append(RemoteEnv.init_EnvTable(XferEnvRecords))

        # todo: handle the exception
        for FutRet in FutRets:
            Ret = FutRet.Ret    # will blow up if we have an exception

        # We're up!
        self.MajorStatus = MajorStatus.Running
        info(f'{self} initialized, starting...')

        # The thread is no longer assigned, so cleanup
        TheThread.TheConcAddr = NullConcAddr


    def create_Corps(self, ModuleName, CorpsClassName, CorpsTag, is_Ext, Managed, LocType, LocVal, *args, **kwargs):
        if Managed == True:
            MgrCorpsIpPort = (my_Ip(), my_Port())
            kwargs['MgrCorpsIpPort'] = MgrCorpsIpPort

        else:
            kwargs['MgrCorpsIpPort'] = None

        WorkerQueue = Queue()

        NewCorpsProcess = Process(target=Workers.__other_process_create_Corps__, \
                              args=(ModuleName, CorpsClassName, WorkerQueue, *args), kwargs=kwargs)
        NewCorpsProcess.start()

        NewCorpsData = WorkerQueue.get()
        NewCorps_Ip = NewCorpsData[0]
        NewCorps_Port = NewCorpsData[1]

        NewCorpsEnvRecord = CorpsEnvRecord(CorpsTag, DefaultEnvRecord.MsgHdlrFactory, DefaultEnvRecord.NetwFactory, \
                                                                                            NewCorps_Ip, NewCorps_Port)

        NewCorps_EnvId = CORPSMGR_ENVID

        if Managed == True:
            if is_Ext == True:
                NewCorps_EnvId = _ExtCorpsEnvTable.register(None, NewCorpsEnvRecord)
            else:
                NewCorps_EnvId = _ContCorpsEnvTable.register(None, NewCorpsEnvRecord)

        NewXferCorpsEnvRecord = XferCorpsEnvRecord(CorpsTag, NewCorps_EnvId, NewCorps_Ip, NewCorps_Port)

        # Add new Corps to all Envs except ours
        if Managed == True:
            NumEnvs = _EnvTable.num_Envs()  # assumes EnvIds are sequential (not true for ContCorps and ExtCorps)
            EnvNames = EnvNameGen(MIN_ENVID_plus_1, NumEnvs-1)
            FutRets = []
            for RemoteEnv in EnvNames:
                FutRets.append(RemoteEnv.add2_CorpsEnvTable(NewCorps_EnvId, is_Ext, NewXferCorpsEnvRecord))

            for FutRet in FutRets:
                Ret = FutRet.Ret  # will blow up if we have an exception


        return NewXferCorpsEnvRecord


    def __kill__(self):
        pid = getpid()
        self.MajorStatus = MajorStatus.Exiting
        info(f'{self} exiting')

        # todo: kill all Corps we are managing

        # Request exit for all Envs except ours
        NumEnvs = _EnvTable.num_Envs()  # assumes EnvIds are sequential (not true for ContCorps and ExtCorps)
        EnvNames = EnvNameGen(MIN_ENVID_plus_1, NumEnvs-1)
        for RemoteEnv in EnvNames:
            RemoteEnv.__kill__(NoReply=True)

        # Now us
        kill(pid, 0)
        kill(pid, SIGTERM)

        self.MajorStatus = MajorStatus.Nonexistent
        info(f'{self} still here')


    def __repr__(self):
        return f'{my_CorpsTag()} CorpsMgr'


class Corps(Conc):
    def __init__(self):
        # Startup the EnvMgr and CorpsMgr first to get the ConcIds right
        MgrEnv = Env(CORPSMGR_ENVID, self.my_Tag(), None, self.ConfigFiles)
        MgrCorps = CorpsMgr(self.ConfigFiles)

        # Self-initialize
        ConcId = _ConcIdMgr.new()
        assert ConcId == CORPS_CONCID, f'Corps has ConcId {ConcId} and not {CORPS_CONCID}'
        self.ConcAddr = ConcAddr(CORPSMGR_ENVID, ConcId, CORPSMGR_ENVID)
        super().__init__()

        # Make sure thread-local data knows the Conc it's assigned to
        TheThread.TheConcAddr = self.ConcAddr

        # Make sure we can be found
        _Addr2Conc.register(self, self.ConcAddr)

        info(f'Corps {self.my_Tag()} initialized, starting...')

        # The thread is no longer assigned, so cleanup
        TheThread.TheConcAddr = NullConcAddr


    def cleanup(self):
        return True


    def exit(self):
        self.cleanup()
        info(f'Corps Mgr in {self.my_Tag()} exiting')

        # Send kill request to CorpsMgr
        CorpsMgrConcAddr = ConcAddr(CORPSMGR_ENVID, CORPSMGR_CONCID, CORPSMGR_ENVID)
        CorpsMgr = CorpsMgrName(CorpsMgrConcAddr)

        CorpsMgr.__kill__(NoReply=True)
        return True


    def my_ExtName(self):
        ''' Returns a new ExtName for the Corps instance '''

        # todo: after we implement to_ExtName(), maybe rewrite using Conc's verion and converting

        SelfClassName = self.__class__.__name__
        CallingModuleName = self.__class__.__module__
        CallingModule = import_module(CallingModuleName)

        CorpsClassProxy = proxy(self.__class__, SelfClassName + 'Name', CallingModule)

        NewProxy = CorpsClassProxy(ConcAddr_to_ExtAddr(self.ConcAddr, my_Ip(), my_Port()))
        NewName = Name(NewProxy, SelfClassName, CallingModuleName)
        return NewName


    def is_Ext(self):
        return self.Ext


    def my_Tag(self):
        return self.Tag


    def __repr__(self):
        if self.is_Ext() == True:
            CorpsType = 'Ext'
        else:
            CorpsType = 'Cont'

        return f'{CorpsType}Corps {self.my_Tag()} {self.ConcAddr}'

