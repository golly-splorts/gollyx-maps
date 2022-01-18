from gollyx_maps.patterns import pattern_union, get_grid_empty
from gollyx_maps.utils import pattern2url
from gollyx_maps.geom import hflip_pattern, vflip_pattern
import random

from stamps import get_grid_stamp, load_stamp


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

    # --------------
    # Parameters:

    stamps_per_team = random.randint(1,6)

    #vertical_stamp_orientation = random.random() < 0.50
    vertical_stamp_orientation = True

    # Thickness of >= 2 is impenetrable
    thickness = 2

    # If set to true, leave a crack to allow lines to peel off
    peel_off = False

    stamp_name = 'solarsail'
    #stamp_name = 'backedupsink'
    #stamp_name = 'spaceship2platform'

    jitterx = 12
    jittery = 8

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


    line_ylocs_top = random.randint(1,4)/10
    line_ylocs_bot = random.randint(6,9)/10

    line_ylocs = [int(line_ylocs_top*rows), int(line_ylocs_bot*rows)]

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
            team1_lines[iy][ix] = 'o'
        # string 2
        for iy in range(*_get_bounds(y2, thickness)):
            team2_lines[iy][ix] = 'o'

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

    team_assignments = [1,]*stamps_per_team + [2,]*stamps_per_team
    random.shuffle(team_assignments)

    # approximately evenly spaced in x dir
    if vertical_stamp_orientation:
        xlocs = [int(((j+1)/(stamps_per_team+1))*cols) for j in range(stamps_per_team)]
    else:
        xlocs = [int(((j+1)/(2*stamps_per_team+1))*cols) for j in range(2*stamps_per_team)]

    dy = y2-y1

    for i, xloc in enumerate(xlocs):

        xx = xloc + random.randint(-jitterx, jitterx)

        if vertical_stamp_orientation:
            yy1 = y1 + int((1/3)*dy) + random.randint(-jittery, jittery)
            yy2 = y1 + int((2/3)*dy) + random.randint(-jittery, jittery) 

            yy1 = min(max(yy1, y1+thickness//2), y2-thickness//2)
            yy2 = min(max(yy2, y1+thickness//2), y2-thickness//2)

            stamp1 = load_stamp(stamp_name)

            if random.random()<0.50:
                stamp1 = hflip_pattern(stamp1)
            if random.random()<0.50:
                stamp1 = vflip_pattern(stamp1)

            gridstamp = get_grid_stamp( 
                stamp1,
                rows, 
                cols, 
                yoffset=yy1, 
                xoffset=xx
            )

            team1_patterns.append(gridstamp)

            stamp2 = load_stamp(stamp_name)

            if random.random()<0.50:
                stamp2 = hflip_pattern(stamp2)
            if random.random()<0.50:
                stamp2 = vflip_pattern(stamp2)

            gridstamp = get_grid_stamp( 
                stamp2,
                rows, 
                cols, 
                yoffset=yy2, 
                xoffset=xx
            )

            team2_patterns.append(gridstamp)

        else:

            stamp = load_stamp(stamp_name)

            if random.random() < 0.50:
                stamp = hflip_pattern(stamp)
            if random.random() < 0.50:
                stamp = vflip_pattern(stamp)

            yy = y1 + int(0.5*dy) + random.randint(-jittery, jittery) 
            gridstamp = get_grid_stamp( 
                rows, 
                cols, 
                yoffset=yy, 
                xoffset=xx
            )

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

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)
