
from Corps import Corps
from Workers import LocType, create_Corps
from sys import exc_info
from Future import wait_next
from EnvGlobals import my_Host, my_Ip, my_Port
from Packer import versions
from Exceptions import AsyncLocalMaxRetries, AsyncRemoteMaxRetries
from traceback import format_exception



'''
    doc
    
    cleanup imports
    
    loc defaults and wait for multi-host to test specifics?
    
    exit/kill code implicit vs explicit?
   
'''



class WorkerCorps(Corps):
    def __init__(self):
        super().__init__()

        print(f'{self} starting')
        self.start()


    def run_tests(self):
        print(f'{self} testing completed')
        return True


    def mirror(self, a):
        return a


    def cleanup(self):
        print(f'{self} exiting')
        return True


class MgrCorps(Corps):
    def __init__(self, MaxLevel, Level, NumWorkers, GlobalWorker, ConfigFiles=[]):
        super().__init__()
        print(f'{self} initializing')

        self.ExtWorkers = []
        self.ContWorkers = []

        self.WorkerTags = []    # incl next MgrCorps and GlobalWorkerCorps

        if GlobalWorker == None:
            Tag = f'GlobalWorkerCorps'
            self.WorkerTags.append(Tag)
            self.GlobalWorker = create_Corps(WorkerCorps, Managed=False, Ext=True, Tag=Tag, ConfigFiles=ConfigFiles)
            self.GlobalCreator = True
        else:
            self.GlobalWorker = GlobalWorker
            self.GlobalCreator = False

        if Level < MaxLevel:
            Tag = 'MgrCorps.' + f'{Level + 1}'
            self.NextMgr = create_Corps(MgrCorps, MaxLevel, Level + 1, NumWorkers, self.GlobalWorker, \
                                                                        Ext=True, Tag=Tag, ConfigFiles=ConfigFiles)
            self.WorkerTags.append(Tag)
        else:
            self.NextMgr = None

        for i in range(NumWorkers):
            Tag = 'ExtWorkerCorps.' + f'{Level}.' + f'{i}'
            self.WorkerTags.append(Tag)
            self.ExtWorkers.append(create_Corps(WorkerCorps, Ext=True, Tag=Tag, ConfigFiles=ConfigFiles))

        for i in range(NumWorkers):
            Tag = 'ContWorkerCorps.' + f'{Level}.' + f'{i}'
            self.WorkerTags.append(Tag)
            self.ContWorkers.append(create_Corps(WorkerCorps, Ext=False, Tag=Tag, ConfigFiles=ConfigFiles))


        # todo: create Conc in Env 1 and pass various Corps to it to test


        print(f'{self} starting')
        self.start()


    def run_tests(self):
        ''' Run all of the tests concurrently

            Must be in same order created for Rets and WorkerTags to be lined up
        '''

        print(f'{self} testing started')


        # test Corps class's my_ExtName()
        aRet = self.GlobalWorker.my_ExtName()
        theGlobal = aRet.Ret

        assert f'{self.GlobalWorker}' == f'{theGlobal}'

        a = '12345678'
        aRet = (self.GlobalWorker.mirror(a)).Ret
        assert aRet == a

        aRet = (theGlobal.mirror(a)).Ret
        assert aRet == a


        Rets = []

        # todo: have Conc test against one global, ext, and cont corps each

        if self.GlobalWorker != None:
            Rets.append(self.GlobalWorker.run_tests())

        if self.NextMgr != None:
            Rets.append(self.NextMgr.run_tests())

        for ExtWorker in self.ExtWorkers:
            Rets.append(ExtWorker.run_tests())

        for ContWorker in self.ContWorkers:
            Rets.append(ContWorker.run_tests())

        # todo: test for True return
        for i in range(len(Rets)):
            try:
                Ret = Rets[i].Ret

            except:
                print(f'\n{self}:  {self.WorkerTags[i]}' +
                                                                f'   E x c e p t i o n: exec_info: {exc_info()}\n')
                return False

        print(f'{self} testing completed')
        return True


    def cleanup(self):
        # todo: no need to kill anything that is managed, leave some to test that path though

        if self.GlobalWorker != None and  self.GlobalCreator == True:
            self.GlobalWorker.exit(NoReply=True)

        if self.NextMgr != None:
            self.NextMgr.exit(NoReply=True)

        for ExtWorker in self.ExtWorkers:
            ExtWorker.exit(NoReply=True)

        for ContWorker in self.ContWorkers:
            ContWorker.exit(NoReply=True)

        print(f'{self} exiting')
        return True


def run_CorpsTest2(Version, ConfigFiles, P):
    '''
        Driver function (P is a CorpsTestParm and we will ignore most attributes).

    '''

    print('\n\nT e s t   2\n')

    # MgrCorps init: MaxLevel, Level, NumWorkers, GlobalWorker

    # todo: put the original back
    #TheMgrCorps = create_Corps(MgrCorps, P.CorpsDepth, 1, P.NumClientsServers, None, Managed=False, Ext=True, \
    #                                                                       Tag='MgrCorps.1', ConfigFiles=ConfigFiles)

    TheMgrCorps = create_Corps(MgrCorps, 3, 1, 2, None, Tag='MgrCorps.1', ConfigFiles=ConfigFiles)
    #TheMgrCorps = create_Corps(MgrCorps, 1, 1, 1, None, Tag='MgrCorps.1', ConfigFiles=ConfigFiles)

    print(f'\n{Version} \nRunning on Host {my_Host()} ({my_Ip()}) Port {my_Port()}\n')
    print(f'Pickle:  {versions()}')

    print(f'TestCorps2 testing started')
    Ret = TheMgrCorps.run_tests()

    try:
        # wait here until testing completed
        if Ret.Ret:
            pass

    except:
        print(f'\nC o r p s   P y t h o n   T e s t   2   E x c e p t i o n: exec_info: {exc_info()}\n')

    print('\nTestCorps2 exiting')
    TheMgrCorps.exit(NoReply=True)
