from gollyx_maps.patterns import get_grid_empty
from gollyx_maps.utils import pattern2url
import random


def bars(rows, cols, seed=None):
    """
    Make two thick vertical bars of each color, with random holes punched
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # These store the the .o diagrams (flat=False means these are lists of lists of one char)
    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    jitterx = 4
    jittery = 10

    starty0 = (2*rows)//10
    endy0 = starty0 + (6*rows)//10

    thickness = random.randint(3, 5)

    gap_prob = 0.4


    # -------------
    # color 1

    jit = random.randint(-jittery, jittery)
    starty = starty0 + jit
    endy = endy0 + jit

    startx = (2*cols)//10 + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team1_pattern[y][x] = "o"

    startx = (6*cols)//10 + random.randint(-jitterx, jitterx)
    endx = startx + 3

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team1_pattern[y][x] = "o"

    # -------------
    # color 2

    jit = random.randint(-jittery, jittery)
    starty = starty0 + jit
    endy = endy0 + jit

    startx = (4*cols)//10 + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team2_pattern[y][x] = "o"

    startx = (8*cols)//10 + random.randint(-jitterx, jitterx)
    endx = startx + 3

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team2_pattern[y][x] = "o"

    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)
