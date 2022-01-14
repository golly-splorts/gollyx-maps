from gollyx_maps.patterns import get_grid_empty
from gollyx_maps.utils import pattern2url
import random


def comb(rows, cols, seed=None):
    """
    Make horizontal rows of thick lines with criss-cross hole punches
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # These store the the .o diagrams (flat=False means these are lists of lists of one char)
    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    jitterx = 16
    jittery = 4

    thickness = random.randint(3, 5)

    # -------------
    # color 1

    starty1 = (3*rows)//10 + random.randint(-jittery, jittery)
    endy1 = starty1 + thickness

    startx = (2*cols)//10 + random.randint(-jitterx, jitterx)
    endx = startx + (6*cols)//10

    for y in range(starty1, endy1 + 1):
        for x in range(startx, endx + 1):
            if y==starty1:
                team1_pattern[y][x] = "o"
            elif y==endy1:
                team1_pattern[y][x] = team1_pattern[y-1][x]
            elif (x%2==y%2):
                team1_pattern[y][x] = "o"

    for x in range(startx, endx+1):
        if random.random()<0.25:
            team1_pattern[starty1-1][x] = "o"

    # -------------
    # color 2

    starty2 = (7*rows)//10 + random.randint(-jittery, jittery)
    endy2 = starty2 + thickness

    startx = (2*cols)//10 + random.randint(-jitterx, jitterx)
    endx = startx + (6*cols)//10

    for y in range(endy2, starty2-1, -1):
        for x in range(startx, endx + 1):
            if y==starty2:
                team2_pattern[y][x] = team2_pattern[y+1][x]
            elif y==endy2:
                team2_pattern[y][x] = "o"
            elif (x%2==y%2):
                team2_pattern[y][x] = "o"
    
    for x in range(startx, endx+1):
        if random.random()<0.25:
            team2_pattern[endy2+1][x] = "o"

    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)



