
'''
    Message Handler base class

    HasA NetwHdlr to do the on-the-wire stuff.

    See CorpsMsgHdlr.py for subclass example.
'''



class MsgHdlr():
    def __init__(self, NetwHdlr):
        self.NetwHdlr = NetwHdlr

    def close(self):
        raise NotImplementedError('MsgHdlr close()')

    def send_msg(self, MsgBody):
        raise NotImplementedError('MsgHdlr send_msg()')

    def rec_msg(self):
        raise NotImplementedError('MsgHdlr rec_msg()')

    def __rec_hdr(self):
        ''' Used by rec_msg to receive header '''

        raise NotImplementedError('MsgHdlr __rec_hdr()')

    def __rec_body(self, BodyLength):
        ''' Used by rec_msg to receive body '''

        raise NotImplementedError('MsgHdlr __rec_body()')
