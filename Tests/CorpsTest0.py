
'''
    CorpsTest0's primary focus is on concurrency (Worker's create_workers() api, using Names (proxies), passing Names,
    operations across Env boundaries, using Futures, executing multiple concurrent requests, etc)

    The Corps creates a list of globals services, distributing them amongst the Envs.  It also creates a list of
    clients, also distributing them amongst the Envs.  All of the services and clients are Concs.

    THe Corps then concurrently requests the clients run their tests.  The completion of the tests is handled as a
    modified form of sleepy waiting - each time the Corps is active it tests each previously uncompleted Future for
    completion and, if any remain uncompleted, sleeps for a short while until the Corps becomes active again.

    Each service has a single idempotent method.

    Each client is instantiated with a list of global services created by the Corps and instantiates a list of its own
    services.  It first tests against the globals and then its own.

    Each client test runs multiple iterations over the list of services, issuing all of the requests concurrently until
    all have been issued.  It utilizes the wait_all() from Future.py (which uses the same modified sleepy waiting
    method Corps used and described above). The client then processes all of the completed results to complete the
    test.

    The Corps processes the results more gradually using wait_next() from Futures.py to process the results
    incrementally.

'''



from Conc import Conc
from Corps import Corps
from Workers import LocType, create_Concs, create_Corps
from sys import exc_info
from Future import NoRet, wait_all, wait_next
from EnvGlobals import my_Host, my_Ip, my_Port
from Packer import versions
from Exceptions import AsyncLocalMaxRetries, AsyncRemoteMaxRetries
from traceback import format_exception



class base0():
    ''' Service 0 base class '''

    def func_adelic(self, Arg1, Arg2, Arg3=10):
        ''' Simple idempotent method so we can pound on it concurrently '''

        return Arg1 + Arg2 + Arg3


class Service0(base0, Conc):
    ''' Service 0 is a Conc derived from a very simple Python class, base0 '''

    def __init__(self):
        super().__init__()

        print(f'Service {self} ready for testing')

        self.start()


    def cleanup(self):
        print(f'Service {self} cleaning up')
        return True


class Client0(Conc):
    '''
        Client0 is a Conc that runs test against a list of global services ("servers") and then against a list
        of services private to each client.

        It exercises create_Concs() by creating all of its private services at once on each Env, for a total of
        NumEnvs times NumClientServers.
    '''

    def __init__(self, Servers, NumEnvs, NumClientsServers, Iters=5):
        ''' Initialize including creating all of the private services '''

        super().__init__()

        self.Servers = Servers                          # global servers
        self.NumEnvs = NumEnvs                          # unused for now
        self.NumClientsServers = NumClientsServers      # number of own clients per Env
        self.ClientsServers = []
        self.Iters = Iters

        self.Me = self.my_Name()
        if self.NumClientsServers > 0:
            self.ClientsServers = create_Concs(Service0, Mgr=self.Me, LocType=LocType.PerEnv, Num=self.NumClientsServers)

        print(f'Client {self} ready for testing')

        self.start()


    def run_all_tests(self):
        ''' Run all of the tests, first against the global services, then against the private ones '''

        print(f'Client {self} starting testing')


        # test Conc's my_Mgr() when both are Concs
        aRet = self.ClientsServers[0].my_Mgr()
        Me = aRet.Ret

        assert f'{self.Me}' == f'{Me}'


        Requests, Errors = self.run_one_test(self.Servers, self.Iters)
        print(f'Client {self} finished {Requests} Requests with {Errors} Errors to ' + \
                                                                            f'{len(self.Servers)} Global Servers')

        Requests, Errors = self.run_one_test(self.ClientsServers, self.Iters)
        print(f'Client {self} finished {Requests} Requests with {Errors} Errors to ' + \
                                                                        f'its own {len(self.ClientsServers)} Servers')

        return True


    def run_one_test(self, Servers, Iters):
        '''
            For Iters times issue a request to each of the services.  Wait for all requests to complete before testing
            the results against their expected values.
        '''

        Requests = 0
        Errors = 0
        FutRets = []
        ExpRets = []

        for i in range(Iters):
            for Server in Servers:
                Arg1, Arg2, Arg3 = i, i * 1.5, 5

                FutRet = Server.func_adelic(Arg1, Arg2, Arg3)
                FutRets.append(FutRet)
                ExpRets.append(Arg1 + Arg2 + Arg3)

        try:
            wait_all(FutRets)

        except AsyncLocalMaxRetries:
            ei = exc_info()
            ftb = format_exception(ei[0], ei[1], ei[2])
            raise AsyncRemoteMaxRetries(ei[0].__name__, ei[1], ''.join(ftb))


        for FutRet, ExpRet in zip(FutRets, ExpRets):
            try:
                Ret = FutRet.Ret

            except:
                Errors += 1
                print(f'\nC l i e n t {self} E x c e p t i o n : exec_info: {exc_info()}\n')

            if Ret == NoRet:
                Errors += 1

            else:
                assert Ret == ExpRet

            Requests += 1

        return Requests, Errors


    def cleanup(self):
        print(f'Client {self} cleaning up')

        for ClientsServer in self.ClientsServers:
            ClientsServer.exit()

        return True


