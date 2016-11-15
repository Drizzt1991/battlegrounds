import asyncio
import struct

import pytest


@pytest.mark.asyncio
async def test_udp_simple_auth(udp_server, udp_test_client, udp_session_id):
    assert udp_server['protocol'].sessions[udp_session_id].status == "created"

    client = udp_test_client
    client.send_raw(b"".join([
        struct.pack('!L', udp_session_id),  # session_id
        b"\x00\x00\x00\x00",                   # channel, op_code, version,
                                               # reserved
    ]))
    auth_ok = await client.get_last_packet()

    assert auth_ok == b"".join([
        struct.pack('!L', udp_session_id),
        b"\x00\x01\x00\x00",                   # channel, op_code, version,
                                               # reserved
        b"\x00" * 8  # timestamp
    ])


@pytest.mark.asyncio
async def test_udp_full_auth(udp_server, udp_test_client, udp_session_id):
    # Perform a proper auth sequence
    client = udp_test_client

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
        auth_ok = await client.get_last_packet()
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
            b"\x10"  # seq
        ]))

        pong = await client.get_last_packet()
        assert pong == b"".join([
            struct.pack('!L', udp_session_id),
            b"\x00\x03\x00\x00",                   # channel, op_code, version,
                                                   # reserved
            b"\x10",     # seq
            b"\x00" * 8  # timestamp
        ])
        assert server_connection.status == "established"

    # Any more auth requests should be ignored by server
    client.send_raw(auth)
    auth_ok = await client.get_last_packet()
    assert auth_ok is None


@pytest.mark.asyncio
async def test_udp_disconnect(
        udp_server, udp_test_client, udp_session_id, loop):
    # Perform a proper auth sequence
    client = udp_test_client

    # Send AUTH
    client.send_raw(b"".join([
        struct.pack('!L', udp_session_id),     # session_id
        b"\x00\x00\x00\x00",                   # channel, op_code, version,
                                               # reserved
    ]))
    auth_ok = await client.get_last_packet()
    assert auth_ok is not None, "Auth failed"
    # Send PING's allowing the connection to stay alive
    for _ in range(5):
        ping = b"".join([
            struct.pack('!L', udp_session_id),     # session_id
            b"\x00\x02\x00\x00",                   # channel, op_code, version,
                                                   # reserved
            b"\x22"  # seq
        ])
        client.send_raw(ping)
        pong = await client.get_last_packet()
        assert pong is not None, "Unexpected disconnect"
        await asyncio.sleep(0.2, loop=loop)

    # Wait for timeout seconds, forcing a disconnect
    await asyncio.sleep(0.5, loop=loop)
    close = await client.get_last_packet()
    assert close == b"".join([
        struct.pack('!L', udp_session_id),
        b"\x00\x04\x00\x00",                   # channel, op_code, version,
                                               # reserved
    ])
    # Now ping will be ignored by server
    client.send_raw(ping)
    pong = await client.get_last_packet()
    assert pong is None
    # Check if session is no longer opened
    assert udp_session_id not in udp_server['protocol'].sessions
