import random
from .error import GollyXMapsError
from .patterns import get_grid_empty
from .utils import pattern2url_chars

# The plus sign ("star") is a still life under B2/S345/C4
PLUS = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

# Distance between plus centers along a frame side
FRAME_PITCH = 5

# Rows between a horizontal line and the first or last plus of a side
SIDE_GAP = 6


def get_star_ix_new_pattern_function_map():
    """Only the patterns NEW in star-ix (not inherited from star or star-vii)."""
    return {
        "pictureframe": pictureframe,
    }


def frame_cells(rows, cols, margin):
    """
    Cells of a picture frame that is a still life under B2/S345/C4.

    The top and bottom are 2-thick lines across the full width of the board; they wrap
    around it, so they have no ends to burn. The left and right sides are columns of
    plus signs, kept clear of the lines.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        margin (int): distance from the board edge to the frame.

    Returns:
        dict: "top", "bottom", "left" and "right" sets of (x, y) cells.

    Raises:
        GollyXMapsError: if the board has no room for the frame.
    """
    first, last = margin + 1 + SIDE_GAP, rows - 1 - margin - 1 - SIDE_GAP
    if last - first < 4 * FRAME_PITCH or cols < 2 * margin + 40:
        raise GollyXMapsError(f"Board {rows}x{cols} is too small for a frame with margin {margin}")
    lines = {"top": (margin, margin + 1), "bottom": (rows - 2 - margin, rows - 1 - margin)}
    cells = {side: {(x, y) for x in range(cols) for y in ys} for side, ys in lines.items()}
    ncenters = (last - first) // FRAME_PITCH
    for side, cx in (("left", margin + 1), ("right", cols - 2 - margin)):
        cells[side] = {(cx + dx, first + FRAME_PITCH * i + dy) for i in range(ncenters + 1) for dx, dy in PLUS}
    return cells


def pictureframe(rows, cols, seed=None):
    """
    A picture frame around a random two-color soup.

    The frame is a still life, so spaceships that leave the picture meet a wall before
    they wrap around the board. Team 1 owns one horizontal and one vertical side, team 2
    the other two; the picture is an even mix of both.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).
    """
    if seed is not None:
        random.seed(seed)

    margin = random.randint(3, 6)
    frame = frame_cells(rows, cols, margin)

    hswap = random.random() < 0.5
    vswap = random.random() < 0.5
    side_team = {
        "top": 2 if hswap else 1,
        "bottom": 1 if hswap else 2,
        "left": 2 if vswap else 1,
        "right": 1 if vswap else 2,
    }

    grids = {1: get_grid_empty(rows, cols, flat=False), 2: get_grid_empty(rows, cols, flat=False)}
    for side, cells in frame.items():
        for x, y in cells:
            grids[side_team[side]][y][x] = "o"

    # Picture: a random soup inside the frame, with clear space next to it
    clearance = margin + random.randint(12, 20)
    if rows - 2 * clearance < 10 or cols - 2 * clearance < 10:
        raise GollyXMapsError(f"Board {rows}x{cols} is too small for a pictureframe map")
    density = random.randint(5, 20) / 100
    cells = [(x, y) for y in range(clearance, rows - clearance) for x in range(clearance, cols - clearance)]
    picture = random.sample(cells, int(density * len(cells)))
    half = len(picture) // 2
    for team, pts in ((1, picture[:half]), (2, picture[half:])):
        for x, y in pts:
            grids[team][y][x] = "o"

    s1, b1, c1 = pattern2url_chars(grids[1])
    s2, b2, c2 = pattern2url_chars(grids[2])
    return s1, b1, c1, s2, b2, c2
