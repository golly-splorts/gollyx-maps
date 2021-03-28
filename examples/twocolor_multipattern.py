from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.utils import pattern2url
import random


ROWS = 100
COLS = 120


def make_map(seed=None):
    """
    Generate a two-color map with multiple patterns for each team.
    """
    rows = ROWS
    cols = COLS
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
        )
        team2_pattern_list.append(p)

    team1_pattern = pattern_union(team1_pattern_list)
    team2_pattern = pattern_union(team2_pattern_list)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8888/simulator/index.html?s1={s1}&s2={s2}"
    #url = f"?s1={s1}"
    #url = f"?s2={s2}"
    print(url)


if __name__=="__main__":
    make_map()
