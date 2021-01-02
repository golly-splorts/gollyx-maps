import subprocess
import os
import unittest
from golly_maps.patterns import (
    get_patterns, 
    get_pattern,
    get_pattern_size,
    get_grid_pattern,
    pattern_union
)



"""
test_patterns

Test patterns functionality in golly_maps
"""

HERE = os.path.split(os.path.abspath(__file__))[0]

ALL_PATTERNS = [
    "78p70",
    "acorn",
    "backrake2",
    "bheptomino",
    "block",
    "cheptomino",
    "coespaceship",
    "cthulhu",
    "dinnertable",
    "dinnertablecenter",
    "dinnertableedges",
    "eheptomino",
    "glider",
    "heavyweightspaceship",
    "justyna",
    "koksgalaxy",
    "lightweightspaceship",
    "middleweightspaceship",
    "multuminparvo",
    "piheptomino",
    "quadrupleburloaferimeter",
    "rabbit",
    "rpentomino",
    "spaceshipgrower",
    "switchengine",
    "tagalong",
    "timebomb",
    "twoglidermess",
    "unidimensionalinfinitegrowth",
    "unidimensionalsixgliders",
    "x66"
]

# [nrows, ncols]
PATTERN_SIZES = {
    "block": (2, 2),
    "cheptomino": (3, 4),
    "justyna": (17, 22),
    "multuminparvo": (4, 6),
    "quadrupleburloaferimeter": (16, 16),
    "x66": (11, 9)
}


class PatternsTest(unittest.TestCase):
    """
    Test patterns functionality in the golly maps package.
    """
    def test_get_patterns(self):
        """
        Compare the list of patterns returned to the hard-coded list.
        """
        patterns = get_patterns()
        self.assertEqual(len(patterns), len(ALL_PATTERNS))
        for pattern_name in ALL_PATTERNS:
            self.assertIn(pattern_name, patterns)

    def test_get_pattern(self):
        """
        Test the get_pattern() method and its arguments.
        This doesn't check the contents of patterns returned,
        only the sizes.
        """
        for pattern_name in ALL_PATTERNS:

            # Test the function with each argument specified
            p = get_pattern(pattern_name)
            hp = get_pattern(pattern_name, hflip=True)
            vp = get_pattern(pattern_name, vflip=True)
            rot90 = get_pattern(pattern_name, rotdeg=90)
            rot180 = get_pattern(pattern_name, rotdeg=180)
            rot270 = get_pattern(pattern_name, rotdeg=270)
            rot360 = get_pattern(pattern_name, rotdeg=360)

            # Assert things that are unconditional on symmetry
            self.assertGreater(len(p), 0)
            self.assertGreater(len(hp), 0)
            self.assertGreater(len(vp), 0)
            self.assertGreater(len(rot90), 0)
            self.assertGreater(len(rot180), 0)
            self.assertGreater(len(rot270), 0)
            self.assertGreater(len(rot360), 0)
            self.assertEqual(p, rot360)
            self.assertEqual(len(p), len(rot180))
            self.assertEqual(len(rot90), len(rot270))

    def test_get_pattern_size(self):
        for pattern_name, (pattern_r, pattern_c) in PATTERN_SIZES.items():
            (r, c) = get_pattern_size(pattern_name)
            self.assertEqual(r, pattern_r)
            self.assertEqual(c, pattern_c)

            (hr, hc) = get_pattern_size(pattern_name, hflip=True)
            self.assertEqual(hr, pattern_r)
            self.assertEqual(hc, pattern_c)

            (vr, vc) = get_pattern_size(pattern_name, vflip=True)
            self.assertEqual(vr, pattern_r)
            self.assertEqual(vc, pattern_c)

            (r90, c90) = get_pattern_size(pattern_name, rotdeg=90)
            self.assertEqual(r90, pattern_c)
            self.assertEqual(c90, pattern_r)

            (r180, c180) = get_pattern_size(pattern_name, rotdeg=180)
            self.assertEqual(r180, pattern_r)
            self.assertEqual(c180, pattern_c)

            (r270, c270) = get_pattern_size(pattern_name, rotdeg=270)
            self.assertEqual(r270, pattern_c)
            self.assertEqual(c270, pattern_r)

