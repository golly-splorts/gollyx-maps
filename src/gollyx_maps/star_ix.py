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

# The strongest shapes of each behavior, chosen from the polyominoes above
POLYOMINO_FAMILY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "star_ix_polyomino_families.json")

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
        "poly3": poly3,
        "poly3a": poly3a,
        "poly3b": poly3b,
        "poly3c": poly3c,
        "poly4": poly4,
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


def load_polyomino_families():
    """
    Returns:
        dict: family name (gliders, beam, sprayer, swarm, burst, scaffold) to a list of
            polyominoes that behave that way alone, each as rows of 'o' and '.'.
    """
    with open(POLYOMINO_FAMILY_FILE) as f:
        return {name: [text.split("/") for text in texts] for name, texts in json.load(f).items()}


def _slot_jitter(size):
    """
    Args:
        size (int): width or height of the slot a polyomino is placed in.

    Returns:
        int: how far the polyomino may move from the slot's center, staying inside it.

    Raises:
        GollyXMapsError: if the slot is too small; the largest polyomino is 10 cells long.
    """
    if size < 14:
        raise GollyXMapsError("Board is too small for a polyomino map")
    return int(0.6 * (size - 12) / 2)


def _draw_polyomino(grid, shape, cx, cy):
    """
    Draw a polyomino, turned and flipped at random, centered at (cx, cy).

    Args:
        grid (list of list of str): board to draw on, changed in place.
        shape (list of str): polyomino, as rows of 'o' and '.'.
        cx (int): column of the center.
        cy (int): row of the center.
    """
    for _ in range(random.randrange(4)):
        shape = ["".join(row) for row in zip(*shape[::-1])]
    if random.random() < 0.5:
        shape = [row[::-1] for row in shape]
    top, left = cy - len(shape) // 2, cx - len(shape[0]) // 2
    for dy, row in enumerate(shape):
        for dx, char in enumerate(row):
            if char == "o":
                grid[(top + dy) % len(grid)][(left + dx) % len(grid[0])] = "o"


def _finish(grids):
    """
    Args:
        grids (dict): board of each team, keyed 1 and 2.

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).
    """
    s1, b1, c1 = pattern2url_chars(grids[1])
    s2, b2, c2 = pattern2url_chars(grids[2])
    return s1, b1, c1, s2, b2, c2


def _polyomino_grid(rows, cols, seed, ypitch, shuffle_teams):
    """
    A loose 4x4 grid of polyominoes across the full width of the board. Both teams get
    the same eight shapes, shuffled and turned independently.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).
        ypitch (int): rows between shape centers.
        shuffle_teams (bool): mix the teams at random, or give each team one side.

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).

    Raises:
        GollyXMapsError: if the grid does not fit on the board.
    """
    if seed is not None:
        random.seed(seed)
    n = 4
    xpitch = cols // n
    xjitter, yjitter = _slot_jitter(xpitch), _slot_jitter(ypitch)
    if n * ypitch > rows:
        raise GollyXMapsError(f"Board {rows}x{cols} is too small for a polyomino grid")

    half = n * n // 2
    picks = random.sample(load_polyominoes(), half)
    queues = {1: random.sample(picks, half), 2: random.sample(picks, half)}
    left, right = random.sample([1, 2], 2)
    teams = [left] * half + [right] * half
    if shuffle_teams:
        random.shuffle(teams)

    grids = {1: get_grid_empty(rows, cols, flat=False), 2: get_grid_empty(rows, cols, flat=False)}
    for k, team in enumerate(teams):
        i, j = divmod(k, n)
        cx = round((i + 0.5) * xpitch) + random.randint(-xjitter, xjitter)
        cy = round(rows / 2 + (j - (n - 1) / 2) * ypitch) + random.randint(-yjitter, yjitter)
        _draw_polyomino(grids[team], queues[team].pop(), cx, cy)
    return _finish(grids)


