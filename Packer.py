
''' Packing and unpacking functions for transport and storage '''



from pickle import dumps, loads, DEFAULT_PROTOCOL, HIGHEST_PROTOCOL
#import cloudpickle
#import dill



CorpsPickleProtocol = 3
assert CorpsPickleProtocol <= HIGHEST_PROTOCOL, f'CorpsPickelProto {CorpsPickleProtocol} not supported'


def pack(UnpackedObj):
    PackedObj = dumps(UnpackedObj, protocol=CorpsPickleProtocol)
    return PackedObj


def unpack(PackedObj):
    UnpackedObj = loads(PackedObj)
    return UnpackedObj


def versions():
    return f'Using Protocol: {CorpsPickleProtocol}  Default Protocol: {DEFAULT_PROTOCOL}  Highest Protocol: {HIGHEST_PROTOCOL}'