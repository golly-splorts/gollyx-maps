import json
import os
import unittest
from golly_maps.maps import (
    get_patterns,
    get_map,
    get_map_data,
    get_all_map_data,
)


HERE = os.path.split(os.path.abspath(__file__))[0]

PATTERNS = [
    "eightpi",
    "eightr",
    "fourrabbits",
    "quadjustyna",
    "random",
    "randompartition",
    "spaceshipcluster",
    "spaceshipcrash",
    "timebomb",
    "twoacorn",
    "twomultum",
    "twospaceshipgenerators",
]

PATTERNS_PRE3 = [
    "eightpi",
    "eightr",
    "fourrabbits",
    "random",
    "timebomb",
    "twoacorn",
    "twomultum",
    "twospaceshipgenerators",
]


class MapsTest(unittest.TestCase):
    """
    Test maps functionality in the golly maps package.
    """

    def test_get_patterns(self):
        patterns = get_patterns()
        for pattern_name in PATTERNS:
            self.assertIn(pattern_name, patterns)

    def test_get_map(self):
        for pattern_name in PATTERNS:
            r = 100
            c = 120
            m = get_map(pattern_name, rows=r, cols=c)
            req_keys = [
                "patternName",
                "mapName",
                "url",
                "rows",
                "columns",
                "cellSize",
                "initialConditions1",
                "initialConditions2",
                "mapZone1Name",
                "mapZone2Name",
                "mapZone3Name",
                "mapZone4Name",
            ]
            for rk in req_keys:
                self.assertIn(rk, m.keys())

    def test_get_all_map_data(self):
        for pattern_name in PATTERNS:
            for season in range(0, 10):
                map_data = get_all_map_data(season)
                pattern_names = [m["patternName"] for m in map_data]
                if season < 3:
                    self.assertEqual(sorted(pattern_names), sorted(PATTERNS_PRE3))
                else:
                    self.assertEqual(sorted(pattern_names), sorted(PATTERNS))

    def test_get_map_data(self):
        for pattern_name in PATTERNS:
            dat = get_map_data(pattern_name)
            req_keys = [
                "patternName",
                "mapName",
                "mapZone1Name",
                "mapZone2Name",
                "mapZone3Name",
                "mapZone4Name",
            ]
            for rk in req_keys:
                self.assertIn(rk, dat.keys())

    def test_random(self):
        """
        Special tests for the two random maps:
        make sure we don't have an off-by-one error
        (artifact: missing any cells for row 0.)
        """
        random_patterns = ["random", "randompartition"]
        for pattern_name in random_patterns:
            r = 100
            c = 120
            m = get_map(pattern_name, r, c)
            ic1 = json.loads(m["initialConditions1"])[0]
            ic2 = json.loads(m["initialConditions2"])[0]
            self.assertTrue(ic1 != "0" or ic2 != "0")
