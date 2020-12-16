
'''
    Tcp Network Handler base classes to send and receive messages on-the-wire

    TcpHdlr is the base class for all Tcp Network Handlers.

    TcpServer and TcpClient are TcpHldr subclasses.

'''



import socket
from NetwHdlr import NetwHdlr
from Exceptions import AsyncLocalMaxRetries



class TcpHdlr(NetwHdlr):
    def __init__(self):
        super().__init__()

        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def close(self):
        try:
            self.Sock.shutdown(socket.SHUT_RDWR)

        except:
            pass

        try:
            self.Sock.close()

        except:
            pass


    def rec_wire_msg(self, MsgLength):
        Msg = None
        chunks = []
        bytes_recd = 0

        while bytes_recd < MsgLength:
            bytes_req = min(MsgLength - bytes_recd, MsgLength)

            chunk = b''

            chunk = self.Sock.recv(bytes_req)

            if chunk == b'':
                return None

            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        Msg = b''.join(chunks)
        return Msg


    def send_wire_msg(self, Buffers):
        ''' Python 3.6 on Windows 7 does not support socket.sendmsg() or socket.recmsg() '''

        for Buffer in Buffers:
            self.Sock.sendall(Buffer)


        return True


class TcpServer(TcpHdlr):
    ''' Tcp Server Network Handler '''

    def __init__(self, MyHost, Sock=None):
        super().__init__()

        from ConfigGlobals import Networking_Server_Timeout, Networking_Max_Queued_Conn_Requests

        self.Host = MyHost

        if Sock == None:
            self.Sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.Sock.settimeout(Networking_Server_Timeout)
            self.Sock.bind((str(self.Host), 0))
            self.Port = self.Sock.getsockname()[1]
            self.Sock.listen(Networking_Max_Queued_Conn_Requests)

        else:
            assert type(Sock) == socket.socket
            self.Sock = Sock
            self.Sock.settimeout(Networking_Server_Timeout)

    def accept(self):
        Sock, Addr = self.Sock.accept()
        return TcpServer(self.Host, Sock)


    def get_stats(self):
        raise NotImplementedError('TcpServer get_stats()')


    def get_port(self):
        return self.Port


class TcpClient(TcpHdlr):
    ''' Tcp Client Network Handler '''

    def __init__(self, ServerHost, ServerPort, MaxRetries=25):
        super().__init__()

        from ConfigGlobals import Networking_Max_Connection_Attempts, Networking_Client_Timeout

        self.Sock.settimeout(Networking_Client_Timeout)

        for i in range(Networking_Max_Connection_Attempts):
            self.SockErr = -1

            try:
                self.SockErr = self.Sock.connect_ex((str(ServerHost), ServerPort))

            except:
                continue

            if self.SockErr == 0:
                return

        # Retries failed
        self.close()
        raise AsyncLocalMaxRetries(\
            f'{Networking_Max_Connection_Attempts} attempts to connect to Host {ServerHost} Port {ServerPort} failed')


    def get_stats(self):
        raise NotImplementedError('TcpClient get_stats()')
