'''
    CorpsTest1's primary focus is on Names, the proxies used by Corps Python to make requests between Concs, intra-
    and inter-Env.

    We are trying to exercise relevant features of class-based Python objects and make sure they work as Concs.
    The service base classes (and the client that exercises them) are not to be considered complete and any relevant
    features not tested should be added and tested.

    Corps1 creates a list of services ("servers") and a list of clients, all distributed evenly across the Envs.

    Each client is paired with a single service.  Many of the service operations are non-idempotent and this is
    more a test of Names than of concurrency.

    It then concurrently requests all of the clients to run their tests.  It utilizes a modified sleepy waiting to
    incrementally get and process results and then wait for more results to complete.

    Each client test runs multiple iterations over the methods of its service, issuing all of the requests concurrently
    until all have been issued.  It utilizes the wait_all() from Future.py (which uses the same modified sleepy waiting
    method Corps used and described above). The client then processes all of the completed results to complete the
    test.

    The Corps processes the results more gradually - some of the clients complete their tests and the Corps processes
    the results and then sleeps waiting for more to complete.  The clients wait for all to complete and then processes
    the results.
'''



from Conc import Conc
from Corps import Corps
from Workers import create_Workers, load_Corps
from sys import exc_info
from time import sleep
from Future import NoRet, wait_all
from EnvGlobals import my_Host, my_Ip, my_Port
from Packer import versions
from Exceptions import AsyncLocalMaxRetries, AsyncRemoteMaxRetries
from traceback import format_exception



class TgtBase0():
    ''' A service base class '''

    def d1(self, d):
        if d == 0:
            self.div0()
            return 0
        else:
            return 1

    def div0(self):
        1/0

    def foobar0(self, x, y):
        return x / y


class TgtBase1():
    ''' A service base class '''

    def foobar1(self, x, y):
        return x / y

    def foobar3(self, x, y):
        return x * y


class TgtBase2(TgtBase0, TgtBase1):
    ''' A service base class '''

    def foobar2(self, x, y):
        return x / y

    # override foobar3
    def foobar3(self, x, y):
        return x / y


class TgtBase3(TgtBase2):
    ''' A service base class '''

    def __init__(self, Y=25):
        super().__init__()

        self.X = 22
        self.Y = Y

    def fob(self, x, y, z=3):
        return x + y + z

    def sumall(self, lst):
        return (sum(lst))

    def exec_func(self, f, a):
        return f(a)

    class_a = 100

    def get_a(self):
        return self.class_a

    def set_a(self, val):
        self.class_a = val
        return val

    the_a = property(get_a, set_a)

    def no_return(self):
        pass

    def pass_class(self, cls):
        return cls.__name__


def ext_sumall(lst):
    ''' Sample external function '''

    return (sum(lst))


class Service1(TgtBase3, Conc):
    ''' Service Conc derived from various base classes '''

    def __init__(self):
        super().__init__()

        print(f'Service {self.my_Name()} ready for testing')

        self.start()


class Client1(Conc):
    ''' Client Conc '''

    def __init__(self):
        super().__init__()

        print(f'Client {self.my_Name()} ready for testing')

        self.start()


    def run_all_tests(self, Server, Iters):
        '''
            Iters times run all of the service's methods.

            All of the requests against the server are issued concurrently.  Process the results after all
            requests have been issued.
        '''

        print(f'Client {self.my_Name()} starting testing against Service {Server}')

        # test exception returns by forcing a divide by zero
        R = Server.d1(0)

        try:
            Res = R.Ret

        except:
            pass

        else:
            print(f'C l i e n t {self.my_Name()}   d i d   n o t   s e e   E x c e p t i o n !\n')


        # regular testing...
        FutRets = []
        ExpRets = []
        Test = []
        Iter = []

        X = TgtBase3()

        for i in range(Iters):
            Test.append('inherited foobar0')
            Iter.append(i)
            FutRets.append(Server.foobar0(25, 5))
            ExpRets.append(X.foobar0(25, 5))

            Test.append('inherited foobar1')
            Iter.append(i)
            FutRets.append(Server.foobar1(78, 4))
            ExpRets.append(X.foobar1(78, 4))

            Test.append('inherited foobar2')
            Iter.append(i)
            FutRets.append(Server.foobar2(100, 2))
            ExpRets.append(X.foobar2(100, 2))

            Test.append('overriden foobar3')
            Iter.append(i)
            FutRets.append(Server.foobar3(99, 3))
            ExpRets.append(X.foobar3(99, 3))

            Test.append('method fob, with kwarg used')
            Iter.append(i)
            FutRets.append(Server.fob(10, 12, z=25))
            ExpRets.append(X.fob(10, 12, z=25))

            Test.append('method fob, with kwarg default')
            Iter.append(i)
            FutRets.append(Server.fob(10, 12))
            ExpRets.append(X.fob(10, 12))

            Test.append('pass a list')
            Iter.append(i)
            alst = [1, 3, 5, 7, 9, 11, 13, 15]
            FutRets.append(Server.sumall(alst))
            ExpRets.append(X.sumall(alst))

            Test.append('pass a function as arg 1')
            Iter.append(i)
            FutRets.append(Server.exec_func(sum, alst))
            ExpRets.append(X.exec_func(sum, alst))

            Test.append('pass a function as arg 2')
            Iter.append(i)
            FutRets.append(Server.exec_func(ext_sumall, alst))
            ExpRets.append(X.exec_func(ext_sumall, alst))

            # Test.append('pass a lambda as arg')
            # FutRets.append(Server.exec_func(lambda x: sum(x), alst))
            # ExpRets.append(X.exec_func(lambda x: sum(x), alst))

            Test.append('setattr/getattr, init create')  # X was created in __init__and set to 22
            Iter.append(i)
            FutRets.append(Server.X)
            ExpRets.append(X.X)
            if i == 0:
                sleep(.15)      # don't want the set to be done before the get in busy conditions, not foolproof
                Server.X = X.X = 33

            Test.append('getattr kwarg, init create')  # Y was created in __init__and set using kwarg
            Iter.append(i)
            FutRets.append(Server.Y)
            ExpRets.append(X.Y)

            Test.append('setattr/getattr, run-time create') # 'b' is being created on first iteration
            Iter.append(i)
            if i == 0:
                Server.b = X.b = 55
                sleep(.15)     # want the set to be done before the get in busy conditions, not foolproof
            FutRets.append(Server.b)
            ExpRets.append(X.b)

            Val = 222
            X.the_a = Val
            Server.the_a = Val
            assert Server.the_a == X.the_a

            Test.append('method with no return')
            Iter.append(i)
            FutRets.append(Server.no_return())
            ExpRets.append(X.no_return())

            Test.append('class as arg')
            Iter.append(i)
            FutRets.append(Server.pass_class(TgtBase3))
            ExpRets.append(X.pass_class(TgtBase3))


        try:
            wait_all(FutRets)

        except AsyncLocalMaxRetries:
            ei = exc_info()
            ftb = format_exception(ei[0], ei[1], ei[2])
            raise AsyncRemoteMaxRetries(ei[0].__name__, ei[1], ''.join(ftb))


        Errors = 0

        for i in range(len(FutRets)):
            try:
                Ret = FutRets[i].Ret

            except:
                Errors += 1
                print(f'\nC l i e n t {self.my_Name()}   E x c e p t i o n : exec_info: {exc_info()} in Test "{Test[i]}" Iter {Iter[i]}\n')

            else:
                if Ret == NoRet or Ret != ExpRets[i]:
                    Errors += 1
                    print(f'\nC l i e n t {self.my_Name()}   E r r o r  {Ret} vs {ExpRets[i]} in Test "{Test[i]}" Iter {Iter[i]}\n')


        print(f'Client {self.my_Name()} finished {i+1} Requests with {Errors} Errors')

        return True


