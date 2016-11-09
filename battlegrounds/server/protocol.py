import struct
from engine.geometry import Circle, Polygon
from engine.geometry import Vector


class Header(object):
    """docstring for header"""
    def __init__(self, opc, ver, session):
        self._op_code = opc
        self._version = ver
        self._session = session

    @property
    def op_code(self):
        return self._op_code

    @property
    def version(self):
        return self._version

    @property
    def session(self):
        return self._session

#    @classmethod
#    def encode(cls, opc, ver, ses):
#        return Header(opc, ver, ses)

    @classmethod
    def decode(cls, data):
        opc, ver, ses = struct.unpack_from('!BBL', data)
        return Header(opc, ver, ses)

    @classmethod
    def size(cls):
        return struct.calcsize('!BBL')


class Auth(object):
    """docstring for Auth"""
    def __init__(self, ver, ses):
        self._header = Header(0, ver, ses)

    def encode(self):
        return struct.pack('!BBL', self._header.op_code,
                           self._header.version, self._header.session)

    @classmethod
    def decode(cls, pack):
        opc, ver, ses = struct.unpack('!BBL', pack)
        return Auth(ver, ses)


class AuthOk(object):
    """docstring for AuthOk"""
    def __init__(self, ver, ses, name, pos, ford, movb):
        self._header = Header(1, ver, ses)
        self._name = name
        self._position = pos
        self._forward = ford
        self._movbits = movb

    @property
    def name_length(self):
        return len(self._name)

    def encode(self):
        data = list()
#        offset = 0

        fmt = '!BBL'
        data.append(struct.pack(
            fmt,
            self._header.op_code, self._header.version, self._header.session))
#        offset += Header.size()

        fmt = '!B' + str(self.name_length) + 's'
        data.append(struct.pack(
            fmt,
            self.name_length, self._name.encode()))
#        offset += struct.calcsize(fmt)

        fmt = '!ddffb'
        data.append(struct.pack(
            fmt,
            self._position.x, self._position.y,
            self._forward.x, self._forward.y,
            self._movbits))

        return b''.join(data)

    @classmethod
    def decode(cls, data):
        header = Header.decode(data)
        [name_len] = struct.unpack_from('!B', data, Header.size())
        name = data[Header.size() + 1:Header.size() + 1 + name_len].decode()
        upack = struct.unpack_from(
            '!ddffB', data, Header.size() + 1 + name_len)
        return AuthOk(
            header.version, header.session, name,
            Vector(upack[0], upack[1]), Vector(upack[2], upack[3]), upack[4])


class Prop(object):
    """docstring for Prop"""
    def __init__(self, ver, ses, pos, shape_t, shape):
        self._header = Header(2, ver, ses)
        self._position = pos
        self._shape_type = shape_t
        if shape_t == 0:
            self._shape = Circle(shape.center, shape.radius)
        elif shape_t == 1:
            self._shape = Polygon(shape.points)

    def encode(self):
        d1_len = struct.calcsize('!BBLddB')
        data = list()
        data.append(struct.pack(
            '!BBLddB',
            self._header.op_code, self._header.version, self._header.session,
            self._position.x, self._position.y, self._shape_type))
        if self._shape_type == 0:
            data.append(struct.pack(
                "!fff", self._shape.center.x, self._shape.center.y,
                self._shape.radius))
        elif self._shape_type == 1:
            data.append(struct.pack(
                '!H', len(self._shape.points)))
            offset = d1_len + struct.calcsize('!H')
            inc = struct.calcsize('!ff')
            for p in self._shape.points:
                data.append(struct.pack('!ff', p.x, p.y))
                offset += inc
        return b''.join(data)

    @classmethod
    def decode(cls, data):
        header = Header.decode(data)
        offset = Header.size()
        posx, posy, shape_t = struct.unpack_from('!ddB', data, offset)
        pos = Vector(posx, posy)
        offset += struct.calcsize('!ddB')
        if shape_t == 0:
            centx, centy, rad = struct.unpack_from('!fff', data, offset)
            return Prop(
                header.version, header.session, pos, shape_t,
                Circle(Vector(centx, centy), rad))
        elif shape_t == 1:
            [p_count] = struct.unpack_from('!H', data, offset)
            offset += struct.calcsize('!H')
            points = list()
            inc = struct.calcsize('!ff')
            while p_count > 0:
                p_count -= 1
                px, py = struct.unpack_from('!ff', data, offset)
                offset += inc
                points.append(Vector(px, py))
            return Prop(
                header.version, header.session, pos, shape_t,
                Polygon(points))


class PropOk(object):
    """docstring for PropOk"""
    def __init__(self, ver, ses):
        self._header = Header(3, ver, ses)

    def encode(self):
        return struct.pack('!BBL', self._header.op_code,
                           self._header.version, self._header.session)

    @classmethod
    def decode(cls, pack):
        opc, ver, ses = struct.unpack('!BBL', pack)
        return PropOk(ver, ses)


class MoveOp(object):
    """docstring for Move_Op"""
    def __init__(self, ver, ses, sig, pos, ford, movb):
        self._header = Header(4, ver, ses)
        self._sign = sig
        self._position = pos
        self._forward = ford
        self._movbits = movb

    def encode(self):
        return struct.pack('!BBLHddffB',
                           self._header.op_code, self._header.version,
                           self._header.session, self._sign,
                           self._position.x, self._position.x,
                           self._forward.x, self._forward.y, self._movbits)

    @classmethod
    def decode(cls, pack):
        upack = struct.unpack('!BBLHddffB', pack)
        return MoveOp(
            upack[1], upack[2], upack[3], Vector(upack[4], upack[5]),
            Vector(upack[6], upack[7]), upack[8])


class MoveEvent(object):
    """docstring for Move_Event"""
    def __init__(self, ver, ses, sig, pos, ford, movb):
        self._header = Header(5, ver, ses)
        self._sign = sig
        self._position = pos
        self._forward = ford
        self._movbits = movb

    def encode(self):
        return struct.pack('!BBLHddffB',
                           self._header.op_code, self._header.version,
                           self._header.session, self._sign,
                           self._position.x, self._position.x,
                           self._forward.x, self._forward.y, self._movbits)

    @classmethod
    def decode(cls, pack):
        upack = struct.unpack('!BBLHddffB', pack)
        return MoveEvent(
            upack[1], upack[2], upack[3], Vector(upack[4], upack[5]),
            Vector(upack[6], upack[7]), upack[8])
