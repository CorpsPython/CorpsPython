
''' Tcp Network factory to create connector threads and server and client endpoints '''



from NetwFactory import NetwFactory
from TcpHdlr import TcpServer, TcpClient
from TcpConnector import TcpConnector



class TcpFactory(NetwFactory):
    def __init__(self, TheThreadPool, TheAddr2Conc):
        NetwFactory.__init__(self, TheThreadPool, TheAddr2Conc)


    def new_connector(self, MyHost, EnvQueue):
        TcpConnector(MyHost, self.TheThreadPool, self.TheAddr2Conc, EnvQueue)


    def new_server_netwhdlr(self, MyHost):
        return TcpServer(MyHost)


    def new_client_netwhdlr(self, ServerHost, ServerPort):
        return TcpClient(ServerHost, ServerPort)
