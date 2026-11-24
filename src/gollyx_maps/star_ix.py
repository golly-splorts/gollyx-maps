import json
import os
import random
from .error import GollyXMapsError
from .geom import hflip_pattern, vflip_pattern
from .patterns import get_grid_empty, get_pattern
from .utils import pattern2url_chars

# The plus sign ("star") is a still life under B2/S345/C4
PLUS = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

# Distance between plus centers along a frame side
FRAME_PITCH = 5

# Rows between a horizontal line and the first or last plus of a side
SIDE_GAP = 6

# Free polyominoes of 7 to 10 cells that take off when played alone under B2/S345/C4,
# written by scripts/make_star_ix_polyominoes.py
POLYOMINO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "star_ix_polyominoes.json")

# Stamps that make up a picture; each one sets off a long reaction when left alone
PORTRAIT_STAMPS = [
    "simpleunstablestar",
    "squarevariation3",
    "sprinkleship",
    "drifter",
    "escapingsatellites",
    "spaceship2platform",
    "arrow",
    "squarepair",
    "doublestar",
    "squarevariationpair",
]


def get_star_ix_new_pattern_function_map():
    """Only the patterns NEW in star-ix (not inherited from star or star-vii)."""
    return {
        "pictureframe": pictureframe,
        "poly1": poly1,
        "poly2": poly2,
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


def _place_stamp(grid, name, cx, cy):
    """
    Draw a stamp, flipped at random, centered at (cx, cy).

    Args:
        grid (list of list of str): board to draw on, changed in place.
        name (str): stamp pattern name.
        cx (int): column of the stamp's center.
        cy (int): row of the stamp's center.
    """
    stamp = get_pattern(name)
    if random.random() < 0.5:
        stamp = hflip_pattern(stamp)
    if random.random() < 0.5:
        stamp = vflip_pattern(stamp)
    top, left = cy - len(stamp) // 2, cx - len(stamp[0]) // 2
    for j, line in enumerate(stamp):
        for i, char in enumerate(line):
            if char != ".":
                grid[top + j][left + i] = char


def pictureframe(rows, cols, seed=None):
    """
    A picture frame around a portrait: two or three of the same stamp per team, the
    teams facing each other across the middle of the board.

    The frame is a still life. Team 1 owns one horizontal and one vertical side, team 2
    the other two. Both teams get the same stamp, nudged and flipped independently so
    the two halves are never mirror images.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).
    """
    if seed is not None:
        random.seed(seed)

    frame = frame_cells(rows, cols, random.randint(3, 6))

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

    jitter = 5
    left_team = random.choice([1, 2])
    stamp = random.choice(PORTRAIT_STAMPS)
    nstamps = random.randint(2, 3)
    for k in range(nstamps):
        y = rows * (k + 1) // (nstamps + 1)
        for team, x in ((left_team, cols // 3), (3 - left_team, 2 * cols // 3)):
            _place_stamp(grids[team], stamp, x + random.randint(-jitter, jitter), y + random.randint(-jitter, jitter))

    s1, b1, c1 = pattern2url_chars(grids[1])
    s2, b2, c2 = pattern2url_chars(grids[2])
    return s1, b1, c1, s2, b2, c2


def load_polyominoes():
    """
    Returns:
        list of list of str: every polyomino, as rows of 'o' and '.'.
    """
    with open(POLYOMINO_FILE) as f:
        return [text.split("/") for text in json.load(f)]


def _polyomino_grid(rows, cols, seed=None, n=4, ownership="checker", pitch=None):
    """
    An n x n grid of polyominoes, half per team. Both teams get the same shapes, shuffled
    and turned independently, so they start with equal cells but never as mirror images.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).
        n (int): shapes along each side of the grid (even).
        ownership (str): "checker" alternates teams, "halves" gives each team a side.
        pitch (int): cells between shape centers, or None to spread across the board.

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).

    Raises:
        GollyXMapsError: if the grid does not fit on the board.
    """
    if seed is not None:
        random.seed(seed)

    jitter = 3
    xpitch, ypitch = (pitch, pitch) if pitch else (cols // (n + 1), rows // (n + 1))
    # The largest shape is 10 cells long
    if min(xpitch, ypitch) < 10 + 2 * jitter + 1 or n * xpitch > cols or n * ypitch > rows:
        raise GollyXMapsError(f"Board {rows}x{cols} is too small for a {n}x{n} polyomino grid")

    half = n * n // 2
    picks = random.sample(load_polyominoes(), half)
    queues = {1: random.sample(picks, half), 2: random.sample(picks, half)}
    swap = random.random() < 0.5

    grids = {1: get_grid_empty(rows, cols, flat=False), 2: get_grid_empty(rows, cols, flat=False)}
    for i in range(n):
        for j in range(n):
            first = (i + j) % 2 == 0 if ownership == "checker" else i < n // 2
            team = 1 if first != swap else 2
            shape = queues[team].pop()
            for _ in range(random.randrange(4)):
                shape = ["".join(row) for row in zip(*shape[::-1])]
            if random.random() < 0.5:
                shape = [row[::-1] for row in shape]
            cx = round(cols / 2 + (i - (n - 1) / 2) * xpitch) + random.randint(-jitter, jitter)
            cy = round(rows / 2 + (j - (n - 1) / 2) * ypitch) + random.randint(-jitter, jitter)
            top, left = cy - len(shape) // 2, cx - len(shape[0]) // 2
            for dy, row in enumerate(shape):
                for dx, char in enumerate(row):
                    if char == "o":
                        grids[team][top + dy][left + dx] = "o"

    s1, b1, c1 = pattern2url_chars(grids[1])
    s2, b2, c2 = pattern2url_chars(grids[2])
    return s1, b1, c1, s2, b2, c2


def poly1(rows, cols, seed=None):
    """
    A 4x4 checkerboard of polyominoes, 40 cells apart.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).
    """
    return _polyomino_grid(rows, cols, seed=seed, ownership="checker", pitch=40)


def poly2(rows, cols, seed=None):
    """
    A 4x4 grid of polyominoes spread across the board, one team on each side.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).
    """
    return _polyomino_grid(rows, cols, seed=seed, ownership="halves")
