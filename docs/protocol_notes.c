


struct HEADER 
{
    op_code char;
    version char;
    session long; // 4 bytes
}

login, password
account = 17
character = 20
---> session

// 

struct VectorF
{
    float x;  // 4 bytes
    float y;  // 4 bytes
};

struct VectorD
{
    double x;  // 8 bytes
    double y;  // 8 bytes
};

struct CharacterMovement
{
    VectorD position;
    VectorF forward; // unit vector
    char movementBits;
    // signed int movement: 2;
    // signed int rotation: 2;
    // signed int strafe: 2;
};

// MOVEMENT_MASK = 0x03
// ROTATION_MASK = 0x03 << 2
// STRAFE_MASK = 0x03 << 4

// movement = movement_bits & MOVEMENT_MASK
// rotation = movement_bits & ROTATION_MASK
// strafe = movement_bits & STRAFE_MASK


// AUTH
struct AUTH
{
    // op_code = x00
    // version = x00
};
// Repeat until user data received
struct AUTH_OK
{
    // op_code = x01
    // version = x00
    name_len char,
    name char[],  // Length == name_len
    VectorD position;
    VectorF forward; // unit vector
    char movementBits;
};

struct PROP
{
    // op_code = x02
    // version = x00
    vectorD position;
    char shape_type;
    // ...
};

struct Polygon
{
    // shape_type = 1
    short vertices_len;
    vectorF[] vertices;
};

struct Circle
{
    // shape_type = 0
    vectorF center;
    float radius;
};

struct PROP_OK
{
    // op_code = x03
    // version = x00
};

struct MOVE_OP
{
    // op_code = x04
    // version = x00
    short op_sig;
    VectorD position;
    VectorF forward; // unit vector
    char movementBits;
};

struct MOVE_EVENT
{
    // op_code = x05
    // version = x00
    short op_sig;
    short event_sig;
    VectorD position;
    VectorF forward; // unit vector
    char movementBits;
};


AUTH     --> Bla bla connect          // With retransmission
AUTH_OK  <-- Character data + Character movement data
PROP     <-- Surrounding environment  // With retransmission
PROP_OK  --> OK
...
MOVE_OP     --> Movement events          // No retransmission
MOVE_EVENT  <-- Character movement data
