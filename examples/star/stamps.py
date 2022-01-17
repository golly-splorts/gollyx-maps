from gollyx_maps.patterns import pattern_union, get_grid_empty
from gollyx_maps.utils import pattern2url
import itertools
import random
import os


def stamps_containment_lines(rows, cols, seed=None):
    """
    Create a containment map - surround a stamp
    with some solid square lines of sufficient thickness
    to keep everything contained.
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    team1_lines = get_grid_empty(rows, cols, flat=False)
    team2_lines = get_grid_empty(rows, cols, flat=False)

    # There are a lot of ways to do this.
    # * cracks:
    #   * completely sealed
    #   * one-cell crack
    # * different stamps
    # 
    # for later methods:
    # * line patterns:
    #   * parallel lines
    #   * rectangle
    #   * square

    # --------------
    # Parameters:

    stamps_per_team = 3

    # Thickness of >= 2 is impenetrable
    thickness = 2

    # If set to true, leave a crack to allow lines to peel off
    peel_off = True

    stamp_name = 'solarsail'
    #stamp_name = 'backedupsink'
    #stamp_name = 'squarepair'

    vertical_stamp_orientation = True

    jitterx = 10
    jittery = 10

    # ---------------
    # Algorithm:

    team1_patterns = []
    team2_patterns = []

    # ----------------
    # Lines:

    def _get_bounds(z, dim):
        zstart = z - dim//2
        zend = z + (dim - dim//2)
        return zstart, zend

    line_ylocs = [int(0.25*rows), int(0.75*rows)]

    # Add the string
    y1 = line_ylocs[0] - random.randint(0, jittery)
    y2 = line_ylocs[1] + random.randint(0, jittery)
    if peel_off:
        start = 1
    else:
        start = 0

    for ix in range(start, cols):
        # string 1
        for iy in range(*_get_bounds(y1, thickness)):
            team1_lines[iy][ix] = 'o'
        # string 2
        for iy in range(*_get_bounds(y2, thickness)):
            team2_lines[iy][ix] = 'o'

    team1_patterns.append(team1_lines)
    team2_patterns.append(team2_lines)

    # ----------------
    # Stamps:

    team_assignments = [1,]*stamps_per_team + [2,]*stamps_per_team
    random.shuffle(team_assignments)
    if vertical_stamp_orientation:
        xlocs = [int(((j+1)/(stamps_per_team+1))*cols) for j in range(stamps_per_team)]
    else:
        xlocs = [int(((j+1)/(2*stamps_per_team+1))*cols) for j in range(2*stamps_per_team)]
    yloc = int(0.50*rows)

    for i, xloc in enumerate(xlocs):
        if vertical_stamp_orientation:
            yy1 = yloc - jittery - random.randint(0, jittery)
            yy2 = yloc + jittery + random.randint(0, jittery)
            xx = xloc + random.randint(-jitterx, jitterx)
            stamp = get_grid_stamp( 
                load_stamp(stamp_name), 
                rows, 
                cols, 
                yoffset=yy1, 
                xoffset=xx
            )
            team1_patterns.append(stamp)

            stamp = get_grid_stamp( 
                load_stamp(stamp_name), 
                rows, 
                cols, 
                yoffset=yy2, 
                xoffset=xx
            )
            team2_patterns.append(stamp)

        else:
            yy = yloc + random.randint(-jittery, jittery)
            xx = xloc + random.randint(-jitterx, jitterx)
            stamp = get_grid_stamp( 
                load_stamp(stamp_name), 
                rows, 
                cols, 
                yoffset=yy, 
                xoffset=xx
            )
            if team_assignments[i] == 1:
                team1_patterns.append(stamp)
            elif team_assignments[i] == 2:
                team2_patterns.append(stamp)

    # --------------------
    # Final assembly:

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)


def stamps_squarepair(rows, cols, seed=None):
    """
    Create a stamps map using the squarepair stamps,
    and add some random scattered stars for randomness.
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # Summary:
    # - add a variable number of squarepair stamps
    # - two columns, 1-3 stamps per team
    # - add random stars, using various methods

    # ---------------
    # Parameters:

    stamps_per_team = 1

    stars_per_stamp = random.randint(5, 15)

    stars_strategy = 'random'
    stars_strategy = 'friendly_neighbors'
    #stars_strategy = 'unfriendly_neighbors'

    stamp_name = 'squarepair'

    # ---------------
    # Algorithm:

    xlocs = [int(0.25*cols), int(0.75*cols)]
    ylocs = [int(((j+1)/(stamps_per_team+1))*rows) for j in range(stamps_per_team)]

    team1_patterns = []
    team2_patterns = []

    for yy in ylocs:

        xx = xlocs[0]
        team1_patterns.append(
            get_grid_stamp(
                load_stamp(stamp_name), 
                rows, 
                cols, 
                yoffset=yy, 
                xoffset=xx
            )
        )

        xx = xlocs[1]
        team2_patterns.append(
            get_grid_stamp(
                load_stamp(stamp_name), 
                rows, 
                cols, 
                yoffset=yy, 
                xoffset=xx
            )
        )

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    if stars_strategy == 'random':
        for _ in range(stars_per_stamp*stamps_per_team):
            xx, yy = get_random_unoccupied_point(team1_pattern, team2_pattern, rows, cols)
            team1_patterns.append(
                get_grid_stamp(
                    load_stamp('star'),
                    rows,
                    cols,
                    yoffset=yy,
                    xoffset=xx
                )
            )

            xx, yy = get_random_unoccupied_point(team1_pattern, team2_pattern, rows, cols)
            team2_patterns.append(
                get_grid_stamp(
                    load_stamp('star'),
                    rows,
                    cols,
                    yoffset=yy,
                    xoffset=xx
                )
            )

            # Update the patterns we're using so we don't
            # have colliding points
            team1_pattern = pattern_union(team1_patterns)
            team2_pattern = pattern_union(team2_patterns)

    elif stars_strategy in ['friendly_neighbors', 'unfriendly_neighbors']:

        for yloc in ylocs:

            if stars_strategy == 'friendly_neighbors':
                # color assignment matches stamps above
                center1 = (xlocs[0], yloc)
                center2 = (xlocs[1], yloc)
            elif stars_strategy == 'unfriendly_neighbors':
                # swap x locs, so stamps are surrounded by opp color
                center1 = (xlocs[1], yloc)
                center2 = (xlocs[0], yloc)

            for _ in range(stars_per_stamp):
                xx, yy = get_gaussian_unoccupied_point(team1_pattern, team2_pattern, rows, cols, center1)
                team1_patterns.append(
                    get_grid_stamp(
                        load_stamp('star'),
                        rows,
                        cols,
                        yoffset=yy,
                        xoffset=xx,
                    )
                )

                xx, yy = get_gaussian_unoccupied_point(team1_pattern, team2_pattern, rows, cols, center2)
                team2_patterns.append(
                    get_grid_stamp(
                        load_stamp('star'),
                        rows,
                        cols,
                        yoffset=yy,
                        xoffset=xx,
                    )
                )

                # Update the patterns we're using so we don't
                # have colliding points
                team1_pattern = pattern_union(team1_patterns)
                team2_pattern = pattern_union(team2_patterns)

    else:
        raise Exception(f"Error: Invalid stars strategy specified: {stars_strategy}")

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)


