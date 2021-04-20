import itertools
from operator import itemgetter
import json
import os
import random
from .geom import hflip_pattern, vflip_pattern, rot_pattern
from .patterns import (
    get_pattern_size,
    get_pattern_livecount,
    get_grid_pattern,
    get_grid_empty,
    segment_pattern,
    methuselah_quadrants_pattern,
    pattern_union,
    cloud_region,
)
from .utils import pattern2url, retry_on_failure
from .error import GollyXPatternsError, GollyXMapsError


##############
# Util methods


def get_toroidal_pattern_function_map():
    return {
        "donutpi": donutpi_twocolor,
        "doublegaussian": doublegaussian_twocolor,
        "donutcore": donutengine_twocolor,
        "quadjustyna": donutquadjustyna_twocolor,
        "donutrandom": donutrandom_twocolor,
        "donutrandompartition": donutrandompartition_twocolor,
        "donuttimebomb": donuttimebomb_twocolor,
        "donuttimebombredux": donuttimebombredux_twocolor,
        "donutmultums": donutmultums_twocolor,
        "bigsegment": donutsegment_twocolor,
        "randomsegment": donutrandomsegment_twocolor,
        "donutmethuselahs": donutmethuselahs_twocolor,
        "donutmath": donutmath_twocolor,
        "randys": randys_twocolor,
        "porchlights": porchlights_twocolor,
        "crabdonuts": crabdonuts_twocolor,
    }