class Corps1(Corps):
    '''
        Corps1 creates a list of services ("servers") and a list of clients, all distributed evenly across the Envs.

        Each client is paired with a single service.  Many of the service operations are non-idempotent and this is
        more a test of Names than of concurrency.

        It then concurrently requests all of the clients to run their tests.  It utilizes a modified sleepy waiting to
        incrementally get and process results and then wait for more results to complete.

        Corps1 utilizes the defaults for create_Workers(), automatically choosing the Env of creation and creating a
        single Conc at time.  By iterating over the number of Envs and sequentially creating a service followed by a
        client we can evenly distribute Concs across Envs and most of the time have the paired clients and servers in
        different Envs.
    '''

    def __init__(self, NumEnvs, NumClientIters):
        ''' Initialize including creating all of the services and clients '''

        super().__init__()

        self.NumEnvs = NumEnvs
        self.NumClientIters = NumClientIters

        self.Servers = []
        self.Clients = []

        for i in range(NumEnvs):
            self.Servers.extend(create_Workers({self.my_Name()}, Service1))
            self.Clients.extend(create_Workers({self.my_Name()}, Client1))

        print(f'\nTestCorps1 initialized')
        self.start()


    def run_all_tests(self):
        ''' Run all of the tests concurrently '''

        print(f'TestCorps1 testing\n')

        FutRets = []
        for i in range(len(self.Clients)):
            FutRets.append(self.Clients[i].run_all_tests(self.Servers[i], self.NumClientIters))


        Delay = 0.01
        NotReady = [i for i in range(len(FutRets))]

        while len(NotReady) > 0:
            sleep(Delay)
            Delay *= 1.1

            StillNotReady = []
            for i in range(len(NotReady)):
                Cli = NotReady[i]
                if FutRets[Cli].ret_ready() == True:
                    try:
                        Ret = FutRets[Cli].Ret
                        print(f'TestCorps0 Client {Cli} {self.Clients[Cli]} completed with return {Ret}')

                    except:
                        print(f'\nT e s t C o r p s 0   C l i e n t {Cli} {self.Clients[Cli]}' +
                                                                    f'   E x c e p t i o n: exec_info: {exc_info()}\n')


                else:
                    StillNotReady.append(Cli)

            NotReady = StillNotReady


        print('\nTestCorps1 done testing')
        return True


def run_CorpsTest1(Version, ConfigFiles, P):
    '''
        Driver function (P is a CorpsTestParm).

        Runs Corps1 in this process (which creates new processes for all of the Envs excepting the one Corps1 runs in).
    '''

    print('\n\nT e s t   1\n')

    TheCorps1 = load_Corps(Corps1, P.NumEnvs, P.NumClientIters, ConfigFiles=ConfigFiles)

    print(f'\n{Version} \nRunning on Host {my_Host()} ({my_Ip()}) Port {my_Port()}\n')
    print(f'Pickle:  {versions()}')

    Ret = TheCorps1.run_all_tests()

    try:
        # wait here until testing completed
        if Ret.Ret:
            pass

    except:
        print(f'\nC o r p s   P y t h o n   T e s t   1   E x c e p t i o n: exec_info: {exc_info()}\n')


    print('\nTestCorps1 exiting')
    TheCorps1.kill()

