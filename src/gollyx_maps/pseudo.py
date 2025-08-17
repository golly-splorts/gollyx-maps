from .utils import pattern2url
from .patterns import (
    get_grid_empty,
    get_grid_pattern,
    methuselah_quadrants_pattern,
    pattern_union,
    segment_pattern,
)
from .geom import hflip_pattern, vflip_pattern
import random
import itertools


##############
# Util methods


def get_pseudo_pattern_function_map():
    return {
        "bigsegment": bigsegment_twocolor,
        "gaussian": gaussian_twocolor,
        "lockpickfence": lockpickfence_twocolor,
        "methuselahdense": methuselahdense_twocolor,
        "methuselahsparse": methuselahsparse_twocolor,
        "nastynonominos": nastynonominos_twocolor,
        "stickyheptominos": stickyheptominos_twocolor,
        "patiolights": patiolights_twocolor,
        "random": random_twocolor,
        "randompartition": randompartition_twocolor,
        "randomsegment": randomsegment_twocolor,
        "stretchydog": stretchydog_twocolor,
        "sunburst": sunburst_twocolor,
        "tripledouble": tripledouble_twocolor,
    }


#############
# Map methods


def bigsegment_twocolor(rows, cols, seed=None):
    """
    Form a map from intersecting line segments.
    """

    if seed is not None:
        random.seed(seed)

    possible_nhseg = [3,5]
    possible_nvseg = [1,3,5]
    gap_probability = random.random() * 0.10

    maxdim = max(rows, cols)

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


