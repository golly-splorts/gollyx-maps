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
        "rainbowmath": rainbowmath_fourcolor,
        "randommethuselahs": randommethuselahs_fourcolor,
        "orchard": orchard_fourcolor,
        "justyna": justyna_fourcolor,
        "rabbits": rabbits_fourcolor,
        "multum": multum_fourcolor,
        "eights": eightx_fourcolor,
        "patiolights": patiolights_fourcolor,
        "rainbow": rainbow_fourcolor,
        "sunburst": sunburst_fourcolor,
        "timebomb": timebomb_fourcolor,
        "timebombredux": timebomb2_fourcolor,
        "crabs": crabs_fourcolor,
        "doublegaussian": doublegaussian_fourcolor,
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


@retry_on_failure
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


@retry_on_failure
def rainbow_fourcolor(rows, cols, seed=None):
    return _rainburst_fourcolor(rows, cols, seed, sunburst=False)


@retry_on_failure
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


@retry_on_failure
def timebomb_fourcolor(rows, cols, seed=None):
    return _timebomb_fourcolor(rows, cols, revenge=False, seed=seed)


@retry_on_failure
def timebomb2_fourcolor(rows, cols, seed=None):
    return _timebomb_fourcolor(rows, cols, revenge=True, seed=seed)


def _timebomb_fourcolor(rows, cols, revenge, seed=None):

    if seed is not None:
        random.seed(seed)

    mindim = min(rows, cols)

    # Geometry
    # L = length scale
    L = 20
    centerx = cols // 2
    centery = rows // 2

    # Each team gets one oscillator and one timebomb
    nteams = 4
    team_assignments = list(range(nteams))
    random.shuffle(team_assignments)

    def _get_oscillator_name():
        if revenge:
            oscillators = ["airforce", "koksgalaxy", "dinnertable", "vring64", "harbor"]
            which_oscillator = random.choice(oscillators)
        else:
            which_oscillator = "quadrupleburloaferimeter"
        return which_oscillator

    rotdegs = [0, 90, 180, 270]


    urls = [None, None, None, None]

    for iteam in range(nteams):
        # Location:
        # x = center + a*L
        # y = center + b*L
        # QI:   a = 1, b = 1
        # QII:  a = -1, b = 1
        # QIII: a = -1, b = -1
        # QIV:  a = 1, b = -1
        if iteam==0 or iteam==3:
            a = 1
        else:
            a = -1

        if iteam==0 or iteam==1:
            b = 1
        else:
            b = -1

        osc_x = centerx + a*L
        osc_y = centery + b*L

        bomb_x = centerx + 2*a*L
        bomb_y = centery + 2*b*L

        # jitter for patterns
        osc_jitter_x = 3
        osc_jitter_y = 3
        timebomb_jitter_x = 6
        timebomb_jitter_y = 6

        osc_pattern = get_grid_pattern(
            _get_oscillator_name(),
            rows,
            cols,
            xoffset=osc_x + random.randint(-osc_jitter_x, osc_jitter_x),
            yoffset=osc_y + random.randint(-osc_jitter_y, osc_jitter_y),
            rotdeg=random.choice(rotdegs),
        )

        bomb_pattern = get_grid_pattern(
            "timebomb",
            rows,
            cols,
            xoffset=bomb_x + random.randint(-timebomb_jitter_x, timebomb_jitter_x),
            yoffset=bomb_y + random.randint(-timebomb_jitter_y, timebomb_jitter_y),
            rotdeg=random.choice(rotdegs),
        )

        team_pattern = pattern_union([osc_pattern, bomb_pattern])
        team_url = pattern2url(team_pattern)

        team_ix = team_assignments[iteam]
        urls[team_ix] = team_url

    return tuple(urls)


