
'''
    Addr2Conc is a dict mapping ConcAddrs to Concs.


    All operations are protected by a lock.

    One instance per Env is instantiated in EnvGlobals.py.
'''



from threading import Lock


class Addr2Conc():
    def __init__(self):
        self.Dict = dict()
        self.Lock = Lock()


    def register(self, aConc, aConcAddr):
        ''' Register a ConcAddr/Conc pair '''

        self.Lock.acquire()

        ConcKey = (aConcAddr.MgrEnvId, aConcAddr.ConcId)

        anotherConc = None
        try:
            anotherConc = self.Dict.get(ConcKey)

        except:
            pass

        self.Dict[ConcKey] = aConc

        self.Lock.release()

        assert anotherConc == None
        return aConcAddr


    def getConc(self, aConcAddr):
        '''
            Find and return a Conc given its ConcAddr.

            An exception will be generated via an assert if the ConcAddr is not
            found.
        '''

        ConcKey = (aConcAddr.MgrEnvId, aConcAddr.ConcId)

        self.Lock.acquire()

        aConc = None
        try:
            aConc = self.Dict.get(ConcKey)

        except:
            pass

        self.Lock.release()

        assert aConc != None
        return aConc


    def unregister(self, aConcAddr):
        ''' Unregister a ConcAddr/Conc pair '''

        ConcKey = (aConcAddr.MgrEnvId, aConcAddr.ConcId)

        self.Lock.acquire()

        try:
            aConc = self.Dict.get(ConcKey)

        except:
            pass

        del self.Dict[ConcKey]

        self.Lock.release()

        assert aConc != None

