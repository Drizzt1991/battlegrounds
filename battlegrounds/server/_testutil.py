import asyncio


class UDPSimpleClient:

    def __init__(self, session_id, transport, protocol, loop):
        self.session_id = session_id
        self.transport = transport
        self.protocol = protocol
        self.loop = loop

    @classmethod
    async def connect(cls, session_id, host, port, loop):
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPSimpleProtocol(session_id, loop),
            remote_addr=(host, port))
        return cls(session_id, transport, protocol, loop)

    def send_raw(self, raw_data):
        self.transport.sendto(raw_data)

    async def get_last_packet(self, timeout=0.1):
        waiter = self.loop.create_task(self.protocol.event.wait())
        await asyncio.wait([waiter], timeout=0.1, loop=self.loop)
        if self.protocol.event.is_set():
            res = self.protocol.buffer.pop()
            if not self.protocol.buffer:
                self.protocol.event.clear()
            return res
        else:
            waiter.cancel()
        return None


class UDPSimpleProtocol:

    def __init__(self, session_id, loop):
        self.buffer = []
        self.session_id = session_id
        self.event = asyncio.Event(loop=loop)

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        self.buffer.append(data)
        self.event.set()

    def connection_lost(self, exc):
        print("Connection lost", exc)  # pragma: no cover
