
'''
    Record types for rows in EnvTables

    Transfer version of them as well - needed so we do not transfer entire MsgHdlr and Netw factories between
    Envs and Corps (and therefore processes and hosts).  Later we will transfer symbolic info on the factories (i.e.
    module and class names)

'''



class EnvRecordBase():
    def __init__(self, MsgHdlrFactory, NetwFactory, IpAddr, Port):
        self.MsgHdlrFactory = MsgHdlrFactory
        self.NetwFactory = NetwFactory
        self.IpAddr = IpAddr
        self.Port = Port


    def __repr__(self):
        return f' MsgHdlr {self.MsgHdlrFactory.__class__} NetF {self.NetwFactory.__class__}' + \
                                                                                f'Ip {self.IpAddr} Port {self.Port}'


class EnvRecord(EnvRecordBase):
    def __init__(self, MsgHdlrFactory, NetwFactory, IpAddr, Port):
        super().__init__(MsgHdlrFactory, NetwFactory, IpAddr, Port)


    def __repr__(self):
        return f'EnvRecord: {super().__repr__()}'


class XferEnvRecord():
    def __init__(self, LocEnvId, IpAddr, Port):
        self.LocEnvId = LocEnvId
        self.IpAddr = IpAddr
        self.Port = Port


class CorpsEnvRecord(EnvRecordBase):
    def __init__(self, Tag, MsgHdlrFactory, NetwFactory, IpAddr, Port):
        super().__init__(MsgHdlrFactory, NetwFactory, IpAddr, Port)
        self.Tag = Tag


    def __repr__(self):
        return f'CorpsEnvRecord: Tag {self.Tag} {super().__repr__()}'


class XferCorpsEnvRecord(XferEnvRecord):
    def __init__(self, Tag, LocEnvId, IpAddr, Port):
        super().__init__(LocEnvId, IpAddr, Port)
        self.Tag = Tag