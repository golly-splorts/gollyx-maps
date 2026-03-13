
import pytest
from gollyx_maps.maps import (
    get_pattern_function_map,
    get_map_realization,
    get_all_map_metadata,
    get_all_map_patterns,
)

# Representative set of cups for testing
# - "hellmouth": legacy
# - "vi": Golly Union, defined, cumulative
# - "v": Golly Union, interpolated
# - "star-vii": Peninsula Union, defined, cumulative
# - "star-vi": Peninsula Union, interpolated
# - "dragon": legacy, different type
# - "rainbow": legacy, different type
# - "klein": legacy, no zones
# - "pseudo": legacy, with zones
REPRESENTATIVE_CUPS = [
    "hellmouth", "vi", "v", "star-vii", "star-vi", "dragon", "rainbow", "klein", "pseudo"
]


@pytest.mark.parametrize("cup", REPRESENTATIVE_CUPS)
def test_get_pattern_function_map(cup):
    """
    Check that get_pattern_function_map returns a non-empty dict of functions.
    """
    pattern_map = get_pattern_function_map(cup)
    assert isinstance(pattern_map, dict)
    assert len(pattern_map) > 0
    # Check that all values are functions
    assert all(callable(f) for f in pattern_map.values())


@pytest.mark.parametrize("cup", REPRESENTATIVE_CUPS)
def test_get_map_realization(cup):
    """
    For each cup, realize a sample pattern and assert that the output is valid.
    This confirms the realization pipeline works for all cup types.
    """
    # Get a sample pattern name for the cup
    pattern_name = list(get_pattern_function_map(cup).keys())[0]

    realization = get_map_realization(cup, pattern_name)
    assert isinstance(realization, dict)
    assert "patternName" in realization
    assert "mapName" in realization
    assert "url" in realization
    assert "initialConditions1" in realization
    assert "initialConditions2" in realization
    assert "rows" in realization
    assert "columns" in realization
    assert "cellSize" in realization

    # Check that the realization has cells
    ic1 = realization["initialConditions1"]
    ic2 = realization["initialConditions2"]
    # At least one of the initial conditions should have some cells
    assert (ic1 != '[{}]') or (ic2 != '[{}]')


def test_get_all_map_metadata_cumulative():
    """
    Check that metadata is correctly fetched and merged for cumulative cups.
    For "vi", metadata from both "ii" and "vi" should be present.
    """
    metadata_vi = get_all_map_metadata("vi")
    patterns_vi = {m["patternName"] for m in metadata_vi}

    metadata_ii = get_all_map_metadata("ii")
    patterns_ii = {m["patternName"] for m in metadata_ii}

    # "vi" patterns should be a superset of "ii" patterns
    assert patterns_ii.issubset(patterns_vi)
    assert len(patterns_vi) > len(patterns_ii)

    # Do the same for star-vii
    metadata_star_vii = get_all_map_metadata("star-vii")
    patterns_star_vii = {m["patternName"] for m in metadata_star_vii}

    metadata_star = get_all_map_metadata("star")
    patterns_star = {m["patternName"] for m in metadata_star}

    assert patterns_star.issubset(patterns_star_vii)
    assert len(patterns_star_vii) > len(patterns_star)


@pytest.mark.parametrize("cup", REPRESENTATIVE_CUPS)
def test_get_all_map_patterns_vs_metadata(cup):
    """
    Check that the patterns from get_all_map_patterns match what's in
    get_all_map_metadata.
    """
    all_patterns = get_all_map_patterns(cup)
    metadata_patterns = {m["patternName"] for m in get_all_map_metadata(cup)}
    assert set(all_patterns) == metadata_patterns
