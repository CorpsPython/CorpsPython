
'''
    Corps Python Integration Test


    Runs a set of integration tests, each emphasizing a different aspect of Corps Python.  See the documentation of
    each test for information about its particular focus.

    CorpsTest0.py can be used as a template for an individual test.

    To add a new test edit Tests[] below.

    Tests parameters are provided to each test as a CorpsTestParms object.  TestParms contains a dict of them.
    Edit ParmsId to choose which TestParms to use.  Not all tests use all of the test parameters.

    To change configuration variables edit CorpsTestConfig.py (master list in ConfigGlobals.py).

    The number of Envs, NumEnvs, is handled as a special case to demonstrate how to use environment variables in the
    configuration files.  The environment variable is set here from its value in the chosen TestParm.
    CorpsTestConfig.py reads it from the environment and sets NumEnv's value from it.
'''



from multiprocessing import Process
from Tests.CorpsTest0 import run_CorpsTest0
from Tests.CorpsTest1 import run_CorpsTest1
from Tests.CorpsTestParms import CorpsTestParms
import os



if __name__ == '__main__':


    # Edit to add tests
    Tests = [
        run_CorpsTest0,
        run_CorpsTest1
        ]

    # Reminder: NumGlobalServers, NumClients and NumClientsServers attrs of CorpsTestParms are per Env
    TestParms = {
        0.0: CorpsTestParms(1, 0, 1, 1, 1),
        0.1: CorpsTestParms(1, 1, 1, 0, 1),
        1: CorpsTestParms(1, 1, 1, 1, 1),
        2: CorpsTestParms(2, 2, 2, 2, 10),
        3: CorpsTestParms(3, 3, 3, 3, 50),

        2.1: CorpsTestParms(2, 1, 1, 1, 1),
        3.1: CorpsTestParms(3, 1, 1, 1, 1),
        25.1: CorpsTestParms(25, 1, 1, 1, 1),
        3.50: CorpsTestParms(3, 1, 1, 1, 50),
        }


    # Edit to get different TestParms
    ParmsId = 3

    P = TestParms[ParmsId]


    # Set an enironment variable for NumEnvs which CorpsTestConfig reads
    os.environ['NumEnvs'] = str(P.NumEnvs)

    ConfigFiles = ['Tests/CorpsTestConfig.py']
    CorpsPythonVersion = 'C o r p s   P y t h o n   0 . 1 . 0'


    print(f'\n{CorpsPythonVersion}   T e s t i n g   S t a r t e d')

    # Each test is run as a separate process from this script.
    # The tests are run sequentially - they run to completion before beginning the next one.
    for Test in Tests:
        TestProcess = Process(target=Test, args=(CorpsPythonVersion, ConfigFiles, P))
        TestProcess.start()
        TestProcess.join()

    print(f'\n{CorpsPythonVersion}   T e s t i n g   C o m p l e t e d')