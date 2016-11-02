Networking
----------

In Battlegrounds game we use 2 protocols for client operation:

    * Rest API for transaction commands (login, statistics, other API's)
    * Socket protocol for Game Logic (character movement, skills, world events,
      etc...)

Game client connection establishment
====================================

Game logic protocol will require the client to first Authenticate using REST
API and obtaning a ``SessionID``. In the process we will also provide
information about:

    * Which protocol to use
    * Character, that we log in as
    * Client capabilities (custom weapon shapes, detailed character closing, etc...)
    * Connection configuration (ping intervals, other)

.. todo::
    Describe how to use REST API to get a ``SessionID``

Togather with ``SessionID`` we also receive the connection address, and server
compatibility information, session expiration information. Client should only
connect via provided address and note, that session will only be created for
a brief period of time, and will require a reconnect if not connected right
away.


Connecting using UDP protocol
=============================

UDP protocol is versionized and packets should be sent using one of the
versions present in server compatibility mapping.

General packet structure:

    * ``session_id`` - 4 bytes *long*
    * ``channel`` - 1 byte *char*
    * ``op_code`` - 1 byte *char*
    * ``version`` - 1 byte *char*
    * ``reserverd`` - 1 byte *char*
    * ``payload`` - depending on ``op_code`` and ``version``

Specific purpose Channels:

    * ``channel==0x00`` - command channel
    * ``channel==0x01`` - character information and movement channel
    * ``channel==0x02`` - environment sync channel. This channel is *Reliable*

Connection **Client** states:

    * None (AUTH not sent yet)
    * 'auth-sent' (AUTH sent and awaiting AUTH_OK)
    * 'established' (AUTH_OK received, loading player)

Connection **Server** states:

    * 'created' (AUTH not received, but we authenticated using REST API)
    * 'auth-recv' (AUTH received and AUTH_OK sent)
    * 'established' (Received any PING packet on command channel)

Client Connection sequence:

    * **Client** performs an REST API request to start game, receives SessionID 
    * **Server** starts new connection in ``"created"`` status, awaiting AUTH
    * **Client** sends AUTH requests once per N ms until AUTH_OK received.
      Client status is set to ``"auth-sent"``.
    * **Server** receives AUTH request and sends 1 AUTH_OK request. State
      changes to ``"auth-sent"``
    * **Client** receives AUTH_OK request, stops sending any more AUTH requests
      and sets state to ``"established"``. Any additional AUTH_OK packets will
      be ignored for this session. **Client** starts sending PING requests in
      constant periods of time.
    * **Server** receives any PING request. Sets state to ``"established"``
      and starts sending event data to client in other channels.


UDP reliable delivery
`````````````````````

Reliable delivery is a way to guarantee package delivery to recipient. In this
protocol, reliability is engaged on channel level. An reliable channel operates
on **messages**, which are:

    * guaranteed to be received by application
    * guaranteed to be received fully and uncorrupted
    * NOT guaranteed to preserve order between messages

We operate the **message** term here, because it can be of arbitrary size and
MAY be split into several UDP packets for delivery.

Those channels operate using private MSG and MSG_ACK packets, described below.

Sender's algorithm:

    * While not all MSG's ACK received
        * For each non ACK'ed block in splitted msg
            * Send block's MSG packet
        * Wait up to ``retransmission_timeout`` milliseconds for all MSG_ACK's

Receiver's algorithm:

    * If msg_id lower than last known MSG (with check for overflow):
        * Just send MSG_ACK this message and skip, as MSG already delivered
        * Return
    * If it's the first MSG block received:
        * Allocate MSG buffer
    * Write MSG block data to MSG buffer
    * Send MSG_ACK for this block
    * If MSG buffer is full:
        * Yield msg to application


UDP binary object presentation
``````````````````````````````

For convinience some objects will be represented here as shortcut structures:

.. code:: C

    typedef struct VectorF
    {
        float x;  // 4 bytes
        float y;  // 4 bytes
    };

    typedef struct VectorD
    {
        double x;  // 8 bytes
        double y;  // 8 bytes
    };

UDP AUTH packet
```````````````

**Client --> Server**

**AUTH** packet is quite unique, as it MUST be the 1-st packet on this session,
MUST always be sent with ``channel==0x00`` and should be repeated until
AUTH_OK received, or expired by connection timeout (received with
``SessionID``).

General params:

.. code:: C

    channel = 0x00
    op_code = 0x00
    version = 0x00

AUTH packet payload is EMPTY

.. code:: C

    struct AUTH {
        HEADER header
        // ... payload empty
    }

UDP AUTH_OK packet
``````````````````

**Server --> Client**

**AUTH_OK** packet is only sent after **AUTH** packet. AUTH_OK will be sent
only 1-ce for each **AUTH** request.

General params:

.. code:: C

    channel = 0x00
    op_code = 0x01
    version = 0x00

AUTH_OK packet payload is EMPTY

.. code:: C

    struct AUTH_OK {
        HEADER header;
        long long timestamp;  // 8 bytes
        // Character Movement structure
        VectorD position;
        VectorF forward; // unit vector
        char movementBits;
        // Character Data structure
        char name_len;
        char name[name_len];  // Length == name_len
    }

UDP PING packet
```````````````

**Client --> Server**

**PING** packets MUST constantly be sent on the ``command`` channel. They
are ment for `calibration` purposes, as server is supposed to have most
constant response time for those, as well as helping keeping the session alive.

General params:

.. code:: C

    channel = 0x00
    op_code = 0x02
    version = 0x00

Packet payload

.. code:: C

    struct PING {
        HEADER header
        // ... payload empty
    }

UDP PONG packet
```````````````

**Server --> Client**

**PONG** packets are sent as responses to PING requests. They are sent right
away.

General params:

.. code:: C

    channel = 0x00
    op_code = 0x03
    version = 0x00

Packet payload

.. code:: C

    struct PONG {
        HEADER header;
        long long timestamp;  // 8 bytes
    }

UDP PROP message
````````````````

**Server --> Client**

**PROP** messages are sent in the ``0x02`` channel and are ment for loading
character surrounding environment.

General params:

.. code:: C

    channel = 0x02
    op_code = 0x00
    version = 0x00

Packet payload

.. code:: C

    struct PROP {
        long long prop_id; // 8 bytes
        vectorD position;
        // Collision shape
        char shape_type;   // Circle - 0, Polygon - 1
        SHAPE shape;       // depending on shape_type
        // Render data
        short render_data_len;
        char render_data[render_data_len];  // Depending on render_data_len
    }

    struct Polygon
    {
        // shape_type = 1
        short vertices_len;
        vectorF vertices[vertices_len];
    };

    struct Circle
    {
        // shape_type = 0
        vectorF center;
        float radius;
    };


UDP MOVE_OP packet
``````````````````

**Client --> Server**

**MOVE_OP** packets are responsible for character movement. Client is
responsible for sending those operations for every movement. If 2 moves are
performed simultaneously, packet order can be undefined, so we include a
simple operation counter.

General params:

.. code:: C

    channel = 0x01
    op_code = 0x00
    version = 0x00

Packet payload

.. code:: C

    struct MOVE_OP {
        HEADER header;
        long long timestamp;  // 8 bytes
        VectorD position;
        VectorF forward;  // unit vector
        char movementBits;
        char op_sig;  // Incremental counter
    }


UDP MOVE_EVENT packet
`````````````````````

**Server --> Client**

**MOVE_EVENT** packets are sent when any movement changing operation occures
with our character. For example: user move operations, collisions and so on.
Client should always use those events as a primary source of player movement,
as the timings for collisions and operations will be a bit different.
For example:

  * User presses move forward button. Client sends MOVE_OP request
  * Server validates the request and starts moving our character, sending back
    a MOVE_EVENT packet, but with different timestamp.
  * Client should smooth the movement of the character based on Server's
    timestamp.

As with client we need a way to differ between 2 events performed
simultaneously. For this we will use `event_sig`, which is an incremental
counter maintained by server for each MOVE_EVENT packet. We also send an
`op_sig` to indicate the last operation server received from client, as
we don't guarantee delivery we will duplicate it in each event.


General params:

.. code:: C

    channel = 0x01
    op_code = 0x01
    version = 0x00

Packet payload

.. code:: C

    struct MOVE_EVENT {
        HEADER header;
        long long timestamp;  // 8 bytes
        VectorD position;
        VectorF forward;  // unit vector
        char movementBits;
        char op_sig;  // Client Incremental counter
        char event_sig;  // Server Incremental counter
    }


UDP Reliable MSG packet
```````````````````````

**Server --> Client**
**Client --> Server**

MSG is a special private packet, that implements reliable delivery on reliable
channels. Those packets fully wrap the outgoing one, possibly splitting it
into several parts.

If message is not splitted block_id will be `0x00`


General params:

.. code:: C

    channel = 0xXX
    op_code = 0x10
    version = 0x00

Packet payload

.. code:: C

    struct MSG {
        HEADER header;
        long msg_id;       // 4 bytes message ID
        long msg_len;      // 4 bytes message length
        short block_id;    // Block position for splitted messages
    }

If we split the UDP packets to send only 508 bytes per packet (the actual
splitted block size is configurable and not part of protocol) the max size of
our message is (as HEADER is 8 bytes, MSG = 10 + 8; we can have 2 ^ 16 blocks):

.. code:: Python
    
    (508 - (8 + 10)) * (2 ** 16) = 32112640  # Or ~ 30MB


UDP Reliable MSG_ACK packet
```````````````````````````

**Server --> Client**
**Client --> Server**

MSG_ACK's are responses to MSG packets. Those are simple ACK's meaning we only
confirm 1 block per packet.

General params:

.. code:: C

    channel = 0xXX
    op_code = 0x11
    version = 0x00

Packet payload

.. code:: C

    struct MSG_ACK {
        HEADER header;
        long msg_id;       // 4 bytes message ID
        short block_id;    // Which blocks were received already
    }
