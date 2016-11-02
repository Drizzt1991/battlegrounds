import asyncio
import struct

import pytest


@pytest.mark.asyncio
async def test_udp_simple_auth(udp_server, udp_simple_client, udp_session_id):
    assert udp_server['protocol'].sessions[udp_session_id].status == "created"

    client = udp_simple_client
    client.send_raw(b"".join([
        struct.pack('!L', udp_session_id),  # session_id
        b"\x00\x00\x00\x00",                   # channel, op_code, version,
                                               # reserved
    ]))
    auth_ok = await udp_simple_client.get_last_packet()

    assert auth_ok == b"".join([
        struct.pack('!L', udp_session_id),
        b"\x00\x01\x00\x00",                   # channel, op_code, version,
                                               # reserved
        b"\x00" * 8  # timestamp
    ])


@pytest.mark.asyncio
async def test_udp_full_auth(udp_server, udp_simple_client, udp_session_id):
    # Perform a proper auth sequence
    client = udp_simple_client

    server_connection = udp_server['protocol'].sessions[udp_session_id]
    assert server_connection.status == "created"

    auth = b"".join([
        struct.pack('!L', udp_session_id),  # session_id
        b"\x00\x00\x00\x00",                # channel, op_code, version,
                                            # reserved
    ])
    # The routine can be repeated many times, if packet's are lost
    for x in range(5):
        # Send AUTH. STATUS="auth-sent", SERVER_STATUS="created"
        client.send_raw(auth)

        # Await auth_ok. STATUS="established", SERVER_STATUS="auth-recv"
        auth_ok = await udp_simple_client.get_last_packet()
        assert auth_ok == b"".join([
            struct.pack('!L', udp_session_id),
            b"\x00\x01\x00\x00",                   # channel, op_code, version,
                                                   # reserved
            b"\x00" * 8  # timestamp
        ])
        assert server_connection.status == "auth-recv"

    for x in range(5):
        # send PING
        client.send_raw(b"".join([
            struct.pack('!L', udp_session_id),  # session_id
            b"\x00\x02\x00\x00",                # channel, op_code, version,
                                                # reserved
        ]))

        pong = await udp_simple_client.get_last_packet()
        assert pong == b"".join([
            struct.pack('!L', udp_session_id),
            b"\x00\x03\x00\x00",                   # channel, op_code, version,
                                                   # reserved
            b"\x00" * 8  # timestamp
        ])
        assert server_connection.status == "established"

    # Any more auth requests should be ignored by server
    client.send_raw(auth)
    auth_ok = await udp_simple_client.get_last_packet()
    assert auth_ok is None


@pytest.mark.asyncio
async def test_udp_disconnect(
        udp_server, udp_simple_client, udp_session_id, loop):
    # Perform a proper auth sequence
    client = udp_simple_client

    # Send AUTH
    client.send_raw(b"".join([
        struct.pack('!L', udp_session_id),     # session_id
        b"\x00\x00\x00\x00",                   # channel, op_code, version,
                                               # reserved
    ]))
    auth_ok = await udp_simple_client.get_last_packet()
    assert auth_ok is not None
    # Send PING
    ping = b"".join([
        struct.pack('!L', udp_session_id),     # session_id
        b"\x00\x02\x00\x00",                   # channel, op_code, version,
                                               # reserved
    ])
    client.send_raw(ping)
    pong = await udp_simple_client.get_last_packet()
    assert pong is not None
    # Wait for timeout seconds
    await asyncio.sleep(0.5, loop=loop)
    # Now ping will be ignored by server
    client.send_raw(ping)
    pong = await udp_simple_client.get_last_packet()
    assert pong is None
    assert udp_session_id not in udp_server['protocol'].sessions
