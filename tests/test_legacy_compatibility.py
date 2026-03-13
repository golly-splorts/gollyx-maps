
import pytest
from gollyx_maps.maps import get_map_realization

# We test a sample of patterns for each legacy cup to ensure their
# realization is deterministic. A full snapshot test is ideal but
# requires pre-computed known-good outputs. This test provides a
# good baseline for catching regressions.

LEGACY_MAP_SAMPLES = {
    "hellmouth": ["crabs", "random", "timebombredux"],
    "toroidal": ["crabdonuts", "donutrandom", "donutmath"],
    "rainbow": ["random", "rainbowmath", "eights"],
    "klein": ["kleinmath", "random", "crabs"],
    "pseudo": ["gaussian", "random", "tripledouble"],
    "dragon": ["starfield", "vector", "isotropic"],
    "star": ["flyingv1", "random", "kitchensink"],
    # Technically "ii" and "vi" are not "legacy" in the same way,
    # but their behavior should be stable too.
    "ii": ["random", "hellmath"],
    "vi": ["detroit_carbomb", "random", "west_seattle"],
}

# Flatten the dictionary into a list of (cup, pattern) tuples for parametrize
TEST_CASES = [
    (cup, pattern)
    for cup, patterns in LEGACY_MAP_SAMPLES.items()
    for pattern in patterns
]

@pytest.mark.parametrize("cup, pattern_name", TEST_CASES)
def test_legacy_determinism(cup, pattern_name):
    """
    Tests that legacy map realizations are deterministic by generating them
    twice and asserting the results are identical.
    """
    # Generate the realization twice
    realization1 = get_map_realization(cup, pattern_name, seed=42)
    realization2 = get_map_realization(cup, pattern_name, seed=42)

    # The entire dictionary output should be identical
    assert realization1 == realization2

    # A more granular check on the initial conditions
    assert realization1["initialConditions1"] == realization2["initialConditions1"]
    assert realization1["initialConditions2"] == realization2["initialConditions2"]
