import struct
import unittest

from engine.geometry import Circle, Polygon, Vector

from server.protocol import Prop


class TestProtocol(unittest.TestCase):
    maxDiff = None

    def assertBinaryEqual(self, data, slices):  # noqa
        slices = list(slices)
        offset = 0
        res = []
        for part in slices:
            res.append(data[offset:offset + len(part)])
            offset += len(part)
        self.assertEqual(res, slices)

    def test_prop(self):
        pos = Vector(112.225, -843.8)
        cr = Circle(Vector(-1, -1), 12)
        points = [[0, 5], [-1, 4], [-2, 1], [-2, 0], [-1, -3], [0, -5]]
        poly = Polygon([Vector(*p) for p in points])
        render_data = b"\x01\x02\x03"

        # Check encode/decode cirlce
        propc = Prop(3, pos, cr, render_data)
        propc_data = bytearray(propc.size)
        propc.encode(propc_data)
        self.assertBinaryEqual(propc_data, [
            b'\x00\x00\x00\x00\x00\x00\x00\x03',  # 8 byte prop_id
            struct.pack("!dd", pos.x, pos.y),     # 16 byte position as doubles
            b'\x00',  # 1 byte shape type
            struct.pack("!ff", -1, -1),   # 8 byte center as floats
            struct.pack("!f", 12),  # 4 byte radius as float
            b'\x00\x03',  # render data length
            render_data
        ])
        self.assertEqual(Prop.decode(propc_data), propc)

        # Check encode/decode polygon
        propc = Prop(4, pos, poly, render_data)
        propc_data = bytearray(propc.size)
        propc.encode(propc_data)
        self.assertBinaryEqual(bytes(propc_data), [
            b'\x00\x00\x00\x00\x00\x00\x00\x04',  # 8 byte prop_id
            struct.pack("!dd", pos.x, pos.y),     # 16 byte position as doubles
            b'\x01',  # 1 byte shape type
            b'\x00\x06',  # 6 vertices
        ] + [struct.pack("!ff", *point) for point in points] + [
            b'\x00\x03',  # render data length
            render_data
        ])
        self.assertEqual(Prop.decode(propc_data), propc)


# class TestMoveEvent(unittest.TestCase):
#     def test_pack(self):
#         ver = 0
#         ses = 1
#         sig = 517
#         pos = Vector(112.225, -843.8)
#         ford = Vector(1, 0)

#         move_e = MoveEvent(ver, ses, sig, pos, ford, 7)
#         data = move_e.encode()
#         move_e_dc = MoveEvent.decode(data)
#         self.assertEqual(move_e_dc.encode(), data)
