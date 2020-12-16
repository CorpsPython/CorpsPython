
''' Network Handler base class to send and receive messages on-the-wire '''



import socket
import time



class NetwHdlr():
    def __init__(self):
        pass

    def close(self):
        raise NotImplementedError('NetwHdlr close()')

    def rec_wire_msg(self, MsgLength):
        raise NotImplementedError('NetwHdlr rec_wire_msg()')

    def send_wire_msg(self, Buffers):
        raise NotImplementedError('NetwHdlr send_wire_msg()')

    def get_stats(self):
        raise NotImplementedError('NetwHdlr get_stats()')