def poly1(rows, cols, seed=None):
    """
    A loose 4x4 grid of polyominoes, the teams mixed at random.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).
    """
    return _polyomino_grid(rows, cols, seed, ypitch=rows // 6, shuffle_teams=True)


def poly2(rows, cols, seed=None):
    """
    A loose 4x4 grid of polyominoes, one team on each side.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).
    """
    return _polyomino_grid(rows, cols, seed, ypitch=rows // 5, shuffle_teams=False)


def _polyomino_quadrants(rows, cols, seed, shapes1, shapes2):
    """
    Polyominoes in quadrants: each quadrant holds 1, 4 (2x2) or 9 (3x3) of them.

    The quadrants are paired at random. Both quadrants of a pair hold the same shapes in
    their own random order, with the teams swapped, so the teams start with equal cells.
    The shapes alternate between the two lists; one pair starts with the first list and
    the other pair with the second.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).
        shapes1 (list of list of str): polyominoes to choose from.
        shapes2 (list of list of str): polyominoes to choose from.

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).

    Raises:
        GollyXMapsError: if a 3x3 quadrant does not fit on the board.
    """
    if seed is not None:
        random.seed(seed)
    qrows, qcols = rows // 2, cols // 2
    jitters = {n: (_slot_jitter(qcols // n), _slot_jitter(qrows // n)) for n in (1, 2, 3)}

    grids = {1: get_grid_empty(rows, cols, flat=False), 2: get_grid_empty(rows, cols, flat=False)}
    quadrants = [(0, 0), (0, qrows), (qcols, 0), (qcols, qrows)]
    random.shuffle(quadrants)
    for first, pair in enumerate((quadrants[:2], quadrants[2:])):
        n = random.choice([1, 2, 3])
        picks = [(random.choice((shapes1, shapes2)[(first + i) % 2]), random.choice([1, 2])) for i in range(n * n)]
        for k, (qx, qy) in enumerate(pair):
            random.shuffle(picks)
            for slot, (shape, team) in enumerate(picks):
                i, j = divmod(slot, n)
                xjitter, yjitter = jitters[n]
                cx = round(qx + (i + 0.5) * qcols / n) + random.randint(-xjitter, xjitter)
                cy = round(qy + (j + 0.5) * qrows / n) + random.randint(-yjitter, yjitter)
                _draw_polyomino(grids[team if k == 0 else 3 - team], shape, cx, cy)
    return _finish(grids)


def poly3(rows, cols, seed=None):
    """
    Polyominoes in quadrants, drawn from every shape.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).

    Raises:
        GollyXMapsError: if a 3x3 quadrant does not fit on the board.
    """
    shapes = load_polyominoes()
    return _polyomino_quadrants(rows, cols, seed, shapes, shapes)


def poly3a(rows, cols, seed=None):
    """
    Polyominoes in quadrants, beam and scaffold shapes: growing lines against solid spines.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).

    Raises:
        GollyXMapsError: if a 3x3 quadrant does not fit on the board.
    """
    families = load_polyomino_families()
    return _polyomino_quadrants(rows, cols, seed, families["beam"], families["scaffold"])


def poly3b(rows, cols, seed=None):
    """
    Polyominoes in quadrants, swarm and scaffold shapes: ship swarms against solid spines.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).

    Raises:
        GollyXMapsError: if a 3x3 quadrant does not fit on the board.
    """
    families = load_polyomino_families()
    return _polyomino_quadrants(rows, cols, seed, families["swarm"], families["scaffold"])


def poly3c(rows, cols, seed=None):
    """
    Polyominoes in quadrants, swarm and burst shapes: small swarms and full explosions of ships.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).

    Raises:
        GollyXMapsError: if a 3x3 quadrant does not fit on the board.
    """
    families = load_polyomino_families()
    return _polyomino_quadrants(rows, cols, seed, families["swarm"], families["burst"])


def poly4(rows, cols, seed=None):
    """
    A staggered row of one polyomino across the board, the teams mixed at random.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).

    Raises:
        GollyXMapsError: if the longest row does not fit on the board.
    """
    if seed is not None:
        random.seed(seed)
    counts = [8, 10, 12, 14, 16]
    _slot_jitter(cols // counts[-1])
    count = random.choice(counts)
    xpitch = cols // count
    xjitter = _slot_jitter(xpitch)
    stagger = random.randint(rows // 24, rows // 8)
    yjitter = rows // 12

    shape = random.choice(load_polyominoes())
    teams = [1, 2] * (count // 2)
    random.shuffle(teams)
    grids = {1: get_grid_empty(rows, cols, flat=False), 2: get_grid_empty(rows, cols, flat=False)}
    for k, team in enumerate(teams):
        cx = round((k + 0.5) * cols / count) + random.randint(-xjitter, xjitter)
        cy = rows // 2 + (stagger if k % 2 else -stagger) + random.randint(-yjitter, yjitter)
        _draw_polyomino(grids[team], shape, cx, cy)
    return _finish(grids)
