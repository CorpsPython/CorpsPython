
'''

    Config Global attributes for each instantiated Corps with defaults.

    Defaults can be overridden by user-supplied Config files passed to load_Corps() in Workers.py.

    Most of these attributes are for experts only!

    Of interest to more casual operators is NumEnvs which declares the number of Envs a particular run of a
    Corps will execute in.  Generally a minimum of one Env per core or processor should be used.

    Multiple user-supplied Config files are supported, with the later files overwriting earlier files' setting
    of particular attributes.

    Config attributes are limited to those listed here.  User-defined attributes are discarded.

    Config attributes can be set in the operating environment via a script:

        from os import environ
        environ['NumEnvs'] = str(P.NumEnvs)

    And then read in a user-supplied Config file and the corresponding attribute set:

        from os import environ
        NumEnvs = int(os.environ['NumEnvs'])


    N u m E n v s   =   8

    Number of Environments when Corps is deployed


    T h r e a d P o o l _ M i n T h r e a d s   =   10

    Minimum number of threads in ThreadPool


    T h r e a d P o o l _ T h r e a d s I n c   =   10

    Number of threads added when ThreadPool's WorkQ's Length exceeds ThreadPool_MaxQueueLength


    T h r e a d P o o l _ M a x Q u e u e L e n g t h   =   10

    Maximum length of ThreadPool's WorkQ before ThreadPool_ThreadsInc threads are added


    N e t w o r k i n g _ M a x _ C o n n e c t i o n _ A t t e m p t s   =   25

    Maximum number of attempts to connect to a service


    N e t w o r k i n g _ C l i e n t _ T i m e o u t   =   10

    Number of seconds before a client network operation times out


    N e t w o r k i n g _ S e r v e r _ T i m e o u t   =   10

    Number of seconds before a server network operation times out


    N e t w o r k i n g _ M a x _ Q u u e u e d _ C o n n _ R e q u e s t s   =   100

    Maximum number of connecton requests in queue before refusing any more


    M a x _ M s g _ R e q u e s t _ A t t e m p t s   =   50

    Max round-trip attempts to send and respond to a Msg request between two Workers


    R e s u l t s C a c h e _ M a x _ E n t r y _ T T L   =   timedelta(seconds=1)

    Maximum time to live for a Cache entry


    R e s u l t s C a c h e _ M i n _ C l e a n _ I n t e r v a l   =   timedelta(seconds=2)

    Minimum time between cleaning of old entries

'''



from datetime import timedelta
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL



''' Number of Environments when Corps is deployed '''
NumEnvs = 8


''' ThreadPool '''
# Minimum number of threads in ThreadPool
ThreadPool_MinThreads = 10

# Number of threads added when ThreadPool's WorkQ's Length exceeds ThreadPool_MaxQueueLength
ThreadPool_ThreadsInc = 10

# Maximum length of ThreadPool's WorkQ before ThreadPool_ThreadsInc threads are added
ThreadPool_MaxQueueLength = 10


''' Networking '''
# Maximum number of attempts to connect to a service
Networking_Max_Connection_Attempts = 25

# Number of seconds before a client network operation times out
Networking_Client_Timeout = 10

# Number of seconds before a server network operation times out
Networking_Server_Timeout = 10

# Maximum number of connecton requests in queue before refusing any more
Networking_Max_Queued_Conn_Requests = 100


''' Message Passing '''
# Max round-trip attempts to send and respond to a Msg request between two Workers
Max_Msg_Request_Attempts = 50


''' Results Cache '''
# Maximum time to live for a Cache entry
ResultsCache_Max_Entry_TTL = timedelta(seconds=1)

# Minimum time between cleaning of old entries
ResultsCache_Min_Clean_Interval = timedelta(seconds=2)


''' Logging '''
Logging_Level = WARNING
Logging_Format = '%(levelno)s %(process)d %(asctime)s.%(msecs)03d %(message)s'
Logging_Datefmt='%y-%m-%d %H:%M:%S'
