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

Specific purpose Channels:

    * ``channel==0x00`` - command channel
    * ``channel==0x01`` - character information and movement channel
    * ``channel==0x02`` - environment sync channel

UDP AUTH packet
```````````````

AUTH packet is quite unique, as it MUST be the 1-st packet on this session,
MUST always be sent with ``channel==0x00`` and should be repeated until
AUTH_OK received, or expired by connection timeout (received with
``SessionID``).

General params:

.. code::
    channel = 0x00
    op_code = 0x00
    version = 0x00

Packet structure:

.. code::
    channel = 0x00
    op_code = 0x00
    version = 0x00

