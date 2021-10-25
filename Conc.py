
'''
    A Conc is a type of Worker with a medium grain-size.


    _ _ i n i t _ _ ( )

    A Conc subclass's __init__() should call:
        super().__init__()


    c l e a n u p ( )

    When exit() is called on a Conc its cleanup() will automatically be called.  Should be overridden if the Conc
    has resources such as files to flush, database transactions to commit, etc.  Can call exit() on any of its
    Workers.


    e x i t ( )

    Should *not* be overridden by subclasses.  Can be called explicitly by the Conc's Mgr to cleanup and exit. Calls
    cleanup(), which should be overridden if the Conc has resources such as files to flush, database transactions to
    commit, etc.


    m y _ C l a s s ( )

    Returns the text name of the Conc's Class


    m y _ M g r ( )

    Returns a Name for the Mgr Conc (the Conc that created this instance), if any.  Otherwise, None.


    m y _ N a m e ( )

    Returns a new Name of the Conc instance.  Used to return the instance Name or to pass the instance Name as a
    method or function argument to another Conc.

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
from EnvGlobals import TheThread, NullConcAddr, _ThreadPool, _Addr2Conc, my_CorpsTag
from ConcMeta import ConcMeta
from sys import exc_info
from traceback import format_exception
from ResultsCache import ResultsCache
from Name import proxy, Name
from logging import error
from importlib import import_module



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

            Messages can be received (i.e. main scheduled) without this being called via MsgRelay.

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

            RetBody = CorpsReturn()

            # todo: handle exception
            Method = getattr(self.__class__, MsgBody.MethodName)

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

            # Done, does client want a response?...
            if MsgBody.MsgFlags & NoReplyBitMask:
                # No
                MsgBody.MsgHdlr.close()
                break

            # Yes, return a response to the client
            RetBody.Ret = Ret
            RetBody.MsgType = CorpsMsgType.ConcRet
            RetBody.ClientAddr = MsgBody.ClientAddr
            RetBody.ServerAddr = MsgBody.ServerAddr

            send_ret = False
            try:
                send_ret = MsgBody.MsgHdlr.send_msg(RetBody)

            except:
                error(f'{self.ConcAddr} main: {exc_info()}...{exc_info()[0]}...{exc_info()[1]}...{exc_info()[2]}')
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
        return True


    def exit(self):
        self.cleanup()
        _Addr2Conc.unregister(self.ConcAddr)
        return True


    def __my_Self__(self):
        return self.ConcAddr


    def my_Class(self):
        return self.__class__.__name__


    def my_Mgr(self):
        return self.Mgr


    def my_Name(self):
        ''' Returns a new Name for the Conc instance '''

        SelfClassName = self.__class__.__name__
        CallingModuleName = self.__class__.__module__
        CallingModule = import_module(CallingModuleName)

        ConcClassProxy = proxy(self.__class__, SelfClassName + 'Name', CallingModule)

        NewProxy = ConcClassProxy(self.ConcAddr)
        NewName = Name(NewProxy, SelfClassName, CallingModuleName)
        return NewName


    def before_rec_msg(self):
        return 0


    def before_request(self, Msg):
        return 0


    def after_request(self, Msg, Ret):
        return 0


    def after_reply(self, Msg, RetBody):
        return 0


    def __repr__(self):
        return f'Conc {my_CorpsTag()}:{self.ConcAddr}'


class Conc(__Conc, metaclass=ConcMeta):
    pass

