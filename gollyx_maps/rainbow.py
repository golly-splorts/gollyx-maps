import math
import itertools
from operator import itemgetter
import json
import os
import random
from .geom import hflip_pattern, vflip_pattern, rot_pattern
from .patterns import (
    get_pattern_size,
    get_pattern_livecount,
    get_grid_empty,
    get_grid_pattern,
    segment_pattern,
    methuselah_quadrants_pattern,
    pattern_union,
    cloud_region,
)
from .utils import pattern2url, retry_on_failure
from .error import GollyXPatternsError, GollyXMapsError


##############
# Util methods


def get_rainbow_pattern_function_map():
    return {
        "random": random_fourcolor,
        "randommethuselahs": randommethuselahs_fourcolor,
        "orchard": orchard_fourcolor,
        "justyna": justyna_fourcolor,
        "rabbits": rabbits_fourcolor,
        "multum": multum_fourcolor,
        "eights": eightx_fourcolor,
        "patiolights": patiolights_fourcolor,
        "rainbow": rainbow_fourcolor,
        "sunburst": sunburst_fourcolor,
    }


def rainbow_jitteryrow_pattern(rows, cols, seed=None, methuselah=None, spacing=None):

    if seed is not None:
        random.seed(seed)

    # L is a characteristic length scale
    if spacing is None:
        L = 10
    else:
        L = spacing

    if methuselah is None:
        methuselah = "rheptomino"

    count = cols // L

    centerx = cols // 2
    centery = rows // 2

    # Place one methuselah every L grid spaces,
    # up to the maximum multiple of 4 possible
    maxshapesperteam = (cols // 4) // L
    maxshapes = 4 * maxshapesperteam

    team_assignments = [0, 1, 2, 3]
    random.shuffle(team_assignments)

    rotdegs = [0, 90, 180, 270]

    patterns_list_all = [[], [], [], []]

    # This algorithm is structured unusually,
    # but ensures everything is centered.
    for i in range(maxshapesperteam):

        # Populate all four quadrants manually...
        end = (i + 1) * L
        start = end - L // 2

        # +---------------+
        # |Q1 |Q2 |Q3 |Q4 |
        # |   |   |   |   |
        # +---------------+
        #
        # Q1
        pattern = get_grid_pattern(
            methuselah,
            rows,
            cols,
            xoffset=centerx - centerx // 2 - random.randint(start, end),
            yoffset=centery + random.randint(-L, L),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
            rotdeg=random.choice(rotdegs),
        )
        team_ix = team_assignments[0]

        team_patterns_list = patterns_list_all[team_ix]
        team_patterns_list.append(pattern)
        patterns_list_all[team_ix] = team_patterns_list

        # Q2
        pattern = get_grid_pattern(
            methuselah,
            rows,
            cols,
            xoffset=centerx - random.randint(start, end),
            yoffset=centery + random.randint(-L, L),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
            rotdeg=random.choice(rotdegs),
        )
        team_ix = team_assignments[1]

        team_patterns_list = patterns_list_all[team_ix]
        team_patterns_list.append(pattern)
        patterns_list_all[team_ix] = team_patterns_list

        # Q3
        pattern = get_grid_pattern(
            methuselah,
            rows,
            cols,
            xoffset=centerx + random.randint(start, end),
            yoffset=centery + random.randint(-L, L),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
            rotdeg=random.choice(rotdegs),
        )
        team_ix = team_assignments[2]

        team_patterns_list = patterns_list_all[team_ix]
        team_patterns_list.append(pattern)
        patterns_list_all[team_ix] = team_patterns_list

        # Q4
        pattern = get_grid_pattern(
            methuselah,
            rows,
            cols,
            xoffset=centerx + centerx // 2 + random.randint(start, end),
            yoffset=centery + random.randint(-L, L),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
            rotdeg=random.choice(rotdegs),
        )
        team_ix = team_assignments[3]

        team_patterns_list = patterns_list_all[team_ix]
        team_patterns_list.append(pattern)
        patterns_list_all[team_ix] = team_patterns_list

    pattern_unions = [pattern_union(pl) for pl in patterns_list_all]
    return tuple(pattern_unions)


def rainbow_methuselah_quadrants_pattern(
    rows, cols, seed=None, methuselah_counts=None, fixed_methuselah=None
):
    """
    Add methuselahs to each quadrant.

    If the user does not specify any args,
    this fills the quadrants with lots of
    small methuselahs.

    The user can specify which methuselahs
    to use and how many to use, so e.g.
    can specify 1 methuselah per quadrant, etc.
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    small_methuselah_names = [
        "bheptomino",
        "cheptomino",
        "eheptomino",
        "piheptomino",
        "rpentomino",
    ]
    reg_methuselah_names = [
        "acorn",
        "bheptomino",
        "cheptomino",
        "eheptomino",
        "multuminparvo",
        "piheptomino",
        "rabbit",
        "rpentomino",
    ]

    BIGDIMLIMIT = 150
    mindim = min(rows, cols)

    if methuselah_counts is None:
        if mindim < BIGDIMLIMIT:
            methuselah_counts = [3, 4, 9]
        else:
            methuselah_counts = [3, 4, 9, 16]

    if fixed_methuselah is None:
        if mindim < BIGDIMLIMIT:
            methuselah_names = reg_methuselah_names + small_methuselah_names
        else:
            methuselah_names = small_methuselah_names
    else:
        methuselah_names = [fixed_methuselah]

    valid_mc = [1, 2, 3, 4, 9, 16]
    for mc in methuselah_counts:
        if mc not in valid_mc:
            msg = "Invalid methuselah counts passed: must be in {', '.join(valid_mc)}\n"
            msg += "you specified {', '.join(methuselah_counts)}"
            raise GollyXPatternsError(msg)

    # Put a cluster of methuselahs in each quadrant,
    # one quadrant per team.

    # Procedure:
    # place random methuselah patterns in each quadrant corner

    # Store each quadrant and its upper left corner in (rows from top, cols from left) format
    quadrants = [
        (1, (0, cols // 2)),
        (2, (0, 0)),
        (3, (rows // 2, 0)),
        (4, (rows // 2, cols // 2)),
    ]

    rotdegs = [0, 90, 180, 270]

    all_methuselahs = []

    for iq, quad in enumerate(quadrants):
        count = random.choice(methuselah_counts)

        if count == 1:

            # Only one methuselah in this quadrant, so use the center

            jitterx = 4
            jittery = 4

            corner = quadrants[iq][1]

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
                jitterx = 3
                jittery = 3
            else:
                jitterx = 5
                jittery = 5

            corner = quadrants[iq][1]

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
                        y = (
                            corner[0]
                            + a * ((rows // 2) // nparts)
                            + random.randint(-jittery, jittery)
                        )
                        x = (
                            corner[1]
                            + b * ((cols // 2) // nparts)
                            + random.randint(-jitterx, jitterx)
                        )

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
                jitterx = 3
                jittery = 3
            else:
                jitterx = 5
                jittery = 5

            corner = quadrants[iq][1]

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
                        y = (
                            corner[0]
                            + a * ((rows // 2) // nslices)
                            + random.randint(-jittery, jittery)
                        )
                        x = (
                            corner[1]
                            + b * ((cols // 2) // nslices)
                            + random.randint(-jitterx, jitterx)
                        )

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
            jitterx = 2
            jittery = 2

            corner = quadrants[iq][1]

            nslices = 5

            for a in range(1, nslices):
                for b in range(1, nslices):

                    y = (
                        corner[0]
                        + a * ((rows // 2) // nslices)
                        + random.randint(-jittery, jittery)
                    )
                    x = (
                        corner[1]
                        + b * ((cols // 2) // nslices)
                        + random.randint(-jitterx, jitterx)
                    )

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

    # Sort by number of live cells
    all_methuselahs.sort(key=itemgetter(0), reverse=True)

    team1_patterns = []
    team2_patterns = []
    team3_patterns = []
    team4_patterns = []

    asc = [1, 2, 3, 4]
    ascrev = list(reversed(asc))
    serpentine_pattern = asc + ascrev

    for i, (_, methuselah_pattern) in enumerate(all_methuselahs):
        serpix = i % len(serpentine_pattern)
        serpteam = serpentine_pattern[serpix]
        if serpteam == 1:
            team1_patterns.append(methuselah_pattern)
        elif serpteam == 2:
            team2_patterns.append(methuselah_pattern)
        elif serpteam == 3:
            team3_patterns.append(methuselah_pattern)
        elif serpteam == 4:
            team4_patterns.append(methuselah_pattern)

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)
    team3_pattern = pattern_union(team3_patterns)
    team4_pattern = pattern_union(team4_patterns)

    return team1_pattern, team2_pattern, team3_pattern, team4_pattern


#############
# Map methods


def random_fourcolor(rows, cols, seed=None):
    """
    Generate a random four-color list life initialization.

    Returns: four listlife strings,
    with the random initializations.
    (8-20% of all cells are alive).

    Strategy: generate a set of (x,y) tuples,
    convert to list, split in four. Use those
    point sets to create listLife URL strings.
    """
    if seed is not None:
        random.seed(seed)

    density = random.randint(8, 18) / 100.0

    ncells = rows * cols
    nlivecells = 4 * ((density * ncells) // 4)

    points = set()
    while len(points) < nlivecells:
        randy = random.randint(0, rows - 1)
        randx = random.randint(0, cols - 1)
        points.add((randx, randy))

    points = list(points)

    pattern_urls = []

    # Loop over each team
    for i in range(4):

        # Subselection of points
        q = len(points) // 4
        start_ix = i * q
        end_ix = (i + 1) * q
        this_points = set(points[start_ix:end_ix])

        # Assemble pattern
        this_pattern = []
        for y in range(rows):
            this_row = []
            for x in range(cols):
                if (x, y) in this_points:
                    this_row.append("o")
                else:
                    this_row.append(".")
            this_rowstr = "".join(this_row)
            this_pattern.append(this_rowstr)

        this_url = pattern2url(this_pattern)
        pattern_urls.append(this_url)

    return tuple(pattern_urls)


@retry_on_failure
def randommethuselahs_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    patterns = rainbow_methuselah_quadrants_pattern(rows, cols, seed)
    result = (pattern2url(pat) for pat in patterns)
    return result


@retry_on_failure
def orchard_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    mindim = min(rows, cols)
    if mindim < 150:
        mc = [4, 9]
    else:
        mc = [4, 9, 16]

    count = random.choice(mc)
    patterns = rainbow_methuselah_quadrants_pattern(
        rows, cols, seed, methuselah_counts=[count], fixed_methuselah="acorn"
    )
    urls = (pattern2url(p) for p in patterns)
    return urls


@retry_on_failure
def justyna_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    mc = [1]

    count = random.choice(mc)
    patterns = rainbow_methuselah_quadrants_pattern(
        rows, cols, seed, methuselah_counts=[count], fixed_methuselah="justyna"
    )
    urls = (pattern2url(p) for p in patterns)
    return urls


@retry_on_failure
def rabbits_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    mindim = min(rows, cols)
    if mindim < 150:
        mc = [1, 2]
    else:
        mc = [1, 2, 3]

    count = random.choice(mc)
    patterns = rainbow_methuselah_quadrants_pattern(
        rows, cols, seed, methuselah_counts=[count], fixed_methuselah="rabbit"
    )
    urls = (pattern2url(p) for p in patterns)
    return urls


@retry_on_failure
def multum_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    mindim = min(rows, cols)
    if mindim < 150:
        mc = [1, 2]
    else:
        mc = [2, 3, 4]
    count = random.choice(mc)
    patterns = rainbow_methuselah_quadrants_pattern(
        rows, cols, seed, methuselah_counts=[count], fixed_methuselah="multuminparvo"
    )
    urls = (pattern2url(p) for p in patterns)
    return urls


@retry_on_failure
def eightx_fourcolor(rows, cols, seed=None):
    fmap = {
        "eightb": _eightb_fourcolor,
        "eightc": _eightc_fourcolor,
        "eighte": _eighte_fourcolor,
        "eightr": _eightr_fourcolor,
        "eightpi": _eightpi_fourcolor,
    }
    k = random.choice(list(fmap.keys()))
    return fmap[k](rows, cols, seed)


def _eightb_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    patterns = rainbow_jitteryrow_pattern(rows, cols, seed, "bheptomino")
    urls = (pattern2url(p) for p in patterns)
    return urls


def _eightc_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    patterns = rainbow_jitteryrow_pattern(rows, cols, seed, "cheptomino")
    urls = (pattern2url(p) for p in patterns)
    return urls


def _eighte_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    patterns = rainbow_jitteryrow_pattern(rows, cols, seed, "eheptomino", spacing=7)
    urls = (pattern2url(p) for p in patterns)
    return urls


def _eightpi_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    patterns = rainbow_jitteryrow_pattern(rows, cols, seed, "piheptomino")
    urls = (pattern2url(p) for p in patterns)
    return urls


def _eightr_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    patterns = rainbow_jitteryrow_pattern(rows, cols, seed, "rpentomino")
    urls = (pattern2url(p) for p in patterns)
    return urls


def patiolights_fourcolor(rows, cols, seed=None):
    """
    Patio lights pattern is a line segments with boxes placed randomly along the segment, like a string of lights
    """

    if seed is not None:
        random.seed(seed)

    urls = []

    thickness = random.randint(2, 3)

    nteams = 4

    # Find the y locations of each light string:
    # Divide rows into Nteams + 1 parts with Nteams slices
    # Place the light strings at the slices
    jittery = 5
    lightstring_ys = [
        ((i + 1) * rows) // (nteams + 1) + random.randint(-jittery, jittery)
        for i in range(nteams)
    ]

    # Randomize order of light string team assignments
    random.shuffle(lightstring_ys)

    # I dunno
    def _get_bounds(z, dim):
        zstart = z - dim // 2
        zend = z + (dim - dim // 2)
        return zstart, zend

    for iteam in range(nteams):

        team_pattern = get_grid_empty(rows, cols, flat=False)

        # Assemble the light string
        lightstring_y = lightstring_ys[iteam]

        for ix in range(0, cols):
            for iy in range(lightstring_y - 1, lightstring_y + thickness):
                team_pattern[iy][ix] = "o"

        for ix in range(0, cols):
            for iy in range(lightstring_y - 1, lightstring_y + thickness):
                team_pattern[iy][ix] = "o"

        # Add some lights to the string
        jitterx = 4

        bounds = (lightstring_y - 1, lightstring_y + thickness)
        maxy = max(bounds)
        miny = min(bounds)
        ylightstop = miny - random.randint(2, 3)
        ylightsbot = maxy + random.randint(2, 3)
        ix = random.randint(4, 12)
        while ix < cols - 1:
            if random.random() < 0.50:
                team_pattern[ylightsbot][ix] = "o"
                team_pattern[ylightsbot][ix + 1] = "o"
                team_pattern[ylightsbot + 1][ix] = "o"
                team_pattern[ylightsbot + 1][ix + 1] = "o"
            else:
                team_pattern[ylightstop][ix] = "o"
                team_pattern[ylightstop][ix + 1] = "o"
                team_pattern[ylightstop - 1][ix] = "o"
                team_pattern[ylightstop - 1][ix + 1] = "o"
            ix += random.randint(10, 12) + random.randint(-jitterx, jitterx)

        pattern_url = pattern2url(team_pattern)
        urls.append(pattern_url)

    return tuple(urls)


def rainbow_fourcolor(rows, cols, seed=None):
    return _rainburst_fourcolor(rows, cols, seed, sunburst=False)


def sunburst_fourcolor(rows, cols, seed=None):
    return _rainburst_fourcolor(rows, cols, seed, sunburst=True)


def _rainburst_fourcolor(rows, cols, seed=None, sunburst=False):
    """
    Create a Gaussian normal distribution in the top left and bottom right quadrants,
    then slice it into radial pieces, which makes a nice rainbow shape.
    """
    SMOL = 1e-12

    if seed is not None:
        random.seed(seed)

    # Algorithm:
    # set the slope
    # generate (x, y) points
    # if slope < 1/g, A
    # if slope < 1, B
    # if slope < g: C
    # else: D

    density = random.randint(8, 18)/100.0

    nteams = 4
    ncells = rows * cols
    npointsperteam = (ncells//nteams)*density
    nlivecells = nteams*npointsperteam

    centerx = cols // 2
    centery = rows // 2

    teams_points = []

    g = 2.5

    slope_checks = [
        0,
        1/g,
        1,
        g,
    ]

    urls = []
        
    for iteam in range(nteams):
        team_points = set()

        while len(team_points) < npointsperteam:
            randx = int(random.gauss(centerx, centerx // 2))
            randy = int(random.gauss(centery, centery // 2))

            slope = (randy - centery) / (randx - centerx + SMOL)

            if iteam==0:
                if slope > slope_checks[iteam] and slope < slope_checks[iteam+1]:
                    team_points.add((randx, randy))
            elif iteam==1:
                if slope > slope_checks[iteam] and slope < slope_checks[iteam+1]:
                    team_points.add((randx, randy))
            elif iteam==2:
                if slope > slope_checks[iteam] and slope < slope_checks[iteam+1]:
                    team_points.add((randx, randy))
            elif iteam==3:
                if slope > slope_checks[iteam]:
                    team_points.add((randx, randy))

        team_pattern = []
        for y in range(rows):
            team_row = []
            for x in range(cols):
                if (x, y) in team_points:
                    team_row.append("o")
                else:
                    team_row.append(".")

            team_row_str = "".join(team_row)
            team_pattern.append(team_row_str)

        if sunburst and iteam%2==0:
            team_pattern = vflip_pattern(team_pattern)

        team_url = pattern2url(team_pattern)
        urls.append(team_url)

    random.shuffle(urls)

    return tuple(urls)
