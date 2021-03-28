import os
import unittest
from gollyx_maps.geom import hflip_pattern, vflip_pattern, rot_pattern


HERE = os.path.split(os.path.abspath(__file__))[0]


class GeomTest(unittest.TestCase):
    """
    Test geometry methods in gollyx_maps
    """

    def test_hflip_pattern(self):
        pattern = ["oooooo......", "oooooo......", "............", "............"]
        hpattern = ["......oooooo", "......oooooo", "............", "............"]
        self.assertEqual(hflip_pattern(pattern), hpattern)

    def test_vfip_pattern(self):
        pattern = ["oooooo......", "oooooo......", "............", "............"]
        vpattern = ["............", "............", "oooooo......", "oooooo......"]
        self.assertEqual(vflip_pattern(pattern), vpattern)

    def test_rot_pattern(self):
        pattern = ["oooooo......", "oooooo......", "............", "............"]
        pattern90 = [
            "..oo",
            "..oo",
            "..oo",
            "..oo",
            "..oo",
            "..oo",
            "....",
            "....",
            "....",
            "....",
            "....",
            "....",
        ]
        pattern180 = ["............", "............", "......oooooo", "......oooooo"]
        pattern270 = [
            "....",
            "....",
            "....",
            "....",
            "....",
            "....",
            "oo..",
            "oo..",
            "oo..",
            "oo..",
            "oo..",
            "oo..",
        ]
        self.assertEqual(rot_pattern(pattern, deg=0), pattern)
        self.assertEqual(rot_pattern(pattern, deg=90), pattern90)
        self.assertEqual(rot_pattern(pattern, deg=180), pattern180)
        self.assertEqual(rot_pattern(pattern, deg=270), pattern270)
        self.assertEqual(rot_pattern(pattern, deg=360), pattern)

        with self.assertRaises(Exception):
            _ = rot_pattern(pattern, deg=111)
            _ = rot_pattern(pattern, deg=-90)
