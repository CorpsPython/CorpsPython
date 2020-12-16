'''
    EnvTable is a dict mapping EnvIds to EnvRecords.


    The CorpsMgr manages the allocation of EnvIds for the Corps.

    All operations are protected by a lock.

    One instance per Env is instantiated in EnvGlobals.py.

    Needed to support Workers' LocType=Auto gen of a next Env to create a Worker in.  Placed it here since it
    required the highest EnvId already alloc'd as N in modulo-N.

    Needed to gen an Env-global MsgId per Msg so put it here to save a lock/unlock...see get_to_connect() here and
    ProxyMakeRequest.py.
'''



from threading import Lock
from copy import copy
from EnvAddrSpace import MIN_ENVID, MAX_CONT_CORPS_ENVID



MAX_MSGID = pow(2, 32) - 1



class EnvTable():
    def __init__(self):
        self.Dict = dict()
        self.Lock = Lock()
        self.HighestEnvId = 0           # Highest alloc'd EnvId in this Corps (i.e. not those Cont or Ext Corps)
        self.NextEnvId = MIN_ENVID
        self.MsgId = 0


    def register(self, EnvId, anEnvRecord):
        ''' Register the EnvRecord of a given EnvId '''

        self.Lock.acquire()

        self.Dict[EnvId] = anEnvRecord

        if EnvId > self.HighestEnvId:
            self.HighestEnvId = EnvId

        self.Lock.release()


    def next_EnvId(self):
        ''' Support for Workers' LocType=Auto '''

        self.Lock.acquire()

        EnvId = self.NextEnvId

        self.NextEnvId += 1
        if self.NextEnvId > self.HighestEnvId:
            self.NextEnvId = MIN_ENVID

        self.Lock.release()

        return EnvId


    def update(self, EnvId, NewEnvRecord):
        ''' Overwrite the EnvRecord of a given EnvId with a replacement '''

        self.Lock.acquire()

        anEnvRecord = None
        try:
            anEnvRecord = self.Dict.get(EnvId)

        except:
            pass

        if anEnvRecord != None:
            self.Dict[EnvId] = NewEnvRecord

        self.Lock.release()

        assert anEnvRecord != None


    def get(self, EnvId):
        ''' Find and return the EnvRecord for a given EnvId '''

        self.Lock.acquire()

        anEnvRecord = None
        try:
            anEnvRecord = self.Dict.get(EnvId)

        except:
            pass

        self.Lock.release()

        assert anEnvRecord != None
        return copy(anEnvRecord)


    def get_to_connect(self, EnvId, Attempt):
        '''
            Find and return the EnvRecord for a given EnvId

            If this is the first attempt (Attempt == 1) alloc and return a MsgId, otw return None

            Used only for gets used in message passing (see ProxyMakeRequest.py)
        '''

        self.Lock.acquire()

        if Attempt == 1:
            self.MsgId += 1

            if self.MsgId > MAX_MSGID:
                self.MsgId = 0

            TempMsgId = self.MsgId

        else:
            TempMsgId = None

        anEnvRecord = None
        try:
            anEnvRecord = self.Dict.get(EnvId)

        except:
            pass

        self.Lock.release()

        assert anEnvRecord != None
        return copy(anEnvRecord), TempMsgId


    def unregister(self, EnvId):
        ''' Find and delete the EnvRecord of a given EnvId '''

        if EnvId > MAX_CONT_CORPS_ENVID:
            raise IndexError(f'Cannot unregister EnvRecord with EnvId {EnvId}')

        self.Lock.acquire()

        anEnvRecord = None
        try:
            anEnvRecord = self.Dict.get(EnvId)

        except:
            pass

        if anEnvRecord != None:
            del self.Dict[EnvId]

        self.Lock.release()

        assert anEnvRecord != None


    def __repr__(self):
        output = []

        self.Lock.acquire()

        for EnvId, anEnvRecord in self.Dict.items():
            output.append(f'\tEnv {EnvId} {anEnvRecord}\n')

        self.Lock.release()

        return ' '.join(output)
