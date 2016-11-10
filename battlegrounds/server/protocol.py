import struct
from collections import namedtuple

from engine.geometry import Circle, Polygon
from engine.geometry import Vector

_SHORT = struct.Struct("!H")  # unsigned short struct
_VECTORF = struct.Struct("!ff")


class Prop(namedtuple("Prop", (
        "prop_id", "position", "shape_struct", "render_data"))):

    __slots__ = ()

    struct_base = struct.Struct("!Qdd")

    def __new__(cls, prop_id, position, shape, render_data):
        if isinstance(shape, CircleShape.shape_class):
            shape_struct = CircleShape(shape)
        else:
            shape_struct = PolygonShape(shape)
        return super().__new__(
            cls, prop_id, position, shape_struct, render_data)

    @property
    def shape(self):
        return self.shape_struct.shape

    @property
    def size(self, _short=_SHORT):
        return (
            # Static data
            self.struct_base.size +
            # shape size (1 byte for shape_type)
            1 + self.shape_struct.size +
            # Render data size
            _short.size + len(self.render_data)
        )

    @classmethod
    def decode(cls, data, offset=0, _short=_SHORT):
        # Unpack static part
        struct_base = cls.struct_base
        prop_id, posx, posy = struct_base.unpack_from(data, offset)
        offset += struct_base.size
        # Unpack shape
        #   char shape_type;   // Circle - 0, Polygon - 1
        #   SHAPE shape;       // depending on shape_type
        shape_t = data[offset]
        offset += 1
        if shape_t == CircleShape.shape_type:
            shape = CircleShape.decode(data, offset)
        elif shape_t == PolygonShape.shape_type:
            shape = PolygonShape.decode(data, offset)
        offset += shape.size
        # Unpack render_data
        #   short render_data_len;
        #   char render_data[];  // Depending on render_data_len
        [render_len] = _short.unpack_from(data, offset)
        offset += _short.size
        render_data = bytes(data[offset:offset + render_len])
        return super().__new__(
            cls, prop_id, Vector(posx, posy), shape, render_data)

    def encode(self, data, offset=0, _short=_SHORT):
        prop_id, pos, shape, render_data = self
        # Pack static part
        struct_base = self.struct_base
        struct_base.pack_into(data, offset, prop_id, pos.x, pos.y)
        offset += struct_base.size
        # Pack shape
        #   char shape_type;   // Circle - 0, Polygon - 1
        #   SHAPE shape;       // depending on shape_type
        data[offset] = shape.shape_type
        offset += 1
        shape.encode(data, offset)
        offset += shape.size
        # Pack render_data
        #   short render_data_len;
        #   char render_data[];  // Depending on render_data_len
        _short.pack_into(data, offset, len(render_data))
        offset += _short.size
        data[offset:] = render_data

_BaseShape = namedtuple("BaseShape", ['shape'])


class CircleShape(_BaseShape):

    __slots__ = ()

    # struct Circle
    #   // shape_type = 0
    #   vectorF center
    #   float radius
    shape_type = 0
    shape_class = Circle
    struct = struct.Struct("!fff")
    size = struct.size

    @classmethod
    def decode(cls, data, offset=0):
        c_x, c_y, radius = cls.struct.unpack_from(data, offset)
        return cls(Circle(Vector(c_x, c_y), radius))

    def encode(self, data, offset=0):
        center = self.shape.center
        self.struct.pack_into(
            data, offset, center.x, center.y, self.shape.radius)


class PolygonShape(_BaseShape):

    __slots__ = ()

    # struct Polygon
    #   // shape_type = 1
    #   short vertices_len
    #   vectorF vertices[vertices_len]
    shape_type = 1
    shape_class = Polygon

    @property
    def size(self, _short=_SHORT, _vector=_VECTORF):
        return _short.size + _vector.size * len(self.shape.points)

    @classmethod
    def decode(cls, data, offset=0, _short=_SHORT, _vector=_VECTORF):
        # Unpack size
        [points_len] = _short.unpack_from(data, offset)
        offset += _short.size
        # Unpack points vectors
        points = []
        for _ in range(points_len):
            p_x, p_y = _vector.unpack_from(data, offset)
            offset += _vector.size
            points.append(Vector(p_x, p_y))
        return cls(Polygon(points))

    def encode(self, data, offset=0, _short=_SHORT, _vector=_VECTORF):
        points = self.shape.points
        points_len = len(points)
        # Pack size
        _short.pack_into(data, offset, points_len)
        offset += _short.size
        # Pack points vectors
        for point in points:
            _vector.pack_into(data, offset, point.x, point.y)
            offset += _vector.size
