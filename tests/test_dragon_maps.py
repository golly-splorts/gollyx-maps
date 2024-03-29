import json
import os
import unittest
from gollyx_maps.maps import (
    get_all_map_patterns,
    get_map_metadata,
    get_all_map_metadata,
    get_map_realization,
)


HERE = os.path.split(os.path.abspath(__file__))[0]

# A list of all patterns ever
DRAGON_PATTERNS = [
    "starfield",
    "vector",
    "matrix",
    "lake",
    "waterfall",
    "river",
    "lighthouse",
    "towers",
    "isotropic",
    "supercritical",
]

# Required keys for map metadata
map_metadata_req_keys = [
    "patternName",
    "mapName",
    "mapDescription",
    "mapStartSeason",
]

# Required keys for map realizations (used by map API)
map_realization_req_keys = [
    "patternName",
    "mapName",
    "url",
    "initialConditions1",
    "initialConditions2",
    "rows",
    "columns",
    "cellSize",
]


class DragonCupMapsTest(unittest.TestCase):
    """
    Test maps functionality for Dragon Cup maps
    in the golly maps package.
    """
    cup = 'dragon'

    def test_get_all_map_patterns(self):
        cup = self.cup
        all_patterns = get_all_map_patterns(cup)
        self.assertEqual(sorted(all_patterns), sorted(DRAGON_PATTERNS))

    def test_get_map_metadata(self):
        cup = self.cup
        for pattern_name in DRAGON_PATTERNS:
            metadata = get_map_metadata(cup, pattern_name)
            for rk in map_metadata_req_keys:
                self.assertIn(rk, metadata)

    def test_get_all_map_metadata(self):
        cup = self.cup

        # -----
        # Check first batch of maps (Season 1)
        season0 = 0
        map_data0 = get_all_map_metadata(cup, season0)

        # Check the metadata returned
        for m in map_data0:
            for rk in map_metadata_req_keys:
                self.assertIn(rk, m)

        # Check the patterns returned
        patterns0 = [m['patternName'] for m in map_data0]
        self.assertEqual(sorted(patterns0), sorted(DRAGON_PATTERNS))

    def test_get_map_realization(self):
        cup = self.cup
        for pattern_name in DRAGON_PATTERNS:
            r = 500
            c = 200
            m = get_map_realization(cup, pattern_name, rows=r, columns=c)
            for rk in map_realization_req_keys:
                self.assertIn(rk, m.keys())

    def test_get_map_01_basicget(self):
        cup = self.cup
        for pattern_name in DRAGON_PATTERNS:
            with self.subTest(pattern_name=pattern_name):
                # Standard size
                r = 500
                c = 200
                get_map_realization(cup, pattern_name, rows=r, columns=c)

    #def test_get_map_02_no_exceptions(self):
    #    cup = self.cup

    #    # Get each map 25 times
    #    # This ensures there are no corner cases to raise exceptions
    #    for pattern_name in DRAGON_PATTERNS:

    #        # Standard size
    #        r = 500
    #        c = 200
    #        for i in range(25):
    #            get_map_realization(cup, pattern_name, rows=r, columns=c)
