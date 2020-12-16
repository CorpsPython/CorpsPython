'''
    R e t   o r   r e t

    Attribute, the returned result, whose access blocks until the result is ready, or returns the result immediately
    if the result is already available.

    Either spelling works the same.


    r e t _ r e a d y ( )

    Futures's non-blocking method ret_ready returns True if the result is ready or False otherwise.


    w a i t _ a l l ( )

    Function that waits until all Futures results have completed.

    wait_all(FutRets, InitDelay=0.05, DelayIncPct=20, MaxTries=25):

        FutRets is a list of Futures.

        Wait until all Futures results have completed or we exceed MaxTries waits for uncompleted results.

        Uses a sleepy waiting algorithm which has an initial wait time of InitDelay which then increases DelayIncPct
        for each wait thereafter.

        Raises a AsyncLocalMaxRetries Exception if MaxTries have been attempted and all results are not complete.  If
        a Worker caller of wait_all is providing a service for another Worker, raising a AsyncRemoteMaxRetries
        Exception is probably the correct response to receiving a AsyncLocalMaxRetries Exception from wait_all.


    w a i t _ n e x t ( )

    Generator that returns the next ready Futures result index into FutRets.

    wait_next(FutRets, InitDelay=0.05, DelayIncPct=20, MaxTries=25):

        FutRets is a list of Futures.

        Return the next ready Futures result index or we exceed MaxTries waits for uncompleted results.

        Uses a sleepy waiting algorithm which has an initial wait time of InitDelay which then increases DelayIncPct
        for each wait thereafter.

        Raises a AsyncLocalMaxRetries Exception if MaxTries have been attempted and all results are not complete.  If
        a Worker caller of wait_next is providing a service for another Worker, raising a AsyncRemoteMaxRetries
        Exception is probably the correct response to receiving a AsyncLocalMaxRetries Exception from wait_next.

'''

'''
    Implements the sync mechanism between the client Worker's thread and the thread implementing the message pass
    protocol.  See also ProxyMakeRequest.py.

    The result is locked at init and remains in that state until it is valid.

    A client can retrieve the result by accessing an attribute named 'Ret' or 'ret' on the Future.  If the result is
    valid it will be returned immediately. Otherwise the client will block unitl it is.

    They can test if the result is available by using the ret_ready() method.


    wait_all() takes an iterable of Futures of outstanding concurrent requests and returns when all are complete,
    or we exceed MaxTries waits for uncompleted results and a AsyncLocalMaxRetries exception is raised.

    wait_next() is a generator that takes an iterable of Futures of outstanding concurrent requests and yields the
    next ready Futures result index, or we exceed MaxTries waits for uncompleted results and a AsyncLocalMaxRetries
    exception is raised.

'''



from threading import Lock
from CorpsMsg import *
from enum import IntEnum
from Exceptions import *
from time import sleep



# For internal comm in __getattr__
class FutureExitType(IntEnum):
    No_Error = 0
    Attr_Error = 1
    AsyncExecution_Error = 2
    AsyncAttribute_Error = 3


# "Return" type if client accesses an attribute other than Ret, ret, or ret_ready
class NoRetType():
    pass

NoRet = NoRetType()     # need an instance to return


class Future():
    def __init__(self):
        super().__init__()

        self.RetBody = None
        self.RetReady = False
        self.ResultAvailLock = Lock()
        self.ResultAvailLock.acquire()


    def __set_result_and_unlock__(self, RetBody):
        ''' Result came back from service Worker, so store and unlock so __getattr__ can finish up '''

        self.RetBody = RetBody
        self.RetReady = True
        self.ResultAvailLock.release()


    def ret_ready(self):
        return self.RetReady


    def __getattr__(self, attr):
        ''' Process the return data from the service Worker and return the result to the client Worker '''

        ExitType = FutureExitType.No_Error

        self.ResultAvailLock.acquire()

        # Result is now available from the service Worker
        if attr == 'ret' or attr == 'Ret':
            if self.RetBody != None:
                if self.RetBody.RetType == CorpsRetType.Ok:
                    TempResult = self.RetBody.Ret

                elif self.RetBody.RetType == CorpsRetType.AsyncExecutionExc:
                    TempResult = NoRet
                    TypeName, Value, TracebackStrings = self.RetBody.Ret
                    ExitType = FutureExitType.AsyncExecution_Error

                elif self.RetBody.RetType == CorpsRetType.AsyncAttributeExc:
                    TempResult = NoRet
                    TypeName, Value, TracebackStrings = self.RetBody.Ret
                    ExitType = FutureExitType.AsyncAttribute_Error

            else:
                TempResult = NoRet

        else:
            ExitType = FutureExitType.Attr_Error
            TempResult = NoRet

        self.ResultAvailLock.release()  # don't really need since we're done with Future

        if ExitType == FutureExitType.No_Error:
            return TempResult

        elif ExitType == FutureExitType.AsyncExecution_Error:
            raise AsyncExecutionError(TypeName, Value, TracebackStrings)

        elif ExitType == FutureExitType.AsyncAttribute_Error:
            raise AsyncAttributeError(TypeName, Value, TracebackStrings)

        elif ExitType == FutureExitType.Attr_Error:
            raise AttributeError(f'{attr} not an attribute of Future')

        return TempResult


def wait_all(FutRets, InitDelay=0.05, DelayIncPct=20, MaxTries=25):
    '''
        Wait until all Futures results have completed or we exceed MaxTries waits for uncompleted results.

        Uses a sleepy waiting algorithm which has an initial wait time of InitDelay which then increases DelayIncPct
        for each wait thereafter.
    '''

    Delay = InitDelay
    DelayInc = 1 + DelayIncPct/100

    NotReady = [i for i in range(len(FutRets))]
    tries = 1

    while tries <= MaxTries and len(NotReady) > 0:
        sleep(Delay)
        Delay *= DelayInc

        StillNotReady = []
        for i in range(len(NotReady)):
            j = NotReady[i]

            if FutRets[j].ret_ready() == False:
                StillNotReady.append(j)

        NotReady = StillNotReady
        tries += 1


    if tries > MaxTries:
        raise AsyncLocalMaxRetries(f'wait_all: {MaxTries} attempts failed!')

    else:
        return True


def wait_next(FutRets, InitDelay=0.05, DelayIncPct=20, MaxTries=25):
    '''
        Return the next ready Futures result index or we exceed MaxTries waits for uncompleted results.

        Uses a sleepy waiting algorithm which has an initial wait time of InitDelay which then increases DelayIncPct
        for each wait thereafter.
    '''

    Delay = InitDelay
    DelayInc = 1 + DelayIncPct/100

    NotReady = [i for i in range(len(FutRets))]
    tries = 1

    while tries <= MaxTries and len(NotReady) > 0:
        sleep(Delay)
        Delay *= DelayInc

        StillNotReady = []
        for i in range(len(NotReady)):
            j = NotReady[i]

            if FutRets[j].ret_ready() == True:
                yield j

            else:
                StillNotReady.append(j)

        NotReady = StillNotReady
        tries += 1


    if tries > MaxTries:
        raise AsyncLocalMaxRetries(f'wait_next: {MaxTries} attempts failed!')