def crabs_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    rotdegs = [0, 90, 180, 270]

    jitter = 1

    # 8 crabs total
    centerys = [rows//4, 3*rows//4]
    centerxs = [cols//5, 2*cols//5, 3*cols//5, 4*cols//5]

    nteams = 4
    team_assignments = list(range(nteams))
    random.shuffle(team_assignments)

    crab_patterns = [[], [], [], []]

    for i, (centerx, centery) in enumerate(itertools.product(centerxs, centerys)):
        imod4 = i%4

        crabcenterx = centerx + random.randint(-jitter, jitter)
        crabcentery = centery + random.randint(-jitter, jitter)

        crab = get_grid_pattern(
            "crabstretcher",
            rows,
            cols,
            xoffset=crabcenterx,
            yoffset=crabcentery,
            hflip=(random.random() < 0.5),
            vflip=(random.random() < 0.5),
            rotdeg=random.choice(rotdegs),
        )
        team_ix = team_assignments[imod4]
        team_pattern = crab_patterns[team_ix]
        team_pattern.append(crab)
        crab_patterns[team_ix] = team_pattern

    pattern_unions = [pattern_union(pl) for pl in crab_patterns]
    urls = [pattern2url(pu) for pu in pattern_unions]
    return tuple(urls)

def doublegaussian_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    # Lower bound of 0.10, upper bound of 0.15
    density = 0.10 + random.random() * 0.05

    ncells = rows * cols
    nlivecells = ((ncells * density)//4)*4
    nlivecellspt = nlivecells // 4

    # Variable blobbiness
    stdx = cols// random.randint(8, 16)
    stdy = rows// random.randint(8, 16)

    jitter = 5

    nteams = 4
    team_assignments = list(range(nteams))
    random.shuffle(team_assignments)

    centerxs = [cols//4, 3*cols//4] 
    centerys = [rows//4, 3*rows//4]

    urls = [None, None, None, None]

    master_points = set()
    for i, (centerx, centery) in enumerate(itertools.product(centerxs, centerys)):

        team_ix = team_assignments[i]

        cx = centerx + random.randint(-jitter, jitter)
        cy = centery + random.randint(-jitter, jitter)

        team_points = set()
        while len(team_points) < nlivecellspt:
            randx = int(random.gauss(cx, stdx))
            randy = int(random.gauss(cy, stdy))
            if (randx >= 0 and randx < cols) and (randy >= 0 and randy < rows):
                if (randx, randy) not in master_points:
                    team_points.add((randx, randy))
                    master_points.add((randx, randy))

        # Assemble the circle dot diagram for team
        team_pattern = []
        for y in range(rows):
            this_row = []
            for x in range(cols):
                if (x, y) in team_points:
                    this_row.append("o")
                else:
                    this_row.append(".")
            this_rowstr = "".join(this_row)
            team_pattern.append(this_rowstr)

        team_url = pattern2url(team_pattern)
        urls[team_ix] = team_url

    return tuple(urls)


#@retry_on_failure
def rainbowmath_fourcolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    def is_prime(n):
        n = abs(n)
        if n == 2 or n == 3: return True
        if n < 2 or n%2 == 0: return False
        if n < 9: return True
        if n%3 == 0: return False
        r = int(n**0.5)
        # since all primes > 3 are of the form 6n ± 1
        # start with f=5 (which is prime)
        # and test f, f+2 for being prime
        # then loop by 6.
        f = 5
        while f <= r:
            if n % f == 0: return False
            if n % (f+2) == 0: return False
            f += 6
        return True

    def is_not_prime(n):
        return not is_prime(n)

    # Random choice of which form to use
    #coin = random.randint(1,3)
    coin = 8

    if coin == 1:
        p = random.choice([k*k for k in [5, 7, 9, 11]])
        f = lambda x, y: int(is_not_prime((x*x & y*y) % p))

    elif coin == 2:

        # Linked diagonals of boxes
        ab = [3, 4, 5]
        a = random.choice(ab)
        b = random.choice(ab)

        cs = [16, 18, 20, 22]
        c = random.choice(cs)

        p = 7

        f = lambda x, y: int((x//a ^ y//a)*c % p)

    elif coin == 3:

        # Linked diagonals of very large boxes
        ab = [9, 10, 11]
        a = random.choice(ab)
        b = random.choice(ab)

        cs = [16, 18, 20, 22]
        c = random.choice(cs)

        p = 7

        f = lambda x, y: int((x//a ^ y//a)*c % p)


    elif coin == 4:

        # Sterpinsky triangles
        ps = [7, 11, 13, 15, 35, 37]
        p = random.choice(ps)
        f = lambda x, y: int((x & y) % p)

    elif coin == 5:

        # This is a one-off that's in perfect sync and makes wild patterns
        a = 3
        b = 3
        p = 99
        f = lambda x, y: int((a**x)%p & (b**y)%p)

    elif coin == 6:

        a = random.randint(1,10)
        b = random.randint(1,10)
        p = 99

        f = lambda x, y: int(is_not_prime((a*x & b*y) % p))


    elif coin == 7:

        ps = [81, 83, 85, 87, 89, 91, 93, 95, 97, 99]

        p = random.choice(ps)

        f = lambda x, y: int(is_not_prime((x//(y+1) ^ y) % p))


    elif coin == 8:

        ps = [69, 99, 299, 699, 999]

        f = lambda x, y: int(is_not_prime((x*x//(y+1)) % p))


    xoffset = 0
    yoffset = 0

    team_patterns = _expression_pattern(
        rows,
        cols,
        seed,
        f,
        xoffset=xoffset,
        yoffset=yoffset,
    )

    urls = [pattern2url(pat) for pat in team_patterns]

    for url in urls:
        if url == "[]":
            raise GollyXPatternsError("Error with bitfield: everything is empty")

    return tuple(urls)


def _expression_pattern(
    rows,
    cols,
    seed,
    f_handle,
    xoffset=0,
    yoffset=0,
):
    nteams = 4

    # These store the the .o diagrams (flat=False means these are lists of lists of one char)
    team_patterns = []
    for i in range(nteams):
        tp = get_grid_empty(rows,cols,flat=False)
        team_patterns.append(tp)

    # Assemble a list of cells that are alive at the roots of f (if f returns 0)
    coordinates = []
    for xtrue in range(0, cols):
        for ytrue in range(0, rows):
            xtransform = xtrue - xoffset
            ytransform = ytrue - yoffset
            if f_handle(xtransform, ytransform) == 0:
                coordinates.append((xtrue, ytrue))

    # Shuffle live cell cordinates
    random.shuffle(coordinates)

    # Assign live cell coordinates to teams using serpentine pattern
    team_order = list(range(nteams))
    random.shuffle(team_order)
    serpentine_pattern = list(team_order) + list(reversed(team_order))

    for i, (x, y) in enumerate(coordinates):
        serp_ix = i % len(serpentine_pattern)
        team_ix = serpentine_pattern[serp_ix]
        team_patterns[team_ix][y][x] = "o"

    return team_patterns




