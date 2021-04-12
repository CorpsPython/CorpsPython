
'''
    Record types for rows in EnvTables

'''



class EnvRecordBase():
    def __init__(self, aMsgHdlrFactory, aNetwFactory, anIpAddr, aPort):
        self.MsgHdlrFactory = aMsgHdlrFactory
        self.NetwFactory = aNetwFactory
        self.IpAddr = anIpAddr
        self.Port = aPort


    def __repr__(self):
        return f' MsgHdlr {self.MsgHdlrFactory.__class__} NetF {self.NetwFactory.__class__}' + \
                                                                                f'Ip {self.IpAddr} Port {self.Port}'


class EnvRecord(EnvRecordBase):
    def __init__(self, aMsgHdlrFactory, aNetwFactory, anIpAddr, aPort):
        super().__init__(aMsgHdlrFactory, aNetwFactory, anIpAddr, aPort)


    def __repr__(self):
        return f'EnvRecord: {super().__repr__()}'


class CorpsEnvRecord(EnvRecordBase):
    def __init__(self, Tag, aMsgHdlrFactory, aNetwFactory, anIpAddr, aPort):
        super().__init__(aMsgHdlrFactory, aNetwFactory, anIpAddr, aPort)
        self.Tag = Tag


    def __repr__(self):
        return f'CorpsEnvRecord: Tag {self.Tag} {super().__repr__()}'