class Corps0(Corps):
    '''
        Corps0 creates a list of global services ("servers") and a list of clients, all distributed evenly across
        the Envs.

        It then concurrently requests all of the clients to run their tests.  It utilizes a modified sleepy waiting to
        incrementally get and process results and then wait for more results to complete.

        Corps0 exercises create_Concs() two ways.  For the services it allows create_Concs to choose which Env
        the services will create on.  For the clients the choice of Env is explicit.
    '''

    def __init__(self, NumEnvs, NumServers, NumClients, NumClientsServers, NumClientIters):
        ''' Initialize including creating the global services and the clients '''

        super().__init__()

        self.NumEnvs = NumEnvs
        self.NumServers = NumServers
        self.NumClients = NumClients
        self.NumClientsServers = NumClientsServers
        self.NumClientIters = NumClientIters
        self.Me = self.my_Name()

        self.Servers = []
        self.Clients = []

        if self.NumServers > 0:
            for i in range(self.NumEnvs):
                NewServers = create_Concs(Service0, Mgr=self.Me, LocType=LocType.Auto, Num=self.NumServers)
                self.Servers.extend(NewServers)

        for env in range(self.NumEnvs):
            NewClients = create_Concs(Client0, self.Servers, self.NumEnvs, \
                self.NumClientsServers, self.NumClientIters, LocType=LocType.EnvId, LocVal=env, Num=self.NumClients)
            self.Clients.extend(NewClients)

        print(f'\n{self} initialized')
        self.start()


    def run_all_tests(self):
        ''' Run all of the tests concurrently '''

        print(f'{self} testing\n')

        # test Conc's my_Name()
        aRet = self.Servers[0].my_Name()
        theServer = aRet.Ret

        assert f'{self.Servers[0]}' == f'{theServer}'

        tot = 123 + 456 + 789
        aRet = (self.Servers[0].func_adelic(123, 456, 789)).Ret
        assert aRet == tot

        aRet = (theServer.func_adelic(123, 456, 789)).Ret
        assert aRet == tot


        # test Conc's my_Mgr() when the Mgr is a Corps' Conc
        aRet = self.Servers[0].my_Mgr()
        Me = aRet.Ret

        assert f'{self.Me}' == f'{Me}'


        FutRets = []
        i = 0
        for Client in self.Clients:
            FutRets.append(Client.run_all_tests())
            i += 1

        next_futret_i = wait_next(FutRets)

        for Cli in next_futret_i:
            try:
                Ret = FutRets[Cli].Ret
                print(f'TestCorps0 {self.Clients[Cli]} completed with return {Ret}')

            except:
                print(f'\nT e s t C o r p s 0   C l i e n t {Cli} {self.Clients[Cli]}' +
                      f'   E x c e p t i o n: exec_info: {exc_info()}\n')


        print(f'\n{self} done testing')
        return True


    def cleanup(self):
        for Client in self.Clients:
            Client.exit()

        for Server in self.Servers:
            Server.exit()

        return True


def run_CorpsTest0(Version, ConfigFiles, P):
    '''
        Driver function (P is a CorpsTestParm).

    '''

    print('\n\nT e s t   0\n')

    TheCorps0 = create_Corps(Corps0, P.NumEnvs, P.NumGlobalServers, P.NumClients, P.NumClientsServers, \
                                                            P.NumClientIters, Tag='Corps0', ConfigFiles=ConfigFiles)

    print(f'New Corps {TheCorps0.my_Tag().Ret} {TheCorps0}')

    print(f'\n{Version} \nRunning on Host {my_Host()} ({my_Ip()}) Port {my_Port()}\n')
    print(f'Pickle:  {versions()}')

    Ret = TheCorps0.run_all_tests()

    try:
        # wait here until testing completed
        if Ret.Ret:
            pass

    except:
        print(f'\nC o r p s   P y t h o n   T e s t   0   E x c e p t i o n: exec_info: {exc_info()}\n')


    print('\nTestCorps0 exiting')
    Ret = TheCorps0.exit(NoReply=True)
    assert Ret.Ret == None


