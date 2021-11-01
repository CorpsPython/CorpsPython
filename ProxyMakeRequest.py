
'''
    Make requests to Workers in other threads or processes.

    The request is initiated in the calling client Worker's thread in ___proxy_make_request().

    A request for another thread to complete the request in ___proxy_finish_request() is placed on the ThreadPool's
    WorkQ.

    A Future with the result locked is then returned to the client.

    When the request is complete (i.e. the service Worker has responded) the Future is requested to finish up and
    make the result available to the client.

    Both functions implement a simple state machine with three states as we progress from making a connection to
    the server port, sending the request, and receiving the response.  A failure in either the send or receive sends
    us back to making a connection.

    If (Config variable) Max_Msg_Request_Attempts are made without success an AsyncLocalTimeout is raised.
'''



from CorpsMsg import *
from EnvGlobals import TheThread, _EnvTable, _ContCorpsEnvTable, _ExtCorpsEnvTable, _ThreadPool, my_Ip, my_Port, \
    _MsgIdMgr, DefaultEnvRecord
from sys import exc_info
from Future import Future
from enum import IntEnum
from ResultsCache import ResultsCacheKey
from Exceptions import AsyncLocalMaxRetries
from logging import debug
from ConcAddr import ConcAddr, ExtAddr
from EnvAddrSpace import *



# State reflects what operation is attempted next
class ProxyState(IntEnum):
    CONN = 1
    SEND_REQU = 2
    RECV_RET = 3


def ___proxy_make_request(self, ServerAddr, MethodName, *Args, **KwArgs):
    ''' Initiate a Msg request to a servicing Worker '''

    from ConfigGlobals import Max_Msg_Request_Attempts

    TheConcAddr = TheThread.TheConcAddr     # the client Conc whose Thread is running and who called the proxy

    # from EnvGlobals import NullConcAddr
    # if TheConcAddr == NullConcAddr:
    #     print(f'proxy: Null ConcAddr on request to {ServerAddr} for {MethodName}()')

    # Initialize a request
    MsgBody = CorpsRequest()

    MsgBody.MsgType = CorpsMsgType.ConcRequ

    NoReply = 'NoReply'
    NoReplyFlag = False
    if NoReply in KwArgs:
        if KwArgs[NoReply] == True:
            MsgBody.MsgFlags |= NoReplyBitMask
            NoReplyFlag = True

        del KwArgs[NoReply]

    MsgBody.MsgId = ResultsCacheKey(my_Ip(), my_Port(), _MsgIdMgr.new())
    MsgBody.ClientAddr = TheConcAddr
    MsgBody.ServerAddr = ServerAddr
    MsgBody.MethodName = MethodName
    MsgBody.Args = Args
    MsgBody.KwArgs = KwArgs


    Attempt = 1
    State = ProxyState.CONN

    # Enter the state machine
    while Attempt <= Max_Msg_Request_Attempts:
        # $ need to handle connect errors
        if State == ProxyState.CONN:
            MsgHdlr = connect_to_server(ServerAddr)

            if MsgHdlr != None:
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

            # success...if client does not want a reply from the service return a None
            # otw schedule ___proxy_finish_request for another thread and return Future to client
            # State is now implicitly ProxyState.RECV_RET for ___proxy_finish_request
            else:
                FutRet = Future()

                if NoReplyFlag == True:
                    RetBody = CorpsReturn()

                    RetBody.Ret = None
                    RetBody.MsgType = CorpsMsgType.ConcRet
                    RetBody.ClientAddr = MsgBody.ClientAddr
                    RetBody.ServerAddr = MsgBody.ServerAddr

                    FutRet.__set_result_and_unlock__(RetBody)
                    MsgHdlr.close()

                else:
                    cmd = lambda: ___proxy_finish_request(MsgHdlr, MsgBody, FutRet, Attempt)
                    _ThreadPool.put_cmd(cmd)

                # cmd = lambda: ___proxy_finish_request(MsgHdlr, MsgBody, FutRet, Attempt)
                # _ThreadPool.put_cmd(cmd)
                return FutRet

    # all attempts failed
    raise AsyncLocalMaxRetries( \
            f'{MsgBody.ClientAddr} make_request to {MsgBody.ServerAddr}: {Max_Msg_Request_Attempts} attempts failed!')


def ___proxy_finish_request(MsgHdlr, MsgBody, FutRet, CurrentAttempt):
    '''
        Finish a Msg request to a servicing Worker

        Assumes MsgHdlr is still connected upon entry and entry State is implicitly ProxyState.RECV_RET
    '''

    from ConfigGlobals import Max_Msg_Request_Attempts

    Attempt = CurrentAttempt
    State = ProxyState.RECV_RET     # make state explicit

    # continue in state machine
    while Attempt <= Max_Msg_Request_Attempts:
        if State == ProxyState.CONN:
            MsgHdlr = connect_to_server(MsgBody.ServerAddr)

            if MsgHdlr != None:
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


def connect_to_server(ServerAddr):
    ''' Make a connection and return a MsgHdlr '''

    # For ConcAddrs get the IpAddr and Port from the EnvRecord in the EnvTable
    if type(ServerAddr) == ConcAddr:
        LocEnvId = ServerAddr.LocEnvId

        # Select the appropriate EnvTable
        if CORPSMGR_ENVID <= LocEnvId <= MAX_ENVID:
            TheEnvTable = _EnvTable

        elif MIN_EXT_CORPS_ENVID <= LocEnvId <= MAX_EXT_CORPS_ENVID:
            TheEnvTable = _ExtCorpsEnvTable

        elif MIN_CONT_CORPS_ENVID <= LocEnvId <= MAX_CONT_CORPS_ENVID:
            TheEnvTable = _ContCorpsEnvTable

        else:
            raise ValueError(f'connect_to_server: Bad ServerAddr {ServerAddr}')

        TheEnvRecord = TheEnvTable.get(LocEnvId)

        try:
            NetwHdlr = TheEnvRecord.NetwFactory.new_client_netwhdlr(TheEnvRecord.IpAddr, TheEnvRecord.Port)

        except:
            return None

    # For ExtAddrs the IpAddr and Port are contained in it
    else:
        TheEnvRecord = DefaultEnvRecord

        try:
            NetwHdlr = TheEnvRecord.NetwFactory.new_client_netwhdlr(ServerAddr.IpAddr, ServerAddr.Port)

        except:
            return None

    MsgHdlr = TheEnvRecord.MsgHdlrFactory.new_client_msghdlr(NetwHdlr)
    return MsgHdlr


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
