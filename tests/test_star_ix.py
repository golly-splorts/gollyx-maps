import json
import pytest
from gollyx_maps import maps
from gollyx_maps.error import GollyXMapsError
from gollyx_maps.star_ix import frame_cells, pictureframe


def _is_still_life(cells, rows, cols):
    """
    Check that live cells neither die nor give birth under B2/S345 on a wrapping board.
    """
    live = {(x % cols, y % rows) for x, y in cells}
    steps = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
    near = {((x + dx) % cols, (y + dy) % rows) for x, y in live for dx, dy in steps} | live
    for x, y in near:
        n = sum(((x + dx) % cols, (y + dy) % rows) in live for dx, dy in steps)
        if (x, y) in live and not 3 <= n <= 5:
            return False
        if (x, y) not in live and n == 2:
            return False
    return True


@pytest.mark.parametrize("rows, cols", [(240, 360), (180, 280), (160, 240)])
@pytest.mark.parametrize("margin", [3, 4, 5, 6])
def test_frame_is_still_life(rows, cols, margin):
    """
    The whole frame never changes under the Star Wars rule.
    """
    cells = set().union(*frame_cells(rows, cols, margin).values())
    assert _is_still_life(cells, rows, cols)


def test_frame_sides_do_not_overlap():
    """
    Every frame cell belongs to exactly one side, so each has one owner.
    """
    sides = frame_cells(240, 360, 4)
    assert len(set().union(*sides.values())) == sum(len(cells) for cells in sides.values())


def test_pictureframe_realization():
    """
    The map realizes for star-ix at the default size, gives both teams live cells in
    range, and is the same for the same seed.
    """
    m = maps.get_map_realization("star-ix", "pictureframe", seed=7)
    assert (m["rows"], m["columns"]) == (240, 360)
    for key in ("initialConditions1", "initialConditions2"):
        cells = [(int(y), x) for row in json.loads(m[key]) for y, xs in row.items() for x in xs]
        assert cells
        assert all(0 <= y < 240 and 0 <= x < 360 for y, x in cells)
    again = maps.get_map_realization("star-ix", "pictureframe", seed=7)
    assert m["initialConditions1"] == again["initialConditions1"]
    assert m["initialConditions2"] == again["initialConditions2"]


def test_pictureframe_is_new_in_star_ix():
    """
    pictureframe is available for star-ix and not for star-viii.
    """
    assert "pictureframe" in maps.get_all_map_patterns("star-ix")
    assert "pictureframe" not in maps.get_all_map_patterns("star-viii")


def test_pictureframe_board_too_small():
    """
    A board with no room for the frame raises GollyXMapsError.
    """
    with pytest.raises(GollyXMapsError):
        pictureframe(20, 20, seed=1)
