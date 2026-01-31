"""
Test that every star-vii pattern function can generate maps successfully.

Each pattern is generated N_REALIZATIONS times with different random seeds
to exercise internal code paths (e.g. faradaycage has multiple chef's-choice
branches, twochoochoo has random track generation with approval loops, etc.).
"""

import pytest
from gollyx_maps.maps import get_map_realization, get_pattern_function_map


CUP = "star-vii"
N_REALIZATIONS = 20

STAR_VII_NEW_PATTERNS = [
    "twochoochoo",
    "candychoochoo",
    "midnightexpress",
    "spaceelevator",
    "faradaycage",
    "housewithears",
    "horsewithears",
    "ironhorse",
    "deadendterminal",
]


@pytest.mark.parametrize("pattern_name", STAR_VII_NEW_PATTERNS)
def test_star_vii_pattern_generates(pattern_name):
    """
    Generate each star-vii pattern N_REALIZATIONS times and verify
    the output is a well-formed map realization.
    """
    for seed in range(N_REALIZATIONS):
        realization = get_map_realization(CUP, pattern_name, seed=seed)

        assert isinstance(realization, dict), (
            f"{pattern_name} seed={seed}: expected dict, got {type(realization)}"
        )

        # Required keys for all map realizations
        for key in ("patternName", "mapName", "initialConditions1", "initialConditions2",
                     "url", "rows", "columns", "cellSize"):
            assert key in realization, (
                f"{pattern_name} seed={seed}: missing key {key!r}"
            )

        assert realization["patternName"] == pattern_name

        # At least one team should have live cells
        ic1 = realization["initialConditions1"]
        ic2 = realization["initialConditions2"]
        assert ic1 != "[]" or ic2 != "[]", (
            f"{pattern_name} seed={seed}: both initial conditions are empty"
        )


@pytest.mark.parametrize("pattern_name", STAR_VII_NEW_PATTERNS)
def test_star_vii_pattern_deterministic(pattern_name):
    """
    Verify that the same seed produces identical output.
    """
    r1 = get_map_realization(CUP, pattern_name, seed=42)
    r2 = get_map_realization(CUP, pattern_name, seed=42)
    assert r1 == r2, f"{pattern_name}: same seed produced different results"


def test_star_vii_inherits_star_patterns():
    """
    Verify that star-vii's pattern function map is a superset of star's.
    """
    star_patterns = set(get_pattern_function_map("star").keys())
    star_vii_patterns = set(get_pattern_function_map(CUP).keys())
    assert star_patterns.issubset(star_vii_patterns), (
        f"star-vii is missing inherited patterns: {star_patterns - star_vii_patterns}"
    )
