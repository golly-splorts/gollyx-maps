from gollyx_maps.patterns import pattern_union, get_grid_empty
from gollyx_maps.utils import pattern2url
import random
import os


def containment_rectangle(rows, cols, seed=None):
    """
    Create a map with lines forming a rectangle
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # --------------
    # Parameters:

    stamps_per_team = random.randint(1,3)
    vertical_stamp_orientation = bool(random.getrandbits(1))

    # Thickness of >= 2 is impenetrable
    thickness = 2

    jitterx = 10
    jittery = 10

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

    team1_hlines = get_grid_empty(rows, cols, flat=False)
    team2_hlines = get_grid_empty(rows, cols, flat=False)

    team1_vlines = get_grid_empty(rows, cols, flat=False)
    team2_vlines = get_grid_empty(rows, cols, flat=False)

    # Add the line
    y1 = line_ylocs[0] - random.randint(0, jittery)
    y2 = line_ylocs[1] + random.randint(0, jittery)

    x1 = line_xlocs[0] + random.randint(0, jitterx)
    x2 = line_xlocs[1] - random.randint(0, jitterx)

    for ix in range(x1+1, x2-1):
        # string 1
        for iy in range(*_get_bounds(y1, thickness)):
            team1_hlines[iy][ix] = 'o'
        # string 2
        for iy in range(*_get_bounds(y2, thickness)):
            team2_hlines[iy][ix] = 'o'

    for iy in range(y1+1, y2-1):
        # string 1
        for ix in range(*_get_bounds(x1, thickness)):
            team1_vlines[iy][ix] = 'o'
        # string 2
        for ix in range(*_get_bounds(x2, thickness)):
            team2_vlines[iy][ix] = 'o'

    if random.random() < 0.50:
        team1_hlines = [j for j in team1_hlines[::-1]]
        team2_hlines = [j for j in team2_hlines[::-1]]
    if random.random() < 0.50:
        team1_vlines = [list(reversed(j)) for j in team1_vlines]
        team2_vlines = [list(reversed(j)) for j in team2_vlines]

    team1_patterns.append(team1_hlines)
    team1_patterns.append(team1_vlines)
    team2_patterns.append(team2_hlines)
    team2_patterns.append(team2_vlines)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)


def stamps_containment_lines(rows, cols, seed=None):
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