def two_stamps(rows, cols, seed=None):
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # Good
    #stamp_name = 'arrow'
    #stamp_name = 'backedupsink'
    #stamp_name = 'scaffoldunfusing'
    #stamp_name = 'spaceship2platform'
    #stamp_name = 'solarsail'

    # Boring
    #stamp_name = 'escapingsatellites'
    #stamp_name = 'satellite'
    #stamp_name = 'simplestablestar'
    #stamp_name = 'simplestablestarsatellite'
    #stamp_name = 'simpleunstablestar'

    # Borderline boring
    #stamp_name = 'square'
    #stamp_name = 'squarepair'

    # Unknown
    #stamp_name = 'squarevariation2'
    #stamp_name = 'squarevariation3'
    #stamp_name = 'squarevariationpair'
    #stamp_name = 'star'
    #stamp_name = 'whatever'


    team1_pattern = pattern_union([
        get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=30, xoffset=41),
        get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=60, xoffset=34),
        get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=90, xoffset=39),
        #get_grid_stamp(load_stamp('star'), rows, cols, yoffset=20, xoffset=53),
        #get_grid_stamp(load_stamp('star'), rows, cols, yoffset=50, xoffset=54),
        #get_grid_stamp(load_stamp('star'), rows, cols, yoffset=80, xoffset=49),
    ])

    team2_pattern = pattern_union([
        get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=30, xoffset=108),
        get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=60, xoffset=114),
        get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=90, xoffset=106),
        #get_grid_stamp(load_stamp('star'), rows, cols, yoffset=20, xoffset=128),
        #get_grid_stamp(load_stamp('star'), rows, cols, yoffset=50, xoffset=122),
        #get_grid_stamp(load_stamp('star'), rows, cols, yoffset=80, xoffset=131),
    ])

    #team1_pattern = pattern_union([
    #    get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=70, xoffset=38),
    #    get_grid_stamp(load_stamp('star'), rows, cols, yoffset=49, xoffset=104),
    #])
    #team2_pattern = pattern_union([
    #    get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=43, xoffset=141),
    #    get_grid_stamp(load_stamp('star'), rows, cols, yoffset=76, xoffset=145),
    #])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)


