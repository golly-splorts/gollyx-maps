import json
import os
import random
from .geom import hflip_pattern, vflip_pattern
from .utils import pattern2url
from .patterns import get_grid_empty, pattern_union, get_pattern, get_grid_pattern
from .utils import pattern2url, retry_on_failure


def get_star_pattern_function_map():
    return {
        "flyingv1": flyingv1,
        "flyingv2": flyingv2,
        "stlouis": stlouis,
        "newyork": newyork,
        "chicago": chicago,
        "combs": combs,
        # containment lines
        "precipitation": precipitation,
        "evaporation": evaporation,
        "denaturation": denaturation,
        # "gastank": gastank,
        # "rustytank": rustytank,
        # "dinnerplate": dinnerplate,
        # "desertplate": desertplate,
        # "squarestar": squarestar,
        # "kitchensink": kitchensink,
        # "ricepudding": ricepudding,
        # "fishsoup": fishsoup,
    }


def flyingv1(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    return _flyingv(
        rows, cols, seed=seed, dx=3, dy=3, kill_count=10, kill_prob=0.20, valign=True
    )


def flyingv2(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    return _flyingv(
        rows,
        cols,
        seed=seed,
        dx=4,
        dy=8,
        kill_count=40,
        kill_prob=0.40,
        valign=random.random() < 0.50,
    )


def stlouis(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    if random.random() < 0.50:
        # chicago style
        return _bars(
            rows,
            cols,
            seed=seed,
            st_louis_style=True,
            tmargin_lim=[3, 4],
            bmargin_lim=[5, 6],
            thickness_lim=[8, 10],
        )
    else:
        # ny style
        return _bars(rows, cols, seed=seed, st_louis_style=True, thickness_lim=[2, 4])


def newyork(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    return _bars(rows, cols, seed=seed, thickness_lim=[2, 4])


def chicago(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    return _bars(
        rows,
        cols,
        seed=seed,
        tmargin_lim=[3, 4],
        bmargin_lim=[5, 6],
        thickness_lim=[8, 10],
    )


def precipitation(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    stamp_names = ["solarsail", "backedupsink", "squarevariation3"]
    return _containment_lines(
        rows,
        cols,
        seed=seed,
        stamp_name=random.choice(stamp_names),
        peel_off=False,
    )


def evaporation(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    stamp_names = ["solarsail", "backedupsink", "squarevariation3"]
    return _containment_lines(
        rows,
        cols,
        seed=seed,
        stamp_name=random.choice(stamp_names),
        peel_off=True,
    )


def denaturation(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    return _containment_lines(
        rows,
        cols,
        seed=seed,
        stamp_name='arrow',
        stamps_per_team_lim=[1, 3],
        vertical_stamp_orientation=random.random()<0.5,
        peel_off=True,
    )


#########################################


def _flyingv(
    rows,
    cols,
    seed=None,
    dx=4,
    dy=8,
    kill_count=0,
    kill_prob=0.5,
    valign=True,
):
    if seed is not None:
        random.seed(seed)

    # These store the the .o diagrams (flat=False means these are lists of lists of one char)
    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    # ---------
    # Parameters

    # Left/right margin
    lmargin = 0.1

    # Top/bottom margins
    tmargin = 0.1
    bmargin = 0.9

    # Set jitter
    jitterx = 7
    jittery = 8

    maxkillprob = kill_prob
    maxkillcounter = kill_count

    # ------------
    # Algorithm:
    #
    # Create diagonal lines by filling in rectangles
    # connected diagonal-to-diagonal.
    # The lines only occupy half of the grid.
    # Create two, flip one of them, and combine to get a V shape.
    #
    # It is also crucial to ensure teams start on even
    # grid numbers, to ensure the diagonal formation does
    # something interesting, hence the times 2/divided by 2 operation.

    starty = int(tmargin * rows) + 2 * random.randint(0, jittery)
    endy = int(bmargin * rows) - random.randint(0, jittery)

    startx = int(lmargin * cols) + (random.randint(0, jitterx) // 2) * 2
    endx = (45 * cols) // 100 - (random.randint(0, jitterx) // 2) * 2

    # -------------
    # color 1

    killcounter = 0

    if valign:
        starty1 = starty
        endy1 = endy
    else:
        offset = (random.randint(-jittery, jittery) // 2) * 2
        starty1 = starty + offset
        endy1 = endy + offset
    yy = starty1

    offset = (random.randint(-jitterx, jitterx) // 2) * 2
    startx1 = startx + offset + 1
    endx1 = endx + offset
    xx = startx1

    while yy < endy1 and xx < endx1:
        for xx_ in range(xx, xx + dx + 1):
            for yy_ in range(yy, yy + dy + 1):
                if xx_ == xx:
                    team1_pattern[yy_][xx_] = "o"
                elif xx_ == (xx + dx + 1):
                    team1_pattern[yy_][xx_] = "o"
                else:
                    if xx_ % 2 == yy_ % 2:
                        if (
                            random.random() < maxkillprob
                            and killcounter != maxkillcounter
                        ):
                            killcounter += 1
                        else:
                            team1_pattern[yy_][xx_] = "o"
        yy += dy
        xx += dx

    # -------------
    # color 2

    killcounter = 0

    if valign:
        starty2 = starty
        endy2 = endy
    else:
        offset = (random.randint(-jittery, jittery) // 2) * 2
        starty2 = starty + offset
        endy2 = endy + offset
    yy = starty2

    offset = (random.randint(-jitterx, jitterx) // 2) * 2
    startx2 = startx + offset + 1
    endx2 = endx + offset
    xx = startx2

    while yy < endy2 and xx < endx2:
        for xx_ in range(xx, xx + dx + 1):
            for yy_ in range(yy, yy + dy + 1):
                if xx_ == xx:
                    team2_pattern[yy_][xx_] = "o"
                elif xx_ == (xx + dx + 1):
                    team2_pattern[yy_][xx_] = "o"
                else:
                    if xx_ % 2 == yy_ % 2:
                        if (
                            random.random() < maxkillprob
                            and killcounter != maxkillcounter
                        ):
                            killcounter += 1
                        else:
                            team2_pattern[yy_][xx_] = "o"
        yy += dy
        xx += dx

    # ---------------

    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    team2_pattern = hflip_pattern(team2_pattern)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return s1, s2


def _bars(
    rows,
    cols,
    tmargin_lim=[2, 3],
    bmargin_lim=[7, 8],
    gap_prob_lim=[2, 4],
    thickness_lim=[3, 5],
    st_louis_style=False,
    st_louis_gap=5,
    seed=None,
):

    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # These store the the .o diagrams (flat=False means these are lists of lists of one char)
    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    # ------------
    # Parameters

    jitterx = 4
    jittery = 10

    tmargin = random.randint(tmargin_lim[0], tmargin_lim[1]) / 10
    bmargin = random.randint(bmargin_lim[0], bmargin_lim[1]) / 10

    xlocs = [0.2, 0.4, 0.6, 0.8]
    random.shuffle(xlocs)

    xlocs1 = [xlocs[0], xlocs[1]]
    xlocs2 = [xlocs[2], xlocs[3]]

    gap_prob = random.randint(gap_prob_lim[0], gap_prob_lim[1]) / 10

    thickness = random.randint(*thickness_lim)

    # -------------
    # color 1

    starty0 = int(tmargin * rows)
    endy0 = int(bmargin * rows)

    jit = random.randint(-jittery, jittery)
    starty = starty0 + jit
    endy = endy0 + jit

    startx = int(xlocs1[0] * cols) + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team1_pattern[y][x] = "o"

    startx = int(xlocs1[1] * cols) + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team1_pattern[y][x] = "o"

    # -------------
    # color 2

    starty0 = int(tmargin * rows)
    endy0 = int(bmargin * rows)

    jit = random.randint(-jittery, jittery)
    starty = starty0 + jit
    endy = endy0 + jit

    startx = int(xlocs2[0] * cols) + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team2_pattern[y][x] = "o"

    startx = int(xlocs2[1] * cols) + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team2_pattern[y][x] = "o"

    # ------------------
    # st louis style
    if st_louis_style:
        for yy in range(rows):
            if yy % st_louis_gap == 0:
                nx = len(team1_pattern[y])
                for xx in range(nx):
                    team1_pattern[yy][xx] = "."
                    team2_pattern[yy][xx] = "."

    # -----------------
    # Adjust number of live cells of each team to be equal
    p1 = set()
    p2 = set()
    for yy in range(rows):
        for xx in range(cols):
            if team1_pattern[yy][xx] == "o":
                p1.add((xx, yy))
            elif team2_pattern[yy][xx] == "o":
                p2.add((xx, yy))

    diff = abs(len(p1) - len(p2))
    if diff != 0:
        if len(p1) > len(p2):
            larger = p1
            patt = team1_pattern
        else:
            larger = p2
            patt = team2_pattern
        for i in range(diff):
            pt = larger.pop()
            patt[pt[1]][pt[0]] = "."

    # ------------
    # Assemble:
    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return s1, s2


def combs(rows, cols, seed=None):
    """
    Make horizontal rows of thick lines with criss-cross hole punches
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # --------------
    # Parameters

    jitterx = 8
    jittery = 8

    thickness = random.randint(3, 5)

    ylocations = [random.randint(20, 45) / 100, random.randint(55, 80) / 100]
    yloc_swap_prob = 0.3

    xstart = random.randint(10, 25) / 100
    xwidth = random.randint(45, 65) / 100

    bumps_prob = random.randint(10, 50) / 100

    # -----------------
    # Algorithm:

    if random.random() < yloc_swap_prob:
        random.shuffle(ylocations)

    # These store the the .o diagrams (flat=False means these are lists of lists of one char)
    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    # -------------
    # color 1

    starty1 = int(ylocations[0] * rows) + random.randint(-jittery, jittery)
    endy1 = starty1 + thickness

    startx = int(xstart * cols) + random.randint(-jitterx, jitterx)
    endx = startx + int(xwidth * cols)

    for y in range(starty1, endy1 + 1):
        for x in range(startx, endx + 1):
            if y == starty1:
                team1_pattern[y][x] = "o"
            elif y == endy1:
                team1_pattern[y][x] = team1_pattern[y - 1][x]
            elif x % 2 == y % 2:
                team1_pattern[y][x] = "o"

    for x in range(startx, endx + 1):
        if random.random() < bumps_prob:
            team1_pattern[starty1 - 1][x] = "o"

    # -------------
    # color 2

    starty2 = int(ylocations[1] * rows) + random.randint(-jittery, jittery)
    endy2 = starty2 + thickness

    startx = int(xstart * cols) + random.randint(-jitterx, jitterx)
    endx = startx + int(xwidth * cols)

    for y in range(endy2, starty2 - 1, -1):
        for x in range(startx, endx + 1):
            if y == starty2:
                team2_pattern[y][x] = team2_pattern[y + 1][x]
            elif y == endy2:
                team2_pattern[y][x] = "o"
            elif x % 2 == y % 2:
                team2_pattern[y][x] = "o"

    for x in range(startx, endx + 1):
        if random.random() < bumps_prob:
            team2_pattern[endy2 + 1][x] = "o"

    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return s1, s2


def get_gridstamp(pattern, rows, cols, yoffset, xoffset, flatten=True):

    ogpattern = [list(j) for j in pattern if len(j) > 0]
    blank_row = ["."] * cols
    newpattern = [blank_row[:] for r in range(rows)]
    (pattern_h, pattern_w) = (len(ogpattern), len(ogpattern[0]))

    # given offset is offset for the center of the pattern,
    # so do some algebra to determine where we should start
    xstart = xoffset - pattern_w // 2
    xend = xstart + pattern_w
    ystart = yoffset - pattern_h // 2
    yend = ystart + pattern_h

    # iterate through the pattern and copy over the cells that are in the final grid
    for iy, y in enumerate(range(ystart, yend)):
        if y > 0 and y < len(newpattern):
            for ix, x in enumerate(range(xstart, xend)):
                if x > 0 and x < len(newpattern[iy]):
                    xx = (x + cols) % cols
                    yy = (y + rows) % rows
                    newpattern[yy][xx] = ogpattern[iy][ix]

    if flatten:
        newpattern = ["".join(j) for j in newpattern]

    return newpattern


def _containment_lines(
    rows,
    cols,
    stamp_name=None,
    peel_off=False,
    thickness=2,
    stamps_per_team_lim=[3, 6],
    vertical_stamp_orientation=None,
    seed=None,
):
    """
    Create a map with lines forming a rectangle.
    This requires a source of randomness.
    """
    if seed is not None:
        random.seed(seed)

    # --------------
    # Parameters:

    # Thickness of >= 2 is impenetrable
    # If peel_off set to true, leave a crack to allow lines to peel off

    stamps_per_team = random.randint(stamps_per_team_lim[0], stamps_per_team_lim[1])

    if vertical_stamp_orientation is None:
        vertical_stamp_orientation = random.random() < 0.50
        #vertical_stamp_orientation = True

    if stamp_name is None:
        raise Exception("Error: stamp_name parameter required for containment lines")

    jitterx = 8
    jittery = 8

    # ---------------
    # Algorithm:

    team1_patterns = []
    team2_patterns = []

    # ----------------
    # Lines:

    def _get_bounds(z, dim):
        zstart = z - dim // 2
        zend = z + (dim - dim // 2)
        return zstart, zend

    line_ylocs_top = random.randint(1, 4) / 10
    line_ylocs_bot = random.randint(6, 9) / 10

    line_ylocs = [int(line_ylocs_top * rows), int(line_ylocs_bot * rows)]

    team1_lines = get_grid_empty(rows, cols, flat=False)
    team2_lines = get_grid_empty(rows, cols, flat=False)

    y1 = line_ylocs[0] + random.randint(0, jittery)
    y2 = line_ylocs[1] - random.randint(0, jittery)

    if peel_off:
        start = 1
    else:
        start = 0

    # Add the line
    for ix in range(start, cols):
        # string 1
        for iy in range(*_get_bounds(y1, thickness)):
            team1_lines[iy][ix] = "o"
        # string 2
        for iy in range(*_get_bounds(y2, thickness)):
            team2_lines[iy][ix] = "o"

    # Vertical flip
    if random.random() < 0.50:
        team1_lines = [j for j in team1_lines[::-1]]
        team2_lines = [j for j in team2_lines[::-1]]
        old_y1 = y1
        old_y2 = y2
        y1 = rows - old_y2
        y2 = rows - old_y1

    team1_patterns.append(team1_lines)
    team2_patterns.append(team2_lines)

    # ----------------
    # Stamps:

    team_assignments = [1,] * stamps_per_team + [
        2,
    ] * stamps_per_team
    random.shuffle(team_assignments)

    # approximately evenly spaced in x dir
    if vertical_stamp_orientation:
        xlocs = [
            int(((j + 1) / (stamps_per_team + 1)) * cols)
            for j in range(stamps_per_team)
        ]
    else:
        xlocs = [
            int(((j + 1) / (2 * stamps_per_team + 1)) * cols)
            for j in range(2 * stamps_per_team)
        ]

    dy = y2 - y1

    for i, xloc in enumerate(xlocs):

        if vertical_stamp_orientation:
            yy1 = y1 + int((1 / 3) * dy) + random.randint(-jittery, jittery)
            yy2 = y1 + int((2 / 3) * dy) + random.randint(-jittery, jittery)

            yy1 = min(max(yy1, y1 + thickness // 2), y2 - thickness // 2)
            yy2 = min(max(yy2, y1 + thickness // 2), y2 - thickness // 2)

            stamp1 = get_pattern(
                stamp_name,
                hflip = random.random() < 0.50,
                vflip = random.random() < 0.50,
            )

            xx = xloc + random.randint(-jitterx, jitterx)
            gridstamp = get_gridstamp(stamp1, rows, cols, yoffset=yy1, xoffset=xx)

            team1_patterns.append(gridstamp)

            stamp2 = get_pattern(
                stamp_name,
                hflip = random.random() < 0.50,
                vflip = random.random() < 0.50,
            )

            xx = xloc + random.randint(-jitterx, jitterx)
            gridstamp = get_gridstamp(stamp2, rows, cols, yoffset=yy2, xoffset=xx)

            team2_patterns.append(gridstamp)

        else:

            stamp = get_pattern(
                stamp_name,
                hflip = random.random() < 0.50,
                vflip = random.random() < 0.50,
            )

            xx = xloc + random.randint(-jitterx, jitterx)
            yy = y1 + int(0.5 * dy) + random.randint(-jittery, jittery)
            gridstamp = get_gridstamp(stamp, rows, cols, yoffset=yy, xoffset=xx)

            if team_assignments[i] == 1:
                team1_patterns.append(gridstamp)
            elif team_assignments[i] == 2:
                team2_patterns.append(gridstamp)

    # --------------------
    # Final assembly:

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return s1, s2
