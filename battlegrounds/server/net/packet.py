import struct
from collections import namedtuple

SESSION_ID = struct.Struct("!L")


class _StructBased:

    @classmethod
    def decode(cls, data, offset=0):
        return cls(*cls.struct.unpack_from(data, offset))

    def encode(self, data, offset=0):
        self.struct.pack_into(data, offset, *self)


class _EmptyPayload:

    size = 0

    @classmethod
    def decode(cls, data, offset=0):
        return cls()

    def encode(self, data, offset=0):
        # Payload is empty
        pass


class Header(_StructBased, namedtuple(
        "Header", ("session_id", "channel_id", "op_code", "version",
                   "reserved"))):

    __slots__ = ()

    struct = struct.Struct("!LBBBB")
    size = struct.size


class Auth(_EmptyPayload, namedtuple("Auth", ())):

    __slots__ = ()

    op_code = 0x00
    version = 0x00


class AuthOk(_StructBased, namedtuple("AuthOk", ("timestamp"))):

    __slots__ = ()

    op_code = 0x01
    version = 0x00

    struct = struct.Struct("!Q")
    size = struct.size


class Ping(_StructBased, namedtuple("Ping", ("seq"))):

    __slots__ = ()

    op_code = 0x02
    version = 0x00

    struct = struct.Struct("!B")
    size = struct.size


class Pong(_StructBased, namedtuple("Pong", ("seq, timestamp"))):

    __slots__ = ()

    op_code = 0x03
    version = 0x00

    struct = struct.Struct("!BQ")
    size = struct.size


class Close(_EmptyPayload, namedtuple("Close", ())):

    __slots__ = ()

    op_code = 0x04
    version = 0x00


_packet_map = {
    0x00: Auth,
    0x01: AuthOk,
    0x02: Ping,
    0x03: Pong,
    0x04: Close,
}


def parse_packet(header, data, *, _packet_map=_packet_map):
    klass = _packet_map.get(header.op_code)
    if klass is None:
        raise KeyError(header.op_code)
    return klass.decode(data, header.size)
