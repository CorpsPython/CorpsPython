
''' Simple record for "row" in EnvTable '''



class EnvRecord():
    def __init__(self, aMsgHdlrFactory, aNetwFactory, anIPAddr, aPort):
        self.MsgHdlrFactory = aMsgHdlrFactory
        self.NetwFactory = aNetwFactory
        self.IPAddr = anIPAddr
        self.Port = aPort


    def __repr__(self):
        #return f'EnvRecord MsgF {self.MsgHdlrFactory} NetF {self.NetwFactory} IP {self.IPAddr} Port {self.Port}'
        return f'EnvRecord IP {self.IPAddr} Port {self.Port}'
