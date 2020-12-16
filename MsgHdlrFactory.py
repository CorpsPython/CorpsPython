
''' Base class Factory to create Message Handlers '''


class MsgHdlrFactory():
    def __init__(self):
        pass


    def new_server_msghdlr(self, NetwHdlr):
        raise NotImplementedError('MsgHdlrFactory create_server_msghdlr()')


    def new_client_msghdlr(self, NetwHdlr):
        raise NotImplementedError('MsgHdlrFactory create_client_msghdlr()')

