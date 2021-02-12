import random
import os
from glob import glob
from .geom import hflip_pattern, vflip_pattern, rot_pattern


def get_patterns():
    patternfiles = glob(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "patterns", "*.txt")
    )
    # trim extension
    patternfiles = [os.path.basename(os.path.splitext(p)[0]) for p in patternfiles]
    return patternfiles


def get_pattern(pattern_name, hflip=False, vflip=False, rotdeg=0):
    """
    For a given pattern, return the .o diagram
    as a list of strings, one string = one row
    """
    fname = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "patterns", pattern_name + ".txt"
    )
    if os.path.exists(fname):
        with open(fname, "r") as f:
            pattern = f.readlines()
        pattern = [r.strip() for r in pattern]
        if hflip:
            pattern = hflip_pattern(pattern)
        if vflip:
            pattern = vflip_pattern(pattern)
        if rotdeg:
            pattern = rot_pattern(pattern, rotdeg)
        return pattern
    else:
        raise Exception(f"Error: pattern {fname} does not exist!")


def get_pattern_size(pattern_name, **kwargs):
    """
    Returns: (nrows, ncols)
    """
    pattern = get_pattern(pattern_name, **kwargs)
    return (len(pattern), len(pattern[0]))


def get_pattern_livecount(pattern_name, **kwargs):
    """
    Returns: count of live cells in the given pattern
    """
    pattern = get_pattern(pattern_name, **kwargs)
    count = 0
    for row in pattern:
        for j in row:
            if j == "o":
                count += 1
    return count


def get_grid_empty(rows, columns, flat=True):
    if columns < 1 or rows < 1:
        err = f"Error: invalid number of rows {rows} or columns {columns}, must be positive integers > 0"
        raise Exception(err)

    blank_row = ["."] * columns
    blank_grid = [blank_row[:] for r in range(rows)]

    if flat:
        blank_grid = ["".join(gridrow) for gridrow in blank_grid]

    return blank_grid


def get_grid_pattern(
    pattern_name,
    rows,
    columns,
    xoffset=0,
    yoffset=0,
    hflip=False,
    vflip=False,
    rotdeg=0,
    check_overflow=True,
):
    """
    Get the pattern corresponding to pattern_name,
    and place it on a grid of size (rows x columns)
    at the given offset.
    If check_overflow is False, the pattern added may be
    partially or fully outside of the specified grid.
    """
    # TODO: add check of rows/columns, and whether this pattern
    # will actually fit on the specified grid size.
    if columns < 1 or rows < 1:
        err = f"Error: invalid number of rows {rows} or columns {columns}, must be positive integers > 0"
        raise Exception(err)

    # convert list of strings to list of lists (for convenience)
    ogpattern = get_pattern(pattern_name, hflip=hflip, vflip=vflip, rotdeg=rotdeg)
    ogpattern = [list(j) for j in ogpattern]
    blank_row = ["."] * columns
    newpattern = [blank_row[:] for r in range(rows)]
    (pattern_h, pattern_w) = (len(ogpattern), len(ogpattern[0]))

    # given offset is offset for the center of the pattern,
    # so do some algebra to determine where we should start
    xstart = xoffset - pattern_w // 2
    xend = xstart + pattern_w
    ystart = yoffset - pattern_h // 2
    yend = ystart + pattern_h

    # Check size of pattern
    if check_overflow:
        if xstart < 0:
            raise Exception(
                f"Error: specified offset {xoffset} is too small, need at least {pattern_w//2}"
            )
        if xend >= columns:
            raise Exception(
                f"Error: specified number of columns {columns} was too small, need at least {xend+1}"
            )
        if ystart < 0:
            raise Exception(
                f"Error: specified offset {yoffset} is too small, need at least {pattern_h//2}"
            )
        if yend >= rows:
            raise Exception(
                f"Error: specified number of rows {rows} was too small, need at least {yend+1}"
            )

    # iterate through the pattern and copy over the cells that are in the final grid
    for iy, y in enumerate(range(ystart, yend)):
        if y > 0 and y < len(newpattern):
            for ix, x in enumerate(range(xstart, xend)):
                if x > 0 and x < len(newpattern[iy]):
                    newpattern[y][x] = ogpattern[iy][ix]

    newpattern = ["".join(j) for j in newpattern]
    return newpattern


def pattern_union(patterns):
    for i in range(1, len(patterns)):
        axis0different = len(patterns[i - 1]) != len(patterns[i])
        axis1different = len(patterns[i - 1][0]) != len(patterns[i][0])
        if axis0different or axis1different:
            err = "Error: cannot perform pattern_union on patterns of dissimilar size"
            err += "\n"
            for i in range(patterns):
                err += "Pattern {i+1}: rows = {len(patterns[i])}, cols = {len(patterns[i][0]}\n"
            raise Exception(err)

    # Turn all patterns into lists of lists (for convenience)
    rows = len(patterns[0])
    cols = len(patterns[0][0])
    newpatterns = []
    for pattern in patterns:
        newpatterns.append([list(j) for j in pattern])
    patterns = newpatterns
    blank_row = ["."] * cols
    newpattern = [blank_row[:] for r in range(rows)]
    for iy in range(rows):
        for ix in range(cols):
            alive = False
            for ip, pattern in enumerate(patterns):
                if pattern[iy][ix] == "o":
                    alive = True
                    break
            if alive:
                newpattern[iy][ix] = "o"

    newpattern = ["".join(j) for j in newpattern]
    return newpattern


