
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
        print(f'{self.my_Tag()} initing')
        super().__init__()
        self.GlobalWorker = GlobalWorkerCorps

        #print(f'{self.my_Tag()} starting')
        self.start()


    def run_tests(self):
        print(f'{self.my_Tag()} testing')

        if self.GlobalWorker != None:
            self.GlobalWorker.run_tests()

        return True


class MgrCorps(Corps):
    def __init__(self, MaxLevel, Level, NumWorkers, GlobalWorker):
        print(f'{self.my_Tag()} initing')
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

        print(f'{self.my_Tag()} starting')
        self.start()


    def run_tests(self):
        ''' Run all of the tests concurrently '''

        #print(f'{self.my_Tag()} testing')

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


def run_CorpsTest2(Version, ConfigFiles, P):
    '''
        Driver function (P is a CorpsTestParm and we will ignore most attributes).

    '''

    print('\n\nT e s t   2\n')

    # TheMgrCorps = create_Corps(MgrCorps, P.CorpsDepth, 0, P.NumClientsServers, None, Ext=True, Tag='MgrCorps.0')
    #
    # print(f'New Corps {TheMgrCorps.___target___}')
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

    print('\nTestCorps2 exiting')
    #TheMgrCorps.exit()