def gaussian_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)
    ncells = rows * cols
    points = set()
    nlivecells = ncells * 0.15
    centerx = cols//2
    centery = rows//2
    while len(points) < nlivecells:
        randx = int(random.gauss(centerx, centerx//2))
        randy = int(random.gauss(centery, centery//2))
        # Should be >= 0, bug
        if (randx >= 0 and randx < cols) and (randy >= 0 and randy < rows):
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


def lockpickfence_twocolor(rows, cols, seed=None):
    """
    Add 3 lockpick methuselahs in each corner, and separate them with line segments
    """

    if seed is not None:
        random.seed(seed)


    # Make the lockpicks
    # ------------------
    mc = [4]

    team1_lockpicks, team2_lockpicks = methuselah_quadrants_pattern(
        rows, cols, seed, methuselah_counts=mc, methuselah_names=["pseudo_lockpick_heptomino"]
    )

    # Make the fence
    # --------------

    # Always 1 horizontal segment, optional vertical segment
    nhseg = 1
    nvseg = 1

    # Set amount of jitter for placement of segments
    jitterx = 9
    jittery = 9

    # Color mode should be broken
    colormode = "randombroken"

    team1_fence, team2_fence = segment_pattern(
        rows,
        cols,
        seed,
        colormode=colormode,
        nhseg=nhseg,
        nvseg=nvseg,
        jitterx=jitterx,
        jittery=jittery,
    )

    team1_pattern = pattern_union([team1_lockpicks, team1_fence])
    team2_pattern = pattern_union([team2_lockpicks, team2_fence])

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


def _methuselahgrid_twocolor(rows, cols, seed=None, dense=False):

    if seed is not None:
        random.seed(seed)

    if dense:
        mc = [9, 16]
        all_meths = [
            "pseudo_angel_heptomino",
            "pseudo_brass_knuckles_nonomino",
            "pseudo_capacitor_octomino",
            "pseudo_l_pentomino",
            "pseudo_lockpick_heptomino",
            "pseudo_nasty_nonomino",
            "pseudo_raygun_heptomino",
            "pseudo_sticky_heptomino",
            "pseudo_stretchydog_octomino",
            "pseudo_swandive_octomino",
        ]
    else:
        mc = [1, 2, 3, 4]
        all_meths = [
            "pseudo_angel_heptomino",
            "pseudo_boomerang_heptomino",
            "pseudo_brass_knuckles_nonomino",
            "pseudo_broken_l_heptomino",
            "pseudo_capacitor_octomino",
            "pseudo_facade_heptomino",
            "pseudo_flower_pentomino",
            "pseudo_kite_heptomino",
            "pseudo_l_pentomino",
            "pseudo_lockpick_heptomino",
            "pseudo_nasty_nonomino",
            "pseudo_raygun_heptomino",
            "pseudo_reverse_f_heptomino",
            "pseudo_sticky_heptomino",
            "pseudo_stretchydog_octomino",
            "pseudo_swandive_octomino",
            "pseudo_t_heptomino",
        ]

    if random.random() < 0.05:
        # Infrequently, we pick a single methuselah pattern for every spot
        all_meths = [random.choice(all_meths)]

    team1_pattern, team2_pattern = methuselah_quadrants_pattern(
        rows, cols, seed, methuselah_counts=mc, methuselah_names=all_meths
    )
    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)
    return pattern1_url, pattern2_url


def methuselahdense_twocolor(rows, cols, seed=None):
    """
    Create a densely-packed grid of methuselah patterns
    """
    return _methuselahgrid_twocolor(rows, cols, seed, dense=True)


def methuselahsparse_twocolor(rows, cols, seed=None):
    """
    Create a sparsely-packed grid of methuselah patterns
    """
    return _methuselahgrid_twocolor(rows, cols, seed, dense=True)


def nastynonominos_twocolor(rows, cols, seed=None):
    """
    A row of nasty nonominos, with jitter and randomly oriented.
    """

    if seed is not None:
        random.seed(seed)

    centerx = cols // 2
    centery = rows // 2

    # Place one methuselah every N grid spaces
    # maximum number - 1
    n = 10
    maxshapes = centerx // n
    c1patterns = []
    c2patterns = []
    for i in range(maxshapes - 1):
        end = (i + 1) * n
        start = end - n//2
        yjitter = 10
        pattern1 = get_grid_pattern(
            #"pseudo_sticky_heptomino",
            "pseudo_nasty_nonomino",
            rows,
            cols,
            xoffset=centerx - random.randint(start, end),
            yoffset=centery + random.randint(-yjitter, yjitter),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c1patterns.append(pattern1)

        pattern2 = get_grid_pattern(
            #"pseudo_sticky_heptomino",
            "pseudo_nasty_nonomino",
            rows,
            cols,
            xoffset=centerx + random.randint(start, end),
            yoffset=centery + random.randint(-yjitter, yjitter),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c2patterns.append(pattern2)

    s1 = pattern_union(c1patterns)
    s2 = pattern_union(c2patterns)

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


def stickyheptominos_twocolor(rows, cols, seed=None):
    """
    A row sticky heptominos, with jitter and randomly oriented.
    """

    if seed is not None:
        random.seed(seed)

    centerx = cols // 2
    centery = rows // 2

    # Place one methuselah every N grid spaces
    # maximum number - 1
    n = 10
    maxshapes = centerx // n
    c1patterns = []
    c2patterns = []
    for i in range(maxshapes - 1):
        end = (i + 1) * n
        start = end - n//2
        yjitter = 10
        pattern1 = get_grid_pattern(
            "pseudo_sticky_heptomino",
            rows,
            cols,
            xoffset=centerx - random.randint(start, end),
            yoffset=centery + random.randint(-yjitter, yjitter),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c1patterns.append(pattern1)

        pattern2 = get_grid_pattern(
            "pseudo_sticky_heptomino",
            rows,
            cols,
            xoffset=centerx + random.randint(start, end),
            yoffset=centery + random.randint(-yjitter, yjitter),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c2patterns.append(pattern2)

    u1 = pattern_union(c1patterns)
    u2 = pattern_union(c2patterns)

    pattern1_url = pattern2url(u1)
    pattern2_url = pattern2url(u2)

    return pattern1_url, pattern2_url


def patiolights_twocolor(rows, cols, seed=None):
    """
    Patio lights pattern is a line segments with boxes placed randomly along the segment, like a string of lights
    """

    if seed is not None:
        random.seed(seed)

    nsegments = 2
    thickness = random.randint(1, 3)

    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    jitterx = 4
    jittery = 10
    intersectys = [(j+1)*rows//(nsegments+1) + random.randint(-jittery, jittery) for j in range(nsegments)]
    random.shuffle(intersectys)

    def _get_bounds(z, dim):
        zstart = z - dim//2
        zend = z + (dim - dim//2)
        return zstart, zend

    # Add the string
    y1s = intersectys[:len(intersectys)//2]
    y2s = intersectys[len(intersectys)//2:]
    for ix in range(0, cols):

        for y1 in y1s:
            for iy in range(*_get_bounds(y1, thickness)):
                team1_pattern[iy][ix] = 'o'

        for y2 in y2s:
            for iy in range(*_get_bounds(y2, thickness)):
                team2_pattern[iy][ix] = 'o'

    # Add some lights to the string

    for y1 in y1s:
        b = _get_bounds(y1, thickness)
        maxy = max(b)
        miny = min(b)
        ylightstop = miny - random.randint(2, 3)
        ylightsbot = maxy + random.randint(2, 3)
        ix = random.randint(4, 12)
        while ix < cols-1:
            if random.random() < 0.50:
                team1_pattern[ylightsbot][ix] = 'o'
                team1_pattern[ylightsbot][ix+1] = 'o'
                team1_pattern[ylightsbot+1][ix] = 'o'
                team1_pattern[ylightsbot+1][ix+1] = 'o'
            else:
                team1_pattern[ylightstop][ix] = 'o'
                team1_pattern[ylightstop][ix+1] = 'o'
                team1_pattern[ylightstop-1][ix] = 'o'
                team1_pattern[ylightstop-1][ix+1] = 'o'
            ix += random.randint(10, 12) + random.randint(-jitterx, jitterx)

    for y2 in y2s:
        b = _get_bounds(y2, thickness)
        maxy = max(b)
        miny = min(b)
        ylightstop = miny - random.randint(2, 3)
        ylightsbot = maxy + random.randint(2, 3)
        ix = random.randint(4, 12)
        while ix < cols-1:
            if random.random() < 0.50:
                team2_pattern[ylightsbot][ix] = 'o'
                team2_pattern[ylightsbot][ix+1] = 'o'
                team2_pattern[ylightsbot+1][ix] = 'o'
                team2_pattern[ylightsbot+1][ix+1] = 'o'
            else:
                team2_pattern[ylightstop][ix] = 'o'
                team2_pattern[ylightstop][ix+1] = 'o'
                team2_pattern[ylightstop-1][ix] = 'o'
                team2_pattern[ylightstop-1][ix+1] = 'o'
            ix += random.randint(10, 12) + random.randint(-jitterx, jitterx)

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


def random_twocolor(rows, cols, seed=None):
    """
    Make 15% of cells come alive.
    Split them evenly between two colors.
    """

    if seed is not None:
        random.seed(seed)

    ncells = rows * cols
    nlivecells = ncells * 0.15
    points = set()
    centerx = rows//2
    centery = cols//2
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


def randompartition_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    ncells = rows * cols
    nlivecells = int(ncells * 0.15)

    mindim = min(rows, cols)
    nhpartitions = random.choice([1, 2, 4, 6])
    nvpartitions = random.choice([2, 4, 8])

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

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


def randomsegment_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    possible_nhseg = [3,5]
    possible_nvseg = [1,3,5]
    gap_probability = random.random() * 0.10

    maxdim = max(rows, cols)

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


def stretchydog_twocolor(rows, cols, seed=None):
    """
    Create a methuselah grid with 3 stretchydogs in each corner
    """

    if seed is not None:
        random.seed(seed)

    mc = [3]

    team1_pattern, team2_pattern = methuselah_quadrants_pattern(
        rows, cols, seed, methuselah_counts=mc, methuselah_names=["pseudo_stretchydog_octomino"]
    )

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)
    return pattern1_url, pattern2_url


def sunburst_twocolor(rows, cols, seed=None):
    """
    Populate the grid with points that are Gaussian normal distributed
    about the center, but only if slope is positive, and with color
    determined by slope. We then reflect the points of one color,
    which creates a nice sunburst shape.
    """

    SMOL = 1e-12

    if seed is not None:
        random.seed(seed)

    ncells = rows * cols
    nlivecells = ncells * 0.10

    centerx = cols // 2
    centery = rows // 2

    team1_points = set()
    team2_points = set()

    while (
        len(team1_points) < nlivecells // 2
        and
        len(team2_points) < nlivecells // 2
    ):
        randx = int(random.gauss(centerx, centerx//2))
        randy = int(random.gauss(centery, centery//2))

        g = 2.5

        slope = (randy - centery)/(randx - centerx + SMOL)

        if slope > 0:

            if slope < 1/g:
                team2_points.add((randx, randy))
            elif slope < 1:
                team1_points.add((randx, randy))
            elif slope < g:
                team2_points.add((randx, randy))
            else:
                team1_points.add((randx, randy))

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

    if bool(random.getrandbits(1)):
        # swap
        temp = team1_pattern
        team1_pattern = team2_pattern
        team2_pattern = temp

    if bool(random.getrandbits(1)):
        team1_pattern = vflip_pattern(team1_pattern)
        team2_pattern = vflip_pattern(team2_pattern)

    s1 = pattern2url(hflip_pattern(team1_pattern))
    s2 = pattern2url(team2_pattern)

    return (s1, s2)


def tripledouble_twocolor(rows, cols, seed=None):
    """
    Create intersecting segments that are 2-3 cells thick.
    Punch out the middle. Keep them all solid. Makes very
    interesting patterns.
    """
    if seed is not None:
        random.seed(seed)

    thickness = random.randint(2, 4)

    if random.random() < 0.33:
        nsegments = 4
        jitterx = 6
        jittery = 6
    else:
        nsegments = 2
        jitterx = 15
        jittery = 15

    intersectxs = [(i+1)*cols//(nsegments+1) + random.randint(-jitterx, jitterx) for i in range(nsegments)]
    intersectys = [(j+1)*rows//(nsegments+1) + random.randint(-jittery, jittery) for j in range(nsegments)]

    random.shuffle(intersectxs)
    random.shuffle(intersectys)

    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    def _get_bounds(z, dim):
        zstart = z - dim//2
        zend = z + (dim - dim//2)
        return zstart, zend

    x1s = intersectxs[:len(intersectxs)//2]
    x2s = intersectxs[len(intersectxs)//2:]
    for iy in range(0, rows):
        
        for x1 in x1s:
            for ix in range(*_get_bounds(x1, thickness)):
                team1_pattern[iy][ix] = 'o'

        for x2 in x2s:
            for ix in range(*_get_bounds(x2, thickness)):
                team2_pattern[iy][ix] = 'o'

    y1s = intersectys[:len(intersectys)//2]
    y2s = intersectys[len(intersectys)//2:]
    for ix in range(0, cols):

        for y1 in y1s:
            for iy in range(*_get_bounds(y1, thickness)):
                team1_pattern[iy][ix] = 'o'

        for y2 in y2s:
            for iy in range(*_get_bounds(y2, thickness)):
                team2_pattern[iy][ix] = 'o'

    # Punch out squares at the intersections
    for (x, y) in itertools.product(intersectxs, intersectys):
        for ix in range(*_get_bounds(x, thickness)):
            for iy in range(*_get_bounds(y, thickness)):
                team1_pattern[iy][ix] = '.'
                team2_pattern[iy][ix] = '.'

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url

