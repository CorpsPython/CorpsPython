
'''
    Function that TcpConnector schedules on the ThreadPool's WorkQ to receive requests from a connected client, queue
    the request on the service Worker's MsgQ, and attempt to service the request (if the Conc is not already assigned
    to another thread).

    See also TcpConnector.py and Conc.py.
'''

from CorpsMsg import *
import sys
from logging import debug, error



def MsgRelay(MsgHdlr, TheAddr2Conc):
    MsgBody = None
    try:
        MsgBody = MsgHdlr.rec_msg()

    except:
        debug(f'MsgRelay: Exception\n\t{sys.exc_info()[1]}')
        MsgHdlr.close()
        return

    if MsgBody == None:
        debug(f'MsgRelay: Error receiving Request')
        MsgHdlr.close()
        return

    assert type(MsgBody) == CorpsRequest, "MsgRelay: MsgBody type not CorpsRequest"
    assert MsgBody.MsgType == CorpsMsgType.ConcRequ, 'MsgRelay: Msg Type not ConcRequ'

    MsgBody.MsgHdlr = MsgHdlr     # Conc will need this to return response to Client

    try:
        aConc = TheAddr2Conc.getConc(MsgBody.ServerAddr)

    except:
        error(f'MsgRelay: Exception {MsgBody.ServerAddr} Not Found\n\t{sys.exc_info()[1]}')
        MsgHdlr.close()
        return

    aConc.MsgQ.put(MsgBody)
    aConc.main()
    return



