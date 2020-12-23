
''' Simple record for "row" in EnvTable '''



class EnvRecord():
    def __init__(self, aMsgHdlrFactory, aNetwFactory, anIpAddr, aPort):
        self.MsgHdlrFactory = aMsgHdlrFactory
        self.NetwFactory = aNetwFactory
        self.IpAddr = anIpAddr
        self.Port = aPort


    def __repr__(self):
        #return f'EnvRecord MsgF {self.MsgHdlrFactory} NetF {self.NetwFactory} Ip {self.IpAddr} Port {self.Port}'
        return f'EnvRecord Ip {self.IpAddr} Port {self.Port}'
