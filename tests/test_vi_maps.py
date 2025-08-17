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
VI_PATTERNS = [
        "detroit_carbomb",
        "jersey_carbomb",
        "northdakota_carbomb",
        "elko_carbomb",
        "crunchy_crash",
        "tasty_crash",
        "butterfly_crash",
        "elephant_crash",
        "sea_turtles",
        "beach_crash",
        "cave_crash",
        "flotilla_crash",
        "bunny_party",
        "domino_party",
        "dove_party",
        "multum_in_party",
        "quad_garden",
        "quad_barstow",
        "quad_bakersfield",
        "spacetime_complex_north",
        "spacetime_complex_east",
        "bifurcating_spacetime_north",
        "bifurcating_spacetime_east",
        "tacoma_standoff",
        "tombstone_standoff",
        "red_rock_standoff",
        "cheyenne_showdown",
        "santa_fe_standoff",
        "caliente_standoff",
        "spaceport_standoff",
        "suns_out_gosper_guns_out",
        "west_baltimore",
        "west_cambridge",
        "west_seattle",
        "west_salt_lake",
        "west_milwaukee",
        "west_detroit",
        "spider_cave",
        "dragon_cave",
        "hellmath",
        "porchlights",
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

# Ensure NOT here
map_realization_unreq_keys = [
    "mapZone1Name",
    "mapZone2Name",
    "mapZone3Name",
    "mapZone4Name"
]



class HellmouthVICupMapsTest(unittest.TestCase):
    """
    Test maps functionality for Hellmouth VI Cup maps
    in the golly maps package.
    """
    cup = 'vi'

    def test_get_all_map_patterns(self):
        cup = self.cup
        all_patterns = get_all_map_patterns(cup)
        self.assertEqual(sorted(all_patterns), sorted(VI_PATTERNS))

    def test_get_map_metadata(self):
        cup = self.cup
        for pattern_name in VI_PATTERNS:
            metadata = get_map_metadata(cup, pattern_name)
            for rk in map_metadata_req_keys:
                self.assertIn(rk, metadata)

    def test_get_map_realization(self):
        cup = self.cup
        for pattern_name in VI_PATTERNS:
            r = 150
            c = 240
            m = get_map_realization(cup, pattern_name, rows=r, columns=c)
            for rk in map_realization_req_keys:
                self.assertIn(rk, m.keys())

    def test_get_map_01_basicget(self):
        cup = self.cup
        for pattern_name in VI_PATTERNS:
            with self.subTest(pattern_name=pattern_name):
                # Standard size
                r = 150
                c = 240
                get_map_realization(cup, pattern_name, rows=r, columns=c)

    def test_get_map_02_no_exceptions(self):
        cup = self.cup

        # Get each map 25 times
        # This ensures there are no corner cases to raise exceptions
        for pattern_name in VI_PATTERNS:

            # Standard size
            r = 150
            c = 240
            for i in range(25):
                get_map_realization(cup, pattern_name, rows=r, columns=c)

