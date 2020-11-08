import random
from .patterns import get_pattern_size, get_grid_pattern, pattern_union
from .utils import pattern2url


def random_twocolor(rows, cols):
    """
    Generate a random two-color list life initialization.

    Returns: two listlife strings, state1 and state2,
    with the random initializations.
    (12% of all cells are alive).

    Strategy: generate a set of (x,y) tuples,
    convert to list, split in half. Use those
    point sets to create listLife URL strings.
    """
    ncells = rows*cols
    nlivecells = ncells*0.12
    points = set()
    while len(points)<nlivecells:
        randy = random.randint(0, rows-1)
        randx = random.randint(0, cols-1) 
        points.add((randx,randy))

    points = list(points)
    points1 = set(points[:len(points)//2])
    points2 = set(points[len(points)//2:])
    pattern1 = []
    pattern2 = []
    for y in range(rows):
        row1 = []
        row2 = []

        # row 1
        for x in range(cols):
            if (x,y) in points1:
                row1.append('o')
            else:
                row1.append('.')
        row1str = "".join(row1)
        pattern1.append(row1str)

        # row 2
        for x in range(cols):
            if (x,y) in points2:
                row2.append('o')
            else:
                row2.append('.')
        row2str = "".join(row2)
        pattern2.append(row2str)

    pattern1_url = pattern2url(pattern1)
    pattern2_url = pattern2url(pattern2)

    return pattern1_url, pattern2_url


def twoacorn_twocolor(rows, cols, seed=None):
    """
    Generate a map wth an acorn on the top and an acorn on the bottom.

    Returns: two listlife strings, state1 and state2,
    with the acorn initializations.

    Strategy:
    - grid size doesn't matter when getting pattern
    - use grid size to determine centerpoints
    - get size of acorn pattern
    - ask for acorn at particular offset
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    die1 = random.randint(1,3)
    if die1 == 1:
        # zone 1
        centerx1 = cols//2 + cols//4
        centery1 = rows//4
    elif die1 == 2:
        # zone 2
        centerx1 = cols//4
        centery1 = rows//4
    else:
        # middle of zone 1 and 2
        centerx1 = cols//2
        centery1 = rows//4

    centerx1 += random.randint(-5, 5)

    die2 = random.randint(1,3)
    if die2 == 1:
        # zone 3
        centerx2 = cols//4
        centery2 = rows//2 + rows//4
    elif die2 == 2:
        # zone 4
        centerx2 = cols//2 + cols//4
        centery2 = rows//2 + rows//4
    else:
        # middle of zone 3 and 4
        centerx2 = cols//2
        centery2 = rows//2 + rows//4

    centerx2 += random.randint(-5, 5)

    pattern1 = get_grid_pattern('acorn', rows, cols, xoffset=centerx1, yoffset=centery1, vflip=True)
    pattern2 = get_grid_pattern('acorn', rows, cols, xoffset=centerx2, yoffset=centery2)

    pattern1_url = pattern2url(pattern1)
    pattern2_url = pattern2url(pattern2)

    return pattern1_url, pattern2_url


def timebomb_oscillators_twocolor(rows, cols, seed=None):
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    centerx1a = cols//2 + cols//4
    centerx1b = cols//4
    centery1a = rows//4
    centery1b = centery1a

    centerx1a += random.randint(-10, 10)
    centerx1b += random.randint(-10, 10)
    centery1a += random.randint(-10, 10)
    centery1b += random.randint(-10, 10)

    osc1a = get_grid_pattern('quadrupleburloaferimeter', rows, cols, xoffset=centerx1a, yoffset=centery1a)
    osc1b = get_grid_pattern('quadrupleburloaferimeter', rows, cols, xoffset=centerx1b, yoffset=centery1b)

    osc_pattern = pattern_union([osc1a, osc1b])

    centerx2 = cols//2
    centery2 = rows//2 + rows//4

    centerx2 += random.randint(-5, 5)
    centery2 += random.randint(-5, 5)

    timebomb = get_grid_pattern('timebomb', rows, cols, xoffset=centerx2, yoffset=centery2)

    pattern1_url = pattern2url(osc_pattern)
    pattern2_url = pattern2url(timebomb)

    return pattern1_url, pattern2_url


def fourrabbits_twocolor(rows, cols, seed=None):
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    rabbit_locations1 = [
        (cols//4, rows//4),
        (cols//2 + cols//4, rows//4),
    ]
    rabbits1 = []
    for (x,y) in rabbit_locations1:
        x += random.randint(-5,5)
        y += random.randint(-5,5)
        vflipopt = bool(random.getrandbits(1))
        hflipopt = bool(random.getrandbits(1))
        rabbit = get_grid_pattern('rabbit', rows, cols, xoffset=x, yoffset=y, vflip=vflipopt, hflip=hflipopt)
        rabbits1.append(rabbit)

    rabbit_locations2 = [
        (cols//4, rows//2 + rows//4),
        (cols//2 + cols//4, rows//2 + rows//4),
    ]
    rabbits2 = []
    for (x,y) in rabbit_locations2:
        x += random.randint(-5,5)
        y += random.randint(-5,5)
        vflipopt = bool(random.getrandbits(1))
        hflipopt = bool(random.getrandbits(1))
        rabbit = get_grid_pattern('rabbit', rows, cols, xoffset=x, yoffset=y, vflip=vflipopt, hflip=hflipopt)
        rabbits2.append(rabbit)

    rabbits_pattern1 = pattern_union(rabbits1)
    rabbits_pattern2 = pattern_union(rabbits2)

    pattern1_url = pattern2url(rabbits_pattern1)
    pattern2_url = pattern2url(rabbits_pattern2)

    return pattern1_url, pattern2_url


def twospaceshipgenerators_twocolor(rows, cols):
    # backrake 2 laying trail of glider ships
    # both backrakes start at very bottom
    # squares in middle, of alternating colors
    (xdim, ydim) = get_pattern_size('backrake2')

    spaceship1x = cols//4;
    spaceship2x = cols//2 + cols//4;
    spaceshipy = rows - 1 - ydim;

    spaceship1x += random.randint(-5,5)
    spaceship2x += random.randint(-5,5)

    generator1 = get_grid_pattern('backrake2', rows, cols, xoffset=spaceship1x, yoffset=spaceshipy, hflip=True)
    generator2 = get_grid_pattern('backrake2', rows, cols, xoffset=spaceship2x, yoffset=spaceshipy)

    nboxes = 15
    interval_height = rows//(nboxes+1)
    box_patterns1 = []
    box_patterns2 = []
    for i in range(nboxes):
        box_x = cols//2
        box_y = (i+1)*(rows//(nboxes+1))

        box_x += random.randint(-5,5)
        box_y += random.randint(-1,1)

        box_pattern = get_grid_pattern('block', rows, cols, xoffset=box_x, yoffset=box_y)
        if (i%2==0):
            box_patterns1.append(box_pattern)
        else:
            box_patterns2.append(box_pattern)

    boxship_pattern1 = pattern_union([generator1] + box_patterns1)
    boxship_pattern2 = pattern_union([generator2] + box_patterns2)

    pattern1_url = pattern2url(boxship_pattern1)
    pattern2_url = pattern2url(boxship_pattern2)

    return pattern1_url, pattern2_url


def eightr_twocolor(rows, cols):

    centerx = cols//2
    centery = rows//2

    # color 1
    r1a = get_grid_pattern(
        'rpentomino', 
        rows, 
        cols, 
        xoffset=centerx - random.randint(5,10), 
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    r1b = get_grid_pattern(
        'rpentomino', 
        rows, 
        cols, 
        xoffset=centerx - random.randint(15,20), 
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    r1c = get_grid_pattern(
        'rpentomino', 
        rows, 
        cols, 
        xoffset=centerx - random.randint(25,30),
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    r1d = get_grid_pattern(
        'rpentomino', 
        rows, 
        cols, 
        xoffset=centerx - random.randint(35,40),
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    s1 = pattern_union([r1a, r1b, r1c, r1d])

    # color 2
    r2a = get_grid_pattern(
        'rpentomino', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(5,10), 
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    r2b = get_grid_pattern(
        'rpentomino', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(15,20), 
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    r2c = get_grid_pattern(
        'rpentomino', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(25,30),
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    r2d = get_grid_pattern(
        'rpentomino', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(35,40),
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    s2 = pattern_union([r2a, r2b, r2c, r2d])

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


def eightpi_twocolor(rows, cols):
    centerx = cols//2
    centery = rows//2

    # color 1
    p1a = get_grid_pattern(
        'piheptomino', 
        rows, 
        cols, 
        xoffset=centerx - random.randint(5,10), 
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    p1b = get_grid_pattern(
        'piheptomino', 
        rows, 
        cols, 
        xoffset=centerx - random.randint(15,20), 
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    p1c = get_grid_pattern(
        'piheptomino', 
        rows, 
        cols, 
        xoffset=centerx - random.randint(25,30),
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    p1d = get_grid_pattern(
        'piheptomino', 
        rows, 
        cols, 
        xoffset=centerx - random.randint(35,40),
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    s1 = pattern_union([p1a, p1b, p1c, p1d])

    # color 2
    p2a = get_grid_pattern(
        'piheptomino', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(5,10), 
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    p2b = get_grid_pattern(
        'piheptomino', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(15,20), 
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    p2c = get_grid_pattern(
        'piheptomino', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(25,30),
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    p2d = get_grid_pattern(
        'piheptomino', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(35,40),
        yoffset=centery + random.randint(-10, 10),
        hflip=bool(random.getrandbits(1)),
        vflip=bool(random.getrandbits(1)),
    )
    s2 = pattern_union([p2a, p2b, p2c, p2d])

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


def twomultum_twocolor(rows, cols):
    centerx = cols//2
    centery1 = rows//2
    centery2 = rows//2 #2*rows//3

    p1 = get_grid_pattern(
        'multuminparvo', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(-10,10), 
        yoffset=centery1 + random.randint(10,30),
        vflip=False
    )

    p2 = get_grid_pattern(
        'multuminparvo', 
        rows, 
        cols, 
        xoffset=centerx + random.randint(-10,10), 
        yoffset=centery2 - random.randint(10,30),
        vflip=True
    )

    pattern1_url = pattern2url(p1)
    pattern2_url = pattern2url(p2)

    return pattern1_url, pattern2_url