def segment_pattern(
    rows, cols, seed=None, colormode=None, jitterx=0, jittery=0, nhseg=0, nvseg=0
):
    """
    Return a two-color pattern consisting of nhseg horizontal segments and nvseg vertical segments.

    In classic color mode, each segment piece is assigned to a single team.
    In random color mode, each segment cell is assigned random teams.
    In random broken mode, each segment cell is assigned random teams or is not alive.
    """
    valid_colormodes = ["classic", "classicbroken", "random", "randombroken"]
    if colormode not in valid_colormodes:
        raise Exception(
            f"Error: invalid color mode {colormode} passed to _segment(), must be in {', '.join(valid_colormodes)}"
        )
    if nhseg == 0 and nvseg == 0:
        raise Exception(
            "Error: invalid number of segments (0 horizontal and 0 vertical) passed to _segment()"
        )

    # Get the snap-to-grid centers
    hsegcenters = [(iy + 1) * rows // (nhseg + 1) - 1 for iy in range(nhseg)]
    vsegcenters = [(ix + 1) * cols // (nvseg + 1) - 1 for ix in range(nvseg)]

    # Add jitter, and bookend with 0 and nrows/ncols
    hseglocs = (
        [-1] + [k + random.randint(-jittery, jittery) for k in hsegcenters] + [rows]
    )
    vseglocs = (
        [-1] + [k + random.randint(-jitterx, jitterx) for k in vsegcenters] + [cols]
    )

    loclenlist = []

    # Construct vertical segments first:
    # ----------------
    # Horizontal segment locations give us the start/end coordinates for vertical segments
    # Skip the first loc - it's 1 past the edge so the segments start at 0
    for ih in range(1, len(hseglocs)):
        yend = hseglocs[ih] - 1
        ystart = hseglocs[ih - 1] + 1
        mag = yend - ystart + 1
        # Skip the first vseg loc - it's 1 past the edge
        # Skip the last vseg loc - it's also 1 past the edge
        for iv in range(1, len(vseglocs) - 1):
            x = vseglocs[iv]
            loclenlist.append((ystart, yend, x, x, mag))

    # Construct horizontal segments:
    # ----------------
    for iv in range(1, len(vseglocs)):
        xend = vseglocs[iv] - 1
        xstart = vseglocs[iv - 1] + 1
        mag = xend - xstart + 1
        for ih in range(1, len(hseglocs) - 1):
            y = hseglocs[ih]
            loclenlist.append((y, y, xstart, xend, mag))

    # These store the the .o diagrams (flat=False means these are lists of lists of one char)
    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    # Color mode:
    # ------------------------
    # We have a list of segments, coordinates and lengths,
    # now the way we populate the map depends on the color mode.

    if colormode == "classic" or colormode == "classicbroken":

        # Classic/classic broken color mode:
        # Each segment is a single solid color,
        # use serpentine pattern to assign colors.
        # If broken, use 0s to represent dead cells.
        serpentine_pattern = [1, 2, 2, 1]

        from operator import itemgetter

        random.shuffle(loclenlist)
        loclenlist.sort(key=itemgetter(4), reverse=True)

        for i, (starty, endy, startx, endx, mag) in enumerate(loclenlist):

            serpix = i % len(serpentine_pattern)
            serpteam = serpentine_pattern[serpix]

            if colormode == "classic":
                team_assignments = [
                    serpteam,
                ] * mag
            elif colormode == "classicbroken":
                magon = 24 * mag // 25
                rem = mag - magon
                team_assignments = [serpteam,] * magon + [ 0, ] * rem # noqa
                random.shuffle(team_assignments)

            ta_ix = 0
            for y in range(starty, endy + 1):
                for x in range(startx, endx + 1):
                    if team_assignments[ta_ix] == 1:
                        team1_pattern[y][x] = "o"
                    elif team_assignments[ta_ix] == 2:
                        team2_pattern[y][x] = "o"
                    ta_ix += 1

    elif colormode == "random" or colormode == "randombroken":

        # Random/random broken color mode:
        # For each segment of length N,
        # create an array of N/2 zeros and N/2 ones,
        # shuffle it, use it to assign colors.
        # If broken, include 0s to represent dead cells
        for i, (starty, endy, startx, endx, mag) in enumerate(loclenlist):
            if colormode == "random":
                magh = mag // 2
                magoh = mag - mag // 2
                team_assignments = [1,] * magh + [ 2, ] * magoh # noqa
                random.shuffle(team_assignments)
            elif colormode == "randombroken":
                magh = 12 * mag // 25
                magoh = 12 * mag // 25
                rem = mag - magh - magoh
                team_assignments = ( [ 1, ] * magh + [ 2, ] * magoh + [ 0, ] * rem) # noqa
                random.shuffle(team_assignments)

            ta_ix = 0
            for y in range(starty, endy + 1):
                if y >= rows:
                    continue
                for x in range(startx, endx + 1):
                    if x >= cols:
                        continue
                    if team_assignments[ta_ix] == 1:
                        team1_pattern[y][x] = "o"
                    elif team_assignments[ta_ix] == 2:
                        team2_pattern[y][x] = "o"
                    ta_ix += 1

    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    return team1_pattern, team2_pattern
