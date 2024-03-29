import math
from collections.abc import Iterable
from operator import itemgetter
import random
import os
from glob import glob
from .geom import hflip_pattern, vflip_pattern, rot_pattern
from .error import GollyXPatternNotFoundError, GollyXPatternsError


def get_pattern_filepaths():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "*_patterns", "*.txt")
    patternfilepaths = glob(p)
    return patternfilepaths


def get_patterns():
    patternpaths = get_pattern_filepaths()
    patternfiles = [os.path.basename(os.path.splitext(p)[0]) for p in patternpaths]
    return patternfiles


def get_pattern(pattern_name, hflip=False, vflip=False, rotdeg=0):
    """
    For a given pattern, return the .o diagram
    as a list of strings, one string = one row
    """
    patternpaths = get_pattern_filepaths()
    fpath = None
    for patternpath in patternpaths:
        if patternpath.endswith("/" + pattern_name+".txt"):
            fpath = patternpath

    if fpath is None or not os.path.exists(fpath):
        raise GollyXPatternNotFoundError(f"Error: pattern {pattern_name} does not exist!")

    with open(fpath, "r") as f:
        pattern = f.readlines()

    pattern = [r.strip() for r in pattern]
    if hflip:
        pattern = hflip_pattern(pattern)
    if vflip:
        pattern = vflip_pattern(pattern)
    if rotdeg:
        pattern = rot_pattern(pattern, rotdeg)

    return pattern


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
        raise GollyXPatternsError(err)

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
        raise GollyXPatternsError(err)

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
            raise GollyXPatternsError(
                f"Error: specified offset {xoffset} is too small, need at least {pattern_w//2}"
            )
        if xend >= columns:
            raise GollyXPatternsError(
                f"Error: specified number of columns {columns} was too small, need at least {xend+1}"
            )
        if ystart < 0:
            raise GollyXPatternsError(
                f"Error: specified offset {yoffset} is too small, need at least {pattern_h//2}"
            )
        if yend >= rows:
            raise GollyXPatternsError(
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


def pattern_union(patterns, flatten=True):
    for i in range(1, len(patterns)):
        axis0different = len(patterns[i - 1]) != len(patterns[i])
        axis1different = len(patterns[i - 1][0]) != len(patterns[i][0])
        if axis0different or axis1different:
            err = "Error: pattern_union() received patterns of dissimilar size"
            err += "\n"
            for i in range(1, len(patterns)):
                err += f"Pattern {i+1}: rows = {len(patterns[i])}, cols = {len(patterns[i][0])}"
                err += "\n"
            raise GollyXPatternsError(err)

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

    if flatten:
        newpattern = ["".join(j) for j in newpattern]
    return newpattern


def segment_pattern(
    rows,
    cols,
    seed=None,
    colormode=None,
    jitterx=0,
    jittery=0,
    nhseg=0,
    nvseg=0,
    gap_probability=None,
):
    """
    Return a two-color pattern consisting of nhseg horizontal segments and nvseg vertical segments.

    In classic color mode, each segment piece is assigned to a single team.
    In classic broken mode, each segment piece is assigned to a single team, with some dead cells.
    In random color mode, each segment cell is assigned random teams.
    In random broken mode, each segment cell is assigned random teams, with some dead cells.

    gap probability dictates how often gaps occur. If there are too many gaps, maps get boring!
    """
    valid_colormodes = ["classic", "classicbroken", "random", "randombroken"]
    if colormode not in valid_colormodes:
        raise GollyXPatternsError(
            f"Error: invalid color mode {colormode} passed to _segment(), must be in {', '.join(valid_colormodes)}"
        )
    if nhseg == 0 and nvseg == 0:
        raise GollyXPatternsError(
            "Error: invalid number of segments (0 horizontal and 0 vertical) passed to _segment()"
        )
    if gap_probability is None:
        # Defaults for gap probability
        if colormode in ["classicbroken", "randombroken"]:
            gap_probability = 0.05
        else:
            gap_probability = 0.0
    elif gap_probability < 0 or gap_probability > 1:
        raise GollyXPatternsError(
            f"Error: specified gap probability for segment is invalid: {gap_probability}"
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

    if colormode in ["classic", "classicbroken"]:

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

            magon = math.floor((1 - gap_probability) * mag)
            rem = mag - magon

            team_assignments = [serpteam,] * magon + [
                0,
            ] * rem  # noqa
            random.shuffle(team_assignments)

            ta_ix = 0
            for y in range(starty, endy + 1):
                for x in range(startx, endx + 1):

                    # Trying to fix a problem with no hsegments
                    if y < 0:
                        y = 1
                    if x < 0:
                        x = 1

                    if team_assignments[ta_ix] == 1:
                        team1_pattern[y][x] = "o"
                    elif team_assignments[ta_ix] == 2:
                        team2_pattern[y][x] = "o"
                    ta_ix += 1

    elif colormode in ["random", "randombroken"]:

        # Random/random broken color mode:
        # For each segment of length N,
        # create an array of N/2 zeros and N/2 ones,
        # shuffle it, use it to assign colors.
        # If broken, include 0s to represent dead cells
        for i, (starty, endy, startx, endx, mag) in enumerate(loclenlist):

            magh = math.floor(0.5 * (1 - gap_probability) * mag)
            rem = mag - (2*magh)
            
            team_assignments = (
                [
                    1,
                ]
                * magh
                + [
                    2,
                ]
                * magh
                + [
                    0,
                ]
                * rem
            )  # noqa
            random.shuffle(team_assignments)

            ta_ix = 0
            for y in range(starty, endy + 1):
                if y >= rows:
                    continue
                for x in range(startx, endx + 1):
                    if x >= cols:
                        continue

                    if y < 0:
                        y = 1
                    if x < 0:
                        x = 1

                    if team_assignments[ta_ix] == 1:
                        team1_pattern[y][x] = "o"
                    elif team_assignments[ta_ix] == 2:
                        team2_pattern[y][x] = "o"

                    ta_ix += 1

    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    return team1_pattern, team2_pattern


def methuselah_quadrants_pattern(
    rows, cols, seed=None, methuselah_counts=None, methuselah_names=None
):
    """
    Returns a map with a cluster of methuselahs in each quadrant.

    The methesela_counts parameter determines how many methuselahs
    may be put in each corner.

    Valid configurations:
    1 (placed in center of quadrant)
    2 (placed on opposite corners of a four-point square formed by cutting quadrant into thirds
    4 (placed on all corners of four-point square)
    3 (placed on diagonal of square with 3 points per edge, or 8 points)
    9 (placed on all corners and center of 8-point square)
    16 (placed on a 4x4 grid)

    Procedure:
    First randomly pair quadrants so their methuselah counts will match.
    Next, place random methuselah patterns in each of the corners.
    """
    if seed is not None:
        random.seed(seed)

    # Basic checks
    BIGDIMLIMIT = 150
    mindim = min(rows, cols)

    if methuselah_counts is None:
        if mindim < BIGDIMLIMIT:
            methuselah_counts = [1, 2, 3, 4, 9]
        else:
            methuselah_counts = [1, 2, 3, 4, 9, 16]

    valid_mc = [1, 2, 3, 4, 9, 16]
    for mc in methuselah_counts:
        if mc not in valid_mc:
            msg = "Invalid methuselah counts passed: must be in {', '.join(valid_mc)}\n"
            msg += "you specified {', '.join(methuselah_counts)}"
            raise GollyXPatternsError(msg)

    if False and 16 in methuselah_counts and min(rows, cols) < BIGDIMLIMIT:
        msg = "Invalid methuselah count specified: grid size too small for 4x4!"
        raise GollyXPatternsError(msg)

    # Store each quadrant and its upper left corner in (rows from top, cols from left) format
    quadrants = [
        (1, (0, cols // 2)),
        (2, (0, 0)),
        (3, (rows // 2, 0)),
        (4, (rows // 2, cols // 2)),
    ]

    # Shuffle quadrants, first two and second two are now paired up as buddies
    random.shuffle(quadrants)

    rotdegs = [0, 90, 180, 270]

    all_methuselahs = []

    for buddy_index in [[0, 1], [2, 3]]:
        # Decide how many methuselahs in this quad pair
        count = random.choice(methuselah_counts)

        if count == 1:

            # Only one methuselah in this quadrant, so use the center

            jitterx = 8
            jittery = 8

            for bi in buddy_index:
                corner = quadrants[bi][1]

                y = corner[0] + rows // 4 + random.randint(-jittery, jittery)
                x = corner[1] + cols // 4 + random.randint(-jitterx, jitterx)

                meth = random.choice(methuselah_names)

                pattern = get_grid_pattern(
                    meth,
                    rows,
                    cols,
                    xoffset=x,
                    yoffset=y,
                    hflip=bool(random.getrandbits(1)),
                    vflip=bool(random.getrandbits(1)),
                    rotdeg=random.choice(rotdegs),
                )
                livecount = get_pattern_livecount(meth)
                all_methuselahs.append((livecount, pattern))

        elif count == 2 or count == 4:

            # Two or four methuselahs in this quadrant, so place at corners of a square
            # Form the square by cutting the quadrant into thirds

            if count == 4:
                jitterx = 2
                jittery = 2
            else:
                jitterx = 4
                jittery = 4

            for bi in buddy_index:
                corner = quadrants[bi][1]

                # Slices and partitions form the inside square
                nslices = 2
                nparts = nslices + 1

                posdiag = bool(random.getrandbits(1))

                for a in range(1, nparts):
                    for b in range(1, nparts):

                        proceed = False
                        if count == 2:
                            if (posdiag and a == b) or (
                                not posdiag and a == (nslices - b + 1)
                            ):
                                proceed = True
                        elif count == 4:
                            proceed = True

                        if proceed:
                            y = corner[0] + a * ((rows // 2) // nparts) + random.randint(-jittery, jittery)
                            x = corner[1] + b * ((cols // 2) // nparts) + random.randint(-jitterx, jitterx)

                            meth = random.choice(methuselah_names)

                            try:
                                pattern = get_grid_pattern(
                                    meth,
                                    rows,
                                    cols,
                                    xoffset=x,
                                    yoffset=y,
                                    hflip=bool(random.getrandbits(1)),
                                    vflip=bool(random.getrandbits(1)),
                                    rotdeg=random.choice(rotdegs),
                                )
                            except GollyXPatternsError:
                                raise GollyXPatternsError(
                                    f"Error with methuselah {meth}: cannot fit"
                                )
                            livecount = get_pattern_livecount(meth)
                            all_methuselahs.append((livecount, pattern))

        elif count == 3 or count == 9:

            # Three or nine methuselahs, place these on a square with three points per side
            # or eight points total
            if count == 9:
                jitterx = 2
                jittery = 2
            else:
                jitterx = 4
                jittery = 4

            for bi in buddy_index:
                corner = quadrants[bi][1]

                nslices = 4

                for a in range(1, nslices):
                    for b in range(1, nslices):

                        proceed = False
                        if count == 3:
                            if a == b:
                                proceed = True
                        elif count == 9:
                            proceed = True

                        if proceed:
                            y = corner[0] + a * ((rows // 2) // nslices) + random.randint(-jittery, jittery) 
                            x = corner[1] + b * ((cols // 2) // nslices) + random.randint(-jitterx, jitterx) 

                            meth = random.choice(methuselah_names)

                            try:
                                pattern = get_grid_pattern(
                                    meth,
                                    rows,
                                    cols,
                                    xoffset=x,
                                    yoffset=y,
                                    hflip=bool(random.getrandbits(1)),
                                    vflip=bool(random.getrandbits(1)),
                                    rotdeg=random.choice(rotdegs),
                                )
                            except GollyXPatternsError:
                                raise GollyXPatternsError(
                                    f"Error with methuselah {meth}: cannot fit"
                                )
                            livecount = get_pattern_livecount(meth)
                            all_methuselahs.append((livecount, pattern))

        elif count == 16:

            # Sixteen methuselahs, place these on a 4x4 square
            jitterx = 1
            jittery = 1

            for bi in buddy_index:
                corner = quadrants[bi][1]

                nslices = 5

                for a in range(1, nslices):
                    for b in range(1, nslices):

                        y = corner[0] + a * ((rows // 2) // nslices) + random.randint(-jittery, jittery)  
                        x = corner[1] + b * ((cols // 2) // nslices) + random.randint(-jitterx, jitterx)  

                        meth = random.choice(methuselah_names)

                        try:
                            pattern = get_grid_pattern(
                                meth,
                                rows,
                                cols,
                                xoffset=x,
                                yoffset=y,
                                hflip=bool(random.getrandbits(1)),
                                vflip=bool(random.getrandbits(1)),
                                rotdeg=random.choice(rotdegs),
                            )
                        except GollyXPatternsError:
                            raise GollyXPatternsError(
                                f"Error with methuselah {meth}: cannot fit"
                            )
                        livecount = get_pattern_livecount(meth)
                        all_methuselahs.append((livecount, pattern))

    random.shuffle(all_methuselahs)
    all_methuselahs.sort(key=itemgetter(0), reverse=True)

    team1_patterns = []
    team2_patterns = []

    serpentine_pattern = [1, 2, 2, 1]
    for i, (_, methuselah_pattern) in enumerate(all_methuselahs):
        serpix = i % len(serpentine_pattern)
        serpteam = serpentine_pattern[serpix]
        if serpteam == 1:
            team1_patterns.append(methuselah_pattern)
        elif serpteam == 2:
            team2_patterns.append(methuselah_pattern)

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    return team1_pattern, team2_pattern


def cloud_region(
    which_pattern, dims, xlim, ylim, margins, jitter, flip, distancing=True
):
    """
    Given a square region defined by the x and y limits, tile the region
    with copies of the specified pattern, plus jitter.

    Parameters:
    dims            (rows, cols) list/tuple
    xlim            (xstart, xend) list/tuple
    ylim            (ystart, yend) list/tuple
    margins         integer or (N, E, S, W) list/tuple
    jitter          (xjitter, yjitter) list/tuple
    flip            (do_hflip, do_vflip) list/tuple
    distancing      boolean: if true, add an extra margin of cells
                    (eliminates overlap in starting positions)
                    (off is more chaotic, on is more ordered)
    """
    if len(dims) != 2:
        err = "Error: could not understand dimensions input, provide (rows, cols)"
        raise Exception(err)
    rows, cols = dims[0], dims[1]

    if len(xlim) != 2 or len(ylim) != 2:
        err = "Error: could not understand xlim/ylim input, provide (xstart, xend) and (ystart, yend)"
        raise Exception(err)

    # Unpack margins
    if isinstance(margins, Iterable):
        if len(margins) != 4:
            err = "Error: could not understand margins input, provide single value or list of 4 values"
            raise Exception(err)
        # list of 4 values in order N E S W
        north = margins[0]
        east = margins[1]
        south = margins[2]
        west = margins[3]
    else:
        # single value, uniform margin
        margins = int(margins)
        north = east = south = west = margins

    # Unpack jitter
    if isinstance(jitter, Iterable):
        if len(jitter) != 2:
            err = "Error: could not understand jitter input, provide two values (xjitter, yjitter)"
            raise Exception(err)
        x_jitter = jitter[0]
        y_jitter = jitter[1]
    else:
        jitter = int(jitter)
        x_jitter = y_jitter = jitter

    # Get whether to hflip or vflip
    if len(flip) != 2:
        err = "Error: could not understand flip input, provide two values (do_hflip, do_vflip)"
        raise Exception(err)
    do_hflip = flip[0]
    do_vflip = flip[1]

    # Determine the core xlim and ylim
    core_xlim = [xlim[0] + west, xlim[1] - east]
    core_w = core_xlim[1] - core_xlim[0]
    if core_w < 0:
        t = core_xlim[1]
        core_xlim[1] = core_xlim[0]
        core_xlim[0] = t
        core_w = abs(core_w)

    core_ylim = [ylim[0] + north, ylim[1] - south]
    core_h = core_ylim[1] - core_ylim[0]
    if core_h < 0:
        t = core_ylim[1]
        core_ylim[1] = core_ylim[0]
        core_ylim[0] = t
        core_h = abs(core_h)

    # Tile the pattern
    (pattern_h, pattern_w) = get_pattern_size(which_pattern)
    (tile_h, tile_w) = (pattern_h + 2 * y_jitter, pattern_w + 2 * x_jitter)
    if distancing:
        tile_h += 2
        tile_w += 2
    tiling_nx = core_w // tile_w - 1
    tiling_ny = core_h // tile_h - 1

    tileset = []
    for i in range(tiling_nx):
        for j in range(tiling_ny):

            if distancing:
                xoffset = core_xlim[0] + (tile_w // 2) + i * (tile_w + 2) + 1
                yoffset = core_ylim[0] + (tile_h // 2) + j * (tile_h + 2) + 1
            else:
                xoffset = core_xlim[0] + (tile_w // 2) + i * tile_w
                yoffset = core_ylim[0] + (tile_h // 2) + j * tile_h

            tileset.append(
                get_grid_pattern(
                    which_pattern,
                    rows,
                    cols,
                    xoffset=xoffset + random.randint(-x_jitter, x_jitter),
                    yoffset=yoffset + random.randint(-y_jitter, y_jitter),
                    hflip=do_hflip,
                    vflip=do_vflip,
                    check_overflow=False,
                )
            )

    tileset_pattern = pattern_union(tileset)
    return tileset_pattern
