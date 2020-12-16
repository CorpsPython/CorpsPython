
''' MsgHdlrFactory subclass to generate CorpsMsgHdlrs '''



from MsgHdlrFactory import *
from CorpsMsgHdlr import *



class CorpsMsgHdlrFactory(MsgHdlrFactory):
    def __init__(self):
        super().__init__()


    def new_server_msghdlr(self, NetwHdlr):
        return CorpsMsgHdlr(NetwHdlr)


    def new_client_msghdlr(self, NetwHdlr):
        return CorpsMsgHdlr(NetwHdlr)

