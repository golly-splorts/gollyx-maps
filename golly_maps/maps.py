import json
import os
import random
from .patterns import get_pattern_size, get_grid_pattern, pattern_union
from .utils import pattern2url


#####################################################
# Map patterns API


def _get_patterns_map():
    patterns_map = {
        'random': random_twocolor,
        'randompartition': randompartition_twocolor,
        'quadjustyna': quadjustyna_twocolor,
        'spaceshipcrash': spaceshipcrash_twocolor,
        'spaceshipcluster': spaceshipcluster_twocolor,
        'twoacorn': twoacorn_twocolor,
        'timebomb': timebomb_oscillators_twocolor,
        'fourrabbits': fourrabbits_twocolor,
        'twospaceshipgenerators': twospaceshipgenerators_twocolor,
        'eightr': eightr_twocolor,
        'eightpi': eightpi_twocolor,
        'twomultum': twomultum_twocolor
    }
    return patterns_map


def get_patterns():
    return list(_get_patterns_map().keys())


def get_map(patternname, rows=100, cols=120):
    """.
    Return a JSON dict with map name, zone names, and initial conditions.
    Use a default map size of 120 cols x 100 rows.
    Returns:
    {
        "patternName": y,
        "mapName": z,
        "mapZone1Name": a,
        "mapZone2Name": b,
        "mapZone3Name": c,
        "mapZone4Name": d,
        "url": e,
        "initialConditions1": f,
        "initialConditions2": g,
        "rows": i,
        "columns": j,
        "cellSize:" k
    }
    """
    # Get map data (pattern, name, zone names)
    mapdat = get_map_data(patternname)

    # Get the initial conditions for this map
    s1, s2 = get_pattern_by_name(patternname, rows, cols)
    url = f"?s1={s1}&s2={s2}"
    mapdat['initialConditions1'] = s1
    mapdat['initialConditions2'] = s2
    mapdat['url'] = url

    # Geometry
    mapdat['rows'] = rows
    mapdat['columns'] = cols
    mapdat['cellSize'] = 7

    return mapdat


#####################################################
# Map patterns

def get_all_map_data(season=999):
    """
    Get all map data for the specified season.
    Season is ZERO-INDEXED.
    """
    map_data_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'maps.json')
    with open(map_data_file, 'r') as f:
        mapdat = json.load(f)

    if season < 3:
        filter_patterns = ['random', 'twoacorn', 'timebomb', 'fourrabbits', 'twospaceshipgenerators', 'eightr', 'eightpi', 'twomultum']
        mapdat = [m for m in mapdat if m['patternName'] in filter_patterns]

    return mapdat


def get_map_data(patternname):
    mapdat = get_all_map_data()
    for m in mapdat:
        if m['patternName']==patternname:
            return m
    raise Exception(f"Error: did not find map labels for pattern {patternname} in data/maps.json, available patterns are: {', '.join([m['patternName'] for m in mapdat])}")


def get_pattern_by_name(patternname, rows, cols, seed=None):
    patterns_map = _get_patterns_map()
    f = patterns_map[patternname]
    return f(rows, cols, seed=seed)


