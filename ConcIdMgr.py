
'''
    ConcIdMgr generates Env-global Conc Id numbers.


    Id numbers begin at 0 and run up to MAX_CONCID.

    In long-running Corps we will eventually run out of Conc Ids and will need to keep track of what's been allocated
    and what's free.  Currently we just gen an exception via an assert.

    The solution is to dealloc a concId when Concs cleanup by having it send a message to the Mgr's EnvMgr which calls
    dealloc here (all code to be implemented).  We will need a way to keep track of alloc'd vs unalloc'd Ids (given the
    size of the space, probably keeping track of ranges would be a reasonable way).

    All operations are protected by a lock.

    One instance per Env is instantiated in EnvGlobals.py.
'''



from threading import Lock



# Top of range for Conc Id numbers
MAX_CONCID = pow(2,32)


# Pre-allocated ConcId numbers...see Corps.py and Env.py
ENVMGR_CONCID = 0
CORPSMGR_CONCID = 1
CORPS_CONCID = 2



class ConcIdMgr():
    def __init__(self):
        self.Lock = Lock()

        self.Lock.acquire()

        self.NextConcId = 0

        self.Lock.release()


    def new(self):
        ''' Gen a new Conc Id number '''

        self.Lock.acquire()

        Next = self.NextConcId
        self.NextConcId += 1

        self.Lock.release()

        assert Next < MAX_CONCID
        return Next
