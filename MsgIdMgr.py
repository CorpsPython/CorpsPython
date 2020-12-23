
'''
    MsgIdMgr generates Env-global Msg Id numbers.


    Id numbers begin at 0 and are modulo-MAX_MSGID.

    All operations are protected by a lock.

    One instance per Env is instantiated in EnvGlobals.py.
'''



from threading import Lock


# Top of range for Msg Id numbers
MAX_MSGID = pow(2,32)


class MsgIdMgr():
    def __init__(self):
        self.Lock = Lock()

        self.Lock.acquire()

        self.MsgId = 0

        self.Lock.release()


    def new(self):
        ''' Gen a new Msg Id number '''

        self.Lock.acquire()

        TempMsgId = self.MsgId

        self.MsgId += 1

        if self.MsgId > MAX_MSGID:
            self.MsgId = 0

        self.Lock.release()

        return TempMsgId
