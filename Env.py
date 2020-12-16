
'''
    Env Conc


    Cooperate with CorpsMgr to establish the run-time environment for a Corps
'''



from Conc import Conc
from ConcAddr import ConcAddr
from EnvGlobals import TheThread, NullConcAddr, set_EnvId, my_EnvId, set_EnvMgrAddr, _ConcIdMgr, _Addr2Conc
from EnvGlobals import _EnvTable, DefaultEnvRecord, set_MyPort
from os import getpid, kill
from importlib import import_module
from EnvAddrSpace import CORPSMGR_ENVID
from ConcIdMgr import ENVMGR_CONCID
import queue
from copy import copy
from signal import SIGTERM
from Config import load_config
from logging import basicConfig, info


class Env(Conc):
    def __init__(self, EnvId, CorpsMgrQueue, ConfigFiles):
        load_config('ConfigGlobals', ConfigFiles)

        from ConfigGlobals import Logging_Format, Logging_Datefmt, Logging_Level
        basicConfig(format=Logging_Format, datefmt=Logging_Datefmt, level=Logging_Level)

        # Self-initialize
        ConcId = _ConcIdMgr.new()
        assert ConcId == ENVMGR_CONCID, f'EnvMgr in Env {EnvId} has ConcId {ConcId} and not {ENVMGR_CONCID}'

        self.ConcAddr = ConcAddr(CORPSMGR_ENVID, ConcId, EnvId)
        self.EnvId = EnvId

        super().__init__()

        # Init some EnvGlobals
        set_EnvId(EnvId)
        set_EnvMgrAddr(self.ConcAddr)

        # Make sure thread-local data knows the Conc it's assigned to
        TheThread.TheConcAddr = self.ConcAddr

        # Make sure we can be found
        _Addr2Conc.register(self, self.ConcAddr)

        # Startup the TcpConnector and get our port number from it
        TheEnvRecord = copy(DefaultEnvRecord)
        EnvQueue = queue.Queue()

        TheEnvRecord.NetwFactory.new_connector(TheEnvRecord.IPAddr, EnvQueue)
        Port = EnvQueue.get()

        # Initialize our EnvRecord and register it in the EnvTable
        TheEnvRecord.Port = Port
        set_MyPort(Port)        # another EnvGlobal
        _EnvTable.register(EnvId, TheEnvRecord)

        # If we are not the CorpsMgr's Env we need to provide the CorpsMgr our
        #   EnvRecord Spec Tuple: 0: LocEnvId, 1: IPAddr, 2: Port
        if EnvId != CORPSMGR_ENVID:
            CorpsMgrQueue.put([EnvId, TheEnvRecord.IPAddr, TheEnvRecord.Port])

        # The thread is no longer assigned, so cleanup
        TheThread.TheConcAddr = NullConcAddr

        info(f'EnvMgr {self.my_Name()} Env {EnvId} initialized')


    def __kill__(self):
        Pid = getpid()
        info(f'EnvMgr {self.my_Name()} Env {self.EnvId} exiting')
        kill(Pid, SIGTERM)


    def init_EnvTable(self, AllEnvMsgList):
        '''
            Init our EnvTable using a list of EnvRecord Spec Tuples: 0: LocEnvId, 1: IPAddr, 2: Port

            Ignore for our own which we did in __init__

            For now use defaults for MsgHdlrFactory and NetwHdlrFactory
        '''

        for EnvMsgList in AllEnvMsgList: # 0: LocEnvId, 1: IPAddr, 2: Port
            EnvId = EnvMsgList[0]
            if EnvId != my_EnvId():
                TheEnvRecord = copy(DefaultEnvRecord)
                TheEnvRecord.IPAddr = EnvMsgList[1]
                TheEnvRecord.Port = EnvMsgList[2]
                _EnvTable.register(EnvId, TheEnvRecord)

        info(f'EnvMgr {self.my_Name()} Env {my_EnvId()} EnvTable:\n{_EnvTable}')

        return True


    def rem2loc_create_Conc(self, NewConcAddr, CallingModule, ConcClass, *args, **kwargs):
        '''
            Create a Conc for another Env to be hosted in our Env

            CallingModule and ConcClass are text names
        '''

        # Find the Class object
        TheCallingModule = import_module(CallingModule)
        ConcClassInModule = getattr(TheCallingModule, ConcClass)

        # Create the Conc
        NewConc = ConcClassInModule(*args, **kwargs)

        # Make sure we can find it
        _Addr2Conc.register(NewConc, NewConcAddr)

        return True


