
''' Network factory base class to create connector threads and server and client endpoints '''



class NetwFactory():
    def __init__(self, TheThreadPool, TheAddr2Conc):
        self.TheThreadPool = TheThreadPool
        self.TheAddr2Conc = TheAddr2Conc


    def new_connector(self, MyHost, EnvQueue):
        raise NotImplementedError('NetwFactory new_connector()')


    def new_server_netwhdlr(self, MyHost):
        raise NotImplementedError('NetwFactory new_server_endpt()')


    def new_client_netwhdlr(self, ServerHost, ServerPort):
        raise NotImplementedError('NetwFactory new_client_endpt()')
