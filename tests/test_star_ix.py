import json
import pytest
from gollyx_maps import maps
from gollyx_maps.error import GollyXMapsError
from gollyx_maps.patterns import get_pattern
from gollyx_maps.star_ix import PORTRAIT_STAMPS, frame_cells, load_polyominoes, pictureframe, poly1, poly2


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


@pytest.mark.parametrize("seed", range(30))
def test_pictureframe_is_frame_plus_equal_stamps(seed):
    """
    Every map is the frame plus a few stamps: the teams start with the same number of
    cells, no cell belongs to both, and few cells lie inside the frame.
    """
    s1, b1, c1, s2, b2, c2 = pictureframe(240, 360, seed=seed)
    cells = [{(x, int(y)) for row in json.loads(s) for y, xs in row.items() for x in xs} for s in (s1, s2)]
    assert len(cells[0]) == len(cells[1])
    assert not cells[0] & cells[1]
    frames = [set().union(*frame_cells(240, 360, m).values()) for m in range(3, 7)]
    frame = next(f for f in frames if f <= cells[0] | cells[1])
    assert 0 < len((cells[0] | cells[1]) - frame) <= 6 * 40


def test_portrait_stamps_exist():
    """
    Every stamp a portrait can use is in the pattern library.
    """
    for name in PORTRAIT_STAMPS:
        assert get_pattern(name)


def test_polyominoes_are_connected_and_sized():
    """
    Every polyomino in the library has 7 to 10 edge-connected cells, with no duplicates.
    """
    shapes = load_polyominoes()
    assert len({tuple(s) for s in shapes}) == len(shapes)
    for shape in shapes:
        cells = {(x, y) for y, row in enumerate(shape) for x, char in enumerate(row) if char == "o"}
        assert 7 <= len(cells) <= 10
        seen, todo = set(), [next(iter(cells))]
        while todo:
            x, y = todo.pop()
            if (x, y) in cells and (x, y) not in seen:
                seen.add((x, y))
                todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        assert seen == cells


@pytest.mark.parametrize("func", [poly1, poly2])
@pytest.mark.parametrize("seed", range(20))
def test_poly_maps_are_even(func, seed):
    """
    The teams start with equal cells in range, share none, and the seed fixes the map.
    """
    result = func(240, 360, seed=seed)
    cells = [{(x, int(y)) for row in json.loads(s) for y, xs in row.items() for x in xs} for s in (result[0], result[3])]
    assert len(cells[0]) == len(cells[1]) >= 8 * 7
    assert not cells[0] & cells[1]
    assert all(0 <= x < 360 and 0 <= y < 240 for x, y in cells[0] | cells[1])
    assert func(240, 360, seed=seed) == result


@pytest.mark.parametrize("func", [poly1, poly2])
def test_poly_maps_board_too_small(func):
    """
    A board with no room for the grid raises GollyXMapsError.
    """
    with pytest.raises(GollyXMapsError):
        func(60, 60, seed=1)
