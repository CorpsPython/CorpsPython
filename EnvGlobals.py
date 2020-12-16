
'''
    Globals per Env

    Many of the items declared here are "managed" - they are thread-safe objects whose operations are locked upon
    entry and unlocked upon exit.

'''



from threading import local
from ConcIdMgr import ConcIdMgr
from Addr2Conc import Addr2Conc
from ThreadPool import ThreadPool
from TcpFactory import TcpFactory
from ConcAddr import ConcAddr
from CorpsMsgHdlrFactory import CorpsMsgHdlrFactory
from EnvRecord import EnvRecord
from EnvTable import EnvTable
from socket import getfqdn, getaddrinfo, AF_INET
from ipaddress import ip_address



MyHost = None

def my_Host():
    global MyHost

    if MyHost == None:
        MyHost = getfqdn()

    return MyHost


MyIp = None

def my_Ip():
    global MyIp

    if MyIp == None:
        MyIp = ip_address(getaddrinfo(my_Host(), 0, family=AF_INET)[0][4][0])

    return MyIp


MyPort = None

def set_MyPort(Port):
    global MyPort
    MyPort = Port

def my_Port():
    global MyPort
    assert MyPort != None, "MyPort not initialzed"
    return MyPort


NullConcAddr = ConcAddr(-1, -1, -1)
TheThread = local()                     # private to and global within every Thread
TheThread.TheConcAddr = NullConcAddr    # set in Conc main() after assignment of the Conc to a Thread, reset before exit


EnvId = 0                   # set during init by Env, read-only thereafter

def set_EnvId(Id):
    global EnvId
    EnvId = Id

def my_EnvId():
    global EnvId
    return EnvId


EnvMgrAddr = NullConcAddr      # set during init by Env, read-only thereafter

def set_EnvMgrAddr(Addr):
    global EnvMgrAddr
    EnvMgrAddr = Addr

def my_EnvMgrAddr():
    global EnvMgrAddr
    return EnvMgrAddr


_ConcIdMgr = ConcIdMgr()

_Addr2Conc = Addr2Conc()

_ThreadPool = ThreadPool()

_EnvTable = EnvTable()

TheTcpFactory = TcpFactory(_ThreadPool, _Addr2Conc)

TheCorpsMsgHdlrFactory = CorpsMsgHdlrFactory()

DefaultEnvRecord = EnvRecord(TheCorpsMsgHdlrFactory, TheTcpFactory, my_Ip(), 0)


