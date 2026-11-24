import random
from .error import GollyXMapsError
from .patterns import get_grid_empty
from .utils import pattern2url_chars

# The plus sign ("star") is a still life under B2/S345/C4
PLUS = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

# Distance between plus centers along a frame side; 5 leaves the sides, corners
# and nested frames all still lifes
FRAME_PITCH = 5


def get_star_ix_new_pattern_function_map():
    """Only the patterns NEW in star-ix (not inherited from star or star-vii)."""
    return {
        "pictureframe": pictureframe,
    }


def frame_centers(rows, cols, margin, pitch=FRAME_PITCH):
    """
    Plus-sign centers of a rectangular frame, with shared corners.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        margin (int): distance from the board edge to the frame's top and left centers.
        pitch (int): distance between neighboring centers along each side.

    Returns:
        dict: "top", "bottom", "left" and "right" lists of (x, y) centers. Corners
            belong to top and bottom; left and right hold the centers between them.
    """
    nx = (cols - 1 - 2 * margin) // pitch
    ny = (rows - 1 - 2 * margin) // pitch
    if nx < 2 or ny < 2:
        raise GollyXMapsError(f"Board {rows}x{cols} is too small for a frame with margin {margin}")
    xs = [margin + pitch * i for i in range(nx + 1)]
    ys = [margin + pitch * i for i in range(ny + 1)]
    return {
        "top": [(x, ys[0]) for x in xs],
        "bottom": [(x, ys[-1]) for x in xs],
        "left": [(xs[0], y) for y in ys[1:-1]],
        "right": [(xs[-1], y) for y in ys[1:-1]],
    }


def pictureframe(rows, cols, seed=None):
    """
    A picture frame of plus signs around a random two-color soup.

    Two nested frames of still lifes sit just inside the board edges, so spaceships
    that leave the picture meet a wall before they wrap around the board. Team 1 owns
    two sides of the frame and team 2 the other two; the picture is an even mix of both.

    Args:
        rows (int): board rows.
        cols (int): board columns.
        seed (int): random seed (optional).

    Returns:
        tuple: s1, b1, c1, s2, b2, c2 listlife strings (live and dead-wait cells per team).
    """
    if seed is not None:
        random.seed(seed)

    # Distance from the board edge to the outer frame, and between the two frames
    margin = random.randint(3, 6)
    inner_margin = margin + FRAME_PITCH

    # Which sides each team owns: horizontal and vertical sides are assigned separately
    hswap = random.random() < 0.5
    vswap = random.random() < 0.5
    side_team = {
        "top": 2 if hswap else 1,
        "bottom": 1 if hswap else 2,
        "left": 2 if vswap else 1,
        "right": 1 if vswap else 2,
    }

    grids = {1: get_grid_empty(rows, cols, flat=False), 2: get_grid_empty(rows, cols, flat=False)}
    for m in (margin, inner_margin):
        for side, centers in frame_centers(rows, cols, m).items():
            for cx, cy in centers:
                for dx, dy in PLUS:
                    grids[side_team[side]][(cy + dy) % rows][(cx + dx) % cols] = "o"

    # Picture: a random soup inside the inner frame, with clear space next to it
    clearance = inner_margin + random.randint(8, 20)
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
