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
from ConcAddr import ConcAddr
from EnvRecord import EnvRecord
from Env import Env, EnvName    # EnvName is dynamically genned by proxy()
from EnvGlobals import TheThread, NullConcAddr, _ConcIdMgr, _Addr2Conc, DefaultEnvRecord, _EnvTable
from os import getpid, kill
from multiprocessing import Process, Queue
from EnvAddrSpace import MIN_ENVID, MAX_ENVID, CORPSMGR_ENVID
from ConcIdMgr import ENVMGR_CONCID, CORPSMGR_CONCID, CORPS_CONCID
from signal import SIGTERM
from logging import info



class CorpsMgr(Conc):
    def __init__(self, ConfigFiles):
        # Import the Config data here to make sure we get the version loaded by EnvMgr
        from ConfigGlobals import NumEnvs

        assert NumEnvs < MAX_ENVID-MIN_ENVID+1, f'Number of Envs must be less than {MAX_ENVID-MIN_ENVID+1}'

        # Self-initialize
        ConcId = _ConcIdMgr.new()
        assert ConcId == CORPSMGR_CONCID, f'CorpsMgr has ConcId {ConcId} and not {CORPSMGR_CONCID}'

        self.ConcAddr = ConcAddr(CORPSMGR_ENVID, ConcId, CORPSMGR_ENVID)
        super().__init__()

        # Make sure thread-local data knows the Conc it's assigned to
        TheThread.TheConcAddr = self.ConcAddr

        # Make sure we can be found
        _Addr2Conc.register(self, self.ConcAddr)

        # Build a list of Envs' list of EnvRecord Spec Tuple: 0: LocEnvId, 1: IPAddr, 2: Port
        # Ours first, the other Envs as we receive them off the Queue
        EnvRecordSpecs = []
        OurEnvRecord = _EnvTable.get(CORPSMGR_ENVID)
        EnvRecordSpecs.append([CORPSMGR_ENVID, OurEnvRecord.IPAddr, OurEnvRecord.Port])

        # Boot all other Envs in this Corps and get their EnvRecord Spec
        # ...Everything is on this Host
        CorpsMgrQueue = Queue()
        for i in range(NumEnvs-1):
            NewEnvId = i + MIN_ENVID + 1
            NewEnv = Process(target=Env, args=(NewEnvId, CorpsMgrQueue, ConfigFiles))
            NewEnv.start()

            EnvMsgList = CorpsMgrQueue.get()
            EnvRecordSpecs.append(EnvMsgList)

            # Create an EnvRecord and add to our EnvTable
            NewEnvRecord = EnvRecord(DefaultEnvRecord.MsgHdlrFactory, DefaultEnvRecord.NetwFactory,
                                    EnvMsgList[1], EnvMsgList[2])
            _EnvTable.register(NewEnvId, NewEnvRecord)

        info(f'CorpsMgr {self.my_Name()} EnvTable:\n{_EnvTable}')

        # Send EnvRecordSpecs to all Envs except ours
        for i in range(NumEnvs-1):
            RemoteEnvId = i + MIN_ENVID + 1
            EnvConcAddr = ConcAddr(CORPSMGR_ENVID, ENVMGR_CONCID, RemoteEnvId)
            RemoteEnv = EnvName(EnvConcAddr)

            FutRes = RemoteEnv.init_EnvTable(EnvRecordSpecs)
            Ret = FutRes.Ret

            assert Ret == True,\
                        f'CorpsMgr {self.my_Name()} Process {getpid()} error initing EnvTable in Env {RemoteEnvId}'

        info(f'CorpsMgr {self.my_Name()} initialized, starting...')

        # The thread is no longer assigned, so cleanup
        TheThread.TheConcAddr = NullConcAddr


    def kill(self):
        # Import the Config data here to make sure we get the version loaded by EnvMgr
        from ConfigGlobals import NumEnvs

        pid = getpid()
        info(f'CorpsMgr {self.my_Name()} exiting')

        # Request exit for all Envs except ours
        for i in range(NumEnvs-1):
            RemoteEnvId = i + MIN_ENVID + 1
            EnvConcAddr = ConcAddr(CORPSMGR_ENVID, ENVMGR_CONCID, RemoteEnvId)
            RemoteEnv = EnvName(EnvConcAddr)
            RemoteEnv.__kill__()

        # Now us
        #self.__kill__(pid)
        kill(pid, 0)
        kill(pid, SIGTERM)

        info(f'CorpsMgr {self.my_Name()} still here')


class Corps(Conc):
    def __init__(self):
        # Startup the EnvMgr and CorpsMgr first to get the ConcIds right
        MgrEnv = Env(CORPSMGR_ENVID, None, self.ConfigFiles)
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

        info(f'Corps {self.my_Name()} initialized, starting...')

        # The thread is no longer assigned, so cleanup
        TheThread.TheConcAddr = NullConcAddr


    def kill(self):
        # Send kill request to CorpsMgr
        CorpsMgrConcAddr = ConcAddr(CORPSMGR_ENVID, CORPSMGR_CONCID, CORPSMGR_ENVID)
        CorpsMgrConc = CorpsMgrName(CorpsMgrConcAddr)
        CorpsMgrConc.kill()


    def cleanup(self):
        pass


    def exit(self):
        self.cleanup()
        self.kill()



