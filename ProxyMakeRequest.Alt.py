
'''

    (This is an alternative, experimental version of ProxyMakeRequest.py.   The regular version passes the request to
    the servicing Worker and then returns control to the requesting Worker.  Here we set up the request and schedule
    the entire request processing - connect, send and receive - to ___proxy_finish_request().  The final thread pool
    sizes across the various Envs when running the CorpsPythonTest integration tests are about two orders of magnitude
    greater compared to the regular version!)

    Make requests to Workers in other threads or processes.

    The request is initiated in the calling client Worker's thread in ___proxy_make_request().

    A request for another thread to complete the request in ___proxy_finish_request() is placed on the ThreadPool's
    WorkQ.

    A Future with the result locked is then returned to the client.

    When the request is complete (i.e. the service Worker has responded) the Future is requested to finish up and
    make the result available to the client.

    Implements a simple state machine with three states as we progress from making a connection to the server port,
    sending the request, and receiving the response.  A failure in either the send or receive sends us back to making
    a connection.

    If (Config variable) Max_Msg_Request_Attempts are made without success an AsyncLocalMaxRetries is raised.
'''

from CorpsMsg import *
from MsgHdlr import *
from EnvGlobals import TheThread, _EnvTable, _ThreadPool, my_Ip, my_Port
from sys import exc_info
from Future import Future
from enum import IntEnum
from ResultsCache import ResultsCacheKey
from ConfigGlobals import Max_Msg_Request_Attempts
from Exceptions import AsyncLocalMaxRetries
from logging import debug



# State reflects what operation is attempted next
class ProxyState(IntEnum):
    CONN = 1
    SEND_REQU = 2
    RECV_RET = 3


def ___proxy_make_request(self, ServerAddr, MethodName, *Args, **KwArgs):
    ''' Initiate a Msg request to a servicing Worker '''

    TheConcAddr = TheThread.TheConcAddr     # the client Conc whose Thread is running and who called the proxy

    # Initialize a request
    MsgBody = CorpsRequest()

    MsgBody.MsgType = CorpsMsgType.ConcRequ
    MsgBody.ClientAddr = TheConcAddr
    MsgBody.ServerAddr = ServerAddr
    MsgBody.MethodName = MethodName
    MsgBody.Args = Args
    MsgBody.KwArgs = KwArgs

    FutRet = Future()

    # Get another thread to finish
    cmd = lambda: ___proxy_finish_request(MsgHdlr, MsgBody, FutRet)
    _ThreadPool.put_cmd(cmd)

    # Return unfinished request's Future
    return FutRet


def ___proxy_finish_request(MsgHdlr, MsgBody, FutRet):
    ''' Finish a Msg request to a servicing Worker '''

    Attempt = 1
    MsgIdSet = False        # Want to set this once
    State = ProxyState.CONN


    # Enter the state machine
    while Attempt <= Max_Msg_Request_Attempts:
        if State == ProxyState.CONN:
            MsgHdlr, MsgId = connect_to_server(MsgBody.ServerAddr, Attempt)     # MsgId invalid after Attempt = 1

            if MsgHdlr != None:
                if MsgIdSet == False:
                    MsgBody.MsgId = ResultsCacheKey(my_Ip(), my_Port(), MsgId)
                    MsgIdSet = True     # Request init is complete

                State = ProxyState.SEND_REQU
                continue

            else:
                Attempt += 1
                continue

        elif State == ProxyState.SEND_REQU:
            if send_request_to_server(MsgHdlr, MsgBody) == False:
                MsgHdlr.close()
                Attempt += 1
                State = ProxyState.CONN
                continue

            else:
                State = ProxyState.RECV_RET

        elif State == ProxyState.RECV_RET:
            RetBody = recv_response_from_server(MsgHdlr, MsgBody)

            if RetBody == None:
                MsgHdlr.close()
                Attempt += 1
                State = ProxyState.CONN
                continue

            # success
            else:
                MsgHdlr.close()
                FutRet.__set_result_and_unlock__(RetBody)
                return FutRet

    # all attempts failed
    raise AsyncLocalMaxRetries( \
            f'{MsgBody.ClientAddr} finish__request to {MsgBody.ServerAddr}: {Max_Msg_Request_Attempts} attempts failed!')


def connect_to_server(ServerAddr, Attempt):
    ''' Make a connection and return a MsgHdlr and a Msgid (valid only for 1st attempt) '''

    TheEnvRecord, MsgId = _EnvTable.get_to_connect(ServerAddr.LocEnvId, Attempt)

    try:
        NetwHdlr = TheEnvRecord.NetwFactory.new_client_netwhdlr(TheEnvRecord.IPAddr, TheEnvRecord.Port)

    except:
        return None, None

    MsgHdlr = TheEnvRecord.MsgHdlrFactory.new_client_msghdlr(NetwHdlr)
    return MsgHdlr, MsgId


def send_request_to_server(MsgHdlr, MsgBody):
    ''' Send the request '''

    send_ret = False
    try:
        send_ret = MsgHdlr.send_msg(MsgBody)

    except:
        debug(f'{MsgBody.ClientAddr} send_request_to_server to {MsgBody.ServerAddr} Exception:\n\t{exc_info()[1]}')
        return False

    if send_ret == False:
        debug(f'{MsgBody.ClientAddr} send_request_to_server to {MsgBody.ServerAddr}: Error sending Request')
        return False

    return True


def recv_response_from_server(MsgHdlr, MsgBody):
    ''' Receive the response '''

    RetBody = None
    try:
        RetBody = MsgHdlr.rec_msg()

    except:
        debug(f'{MsgBody.ClientAddr} recv_response_from_server {MsgBody.ServerAddr} Exception:\n\t{exc_info()[1]}')
        return None

    if RetBody == None:
        debug(f'{MsgBody.ClientAddr} recv_response_from_server {MsgBody.ServerAddr}: Error receiving Return')
        return None

    assert type(RetBody) == CorpsReturn, '{MsgBody.ClientAddr} finish_request to {MsgBody.ServerAddr}: RetBody not CorpsReturn type'
    assert RetBody.MsgType == CorpsMsgType.ConcRet, '{MsgBody.ClientAddr} finish_request {MsgBody.ClientAddr} to {MsgBody.ServerAddr}: Msg Type not ConcRet'

    return RetBody
