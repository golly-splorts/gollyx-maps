from gollyx_maps.patterns import pattern_union, get_grid_empty
from gollyx_maps.utils import pattern2url
import random
import os


def containment_rectangle(rows, cols, seed=None):
    """
    Create a map with lines forming a rectangle.
    This requires a source of randomness:
    - static stamps
    - methuselah stamps
    - random cells
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # --------------
    # Parameters:

    # Thickness of >= 2 is impenetrable
    thickness = 2

    ylocs_top = random.randint(10,40)/100
    ylocs_bot = random.randint(60,90)/100

    xlocs_left = random.randint(10,30)/100
    xlocs_right = random.randint(70,90)/100

    jitterx = 10
    jittery = 10

    #fill_style = 'random'
    fill_style = 'bumps'
    #fill_style = 'none'

    fill_density = random.randint(5,30)/100


    # ---------------
    # Algorithm:

    team1_patterns = []
    team2_patterns = []

    # ---------------
    # Lines:

    ylocs = [int(ylocs_top*rows), int(ylocs_bot*rows)]
    xlocs = [int(xlocs_left*rows), int(xlocs_right*rows)]

    def _get_bounds(z, dim):
        zstart = z - dim//2
        zend = z + (dim - dim//2)
        return zstart, zend

    team1_hlines = get_grid_empty(rows, cols, flat=False)
    team2_hlines = get_grid_empty(rows, cols, flat=False)

    team1_vlines = get_grid_empty(rows, cols, flat=False)
    team2_vlines = get_grid_empty(rows, cols, flat=False)

    # Add the line
    y1 = ylocs[0] - random.randint(0, jittery)
    y2 = ylocs[1] + random.randint(0, jittery)

    x1 = xlocs[0] + random.randint(0, jitterx)
    x2 = xlocs[1] - random.randint(0, jitterx)

    # If fill style is bumps, handle it
    if fill_style == 'bumps':
        bumps = True
        fill_points = int((fill_density*(x2-x1))//2)
        t1bumps = 0
        t2bumps = 0

    # make this thickness//2 instead of +-1
    for ix in range(x1+1, x2-1):
        # string 1
        bounds = _get_bounds(y1, thickness)
        for iy in range(*bounds):
            team1_hlines[iy][ix] = 'o'
        if bumps:
            if t1bumps < fill_points:
                if random.random() < fill_density:
                    # add a random bump
                    team1_hlines[bounds[-1]][ix] = 'o'
                    t1bumps += 1

        # string 2
        bounds = _get_bounds(y2, thickness)
        for iy in range(*bounds):
            team2_hlines[iy][ix] = 'o'
        if bumps:
            if t2bumps < fill_points:
                if random.random() < fill_density:
                    # add a random bump
                    team2_hlines[bounds[0]-1][ix] = 'o'
                    t2bumps += 1

    if fill_style=='bumps':
        fill_points = int((fill_density*(y2-y1))//2)
        t1bumps = 0
        t2bumps = 0

    for iy in range(y1+1, y2-1):

        # string 1
        bounds = _get_bounds(x1, thickness)
        for ix in range(*bounds):
            team1_vlines[iy][ix] = 'o'
        if bumps:
            if t1bumps < fill_points:
                if random.random() < fill_density:
                    # add a random bump
                    team1_vlines[iy][bounds[-1]] = 'o'
                    t1bumps += 1

        # string 2
        bounds = _get_bounds(x2, thickness)
        for ix in range(*bounds):
            team2_vlines[iy][ix] = 'o'
        if bumps:
            if t2bumps < fill_points:
                if random.random() < fill_density:
                    # add a random bump
                    team2_vlines[iy][bounds[0]-1] = 'o'
                    t2bumps += 1

    # swap top/bottom and left/right colors randomly
    if random.random() < 0.50:
        temp = team2_hlines[:]
        team2_hlines = team1_hlines[:]
        team1_hlines = temp
    if random.random() < 0.50:
        temp = team2_vlines[:]
        team2_vlines = team1_vlines[:]
        team1_vlines = temp

    team1_patterns.append(team1_hlines)
    team1_patterns.append(team1_vlines)

    team2_patterns.append(team2_hlines)
    team2_patterns.append(team2_vlines)

    # --------------------
    # Fill:

    # (bumps handled in line construction)

    if fill_style == 'random':
        team1_pts = get_grid_empty(rows, cols, flat=False)
        team2_pts = get_grid_empty(rows, cols, flat=False)

        def _get_rand_xy(x1, y1, x2, y2, thickness):
            x_ = x1 + thickness + random.randint(0, x2-x1-2*thickness)
            y_ = y1 + thickness + random.randint(0, y2-y1-2*thickness)
            return x_, y_

        # Divide this quantity by 2, for each team
        fill_points = int((fill_density * (y2-y1-2*thickness)*(x2-x1-2*thickness))//2)

        for team in [1, 2]:
            for _ in range(fill_points):
                xx, yy = _get_rand_xy(x1, y1, x2, y2, thickness)
                while team1_pts[yy][xx] == 'o' or team2_pts[yy][xx] == 'o':
                    xx, yy = _get_rand_xy(x1, y1, x2, y2, thickness)
                if team==1:
                    team1_pts[yy][xx] = 'o'
                elif team==2:
                    team2_pts[yy][xx] = 'o'

        team1_patterns.append(team1_pts)
        team2_patterns.append(team2_pts)

    # --------------------
    # Final assembly:

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)


def containment_lines(rows, cols, seed=None):
    """
    Create a containment map - surround a stamp
    with some solid square lines of sufficient thickness
    to keep everything contained.
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

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

    stamps_per_team = random.randint(1,6)
    vertical_stamp_orientation = bool(random.getrandbits(1))

    # Thickness of >= 2 is impenetrable
    thickness = 2

    # If set to true, leave a crack to allow lines to peel off
    peel_off = True

    stamp_name = 'solarsail'
    #stamp_name = 'backedupsink'
    #stamp_name = 'squarepair'

    jitterx = 20
    jittery = 20

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

    line_ylocs_top = random.randint(1,3)/10
    line_ylocs_bot = random.randint(6,9)/10
    line_ylocs = [int(line_ylocs_top*rows), int(line_ylocs_bot*rows)]

    line_xlocs_left = random.randint(5,25)/100
    line_xlocs_right = random.randint(75,95)/100
    line_xlocs = [int(line_xlocs_left*rows), int(line_xlocs_right*rows)]

    team1_lines = get_grid_empty(rows, cols, flat=False)
    team2_lines = get_grid_empty(rows, cols, flat=False)

    # Add the line
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

    if random.random() < 0.50:
        team1_lines = [j for j in team1_lines[::-1]]
        team2_lines = [j for j in team2_lines[::-1]]

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
