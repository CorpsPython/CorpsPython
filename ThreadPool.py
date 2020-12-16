
'''
    ThreadPool and ThreadPool Thread classes

    Each Env has a pool of threads, the ThreadPool, that grab work off of the ThreadPool's WorkQ.

    The work, a command, or cmd, is a lambda placed there by a thread or a Worker using the ThreadPool's put_cmd().

    Each thread, a PoolThread, loops on the ThreadPool's get_cmd() and simply executes the cmd.

    The Worker's all run on a PoolThread.  The thread has a UsesA relationship with the Worker, with the Worker's
    main() executed by the thread (TcpConnector places RequestRelay() as the cmd which calls the Worker's main()).
    The thread's next get_cmd() may result in its being assigned to a different Worker.

    The size of the ThreadPool begins at (Config variable) ThreadPool_MinThreads.

    The size may increase due to the WorkQ length exceeding (Config variable) ThreadPool_MaxQueueLength.  The size
    of the ThreadPool is incremented by (Config variable) ThreadPool_ThreadsInc.
'''



from queue import Queue
from threading import Thread, Lock, Event, current_thread
from logging import info



class WorkQueue(Queue):
    def __init__(self):
        super().__init__()


class PoolThread(Thread):
    def __init__(self, ThreadPool):
        super().__init__(daemon=True)

        self.ThreadPool = ThreadPool
        self._stopevent = Event()

        self.start()


    def run(self):
        while True:
            if self._stopevent.isSet():
                break

            cmd = self.ThreadPool.get_cmd()
            cmd()


    def exit(self):
        self._stopevent.set()


class ThreadPool():
    def __init__(self, ):
        self.TotalThreads = 0
        self.WorkQ = WorkQueue()
        self.Lock = Lock()

        self.__check_pool_size()


    def put_cmd(self, cmd):
        Added = self.__check_pool_size()
        if Added > 0:
            info(f'Thread Pool added {Added} threads,  Total: {self.TotalThreads}')

        self.WorkQ.put(cmd)


    def get_cmd(self):
        cmd = self.WorkQ.get()
        return cmd


    def __check_pool_size(self):
        from ConfigGlobals import ThreadPool_MinThreads, ThreadPool_ThreadsInc, ThreadPool_MaxQueueLength

        Added = 0

        self.Lock.acquire()

        if self.TotalThreads < ThreadPool_MinThreads:
            Added = self.__add_threads(ThreadPool_MinThreads - self.TotalThreads)

        elif self.WorkQ.qsize() >= ThreadPool_MaxQueueLength:
            Added = self.__add_threads(ThreadPool_ThreadsInc)

        self.Lock.release()

        return Added


    # only call within locked code (only from _check_pool_size at this time)
    def __add_threads(self, NoThreads):
        self.TotalThreads += NoThreads
        for i in range(NoThreads):
            PoolThread(self)

        return NoThreads


    def __del_threads(self, Count):
        info(f'ThreadPool terminating {Count} Threads from {self.TotalThreads} total')

        self.Lock.acquire()

        assert Count <= self.TotalThreads
        self.TotalThreads -= Count

        self.Lock.release()

        for i in range(Count):
            cmd = lambda : current_thread().exit()
            self.put_cmd(cmd)


    # delete all but the minimum number
    def __del_allthreads(self):
        from ConfigGlobals import ThreadPool_MinThreads

        self.__del_threads(self.TotalThreads-ThreadPool_MinThreads)
