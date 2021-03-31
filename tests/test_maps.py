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
PATTERNS = [
    "bigsegment",
    "crabs",
    "eightpi",
    "eightr",
    "fourrabbits",
    "orchard",
    "quadjustyna",
    "rabbitfarm",
    "random",
    "randommethuselahs",
    "randompartition",
    "randomsegment",
    "spaceshipcluster",
    "spaceshipcrash",
    "spaceshipsegment",
    "spiders",
    "switchengines",
    "timebomb",
    "timebombredux",
    "twoacorn",
    "twomultum",
    "twospaceshipgenerators",
]

PATTERNS_S13 = [
    "bigsegment",
    "crabs",
    "eightpi",
    "eightr",
    "fourrabbits",
    "orchard",
    "quadjustyna",
    "rabbitfarm",
    "random",
    "randommethuselahs",
    "randompartition",
    "randomsegment",
    "spaceshipcluster",
    "spaceshipcrash",
    "spaceshipsegment",
    "spiders",
    "switchengines",
    "timebomb",
    "timebombredux",
    "twomultum",
]

PATTERNS_S11 = [
    "bigsegment",
    "eightpi",
    "eightr",
    "fourrabbits",
    "orchard",
    "quadjustyna",
    "rabbitfarm",
    "random",
    "randommethuselahs",
    "randompartition",
    "randomsegment",
    "spaceshipcluster",
    "spaceshipcrash",
    "spaceshipsegment",
    "switchengines",
    "timebomb",
    "timebombredux",
    "twoacorn",
    "twomultum",
    "twospaceshipgenerators",
]

# A list of patterns after new Season 4 maps
PATTERNS_S4 = [
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

# A list of patterns after new Season 0 maps
PATTERNS_S0 = [
    "eightpi",
    "eightr",
    "fourrabbits",
    "random",
    "timebomb",
    "twoacorn",
    "twomultum",
    "twospaceshipgenerators",
]

# Required keys for map metadata
map_metadata_req_keys = [
    "patternName",
    "mapName",
    "mapZone1Name",
    "mapZone2Name",
    "mapZone3Name",
    "mapZone4Name",
    "mapDescription",
    "mapStartSeason",
]

# Required keys for map realizations (used by map API)
map_realization_req_keys = [
    "patternName",
    "mapName",
    "mapZone1Name",
    "mapZone2Name",
    "mapZone3Name",
    "mapZone4Name",
    "url",
    "initialConditions1",
    "initialConditions2",
    "rows",
    "columns",
    "cellSize",
]


class HellmouthCupMapsTest(unittest.TestCase):
    """
    Test maps functionality for Hellmouth Cup maps
    in the golly maps package.
    """
    cup = 'hellmouth'

    def test_get_all_map_patterns(self):
        cup = self.cup
        all_patterns = get_all_map_patterns(cup)
        self.assertEqual(sorted(all_patterns), sorted(PATTERNS))

    def test_get_map_metadata(self):
        cup = self.cup
        for pattern_name in PATTERNS:
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
        self.assertEqual(sorted(patterns0), sorted(PATTERNS_S0))

        # -----
        # Check second batch of maps (Season 4)
        season4 = 4
        map_data4 = get_all_map_metadata(cup, season4)

        # Check the metadata returned
        for m in map_data4:
            for rk in map_metadata_req_keys:
                self.assertIn(rk, m)

        # Check the patterns returned
        patterns4 = [m['patternName'] for m in map_data4]
        self.assertEqual(sorted(patterns4), sorted(PATTERNS_S4))

        # -----
        # Check third batch of maps (Season 11)
        seasonX = 11
        map_dataX = get_all_map_metadata(cup, seasonX)

        # Check the metadata returned
        for m in map_dataX:
            for rk in map_metadata_req_keys:
                self.assertIn(rk, m)

        # Check the patterns returned
        patternsX = [m['patternName'] for m in map_dataX]
        self.assertEqual(sorted(patternsX), sorted(PATTERNS_S11))

        # -----
        # Check fourth batch of maps (Season 13)
        seasonY = 13
        map_dataY = get_all_map_metadata(cup, seasonY)

        # Check the metadata returned
        for m in map_dataY:
            for rk in map_metadata_req_keys:
                self.assertIn(rk, m)

        # Check the patterns returned
        patternsY = [m['patternName'] for m in map_dataY]
        self.assertEqual(sorted(patternsY), sorted(PATTERNS_S13))

    def test_get_map_realization(self):
        cup = self.cup
        for pattern_name in PATTERNS:
            r = 100
            c = 120
            m = get_map_realization(cup, pattern_name, rows=r, columns=c)
            for rk in map_realization_req_keys:
                self.assertIn(rk, m.keys())

    def test_get_map_01_basicget(self):
        cup = self.cup
        for pattern_name in PATTERNS:
            with self.subTest(pattern_name=pattern_name):
                # Standard size
                r = 100
                c = 120
                get_map_realization(cup, pattern_name, rows=r, columns=c)

    def test_get_map_02_no_exceptions(self):
        cup = self.cup

        # Get each map 25 times
        # This ensures there are no corner cases to raise exceptions
        for pattern_name in PATTERNS:

            # Standard size
            r = 100
            c = 120
            for i in range(25):
                get_map_realization(cup, pattern_name, rows=r, columns=c)

            # Double size
            r = 200
            c = 240
            for i in range(25):
                get_map_realization(cup, pattern_name, rows=r, columns=c)

    def test_random(self):
        """
        Special tests for the two random maps:
        make sure we don't have an off-by-one error
        (artifact: missing any cells for row 0.)
        """
        cup = self.cup
        random_patterns = ["random", "randompartition"]
        for pattern_name in random_patterns:
            r = 100
            c = 120
            m = get_map_realization(cup, pattern_name, rows=r, columns=c)
            ic1 = json.loads(m["initialConditions1"])[0]
            ic2 = json.loads(m["initialConditions2"])[0]
            state1_has_row0 = "0" in ic1.keys()
            state2_has_row0 = "0" in ic1.keys()
            self.assertTrue(state1_has_row0 or state2_has_row0)
