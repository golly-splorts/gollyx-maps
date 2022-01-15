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

    # ------------
    # Parameters

    jitterx = 4
    jittery = 10

    tmargin = random.randint(2, 3)/10
    bmargin = random.randint(7, 8)/10

    xlocs1 = [0.2, 0.6]
    xlocs2 = [0.4, 0.8]

    thickness = random.randint(3, 5)

    gap_prob = random.randint(2, 3)/10

    st_louis_gap = 4


    # -------------
    # color 1

    starty0 = int(tmargin*rows)
    endy0 = int(bmargin*rows)

    jit = random.randint(-jittery, jittery)
    starty = starty0 + jit
    endy = endy0 + jit

    startx = int(xlocs1[0]*cols) + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team1_pattern[y][x] = "o"

    startx = int(xlocs1[1]*cols) + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team1_pattern[y][x] = "o"

    # -------------
    # color 2

    starty0 = int(tmargin*rows)
    endy0 = int(bmargin*rows)

    jit = random.randint(-jittery, jittery)
    starty = starty0 + jit
    endy = endy0 + jit

    startx = int(xlocs2[0]*cols) + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team2_pattern[y][x] = "o"

    startx = int(xlocs2[1]*cols) + random.randint(-jitterx, jitterx)
    endx = startx + thickness

    for y in range(starty, endy + 1):
        for x in range(startx, endx + 1):
            if random.random() > gap_prob:
                team2_pattern[y][x] = "o"


    # st louis style
    for yy in range(rows):
        if yy%st_louis_gap==0:
            nx = len(team1_pattern[y])
            for xx in range(nx):
                team1_pattern[yy][xx] = '.'
                team2_pattern[yy][xx] = '.'


    # adjust nubmer of live cells of each team to be equal
    p1 = set()
    p2 = set()
    for yy in range(rows):
        for xx in range(cols):
            if team1_pattern[yy][xx] == 'o':
                p1.add((xx,yy))
            elif team2_pattern[yy][xx] == 'o':
                p2.add((xx,yy))

    diff = abs(len(p1)-len(p2))
    if diff != 0:
        if len(p1)>len(p2):
            larger = p1
            patt = team1_pattern
        else:
            larger = p2
            patt = team2_pattern
        for i in range(diff):
            pt = larger.pop()
            patt[pt[1]][pt[0]] = '.'


    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)
