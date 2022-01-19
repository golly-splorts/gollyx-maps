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

# All patterns ever
STAR_PATTERNS = [
    "flyingv1",
    "flyingv2",
    "stlouis",
    "newyork",
    "chicago",
    "combs",
    "precipitation",
    "evaporation",
    "denaturation",
    "gastank",
    "rustytank",
    "dinnerplate",
    "dessertplate",
    "squarestar",
    "kitchensink",
    "ricepudding",
    "fishsoup"
]

STAR_PATTERNS_S0 = STAR_PATTERNS[:]

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


class StarCupMapsTest(unittest.TestCase):
    """
    Test maps functionality for Star Cup maps
    in the golly maps package.
    """
    cup = 'star'

    def test_get_all_map_patterns(self):
        cup = self.cup
        all_patterns = get_all_map_patterns(cup)
        self.assertEqual(sorted(all_patterns), sorted(STAR_PATTERNS))

    def test_get_map_metadata(self):
        cup = self.cup
        for pattern_name in STAR_PATTERNS:
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
        self.assertEqual(sorted(patterns0), sorted(STAR_PATTERNS_S0))

    def test_get_map_realization(self):
        cup = self.cup
        for pattern_name in STAR_PATTERNS:
            r = 160
            c = 240
            m = get_map_realization(cup, pattern_name, rows=r, columns=c)
            for rk in map_realization_req_keys:
                self.assertIn(rk, m.keys())

    def test_get_map_01_basicget(self):
        cup = self.cup
        for pattern_name in STAR_PATTERNS:
            with self.subTest(pattern_name=pattern_name):
                # Standard size
                r = 160
                c = 240
                get_map_realization(cup, pattern_name, rows=r, columns=c)

    def test_get_map_02_no_exceptions(self):
        cup = self.cup

        # Get each map 25 times
        # This ensures there are no corner cases to raise exceptions
        for pattern_name in STAR_PATTERNS:

            # Standard size
            r = 160
            c = 240
            for i in range(20):
                get_map_realization(cup, pattern_name, rows=r, columns=c)

