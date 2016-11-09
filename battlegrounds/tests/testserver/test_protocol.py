from engine.geometry import Circle, Polygon, Vector
from server.protocol import Auth, AuthOk, MoveOp, MoveEvent, Prop, PropOk
import unittest


class TestAuth(unittest.TestCase):
    def test_pack(self):
        ver = 0
        ses = 1
        au = Auth(ver, ses)
        data = au.encode()

        audc = Auth.decode(data)
        self.assertEqual(au._header.op_code, audc._header.op_code)
        self.assertEqual(au._header.version, audc._header.version)
        self.assertEqual(au._header.session, audc._header.session)


class TestAuthOk(unittest.TestCase):
    def test_pack(self):
        ver = 0
        ses = 1
        name = "qwerty123~"
        pos = Vector(112.225, -843.8)
        ford = Vector(1, 0)
        auok = AuthOk(ver, ses, name, pos, ford, 7)
        data = auok.encode()

        auokdc = AuthOk.decode(data)
        self.assertEqual(auokdc.encode(), data)


class TestHeader(unittest.TestCase):
    pass


class TestProp(unittest.TestCase):
    def test_pack(self):
        ver = 0
        ses = 1
        pos = Vector(112.225, -843.8)

        cr = Circle(Vector(-1, -1), 12)

        points = [[0, 5], [-1, 4], [-2, 1], [-2, 0], [-1, -3], [0, -5]]
        poly = Polygon([Vector(*p) for p in points])

        propc = Prop(ver, ses, pos, 0, cr)
        propc_data = propc.encode()
        propc_dc = Prop.decode(propc_data)
        self.assertEqual(propc_data, propc_dc.encode())

        propp = Prop(ver, ses, pos, 1, poly)
        propp_data = propp.encode()
        propp_dc = Prop.decode(propp_data)
        self.assertEqual(propp_data, propp_dc.encode())


class TestPropOk(unittest.TestCase):
    def test_pack(self):
        ver = 0
        ses = 1
        prok = PropOk(ver, ses)
        data = prok.encode()

        prok_dc = PropOk.decode(data)
        self.assertEqual(prok_dc.encode(), data)


class TestMoveOp(unittest.TestCase):
    def test_pack(self):
        ver = 0
        ses = 1
        sig = 517
        pos = Vector(112.225, -843.8)
        ford = Vector(1, 0)

        move_op = MoveOp(ver, ses, sig, pos, ford, 7)
        data = move_op.encode()
        move_op_dc = MoveOp.decode(data)
        self.assertEqual(move_op_dc.encode(), data)


class TestMoveEvent(unittest.TestCase):
    def test_pack(self):
        ver = 0
        ses = 1
        sig = 517
        pos = Vector(112.225, -843.8)
        ford = Vector(1, 0)

        move_e = MoveEvent(ver, ses, sig, pos, ford, 7)
        data = move_e.encode()
        move_e_dc = MoveEvent.decode(data)
        self.assertEqual(move_e_dc.encode(), data)
