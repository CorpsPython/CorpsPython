

''' CorpsMsg Message Formats '''



from enum import IntEnum
from ResultsCache import ResultsCacheKey



class CorpsMsgType(IntEnum):
    ConcRet = 0
    ConcRequ = 1


class CorpsMsgPriority(IntEnum):
    MetaRet = 0         # Highest priority
    MetaRequ = 1        # ...to
    BaseRet = 2         # ...the
    BaseRequ = 3        # ...lowest


CORPSMSG_HDR_SIZE = 8

MAX_BODY_LENGTH = pow(2,64)-1


class CorpsRequest():
    def __init__(self):
        self.MsgType = CorpsMsgType.ConcRequ
        self.MsgPriority = CorpsMsgPriority.BaseRequ
        self.MsgId = ResultsCacheKey(0,0,0)
        self.ClientAddr = 0
        self.ServerAddr = 0
        self.MethodName = 0
        self.Args = 0
        self.KwArgs = 0
        self.MsgHdlr = 0              # used on server to pass between threads


    def __repr__(self):
        output = []

        output.append(f'\tMsgType: {self.MsgType.name}\n')
        output.append(f'\tMsgPriority: {self.MsgPriority.name}\n')
        output.append(f'\tMsgId: {self.MsgId}\n')
        output.append(f'\tClientAddr: {self.ClientAddr}\n')
        output.append(f'\tServerAddr: {self.ServerAddr}\n')
        output.append(f'\tMethodName: {self.MethodName}\n')
        output.append(f'\tArgs: {self.Args}\n')
        output.append(f'\tKwArgs: {self.KwArgs}\n')

        return ' '.join(output)


class CorpsRetType(IntEnum):
    Ok = 0
    AsyncExecutionExc = 1
    AsyncAttributeExc = 2


class CorpsReturn():
    def __init__(self):
        self.MsgType = CorpsMsgType.ConcRet
        self.MsgPriority = CorpsMsgPriority.BaseRet
        self.ClientAddr = 0
        self.ServerAddr = 0
        self.Ret = 0
        self.RetType = CorpsRetType.Ok


    def __repr__(self):
        output = []

        output.append(f'\tMsgType: {self.MsgType.name}\n')
        output.append(f'\tMsgPriority: {self.MsgPriority.name}\n')
        output.append(f'\tClientAddr: {self.ClientAddr}\n')
        output.append(f'\tServerAddr: {self.ServerAddr}\n')
        output.append(f'\tRet: {self.Ret}\n')
        output.append(f'\tRetType: {self.RetType.name}\n')

        return ' '.join(output)