def random_twocolor(rows, cols, seed=None):
    """
    Generate a random two-color list life initialization.

    Returns: two listlife strings, state1 and state2,
    with the random initializations.
    (12% of all cells are alive).

    Strategy: generate a set of (x,y) tuples,
    convert to list, split in half. Use those
    point sets to create listLife URL strings.
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)
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

        # team 1 row
        for x in range(cols):
            if (x,y) in points1:
                row1.append('o')
            else:
                row1.append('.')
        row1str = "".join(row1)
        pattern1.append(row1str)

        # team 2 row
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

def randompartition_twocolor(rows, cols, seed=None):
    """
    Generate a two-color map with multiple patterns for each team.
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)
    ncells = rows*cols
    nlivecells = int(ncells*0.12)

    nhpartitions = random.choice([1, 2, 4, 5])
    nvpartitions = random.choice([2, 4, 8])

    w_vpartition = cols//nvpartitions
    h_hpartition = rows//nhpartitions

    team1_points = set()
    while len(team1_points)<nlivecells//2:
        randy = random.randint(0, rows-1)
        randx = random.randint(0, cols-1)
        if (randx//w_vpartition)%2==(randy//h_hpartition)%2:
            team1_points.add((randx, randy))

    team2_points = set()
    while len(team2_points)<nlivecells//2:
        randy = random.randint(0, rows-1)
        randx = random.randint(0, cols-1)
        if (randx//w_vpartition)%2!=(randy//h_hpartition)%2:
            team2_points.add((randx, randy))

    team1_pattern = []
    team2_pattern = []
    for y in range(rows):
        team1_row = []
        team2_row = []

        for x in range(cols):
            if (x,y) in team1_points:
                team1_row.append('o')
            else:
                team1_row.append('.')

            if (x,y) in team2_points:
                team2_row.append('o')
            else:
                team2_row.append('.')

        team1_row_str = "".join(team1_row)
        team2_row_str = "".join(team2_row)
        team1_pattern.append(team1_row_str)
        team2_pattern.append(team2_row_str)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return (s1, s2)

def quadjustyna_twocolor(rows, cols, seed=None):
    """
    Four justyna metheuselas.
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    rotdegs = [0, 90, 180, 270]

    centerx1 = cols//4
    centerx1a = centerx1 + random.randint(-5, 30)
    centerx1b = centerx1 + random.randint(-5, 30)

    centery1a = rows//4 + random.randint(-10, 10)
    centery1b = rows//2 + rows//4 + random.randint(-10, 10)

    j1a = get_grid_pattern(
        'justyna',
        rows,
        cols,
        xoffset=centerx1a,
        yoffset=centery1a,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs)
    )
    j1b = get_grid_pattern(
        'justyna',
        rows,
        cols,
        xoffset=centerx1b,
        yoffset=centery1b,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs)
    )
    j1_pattern = pattern_union([j1a, j1b])

    centerx2 = cols//2 + cols//4
    centerx2a = centerx2 - random.randint(-5, 30)
    centerx2b = centerx2 - random.randint(-5, 30)

    centery2a = rows//4 + random.randint(-10, 10)
    centery2b = rows//2 + rows//4 + random.randint(-10, 10)

    j2a = get_grid_pattern(
        'justyna',
        rows,
        cols,
        xoffset=centerx2a,
        yoffset=centery2a,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs)
    )
    j2b = get_grid_pattern(
        'justyna',
        rows,
        cols,
        xoffset=centerx2b,
        yoffset=centery2b,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs)
    )
    j2_pattern = pattern_union([j2a, j2b])

    s1 = pattern2url(j1_pattern)
    s2 = pattern2url(j2_pattern)

    return (s1, s2)

def spaceshipcrash_twocolor(rows, cols, seed=None):
    """
    Clouds of spaceships in each quadrant crashing into each other at the origin.
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # Spacing between spaceships
    w = 12

    # Spaceship locations for team 1
    s_centerx1 = cols//4
    s_centery1 = rows//3
    s1_locations = []
    for i in [-2, -1, 0, 1]:
        for j in [-2, -1, 0, 1]:
            xx = s_centerx1 + i*w + random.randint(-4, 4)
            yy = s_centery1 + j*w + random.randint(-3, 3)
            s1_locations.append((xx, yy))

    # Spaceship locations for team 2
    s_centerx2 = cols//2 + cols//4
    s_centery2 = rows//3
    s2_locations = []
    for i in [-1, 0, 1, 2]:
        for j in [-3, -2, -1, 0]:
            xx = s_centerx2 + i*w + random.randint(-4, 4)
            yy = s_centery2 + j*w + random.randint(-3, 3)
            s2_locations.append((xx, yy))

    # aferimeter locations for team 1
    b_centerx1 = cols//3 + random.randint(-15, 5)
    b_centery1 = 3*rows//4 + random.randint(0, 8)

    # aferimeter locations for team 2
    b_centerx2 = 2*cols//3 + random.randint(-15, 5)
    b_centery2 = 3*rows//4 + random.randint(0, 8)

    # Assemble and combine spaceship patterns for team 1
    team1_pattern_list = []
    for i in range(len(s1_locations)):
        xx, yy = s1_locations[i]
        p = get_grid_pattern(
            'glider',
            rows,
            cols,
            xoffset=xx,
            yoffset=yy,
            check_overflow = False
        )
        team1_pattern_list.append(p)

    p = get_grid_pattern(
        'quadrupleburloaferimeter',
        rows,
        cols,
        xoffset=b_centerx1,
        yoffset=b_centery1,
    )
    team1_pattern_list.append(p)

    # Assemble and combine spaceship patterns for team 2
    team2_pattern_list = []
    for i in range(len(s2_locations)):
        xx, yy = s2_locations[i]
        p = get_grid_pattern(
            'glider',
            rows,
            cols,
            xoffset=xx,
            yoffset=yy,
            hflip=True,
            check_overflow = False
        )
        team2_pattern_list.append(p)

    p = get_grid_pattern(
        'quadrupleburloaferimeter',
        rows,
        cols,
        xoffset=b_centerx2,
        yoffset=b_centery2,
    )
    team2_pattern_list.append(p)

    team1_pattern = pattern_union(team1_pattern_list)
    team2_pattern = pattern_union(team2_pattern_list)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return (s1, s2)

def spaceshipcluster_twocolor(rows, cols, seed=None):
    """
    Clouds of spaceships in the upper quadrants crashing into burloaferimeters below.
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # Spacing between spaceships
    w = 12

    # Spaceship locations for team 1

    # NW corner
    s_centerx1 = cols//4
    s_centery1 = rows//3
    s1_nw_locations = []
    #for i in [-2, -1, 0, 1]:
    for i in [-2, -1, 0, 1, 2]:
        for j in [-2, -1, 0, 1]:
            xx = s_centerx1 + i*w + random.randint(-4, 4)
            yy = s_centery1 + j*w + random.randint(-3, 3)
            s1_nw_locations.append((xx, yy))

    # SE corner
    s_centerx1 = 3*cols//4
    s_centery1 = 2*rows//3
    s1_se_locations = []
    #for i in [-1, 0, 1, 2]:
    for i in [-2, -1, 0, 1, 2]:
        for j in [-1, 0, 1, 2]:
            xx = s_centerx1 + i*w + random.randint(-4, 4)
            yy = s_centery1 + j*w + random.randint(-3, 3)
            s1_se_locations.append((xx, yy))

    # Spaceship locations for team 2

    # NE corner
    s_centerx2 = 3*cols//4
    s_centery2 = rows//3
    s2_ne_locations = []
    #for i in [-1, 0, 1, 2]:
    for i in [-2, -1, 0, 1, 2]:
        for j in [-2, -1, 0, 1]:
            xx = s_centerx2 + i*w + random.randint(-4, 4)
            yy = s_centery2 + j*w + random.randint(-3, 3)
            s2_ne_locations.append((xx, yy))

    # SW corner
    s_centerx2 = cols//4
    s_centery2 = 2*rows//3
    s2_sw_locations = []
    #for i in [-2, -1, 0 ,1]:
    for i in [-2, -1, 0, 1, 2]:
        for j in [-1, 0, 1, 2]:
            xx = s_centerx2 + i*w + random.randint(-4, 4)
            yy = s_centery2 + j*w + random.randint(-3, 3)
            s2_sw_locations.append((xx, yy))


    # Assemble and combine spaceship patterns for team 1
    team1_pattern_list = []

    for i in range(len(s1_nw_locations)):
        xx, yy = s1_nw_locations[i]
        p = get_grid_pattern(
            'glider',
            rows,
            cols,
            xoffset=xx,
            yoffset=yy,
            check_overflow = False
        )
        team1_pattern_list.append(p)

    for i in range(len(s1_se_locations)):
        xx, yy = s1_se_locations[i]
        p = get_grid_pattern(
            'glider',
            rows,
            cols,
            xoffset=xx,
            yoffset=yy,
            rotdeg=180,
            check_overflow = False
        )
        team1_pattern_list.append(p)


    # Assemble and combine spaceship patterns for team 2
    team2_pattern_list = []
    for i in range(len(s2_ne_locations)):
        xx, yy = s2_ne_locations[i]
        p = get_grid_pattern(
            'glider',
            rows,
            cols,
            xoffset=xx,
            yoffset=yy,
            hflip=True,
            check_overflow = False
        )
        team2_pattern_list.append(p)

    for i in range(len(s2_sw_locations)):
        xx, yy = s2_sw_locations[i]
        p = get_grid_pattern(
            'glider',
            rows,
            cols,
            xoffset=xx,
            yoffset=yy,
            hflip=True,
            rotdeg=180,
            check_overflow = False
        )
        team2_pattern_list.append(p)

    team1_pattern = pattern_union(team1_pattern_list)
    team2_pattern = pattern_union(team2_pattern_list)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return (s1, s2)

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
    centerx1c = cols//2

    centery1a = rows//4
    centery1b = centery1a
    centery1c = centery1a

    centerx1a += random.randint(-8, 8)
    centerx1b += random.randint(-8, 8)
    centerx1c += random.randint(-4, 4)
    centery1a += random.randint(-8, 8)
    centery1b += random.randint(-8, 8)
    centery1c += random.randint(-4, 4) 

    osc1a = get_grid_pattern('quadrupleburloaferimeter', rows, cols, xoffset=centerx1a, yoffset=centery1a)
    osc1b = get_grid_pattern('quadrupleburloaferimeter', rows, cols, xoffset=centerx1b, yoffset=centery1b)
    osc1c = get_grid_pattern('quadrupleburloaferimeter', rows, cols, xoffset=centerx1c, yoffset=centery1c)

    osc_pattern = pattern_union([osc1a, osc1b, osc1c])

    centerx2 = cols//2
    centery2 = 2*rows//3

    centerx2 += random.randint(-8, 8)
    centery2 += random.randint(-8, 8)

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


def twospaceshipgenerators_twocolor(rows, cols, seed=None):
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

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


def eightr_twocolor(rows, cols, seed=None):

    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

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


def eightpi_twocolor(rows, cols, seed=None):

    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

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


def twomultum_twocolor(rows, cols, seed=None):

    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

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