def toroidal_methuselah_quadrants_pattern(
    rows, cols, seed=None, hmc=None, fixed_methuselah=None
):
    methuselah_names = [
        "bheptomino",
        "cheptomino",
        "eheptomino",
        "piheptomino",
        "rabbit",
        "rpentomino",
    ]

    # For toroids, always one row of methuselahs per quadrant
    # Only parameter to modify is number of methuselahs in each quadrant row
    # e.g., hmc = 4 means 4 methuselahs in one row, per quadrant
    if hmc is None:
        hmcs = [1, 2, 3, 4]
    else:
        hmcs = [hmc]

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
        hmcount = random.choice(hmcs)

        jitterx = 3 + (10 - hmcount)
        jittery = 3

        for bi in buddy_index:
            corner = quadrants[bi][1]

            # Number of slices, and partitions those slices form, inside the quadrant
            nslices = hmcount
            nparts = nslices + 1

            for a in range(1, nparts):

                y = corner[0] + (rows // 4) + random.randint(-jittery, jittery)
                x = (
                    corner[1]
                    + a * ((cols // 2) // nparts)
                    + random.randint(-jitterx, jitterx)
                )

                if fixed_methuselah:
                    meth = fixed_methuselah
                else:
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


#############
# Map methods


@retry_on_failure
def donutpi_twocolor(rows, cols, seed=None):
    """
    Fill a row with pi heptominos
    """
    if seed is not None:
        random.seed(seed)

    centerx = cols // 2
    centery = rows // 2

    # Place one pi omino every 10 grid spaces,
    # maximum number - 1
    maxshapes = centerx // 10
    c1patterns = []
    c2patterns = []
    for i in range(maxshapes - 1):
        end = (i + 1) * 10
        start = end - 5
        pattern1 = get_grid_pattern(
            "piheptomino",
            rows,
            cols,
            xoffset=centerx - random.randint(start, end),
            yoffset=centery + random.randint(-10, 10),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c1patterns.append(pattern1)

        pattern2 = get_grid_pattern(
            "piheptomino",
            rows,
            cols,
            xoffset=centerx + random.randint(start, end),
            yoffset=centery + random.randint(-10, 10),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c2patterns.append(pattern2)

    s1 = pattern_union(c1patterns)
    s2 = pattern_union(c2patterns)

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


def doublegaussian_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    # Lower bound of 0.10, upper bound of 0.18
    density = 0.10 + random.random() * 0.08

    ncells = rows * cols
    nlivecells = ncells * density
    nlivecellspt = nlivecells // 2

    stdx = cols // random.randint(10, 16)
    stdy = rows // random.randint(3, 8)

    # Left gaussian
    centerx = cols // 3
    centery = rows // 2
    left_points = set()
    while len(left_points) < nlivecellspt:
        randx = int(random.gauss(centerx, stdx))
        randy = int(random.gauss(centery, stdy))
        if (randx >= 0 and randx < cols) and (randy >= 0 and randy < rows):
            left_points.add((randx, randy))

    # Right gaussian
    centerx = 2 * cols // 3
    centery = rows // 2
    right_points = set()
    while len(right_points) < nlivecellspt:
        randx = int(random.gauss(centerx, stdx))
        randy = int(random.gauss(centery, stdy))
        if (randx >= 0 and randx < cols) and (randy >= 0 and randy < rows):
            right_points.add((randx, randy))

    # Assign teams left/right side
    if random.random() < 0.50:
        points1 = left_points
        points2 = right_points
    else:
        points1 = right_points
        points2 = left_points

    # Assemble the circle dot diagram
    pattern1 = []
    pattern2 = []
    for y in range(rows):
        row1 = []
        row2 = []

        # team 1 row
        for x in range(cols):
            if (x, y) in points1:
                row1.append("o")
            else:
                row1.append(".")
        row1str = "".join(row1)
        pattern1.append(row1str)

        # team 2 row
        for x in range(cols):
            if (x, y) in points2:
                row2.append("o")
            else:
                row2.append(".")
        row2str = "".join(row2)
        pattern2.append(row2str)

    pattern1_url = pattern2url(pattern1)
    pattern2_url = pattern2url(pattern2)

    return pattern1_url, pattern2_url


def donutengine_twocolor(rows, cols, seed=None):
    team1_pattern, team2_pattern = toroidal_methuselah_quadrants_pattern(
        rows, cols, seed=seed, fixed_methuselah="switchengine"
    )
    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)
    return pattern1_url, pattern2_url


def donutquadjustyna_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    rotdegs = [0, 90, 180, 270]

    centery = rows // 2
    centerxs = [cols // 5, 2 * cols // 5, 3 * cols // 5, 4 * cols // 5]

    justynas = []
    for centerx in centerxs:

        justcenterx = centerx + random.randint(-8, 8)
        justcentery = centery + random.randint(-8, 8)

        just = get_grid_pattern(
            "justyna",
            rows,
            cols,
            xoffset=justcenterx,
            yoffset=justcentery,
            hflip=(random.random() < 0.5),
            vflip=(random.random() < 0.5),
            rotdeg=random.choice(rotdegs),
        )
        justynas.append(just)

    random.shuffle(justynas)

    team1_pattern = pattern_union([justynas[0], justynas[1]])
    team2_pattern = pattern_union([justynas[2], justynas[3]])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return (s1, s2)


def donutrandom_twocolor(rows, cols, seed=None):
    """
    Generate random two-color initial grid
    """
    if seed is not None:
        random.seed(seed)
    ncells = rows * cols
    nlivecells = ncells * 0.12
    points = set()
    while len(points) < nlivecells:
        randy = random.randint(0, rows - 1)
        randx = random.randint(0, cols - 1)
        points.add((randx, randy))

    points = list(points)
    points1 = set(points[: len(points) // 2])  # noqa
    points2 = set(points[len(points) // 2 :])  # noqa
    pattern1 = []
    pattern2 = []
    for y in range(rows):
        row1 = []
        row2 = []

        # team 1 row
        for x in range(cols):
            if (x, y) in points1:
                row1.append("o")
            else:
                row1.append(".")
        row1str = "".join(row1)
        pattern1.append(row1str)

        # team 2 row
        for x in range(cols):
            if (x, y) in points2:
                row2.append("o")
            else:
                row2.append(".")
        row2str = "".join(row2)
        pattern2.append(row2str)

    pattern1_url = pattern2url(pattern1)
    pattern2_url = pattern2url(pattern2)

    return pattern1_url, pattern2_url


def donutrandompartition_twocolor(rows, cols, seed=None):
    """
    Generate a two-color random map, and assign points to colors
    after subdividing the grid into rectangles.
    """
    if seed is not None:
        random.seed(seed)

    ncells = rows * cols
    density = 0.10 + random.random() * 0.05
    nlivecells = int(ncells * density)

    mindim = min(rows, cols)
    nhpartitions = random.choice([1, 2, 4, 6, 8])
    nvpartitions = random.choice([1, 2, 4, 6, 8, 10, 12])

    w_vpartition = cols // nvpartitions
    h_hpartition = rows // nhpartitions

    team1_points = set()
    while len(team1_points) < nlivecells // 2:
        randy = random.randint(0, rows - 1)
        randx = random.randint(0, cols - 1)
        if (randx // w_vpartition) % 2 == (randy // h_hpartition) % 2:
            team1_points.add((randx, randy))

    team2_points = set()
    while len(team2_points) < nlivecells // 2:
        randy = random.randint(0, rows - 1)
        randx = random.randint(0, cols - 1)
        if (randx // w_vpartition) % 2 != (randy // h_hpartition) % 2:
            team2_points.add((randx, randy))

    team1_pattern = []
    team2_pattern = []
    for y in range(rows):
        team1_row = []
        team2_row = []

        for x in range(cols):
            if (x, y) in team1_points:
                team1_row.append("o")
            else:
                team1_row.append(".")

            if (x, y) in team2_points:
                team2_row.append("o")
            else:
                team2_row.append(".")

        team1_row_str = "".join(team1_row)
        team2_row_str = "".join(team2_row)
        team1_pattern.append(team1_row_str)
        team2_pattern.append(team2_row_str)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return (s1, s2)


def donuttimebomb_twocolor(rows, cols, seed=None):
    return _timebomb_oscillators_twocolor(rows, cols, revenge=False, seed=seed)


def donuttimebombredux_twocolor(rows, cols, seed=None):
    return _timebomb_oscillators_twocolor(rows, cols, revenge=True, seed=seed)


def _timebomb_oscillators_twocolor(rows, cols, revenge, seed=None):

    if seed is not None:
        random.seed(seed)

    centerx = cols // 2
    centery = rows // 2

    osc_x = [
        1 * cols // 9,
        2 * cols // 9,
        3 * cols // 9,
        5 * cols // 9,
        6 * cols // 9,
        7 * cols // 9,
    ]
    osc_y = [
        centery,
    ] * 6

    timebomb_x = [
        4 * cols // 9,
        8 * cols // 9,
    ]
    timebomb_y = [
        centery,
    ] * 2

    def _get_oscillator_name():
        if revenge:
            oscillators = ["airforce", "koksgalaxy", "dinnertable", "vring64", "harbor"]
            which_oscillator = random.choice(oscillators)
        else:
            which_oscillator = "quadrupleburloaferimeter"
        return which_oscillator

    # jitter for patterns
    osc_jitter_x = 1  # 5
    osc_jitter_y = 1  # 5
    timebomb_jitter_x = 1  # 8
    timebomb_jitter_y = 1  # 8

    # Team assignments - even
    osc_team_ass = [1, 1, 1, 2, 2, 2]
    timebomb_team_ass = [2, 1]

    if random.random() < 0.50:
        osc_team_ass.reverse()

    if random.random() < 0.50:
        timebomb_team_ass.reverse()

    if random.random() < 0.50:
        random.shuffle(osc_team_ass)

    # Assemble the team patterns
    team1_patterns = []
    team2_patterns = []

    # Assemble the oscillator patterns
    for k, (oscxx, oscyy, team_ass) in enumerate(zip(osc_x, osc_y, osc_team_ass)):
        pattern = get_grid_pattern(
            _get_oscillator_name(),
            rows,
            cols,
            xoffset=oscxx + random.randint(-osc_jitter_x, osc_jitter_x),
            yoffset=oscyy + random.randint(-osc_jitter_y, osc_jitter_y),
        )
        if team_ass == 1:
            team1_patterns.append(pattern)
        else:
            team2_patterns.append(pattern)

    # Assemble the timebomb patterns
    for k, (timebombxx, timebombyy, team_ass) in enumerate(
        zip(timebomb_x, timebomb_y, timebomb_team_ass)
    ):
        do_rotate = random.random() < 0.5
        do_vflip = bool(random.getrandbits(1))

        rotdeg = 0
        if do_rotate:
            if k == 0:
                rotdeg = 90
            elif k == 1:
                rotdeg = 270

        # We have to rotate first, then hflip, so don't provide hflip argument here
        pattern = get_grid_pattern(
            "timebomb",
            rows,
            cols,
            xoffset=timebombxx + random.randint(-timebomb_jitter_x, timebomb_jitter_x),
            yoffset=timebombyy + random.randint(-timebomb_jitter_y, timebomb_jitter_y),
            rotdeg=rotdeg,
        )

        if do_vflip:
            pattern = vflip_pattern(pattern)

        if team_ass == 1:
            team1_patterns.append(pattern)
        else:
            team2_patterns.append(pattern)

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


def donutmultums_twocolor(rows, cols, seed=None):
    """
    Scattered multums across the map
    """
    if seed is not None:
        random.seed(seed)

    L = 22

    multum_x_loc = [
        cols // 2 - 4 * L,
        cols // 2 - 3 * L,
        cols // 2 - 2 * L,
        cols // 2 - L,
        cols // 2 + L,
        cols // 2 + 2 * L,
        cols // 2 + 3 * L,
        cols // 2 + 4 * L,
    ]

    multum_y_loc = [rows // 2]

    npoints = len(multum_x_loc) * len(multum_y_loc)
    team_assignments = [
        1,
    ] * (npoints // 2)
    team_assignments += [
        2,
    ] * (npoints - npoints // 2)
    random.shuffle(team_assignments)

    jitterx = 8
    jittery = 6

    team1_patterns = []
    team2_patterns = []
    for i, (x, y) in enumerate(itertools.product(multum_x_loc, multum_y_loc)):
        m = get_grid_pattern(
            "multuminparvo",
            rows,
            cols,
            xoffset=x + random.randint(-jitterx, jitterx),
            yoffset=y + random.randint(-jittery, jittery),
            vflip=(y < rows // 2 or random.random() < 0.25),
        )
        if team_assignments[i] == 1:
            team1_patterns.append(m)
        else:
            team2_patterns.append(m)

    s1 = pattern_union(team1_patterns)
    s2 = pattern_union(team2_patterns)

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


def donutsegment_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    possible_nhseg = [0, 1, 3]

    possible_nvseg = [1, 2, 3, 5]

    maxdim = max(rows, cols)
    gap_probability = random.random() * 0.05

    nhseg = 0
    nvseg = 0
    while (nhseg == 0 and nvseg == 0) or (nhseg % 2 != 0 and nvseg == 0):
        nhseg = random.choice(possible_nhseg)
        nvseg = random.choice(possible_nvseg)

    jitterx = 15
    jittery = 15

    team1_pattern, team2_pattern = segment_pattern(
        rows,
        cols,
        seed,
        colormode="classic",
        nhseg=nhseg,
        nvseg=nvseg,
        jitterx=jitterx,
        jittery=jittery,
        gap_probability=gap_probability,
    )

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


def donutrandomsegment_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    nhseg = random.randint(0, 4)
    nvseg = random.randint(1, 10)

    jitterx = 6
    jittery = 8

    gap_probability = random.random() * 0.06

    team1_pattern, team2_pattern = segment_pattern(
        rows,
        cols,
        seed,
        colormode="random",
        nhseg=nhseg,
        nvseg=nvseg,
        jitterx=jitterx,
        jittery=jittery,
        gap_probability=gap_probability,
    )

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


def donutmethuselahs_twocolor(rows, cols, seed=None):
    team1_pattern, team2_pattern = toroidal_methuselah_quadrants_pattern(
        rows, cols, seed=seed
    )
    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)
    return pattern1_url, pattern2_url


@retry_on_failure
def donutmath_twocolor(rows, cols, seed=None):

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
    coin = random.random()

    if coin < 0.33:
        p = random.choice([7, 11, 13, 19, 23, 25, 27, 32, 37, 47, 57, 77, 99])
        f = lambda x, y: int(is_not_prime((x*x & y*y) % p))

    elif coin < 0.66:
        p = random.choice([7, 11, 13, 19, 23, 25, 27, 32, 37, 47, 57, 77, 99])
        f = lambda x, y: int(is_not_prime((x & y) % p))

    else:
        p = random.choice([27, 32, 37, 47, 57, 77, 99])
        f = lambda x, y: int(is_not_prime((x ^ y) % p))

    xoffset = 0
    yoffset = 0

    team1_pattern, team2_pattern = _expression_pattern(
        rows,
        cols,
        seed,
        f,
        xoffset=xoffset,
        yoffset=yoffset,
    )

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    if pattern1_url == "[]" or pattern2_url == "[]":
        raise GollyXPatternsError("Error with bitfield: everything is empty")

    return pattern1_url, pattern2_url


def _expression_pattern(
    rows,
    cols,
    seed,
    f_handle,
    xoffset=0,
    yoffset=0,
):
    # These store the the .o diagrams (flat=False means these are lists of lists of one char)
    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    # Not the most efficient way, but the lazy way

    # Assemble a list of live cell coordinates
    coordinates = []
    for xtrue in range(0, cols):
        for ytrue in range(0, rows):
            xtransform = xtrue - xoffset
            ytransform = ytrue - yoffset
            if f_handle(xtransform, ytransform) == 0:
                coordinates.append((xtrue, ytrue))

    # Shuffle live cell cordinates
    random.shuffle(coordinates)

    # Assign live cell coordinates to team 1/2 using serpentine pattern
    serpentine_pattern = [1, 2, 2, 1]
    for i, (x, y) in enumerate(coordinates):
        serpix = i % len(serpentine_pattern)
        serp_team = serpentine_pattern[serpix]
        if serp_team == 1:
            team1_pattern[y][x] = "o"
        elif serp_team == 2:
            team2_pattern[y][x] = "o"

    return team1_pattern, team2_pattern


@retry_on_failure
def randys_twocolor(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)

    centerx = cols // 2
    centery = rows // 2

    # Place one r omino every 15 grid spaces,
    # maximum number - 1
    maxshapes = centerx // 15
    c1patterns = []
    c2patterns = []
    for i in range(maxshapes - 1):
        end = (i + 1) * 15
        start = end - 7
        pattern1 = get_grid_pattern(
            "rpentomino",
            rows,
            cols,
            xoffset=centerx - random.randint(start, end),
            yoffset=centery + random.randint(-12, 12),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c1patterns.append(pattern1)

        pattern2 = get_grid_pattern(
            "rpentomino",
            rows,
            cols,
            xoffset=centerx + random.randint(start, end),
            yoffset=centery + random.randint(-12, 12),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c2patterns.append(pattern2)

    s1 = pattern_union(c1patterns)
    s2 = pattern_union(c2patterns)

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


def porchlights_twocolor(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)

    nsegments = 2
    thickness = random.randint(1, 3)

    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    jitterx = 4
    jittery = 4
    intersectys = [
        (j + 1) * rows // (nsegments + 1) + random.randint(-jittery, jittery)
        for j in range(nsegments)
    ]
    random.shuffle(intersectys)

    def _get_bounds(z, dim):
        zstart = z - dim // 2
        zend = z + (dim - dim // 2)
        return zstart, zend

    # Add the string
    y1s = intersectys[: len(intersectys) // 2]
    y2s = intersectys[len(intersectys) // 2 :]
    for ix in range(0, cols):

        for y1 in y1s:
            for iy in range(*_get_bounds(y1, thickness)):
                team1_pattern[iy][ix] = "o"

        for y2 in y2s:
            for iy in range(*_get_bounds(y2, thickness)):
                team2_pattern[iy][ix] = "o"

    # Add some lights to the string

    for y1 in y1s:
        b = _get_bounds(y1, thickness)
        maxy = max(b)
        miny = min(b)
        ylightstop = miny - random.randint(2, 3)
        ylightsbot = maxy + random.randint(2, 3)
        ix = random.randint(4, 12)
        while ix < cols - 1:
            if random.random() < 0.50:
                team1_pattern[ylightsbot][ix] = "o"
                team1_pattern[ylightsbot][ix + 1] = "o"
                team1_pattern[ylightsbot + 1][ix] = "o"
                team1_pattern[ylightsbot + 1][ix + 1] = "o"
            else:
                team1_pattern[ylightstop][ix] = "o"
                team1_pattern[ylightstop][ix + 1] = "o"
                team1_pattern[ylightstop - 1][ix] = "o"
                team1_pattern[ylightstop - 1][ix + 1] = "o"
            ix += random.randint(10, 12) + random.randint(-jitterx, jitterx)

    for y2 in y2s:
        b = _get_bounds(y2, thickness)
        maxy = max(b)
        miny = min(b)
        ylightstop = miny - random.randint(2, 3)
        ylightsbot = maxy + random.randint(2, 3)
        ix = random.randint(4, 12)
        while ix < cols - 1:
            if random.random() < 0.50:
                team2_pattern[ylightsbot][ix] = "o"
                team2_pattern[ylightsbot][ix + 1] = "o"
                team2_pattern[ylightsbot + 1][ix] = "o"
                team2_pattern[ylightsbot + 1][ix + 1] = "o"
            else:
                team2_pattern[ylightstop][ix] = "o"
                team2_pattern[ylightstop][ix + 1] = "o"
                team2_pattern[ylightstop - 1][ix] = "o"
                team2_pattern[ylightstop - 1][ix + 1] = "o"
            ix += random.randint(10, 12) + random.randint(-jitterx, jitterx)

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


def crabdonuts_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    rotdegs = [0, 90, 180, 270]

    centery = rows // 2
    centerxs = [cols // 5, 2 * cols // 5, 3 * cols // 5, 4 * cols // 5]

    crabs = []
    for centerx in centerxs:

        crabcenterx = centerx + random.randint(-8, 8)
        crabcentery = centery + random.randint(-8, 8)

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
        crabs.append(crab)

    random.shuffle(crabs)

    team1_pattern = pattern_union([crabs[0], crabs[1]])
    team2_pattern = pattern_union([crabs[2], crabs[3]])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return (s1, s2)
