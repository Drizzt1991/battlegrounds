class UDPServerEchoProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        print('Sending %r to %s' % (message, addr))
        self.transport.sendto(data, addr)
