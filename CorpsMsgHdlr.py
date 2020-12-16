
'''
    MsgHdlr subclass to send and receive CorpsMsgs on the wire via a NetwHdlr subclass object


    Msgs are two parts, a fixed length Msg Header, with the length of the Msg Body, and the Msg Body.

    The Msg Body is either a CorpsRequest or CorpsReturn.

    The Header and Body are packed (i.e. pickled) on the wire and unpacked in the Env.
'''

from CorpsMsg import *
from MsgHdlr import *
from Packer import pack, unpack
import struct


class CorpsMsgHdlr(MsgHdlr):
    def __init__(self, NetwHdlr):
        super().__init__(NetwHdlr)


    def close(self):
        self.NetwHdlr.close()


    def send_msg(self, MsgBody):
        PackedBody = pack(MsgBody)

        BodyLength = len(PackedBody)

        assert BodyLength <= MAX_BODY_LENGTH, f'send_msg: BodyLength {BodyLength} bytes exceeds max of {MAX_BODY_LENGTH}'

        PackedHdr = struct.pack('q', BodyLength)
        assert len(PackedHdr) == CORPSMSG_HDR_SIZE, f'send_msg: PackedHdr has bad size {len(PackedHdr)}'

        return self.NetwHdlr.send_wire_msg([PackedHdr, PackedBody])  # returns True or False


    def __rec_hdr(self):
        PackedMsgHdr = self.NetwHdlr.rec_wire_msg(CORPSMSG_HDR_SIZE)

        assert PackedMsgHdr != None, "rec_hdr: No Msg Header received"
        assert len(PackedMsgHdr) == CORPSMSG_HDR_SIZE, f'rec_hdr: PackedHdr has size {len(PackedMsgHdr)}'

        BodyLength = struct.unpack('q', PackedMsgHdr)[0]

        assert BodyLength > 0,  f'send_msg: BodyLength too small {BodyLength}'
        assert BodyLength <= MAX_BODY_LENGTH, f'send_msg: BodyLength {BodyLength} bytes exceeds max of {MAX_BODY_LENGTH}'

        return BodyLength


    def __rec_body(self, BodyLength):
        PackedRetBody = self.NetwHdlr.rec_wire_msg(BodyLength)

        assert PackedRetBody != None, f"__rec_body: No Return Body received"

        RetBody = unpack(PackedRetBody)

        return RetBody


    def rec_msg(self):
        BodyLength = self.__rec_hdr()

        RetBody = self.__rec_body(BodyLength)

        return RetBody
