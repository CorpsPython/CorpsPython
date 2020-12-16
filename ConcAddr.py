
'''
    ConcAddr is a Worker's Corps-global reference.


    Attributes:
        The MgrEnvId is the Env Id of the Env where the Worker's creation was requested.

        The ConcId is MgrEnv-global Id number.

        The LocEnvId is the Env Id of the Env where the Worker is hosted.


    See also Addr2Conc.py and ConcIdMgr.py.
'''



class ConcAddr():
    def __init__(self, MgrEnvId, ConcId, LocEnvId):
        self.MgrEnvId = MgrEnvId
        self.ConcId = ConcId
        self.LocEnvId = LocEnvId


    def __eq__(self, aConcAddr):
        if self.MgrEnvId == aConcAddr.MgrEnvId and self.ConcId == aConcAddr.ConcId and \
                                                                            self.LocEnvId == aConcAddr.LocEnvId:
            return True

        else:
            return False


    def __repr__(self):
        return f'L{self.LocEnvId}:M{self.MgrEnvId}.{self.ConcId}'