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
    Test patterns functionality in golly_maps
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
        Check the get_pattern() method and its arguments.
        This doesn't check the contents of patterns returned, only the sizes.
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
        """
        Check that the get_pattern_size() method returns the correct sizes.
        Check that hflip/vflip/rotdeg arguments modify the size correctly.
        """
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

            with self.assertRaises(Exception):
                _ = get_pattern_size(pattern_name, rotdeg=111)

    def test_get_grid_pattern(self):
        """
        Call the get_grid_pattern() function with its various arguments.
        Check that the grid patterns returned are the correct size.
        """
        for pattern_name, (pattern_r, pattern_c) in PATTERN_SIZES.items():
            pattern = get_pattern(pattern_name)
            rows = 80
            cols = 80
            xoffset = 40
            yoffset = 40

            grid_patterns = []
            grid_patterns.append(get_grid_pattern(pattern_name, rows, cols, xoffset=xoffset, yoffset=yoffset))
            grid_patterns.append(get_grid_pattern(pattern_name, rows, cols, xoffset=xoffset, yoffset=yoffset, hflip=True))
            grid_patterns.append(get_grid_pattern(pattern_name, rows, cols, xoffset=xoffset, yoffset=yoffset, vflip=True))
            grid_patterns.append(get_grid_pattern(pattern_name, rows, cols, xoffset=xoffset, yoffset=yoffset, rotdeg=90))
            grid_patterns.append(get_grid_pattern(pattern_name, rows, cols, xoffset=xoffset, yoffset=yoffset, rotdeg=180))
            grid_patterns.append(get_grid_pattern(pattern_name, rows, cols, xoffset=xoffset, yoffset=yoffset, rotdeg=270))
            grid_patterns.append(get_grid_pattern(pattern_name, rows, cols, xoffset=xoffset, yoffset=yoffset, rotdeg=360))

            for gp in grid_patterns:
                self.assertEqual(len(gp), rows)
                self.assertEqual(len(gp[0]), cols)

            with self.assertRaises(Exception):
                get_grid_pattern(pattern_name, rows=-1, cols=-1)
                get_grid_pattern(pattern_name, rows=0, cols=0)
                get_grid_pattern(pattern_name, rows=1, cols=1)
                get_grid_pattern(pattern_name, rows=10, cols=10, xoffset=100, yoffset=100)
                get_grid_pattern(pattern_name, rows, cols, xoffset=xoffset, yoffset=yoffset, rotdeg=111)

    def test_pattern_union(self):
        pattern1 = [
            ".......ooo",
            ".......ooo",
            "...ooooooo",
            "...ooooooo"
        ]
        pattern2 = [
            "ooooooo...",
            "ooooooo...",
            "ooo.......",
            "ooo......."
        ]
        union = pattern_union([pattern1, pattern2])
        for row in union:
            for ch in row:
                self.assertEqual(ch, "o")
