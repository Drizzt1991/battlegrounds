import argparse
import asyncio

from net import UDPServerEchoProtocol


def get_parser():
    parser = argparse.ArgumentParser(
        description='Supposedly, server')
    parser.add_argument(
        '--host', help='IP address to use. Default: %(default)s',
        default="127.0.0.1")
    parser.add_argument(
        '--port', help='Port to use. Default: %(default)s',
        type=int,
        default=9999)
    return parser


async def xxx():
    try:
        while True:
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass


def main():
    parser = get_parser()
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    print("Starting UDP server")
    # One protocol instance will be created to serve all client requests
    listen = loop.create_datagram_endpoint(
        UDPServerEchoProtocol, local_addr=(args.host, args.port))
    transport, protocol = loop.run_until_complete(listen)
    t = loop.create_task(xxx())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Received SIG_INT. Quiting...")
    finally:
        t.cancel()
        loop.run_until_complete(t)
        transport.close()
        loop.close()

main()
