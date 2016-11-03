import argparse
import asyncio
import pathlib
from logging.config import dictConfig

import yaml

from .net import UDPGameProtocol


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
    parser.add_argument(
        '--logging', help='Logging file to use. Default: %(default)s',
        type=pathlib.Path,
        default="config/logging.yaml")
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

    with args.logging.open("r+") as f:
        log_conf = yaml.load(f)
        dictConfig(log_conf)

    loop = asyncio.get_event_loop()
    print("Starting UDP server")
    # One protocol instance will be created to serve all client requests
    listen = loop.create_datagram_endpoint(
        lambda loop=loop: UDPGameProtocol(loop=loop),
        local_addr=(args.host, args.port))
    transport, protocol = loop.run_until_complete(listen)
    t = loop.create_task(xxx())
    print("Started UDP server")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Received SIG_INT. Quiting...")
    finally:
        t.cancel()
        loop.run_until_complete(t)
        transport.close()
        loop.close()

if __name__ == "__main__":
    main()
