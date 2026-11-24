import pytest
import roman
from gollyx_maps.error import GollyXMapsError
from gollyx_maps.registry import (
    get_cup_maps,
    CupMaps,
    GOLLY_REGISTRY,
    PENINSULA_REGISTRY,
)
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
    instance with only its own map functions and metadata file (not cumulative).
    """
    cm = get_cup_maps("vi")
    assert isinstance(cm, CupMaps)
    assert cm.type == "standard"
    assert cm.default_rows == 150
    assert cm.default_columns == 240
    assert cm.metadata_files == ["vi.json"]

    # Golly Union patterns are not cumulative
    pattern_map = cm.pattern_function_map()
    assert pattern_map.keys() == get_vi_pattern_function_map().keys()


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

@pytest.mark.parametrize("cup", ["ix", "star-ix"])
def test_cup_ix_board_size(cup):
    """
    Verify that cup ix in both unions defaults to a 240x360 board with cell size 2.
    """
    cm = get_cup_maps(cup)
    assert (cm.default_rows, cm.default_columns, cm.default_cell_size) == (240, 360, 2)


def test_cup_ix_patterns():
    """
    Verify that ix keeps the viii maps, and star-ix adds its own new patterns and
    metadata file to the star-viii maps.
    """
    ix, viii = get_cup_maps("ix"), get_cup_maps("viii")
    assert ix.pattern_function_map().keys() == viii.pattern_function_map().keys()
    assert ix.metadata_files == viii.metadata_files

    star_ix, star_viii = get_cup_maps("star-ix"), get_cup_maps("star-viii")
    assert star_ix.pattern_function_map().keys() == star_viii.pattern_function_map().keys() | {"pictureframe"} | {f"poly{n}{v}" for n in "1234" for v in ("", "a", "b", "c")}
    assert star_ix.metadata_files == ["star_ix.json"] + star_viii.metadata_files


@pytest.mark.parametrize("cup, size", [("viii", (150, 240, 3)), ("star-viii", (180, 280, 3))])
def test_cup_viii_board_size(cup, size):
    """
    Verify that cup viii in both unions keeps its board size.
    """
    cm = get_cup_maps(cup)
    assert (cm.default_rows, cm.default_columns, cm.default_cell_size) == size
