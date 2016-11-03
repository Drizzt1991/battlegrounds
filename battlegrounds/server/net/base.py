import asyncio
from collections import defaultdict, deque

from .packet import Header, parse_packet


class ConnectionClose(Exception):
    pass


class UDPBaseConnection:

    def __init__(self, *, loop):
        self.loop = loop
        self._channels = {}

    def open_channel(self, channel_id, channel_type=None):
        if channel_type is None:
            channel_type = UDPChannel
        if channel_id in self._channels:
            raise KeyError("Channel {} already opened".format(channel_id))
        self._channels[channel_id] = channel = channel_type(
            self, channel_id, loop=self.loop)
        return channel

    def dispatch(self, data):
        header = Header.decode(data)
        if header.channel_id not in self._channels:
            self.log.log("Received packet to unknown channel %r", header)
            return
        channel = self._channels[header.channel_id]
        packet = parse_packet(header, data)
        channel.feed(header, packet)

    def close(self, msg=""):
        for channel in self._channels.values():
            if channel is not None:
                channel.close(msg)


class UDPChannel:

    def __init__(self, conn, channel_id, *, loop):
        self.channel_id = channel_id
        self.loop = loop
        self._conn = conn
        self._waiters = defaultdict(deque)

    # Protected methods

    def feed(self, header, packet):
        queue = self._waiters[type(packet)]
        while True:
            try:
                waiter = queue.popleft()
            except IndexError:
                # Either duplicate or out of order packet
                break
            # We might have canceled the waiting future, in that case just take
            # the next waiter
            if waiter.cancelled():
                continue
            waiter.set_result((header, packet))
            break

    def close(self, msg=""):
        for queue in self._waiters:
            for waiter in queue:
                waiter.set_exception(ConnectionClose(msg))
            queue.clear()

    # Public methods

    def send_packet(self, packet):
        self._conn.send_packet(self.channel_id, packet)

    def wait_packet(self, packet_type, *, timeout=None):
        fut = asyncio.Future(loop=self.loop)
        self._waiters[packet_type].append(fut)
        if timeout is None:
            return fut
        return asyncio.wait_for(fut, timeout=timeout, loop=self.loop)
