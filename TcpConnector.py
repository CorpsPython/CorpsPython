
'''
    Thread to handle Tcp connection requests

    At init time returns the port via a queue to the thread (the Env) that created it.

    Loops on accepting connection requests and placing requests to RequestRelay() on the ThreadPool's WorkQ to
    service the connections (requests from client Workers).
'''



import threading
from TcpHdlr import TcpServer
from MsgRelay import RequestRelay
from CorpsMsgHdlr import CorpsMsgHdlr
from logging import info, warning




class TcpConnector(threading.Thread):
    def __init__(self, Host, TheThreadPool, TheAddr2Conc, EnvQueue):
        super().__init__()
        self.Id = threading.get_ident()

        self.Host = Host
        self.TheThreadPool = TheThreadPool
        self.TheAddr2Conc = TheAddr2Conc

        self.NetwHdlr = TcpServer(Host)
        self.Port = self.NetwHdlr.get_port()

        info(f'TcpConnector: Host {self.Host} Port {self.Port}')
        EnvQueue.put(self.Port)

        self.start()


    def run(self):
        while True:
            NetwHdlr = None

            try:
                NetwHdlr = self.NetwHdlr.accept()

            except:
                warning(f'\n\nTcpConnector: accept exception\n\n')
                continue

            MsgHdlr = CorpsMsgHdlr(NetwHdlr)
            
            cmd = lambda : RequestRelay(MsgHdlr, self.TheAddr2Conc)
            self.TheThreadPool.put_cmd(cmd)


