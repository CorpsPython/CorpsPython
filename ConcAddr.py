
'''
    ConcAddr is a Worker's Corps-global reference. It is used internal to a Corps.


    Attributes:
        The MgrEnvId is the Env Id of the Env where the Worker's creation was requested.

        The ConcId is MgrEnv-global Id number.

        The LocEnvId is the Env Id of the Env where the Worker is hosted.


    See also Addr2Conc.py and ConcIdMgr.py.


    ExtAddr is a ConcAddr with added Ip Addr and Port.  It is used for references external to a Corps.  It usually
    refers to a Corps but could also be that of any Worker, such as a Conc or Func (when we say it refers to a Corps we
    are really referring to the Corps Conc, the Conc that fronts for the Corps).
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


class ExtAddr(ConcAddr):
    def __init__(self, MgrEnvId, ConcId, LocEnvId, IpAddr, Port):
        super().__init__(MgrEnvId, ConcId, LocEnvId)
        self.IpAddr = IpAddr
        self.Port = Port


    def __eq__(self, anExtAddr):
        if super().__eq__(anExtAddr) and self.IpAddr == anExtAddr.IPAddr and self.Port == anExtAddr.Port:
            return True

        else:
            return False


    def __repr__(self):
        return f'{super().__repr__()}@{self.IpAddr}:{self.Port}'