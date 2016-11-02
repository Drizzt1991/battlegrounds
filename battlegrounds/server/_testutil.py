import asyncio


class UDPSimpleClient:

    def __init__(self, transport, protocol, loop):
        self.transport = transport
        self.protocol = protocol
        self.loop = loop

    @classmethod
    async def connect(cls, host, port, loop):
        transport, protocol = await loop.create_datagram_endpoint(
            UDPSimpleProtocol, remote_addr=(host, port))
        protocol.set_loop(loop)
        return cls(transport, protocol, loop)

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

    def set_loop(self, loop):
        self.buffer = []
        self.event = asyncio.Event(loop=loop)

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        self.buffer.append(data)
        self.event.set()

    def connection_lost(self, exc):
        print("Connection lost", exc)  # pragma: no cover