def load_stamp(pattern_name):
    fpath = os.path.join('b2s345c4_patterns', f'{pattern_name}.txt')
    if not os.path.exists(fpath):
        raise Exception(f"Error: pattern file {fpath} does not exist")
    with open(fpath, "r") as f:
        pattern = f.readlines()
    pattern = [r.strip() for r in pattern]
    return pattern


def get_grid_stamp(pattern, rows, cols, xoffset=0, yoffset=0, flatten=True):
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
                    newpattern[y][x] = ogpattern[iy][ix]

    if flatten:
        newpattern = ["".join(j) for j in newpattern]

    return newpattern


def get_random_unoccupied_point(team1_pattern, team2_pattern, rows, cols):
    x, y = random.randint(0, cols-1), random.randint(0, rows-1)

    tries = 0
    finished = False
    while not finished:
        # Check if this randomly-chosen point has neighbors
        okay = True
        for ix in [-2, -1, 0, 1, 2]:
            for iy in [-2, -1, 0, 1, 2]:
                if y+iy < rows and x+ix < cols:
                    if team1_pattern[y+iy][x+ix]=='o' or team2_pattern[y+iy][x+ix]=='o':
                        okay = False
                        break
        if not okay:
            # Try another point
            x, y = random.randint(0, cols-1), random.randint(0, rows-1)
            tries += 1
            if tries > 10:
                raise Exception(f"Error: Failed to find unoccupied x,y point in 10 tries")
        else:
            return x, y

def get_gaussian_unoccupied_point(team1_pattern, team2_pattern, rows, cols, center):
    cx, cy = center
    stdx, stdy = [40, 40]

    def _getxy():
        randx = int(random.gauss(cx, stdx))
        randy = int(random.gauss(cy, stdy))
        return randx, randy

    x, y = _getxy()

    tries = 0
    finished = False
    while not finished:
        # Check if this randomly-chosen point has neighbors
        okay = True
        for ix in [-2, -1, 0, 1, 2]:
            for iy in [-2, -1, 0, 1, 2]:
                if y+iy < rows and x+ix < cols:
                    if team1_pattern[y+iy][x+ix]=='o' or team2_pattern[y+iy][x+ix]=='o':
                        okay = False
                        break
        if not okay:
            # Try another point
            x, y = _getxy()
            tries += 1
            if tries > 100:
                raise Exception(f"Error: Failed to find unoccupied x,y point in 10 tries")
        else:
            return x, y


