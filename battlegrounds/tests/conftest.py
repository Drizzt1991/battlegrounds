import asyncio
import random
import socket

from engine._testutil import debug_draw as _debug_draw

import pytest

from server._testutil import UDPSimpleClient
from server.net import UDPGameProtocol


@pytest.fixture(scope="session")
def debug_draw():
    return _debug_draw


@pytest.fixture(scope='session')
def unused_port():
    def f():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]
    return f


@pytest.yield_fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    yield loop

    if not loop.is_closed():
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()


@pytest.fixture(scope='session')
def loop(event_loop):
    return event_loop


@pytest.yield_fixture
def udp_session_id(udp_server):
    session = random.randint(0, 65000)
    while session in udp_server['protocol'].sessions:
        session = random.randint(0, 65000)
    udp_server['protocol'].open_connection(session)
    yield session
    udp_server['protocol'].close_connection(session)


@pytest.fixture(scope="session")
def udp_server(loop, unused_port):
    port = unused_port()
    listen = loop.create_datagram_endpoint(
        lambda loop=loop: UDPGameProtocol(loop=loop),
        local_addr=("localhost", port))
    transport, protocol = loop.run_until_complete(listen)
    return {
        "transport": transport,
        "protocol": protocol,
        "port": port,
        "host": "localhost"
    }


@pytest.fixture(scope="session")
def udp_simple_client(udp_server, loop):
    coro = UDPSimpleClient.connect(
        udp_server['host'], udp_server['port'], loop)
    return loop.run_until_complete(coro)
