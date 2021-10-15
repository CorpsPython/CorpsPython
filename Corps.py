'''
    A Corps is a large-grained Worker.


    i n i t ( )

    A Corps subclass's __init__() should call:
        super().__init__()


    c l e a n u p ( )

    When exit() is called on a Corps its cleanup() will automatically be called.  It, in turn, should call cleanup()
    on all of its Workers.  All cleanup() implementations should also close database transactions, flush and close
    files, etc.


    m y _ N a m e ( )

    Returns a new Name of the Corps instance.
'''

'''
    Corps and CorpsMgr Concs


    Instantiate and cooperate with Envs to establish the run-time environment for a Corps
'''



from Conc import Conc
from ConcAddr import ConcAddr, ExtAddr
from EnvRecord import EnvRecord, XferEnvRecord, CorpsEnvRecord, XferCorpsEnvRecord
from Env import Env, EnvName    # EnvName is dynamically genned by proxy()
from EnvGlobals import TheThread, NullConcAddr, _ConcIdMgr, _Addr2Conc, DefaultEnvRecord, _EnvTable,  my_Ip, my_Port, \
    DefaultCorpsEnvRecord, _ExtCorpsEnvTable, _ContCorpsEnvTable
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
            NewEnv = Process(target=Env, args=(NewEnvId, CorpsMgrQueue, ConfigFiles))

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

        info(f'CorpsMgr {self.my_Name()} EnvTable:\n{_EnvTable}')

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
        info(f'CorpsMgr {self.my_Name()} initialized, starting...')

        # The thread is no longer assigned, so cleanup
        TheThread.TheConcAddr = NullConcAddr


    def create_Corps(self, ModuleName, CorpsClassName, Mgr, CorpsTag, is_Ext, Managed, LocType, LocVal, *args, **kwargs):
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
        info(f'CorpsMgr {self.my_Name()} exiting')

        # todo: kill all Corps we are managing

        # Request exit for all Envs except ours
        NumEnvs = _EnvTable.num_Envs()  # assumes EnvIds are sequential (not true for ContCorps and ExtCorps)
        EnvNames = EnvNameGen(MIN_ENVID_plus_1, NumEnvs-1)
        for RemoteEnv in EnvNames:
            RemoteEnv.__kill__()

        time.sleep(0.1 * NumEnvs)

        # Now us
        kill(pid, 0)
        kill(pid, SIGTERM)

        self.MajorStatus = MajorStatus.Nonexistent
        info(f'CorpsMgr {self.my_Name()} still here')


class Corps(Conc):
    def __init__(self):
        # Startup the EnvMgr and CorpsMgr first to get the ConcIds right
        MgrEnv = Env(CORPSMGR_ENVID, None, self.ConfigFiles)
        MgrCorps = CorpsMgr(self.ConfigFiles)

        # Self-initialize
        ConcId = _ConcIdMgr.new()
        assert ConcId == CORPS_CONCID, f'Corps has ConcId {ConcId} and not {CORPS_CONCID}'

        # todo: add test and assign for contcorps
        # todo: always use ExtAddrs?  assume short-lived and used to pass parms?  ok between Concs in same Corps?
        # For ContCorps
        #self.ConcAddr = ConcAddr(CORPSMGR_ENVID, ConcId, CORPSMGR_ENVID)
        # For ExtCorps
        self.ConcAddr = ExtAddr(CORPSMGR_ENVID, ConcId, CORPSMGR_ENVID, my_Ip(), my_Port())
        super().__init__()

        # Make sure thread-local data knows the Conc it's assigned to
        TheThread.TheConcAddr = self.ConcAddr

        # Make sure we can be found
        _Addr2Conc.register(self, self.ConcAddr)

        info(f'Corps Mgr {self.my_Tag()} initialized, starting...')

        # The thread is no longer assigned, so cleanup
        TheThread.TheConcAddr = NullConcAddr


    def __kill__(self):
        info(f'Corps Mgr in {self.my_Tag()} exiting')

        # Send kill request to CorpsMgr
        CorpsMgrConcAddr = ConcAddr(CORPSMGR_ENVID, CORPSMGR_CONCID, CORPSMGR_ENVID)
        CorpsMgr = CorpsMgrName(CorpsMgrConcAddr)

        CorpsMgr.__kill__(NoReply=True)


    def cleanup(self):
        return True


    def exit(self):
        self.cleanup()
        time.sleep(0.1)
        self.__kill__()
        return True


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

