import pytest
import roman
from gollyx_maps.error import GollyXMapsError
from gollyx_maps.registry import (
    get_cup_maps,
    CupMaps,
    GOLLY_REGISTRY,
    PENINSULA_REGISTRY,
)
from gollyx_maps.ii import get_ii_pattern_function_map
from gollyx_maps.vi import get_vi_pattern_function_map
from gollyx_maps.star import get_star_pattern_function_map
from gollyx_maps.star_vii import get_star_vii_new_pattern_function_map


def test_get_cup_maps_legacy():
    """
    Test that legacy cups return a CupMaps instance with the correct
    hardcoded properties.
    """
    # Test one legacy cup to make sure it's working
    cm = get_cup_maps("hellmouth")
    assert isinstance(cm, CupMaps)
    assert cm.type == "standard"
    assert cm.default_rows == 100
    assert cm.default_columns == 120
    assert cm.zone_labels is True
    assert "hellmouth.json" in cm.metadata_files


def test_golly_union_defined():
    """
    Verify that a defined Golly Union cup (e.g., "vi") returns a CupMaps
    instance with the correct cumulative map functions and merged metadata files.
    """
    cm = get_cup_maps("vi")
    assert isinstance(cm, CupMaps)
    assert cm.type == "standard"
    assert cm.default_rows == 150
    assert cm.default_columns == 240
    assert "ii.json" in cm.metadata_files
    assert "vi.json" in cm.metadata_files

    # Check for cumulative patterns
    pattern_map = cm.pattern_function_map()
    assert set(get_ii_pattern_function_map().keys()).issubset(pattern_map.keys())
    assert set(get_vi_pattern_function_map().keys()).issubset(pattern_map.keys())


def test_golly_union_interpolated():
    """
    Verify that an interpolated Golly Union cup (e.g., "v") correctly
    resolves to the configuration of the previous defined cup ("ii").
    """
    cm_v = get_cup_maps("v")
    cm_ii = get_cup_maps("ii")
    assert cm_v.pattern_function_map().keys() == cm_ii.pattern_function_map().keys()
    assert cm_v.metadata_files == cm_ii.metadata_files
    assert cm_v.default_rows == cm_ii.default_rows


def test_golly_union_future():
    """
    Verify that a future Golly Union cup (e.g., "c") resolves to the
    configuration of the latest defined Golly Union cup.
    """
    latest_golly_cup_num = GOLLY_REGISTRY[-1][0]
    cm_future = get_cup_maps("c")  # 100
    cm_latest = get_cup_maps(roman.toRoman(latest_golly_cup_num))
    cm_xxi = get_cup_maps("xxi")

    assert len(cm_future.pattern_function_map()) == len(cm_latest.pattern_function_map())
    assert len(cm_xxi.pattern_function_map()) == len(cm_latest.pattern_function_map())


def test_peninsula_union_defined():
    """
    Verify a defined Peninsula cup (e.g., "star-vii") has the right
    cumulative maps.
    """
    cm = get_cup_maps("star-vii")
    assert isinstance(cm, CupMaps)
    assert cm.type == "star"
    assert cm.default_rows == 180
    assert cm.default_columns == 280
    assert "star.json" in cm.metadata_files
    assert "star_vii.json" in cm.metadata_files

    # Check for cumulative patterns
    pattern_map = cm.pattern_function_map()
    assert set(get_star_pattern_function_map().keys()).issubset(pattern_map.keys())
    assert set(get_star_vii_new_pattern_function_map().keys()).issubset(pattern_map.keys())


def test_peninsula_union_interpolated():
    """
    Verify an interpolated Peninsula cup (e.g., "star-vi") resolves to
    the previous definition ("star").
    """
    cm_star_vi = get_cup_maps("star-vi")
    cm_star = get_cup_maps("star")
    assert cm_star_vi.pattern_function_map().keys() == cm_star.pattern_function_map().keys()
    assert cm_star_vi.metadata_files == cm_star.metadata_files
    assert cm_star_vi.default_rows == cm_star.default_rows


def test_peninsula_union_future():
    """
    Verify that a future Peninsula cup (e.g., "star-c") resolves to
    the latest Peninsula Union cup.
    """
    latest_peninsula_cup_num = PENINSULA_REGISTRY[-1][0]
    cm_future = get_cup_maps("star-c")
    cm_latest = get_cup_maps(f"star-{roman.toRoman(latest_peninsula_cup_num)}")

    cm_future_patterns = cm_future.pattern_function_map()
    cm_latest_patterns = cm_latest.pattern_function_map()
    assert len(cm_future_patterns) == len(cm_latest_patterns)


def test_error_handling():
    """
    Assert that GollyXMapsError is raised for invalid cup names or numbers.
    """
    with pytest.raises(GollyXMapsError):
        get_cup_maps("foo")
    with pytest.raises(GollyXMapsError):
        get_cup_maps("i")  # Too small
    with pytest.raises(GollyXMapsError):
        get_cup_maps("star-0")
    with pytest.raises(GollyXMapsError):
        get_cup_maps(1)
    with pytest.raises(GollyXMapsError):
        get_cup_maps("")
    with pytest.raises(GollyXMapsError):
        get_cup_maps(None)