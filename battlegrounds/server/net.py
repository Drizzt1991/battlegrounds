import asyncio
import logging
import struct
from collections import namedtuple

log = logging.getLogger(__name__)

SESSION_ID = struct.Struct("!L")


class Header(namedtuple(
        "Header", ("session_id", "channel_id", "op_code", "version",
                   "reserved"))):

    struct = struct.Struct("!LBBBB")
    size = struct.size

    @classmethod
    def decode(cls, data, offset=0):
        return cls(*cls.struct.unpack_from(data, offset))

    def encode(self, data, offset=0):
        self.struct.pack_into(data, offset, *self)


class Auth(namedtuple("Auth", ())):

    op_code = 0x00
    version = 0x00

    size = 0

    @classmethod
    def decode(cls, data, offset=0):
        return cls()

    def encode(self, data, offset=0):
        # Payload is empty
        pass


class AuthOk(namedtuple("AuthOk", ("timestamp"))):

    op_code = 0x01
    version = 0x00

    struct = struct.Struct("!Q")
    size = struct.size

    @classmethod
    def decode(cls, data, offset=0):
        return cls(*cls.struct.unpack_from(data, offset))

    def encode(self, data, offset=0):
        self.struct.pack_into(data, offset, *self)


class Ping(namedtuple("Ping", ())):

    op_code = 0x02
    version = 0x00

    size = 0

    @classmethod
    def decode(cls, data, offset=0):
        return cls()

    def encode(self, data, offset=0):
        # Payload is empty
        pass


class Pong(namedtuple("Pong", ("timestamp"))):

    op_code = 0x03
    version = 0x00

    struct = struct.Struct("!Q")
    size = struct.size

    @classmethod
    def decode(cls, data, offset=0):
        return cls(*cls.struct.unpack_from(data, offset))

    def encode(self, data, offset=0):
        self.struct.pack_into(data, offset, *self)


class UDPGameProtocol(asyncio.DatagramProtocol):

    def __init__(self, *, loop):
        self._sessions = {}
        self.loop = loop

    @property
    def sessions(self):
        return self._sessions

    def open_connection(self, session_id):
        self._sessions[session_id] = UDPConnection(
            session_id, self.transport, self)

    def close_connection(self, session_id):
        conn = self._sessions.pop(session_id, None)
        if conn is not None:
            conn.close()

    # Protocol interface method implementation

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        log.debug('Received %r from %s' % (data, addr))
        # We must have a proper header
        if len(data) < Header.size:
            return
        # Fast check for session to be registered
        [session_id] = SESSION_ID.unpack_from(data)
        if session_id not in self._sessions:
            return
        # Ok, looks valid, lets pass to the proper channel
        self._sessions[session_id].dispatch(data, addr)

    def error_received(self, exc):
        log.warn("Datagram operation failed, exc=%r", exc)

    def connection_lost(self, exc):
        log.info("Connection lost, exc=%r", exc)


class UDPConnection:

    def __init__(self, session_id, transport, protocol):
        self.session_id = session_id
        self._channels = {
            0x00: None   # This channel is handled by Connection directly
        }
        self._status = "created"
        self._addr = None
        self.transport = transport
        self.protocol = protocol
        self.loop = protocol.loop
        # Timeout handler
        self._last_action = self.loop.time()
        # TODO: Make it configurable
        self._timeout_delay = 0.5
        self._timeout_handle = self.loop.call_later(
            self._timeout_delay, self.timeout_check)

    @property
    def status(self):
        return self._status

    @property
    def addr(self):
        return self._addr

    def __repr__(self):
        return "UDPConnection<{!r}, status={!r}, addr={!r}>".format(
            self.session_id, self._status, self._addr)

    def open_channel(self, channel_id, channel_type=None):
        if channel_type is None:
            channel_type = UDPChannel
        if channel_id in self._channels:
            raise KeyError("Channel {} already opened".format(channel_id))
        self._channels[channel_id] = channel = channel_type(
            self, channel_id, self.transport)
        return channel

    # Timeout management

    def timeout_check(self):
        cur_time = self.loop.time()
        last_time = self._last_action
        timeout = self._timeout_delay

        if cur_time - last_time > timeout:
            self.protocol.close_connection(self.session_id)
        else:
            next_check_in = timeout - (cur_time - last_time)
            self._timeout_handle = self.loop.call_later(
                next_check_in, self.timeout_check)

    def close(self):
        self._timeout_handle.cancel()
        self._timeout_handle = None
        self.protocol = None
        self.transport = None

    # Packet processing methods

    def dispatch(self, data, addr):
        header = Header.decode(data)
        if header.channel_id == 0x00:
            if header.op_code == Auth.op_code:
                # In case AuthOk did not arrive to client, we always resend it
                if self._status != "established":
                    self._do_auth(header, data, addr)
            elif header.op_code == Ping.op_code:
                self._do_ping(header, data, addr)
            else:
                log.warn("Unexpected %r on channel=0x00", header.op_code)
                return
        else:
            assert header.channel_id in self._channels
            assert self._status == "established"
            channel = self._channels[header.channel_id]
            # TODO: parse data and only feed parsed packet
            channel.feed(header, data)

    def _do_auth(self, header, data, addr):
        if self._status == "created":
            log.info("New connection from addr=%r session_id=%r",
                     addr, self.session_id)
            # Change status and save connection remote addr
            self._status = "auth-recv"
            self._addr = addr
        # TODO: set a proper game timestamp
        self.send_packet(0, AuthOk(timestamp=0))

    def _do_ping(self, header, data, addr):
        if self._status == "auth-recv":
            self._status = "established"
            # Open other channels
            self.open_channel(1)
            self.open_channel(2)
        # TODO: set a proper game timestamp
        self.send_packet(0, Pong(timestamp=0))

    def send_packet(self, channel_id, packet, *, addr=None):
        header = Header(self.session_id, channel_id,
                        packet.op_code, packet.version, reserved=0)
        data = bytearray(packet.size + header.size)
        header.encode(data)
        packet.encode(data, offset=Header.size)
        self.transport.sendto(data, addr=addr or self.addr)


class UDPChannel:

    def __init__(self, conn, channel_id, transport):
        self._conn = conn
        self.channel_id = channel_id
        self.transport = transport

    def feed(self, header, packet):
        pass

    def send_packet(self, packet):
        self._conn.send_packet(self.channel_id, packet)
