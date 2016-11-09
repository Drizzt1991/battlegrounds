import asyncio
import logging

from .base import ConnectionClose, UDPBaseConnection
from .packet import Auth, AuthOk, Close, Header, Ping, Pong, SESSION_ID


async def connect_client(session_id, host, port, loop):
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPClientProtocol(session_id, loop),
        remote_addr=(host, port))
    return transport, protocol


class UDPClientProtocol(UDPBaseConnection, asyncio.DatagramProtocol):

    log = logging.getLogger(__name__)

    def __init__(self, session_id, loop):
        self.session_id = session_id
        self.loop = loop
        self.transport = None
        self._status = None
        self._background_task = None
        self._channels = {}
        # Clock sync veriables

    @property
    def status(self):
        return self._status

    @property
    def channels(self):
        return self._channels

    def __repr__(self):
        return "UDPClientProtocol<{!r}, status={!r}>".format(
            self.session_id, self._status)

    async def auth(self):
        """ Perform authorization sequence, send/receive pings until connection
            timeouts. Basically everything on channel 0x00. Something like:
                -> AUTH    status: auth-sent
                -> AUTH    status: auth-sent
                <- AUTH_OK status: established
                -> Ping    status: established
                -> Ping    status: established
                <- Pong    status: established
                <- Close   status: closed
        """
        channel = self.open_channel(0)
        # TODO: make retries configurable
        for _ in range(10):
            sent = self.loop.time()
            channel.send_packet(Auth())
            self._status = "auth-sent"
            try:
                # TODO: make timeout configurable
                auth_ok = await channel.wait_packet(AuthOk, timeout=0.05)
            except asyncio.TimeoutError:
                continue
            # It will be calibrated further later, so we ignore the posibility
            # that this auth_ok is not a response to prev auth.
            self._calibrate(sent, self.loop.time(), auth_ok.timestamp)
            break
        else:
            return self.close("Could not connect to server")
        self._status = "established"

        # Ping server until timeout
        # TODO: make timeout configurable
        ping_interval = 0.5
        disconnect_timeout = 0
        last_pong = self.loop.time()
        seq = 0
        while True:
            last_ping = self.loop.time()
            seq = (seq + 1) % 256
            channel.send_packet(Ping(seq))
            # TODO: make timeout configurable
            try:
                pong = await channel.wait_packet(Pong, timeout=ping_interval)
            except asyncio.TimeoutError:
                if (self.loop.time() - last_pong) > disconnect_timeout:
                    self.close("Connection timeout")
                    return
            else:
                last_pong = self.loop.time()
                self._calibrate(last_ping, last_pong, pong.timestamp)
            sleep_for = ping_interval - (self.loop.time() - last_ping)
            if sleep_for > 0:
                await asyncio.sleep(sleep_for, loop=self.loop)

    def close(self, msg=""):
        # Last attempt to notify server about connection close
        self.send_packet(0, Close())
        if self._background_task is not None and \
                not self._background_task.done():
            self._background_task.cancel()
            self._background_task = None
        super().close(msg)
        self._status = "closed"
        self.protocol = None
        self.transport = None

    def _calibrate(self, t_send, t_recv, server_timestamp):
        """ Performs simple clock synchronization. It will remember last
            N measurements, record average latency and set client-server time
            delta.
        """
        pass

    # Protocol interface method implementation

    def connection_made(self, transport):
        self.transport = transport
        self._background_task = self.loop.create_task(self.auth)

    def datagram_received(self, data, addr):
        self.log.debug('Received %r from %s' % (data, addr))
        # We must have a proper header
        if len(data) < Header.size:
            return
        # Fast check for session to be same
        [session_id] = SESSION_ID.unpack_from(data)
        if session_id != self.session_id:
            self.log.info("Received datagram from another session \n%r", data)
            return
        # Ok, looks valid, lets pass to the proper channel
        self.dispatch(data)

    def error_received(self, exc):
        self.log.warn("Datagram operation failed, exc=%r", exc)

    def connection_lost(self, exc):
        self.log.info("Connection lost, exc=%r", exc)

    # Packet processing methods

    def send_packet(self, channel_id, packet):
        if self._status == "closed":
            raise ConnectionClose("Connection closed")
        header = Header(self.session_id, channel_id,
                        packet.op_code, packet.version, reserved=0)
        data = bytearray(packet.size + header.size)
        header.encode(data)
        packet.encode(data, offset=Header.size)
        self.transport.sendto(data)
