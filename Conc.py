
'''
    A Conc is a type of Worker with a medium grain-size.


    i n i t ( )

    A Conc subclass's __init__() should call:
        super().__init__()


    c l e a n u p ( )

    When exit() is called on a Corps its cleanup() will automatically be called.  It, in turn, should call cleanup()
    on all of its Workers, including Concs.  Conc subclasses should call it on all of its Workers.  All cleanup()
    implementations should also close database transactions, flush and close files, etc.


    m y _ N a m e ( )

    Returns a new Name of the Conc instance.

'''

'''
    The main loop in main() is very basic - the thread receives and processes messages.

    All special processing methods (before_loop, before_rec_msg, before_request, after_request, after_reply and
    after_loop) are commented out in the main loop as suggestions to where they go.

    The developer can re-implement main() in sublasses.  The implementaton of the special processing methods should be
    overridden when utilized as well.
'''



from threading import Lock
from CorpsMsg import *
from queue import Queue
from EnvGlobals import TheThread, NullConcAddr, _ThreadPool
from ConcMeta import ConcMeta
from sys import exc_info
from traceback import format_exception
from ResultsCache import ResultsCache
from inspect import stack, getmodule
from Name import proxy, Name
from logging import error



class __Conc():
    def __init__(self):
        super().__init__()

        self.MsgQ = Queue()
        self.ResultsCache = ResultsCache()
        self.AssignedLock = Lock()


    def ___remote_getattr___(self, name):
        ''' Support for Name's remote attribute reads '''

        return super().__getattribute__(name)


    def ___remote_setattr___(self, name, value):
        ''' Support for Name's remote attribute writes '''

        return setattr(self, name, value)


    def start(self):
        '''
            Schedules main loop.

            Messages can be received (i.e. main scheduled) without this being called via RequestRelay.

            Must be called for Conc to run without a message being received first.
        '''

        cmd = lambda: self.main()
        _ThreadPool.put_cmd(cmd)


    def main(self):
        ''' Main function and main loop '''

        # If Conc is already 'assigned' to a thread it has acquired the lock and we will get a False on acquire()
        if self.AssignedLock.acquire(blocking=False) == False:
            return

        # Make sure thread-local data knows the Conc it's assigned to
        TheThread.TheConcAddr = self.ConcAddr


        # The thread will keep processing incoming messages until there are no more
        while self.MsgQ.empty() == False:
            MsgBody = self.MsgQ.get()

            Method = getattr(self.__class__, MsgBody.MethodName)

            RetBody = CorpsReturn()

            # Make sure we haven't already completed this particular request from this client on a previous attempt
            Ret = self.ResultsCache.get(MsgBody.MsgId)
            if Ret == None:
                try:
                    Ret = Method(self, *MsgBody.Args, **MsgBody.KwArgs)

                except:
                    #
                    ei = exc_info()
                    ftb = format_exception(ei[0], ei[1], ei[2])
                    ftb[1] = f'  Async Execution Exception: {self.ConcAddr} executing {MsgBody.MethodName}() for ' + \
                                                                                                f'{MsgBody.ClientAddr}:\n'
                    Ret = (ei[0].__name__, ei[1], ''.join(ftb))
                    RetBody.RetType = CorpsRetType.AsyncExecutionExc

                else:
                    RetBody.RetType = CorpsRetType.Ok
                    self.ResultsCache.set(MsgBody.MsgId, Ret)

            # Done, return a response to the client
            RetBody.Ret = Ret
            RetBody.MsgType = CorpsMsgType.ConcRet
            RetBody.ClientAddr = MsgBody.ClientAddr
            RetBody.ServerAddr = MsgBody.ServerAddr


            send_ret = False
            try:
                send_ret = MsgBody.MsgHdlr.send_msg(RetBody)

            except:
                error(f'{self.ConcAddr} main: {exc_info()[1]}')
                MsgBody.MsgHdlr.close()
                break

            if send_ret == False:
                error(f'{self.ConcAddr} main: Error sending return')
                MsgBody.MsgHdlr.close()
                break



        # The thread is no longer assigned, so cleanup
        TheThread.TheConcAddr = NullConcAddr

        self.AssignedLock.release()


    def cleanup(self):
        pass


    def __my_Self__(self):
        return self.ConcAddr


    def my_Name(self):
        frm = stack()[1]
        CallingModule = getmodule(frm[0])

        SelfClassName = self.__class__.__name__
        ConcClassProxy = proxy(self.__class__, SelfClassName + 'Name', CallingModule)

        NewProxy = ConcClassProxy(self.ConcAddr)
        NewName = Name(NewProxy, SelfClassName, CallingModule.__name__)
        return NewName


    def before_rec_msg(self):
        return 0


    def before_request(self, Msg):
        return 0


    def after_request(self, Msg, Ret):
        return 0


    def after_reply(self, Msg, RetBody):
        return 0


class Conc(__Conc, metaclass=ConcMeta):
    pass

