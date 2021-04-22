
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
    def __init__(self, GlobalWorkerCorps):
        print(f'{self} initing')
        super().__init__()
        self.GlobalWorker = GlobalWorkerCorps

        #print(f'{self} starting')
        self.start()


    def run_tests(self):
        print(f'{self} testing')

        if self.GlobalWorker != None:
            self.GlobalWorker.run_tests()

        return True


class MgrCorps(Corps):
    def __init__(self, MaxLevel, Level, NumWorkers, GlobalWorker):
        print(f'{self} initing')
        super().__init__()

        self.ExtWorkers = []
        self.ContWorkers = []

        self.WorkerTags = []    # incl next MgrCorps and GlobalWorkerCorps

        if GlobalWorker == None:
            Tag = f'GlobalWorkerCorps Level {Level} use'
            self.WorkerTags.append(Tag)
            self.GlobalWorker = create_Corps(WorkerCorps, Ext=True, Tag=Tag)

        if Level != MaxLevel:
            Tag = 'MgrCorps.' + f'{Level + 1}'
            self.NextMgr = create_Corps(MgrCorps, MaxLevel, Level + 1, NumWorkers, self.GlobalWorker, Ext=True, Tag=Tag)
        else:
            Tag = "No next MgrCorps"
            self.NextMgr = None

        self.WorkerTags.append(Tag)
            
        for i in range(NumWorkers):
            Tag = 'ExtWorkerCorps.' + f'{Level}.' + f'{i}'
            self.WorkerTags.append(Tag)
            self.ExtWorkers.append(create_Corps(WorkerCorps, Ext=True, Tag=Tag))

        for i in range(NumWorkers):
            Tag = 'ContWorkerCorps.' + f'{Level}.' + f'{i}'
            self.WorkerTags.append(Tag)
            self.ContWorkers.append(create_Corps(WorkerCorps, Ext=False, Tag=Tag))

        print(f'{self} starting')
        self.start()


    def run_tests(self):
        ''' Run all of the tests concurrently '''

        #print(f'{self} testing')

        Rets = []

        if self.GlobalWorker != None:
            Rets.append(self.GlobalWorker.run_tests())

        if self.NextMgr != None:
            Rets.append(self.NextMgr.run_tests())
        else:
            Rets.append(None)
            
        for ExtWorker in self.ExtWorkers:
            Rets.append(ExtWorker.run_tests())
            
        for ContWorker in self.ContWorkers:
            Rets.append(ContWorker.run_tests())


        next_ret_i = wait_next(Rets)

        for i in next_ret_i:
            if Ret != None:
                try:
                    Ret = Rets[i].Ret

                except:
                    print(f'\nC o r p s   T e s t 2   W o r k e r  {self.WorkerTags[i]}' +
                                                                f'   E x c e p t i o n: exec_info: {exc_info()}\n')

        return True


    def cleanup(self):
        pass


class TestCorps1(Corps):
    def __init__(self):
        print(f'{self.my_Tag()} created')
        super().__init__()
        self.start()

    def runit(self):
        print(f'{self.my_Tag()} running')
        return True

    def cleanup(self):
        print(f'{self.my_Tag()} exiting')


class TestCorps(Corps):
    def __init__(self):
        print(f'{self.my_Tag()} created')
        super().__init__()
        self.TheTestCorps1 = create_Corps(TestCorps1, Tag='T e s t C o r p s  1', ConfigFiles=self.ConfigFiles)
        self.start()

    def runit(self):
        print(f'{self.my_Tag()} running')

        FutRet = self.TheTestCorps1.runit()
        Ret = FutRet.Ret
        self.TheTestCorps1.exit()
        return True

    def cleanup(self):
        print(f'{self.my_Tag()} exiting')


def run_CorpsTest2(Version, ConfigFiles, P):
    '''
        Driver function (P is a CorpsTestParm and we will ignore most attributes).

    '''

    print('\n\nT e s t   2\n')

    TheTestCorps = create_Corps(TestCorps, Tag='T e s t C o r p s', ConfigFiles=ConfigFiles)
    FutRet = TheTestCorps.runit()
    Ret = FutRet.Ret
    TheTestCorps.exit()
    print(f'run_CorpsTest2 exiting')

    # TheMgrCorps = create_Corps(MgrCorps, P.CorpsDepth, 0, P.NumClientsServers, None, Ext=True, Tag='MgrCorps.0', \
    #                                                                                           ConfigFiles=ConfigFiles)
    #
    # print(f'New Corps {TheMgrCorps.my_Tag().Ret} {TheMgrCorps}')
    #
    # print(f'\n{Version} \nRunning on Host {my_Host()} ({my_Ip()}) Port {my_Port()}\n')
    # print(f'Pickle:  {versions()}')
    #
    # Ret = TheMgrCorps.run_tests()
    #
    # try:
    #     # wait here until testing completed
    #     if Ret.Ret:
    #         pass
    #
    # except:
    #     print(f'\nC o r p s   P y t h o n   T e s t   2   E x c e p t i o n: exec_info: {exc_info()}\n')

    #print('\nTestCorps2 exiting')
    #TheMgrCorps.exit()
