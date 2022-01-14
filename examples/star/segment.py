from gollyx_maps.patterns import pattern_union, segment_pattern, get_grid_empty
from gollyx_maps.utils import pattern2url
from gollyx_maps.geom import hflip_pattern, vflip_pattern
import math
import random


ROWS = 160
COLS = 240


def make_map3(seed=None):
    """
    Make a V shape, one wing for each color
    """
    rows = ROWS
    cols = COLS

    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # These store the the .o diagrams (flat=False means these are lists of lists of one char)
    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    # --------------
    # Parameters

    # Height and width of rectangles used to assemble diagonal line
    dy = 6
    dx = 4

    # Adding higher probabilty and fewer max kills
    # causes a weird dynamic:
    # - top of the diagonal has fewer cells, more random
    # - bottom of diagonal has denser, ordered behavior

    # Larger maxkillprob leads to more holes

    # Sharp contrast in hole densities halfway down
    maxkillcounter = 40
    maxkillprob = 0.5

    # Less sharp, less holes
    maxkillcounter = 30
    maxkillprob = 0.3

    ## A little randomness goes a long way
    #maxkillcounter = 5
    #maxkillprob = 0.4

    ## A little more randomness goes a little further
    #maxkillcounter = 15
    #maxkillprob = 0.4

    ## Just a few dead cells makes it interesting
    #maxkillcounter = 20
    #maxkillprob = 0.8

    ## Missing many cells at the top leaves a smaller core 
    ## at the bottom to behave as usual, leaving more room
    ## for randomness to take over.
    #maxkillcounter = 60
    #maxkillprob = 0.8

    # Specify whether the two wings of the V are
    # always perfectly vertially aligned
    valign = True 

    # Set jitter
    jitterx = 7
    jittery = 8

    # ------------
    # Algorithm:
    # 
    # Create diagonal lines by filling in rectangles
    # connected diagonal-to-diagonal.
    # The lines only occupy half of the grid.
    # Create two, flip one of them, and combine to get a V shape.
    # 
    # It is also crucial to ensure teams start on even
    # grid numbers, to ensure the diagonal formation does
    # something interesting, hence the times 2/divided by 2 operation.

    starty = (1*rows)//10 + 2*random.randint(0, jittery)
    endy = (9*rows)//10 - random.randint(0, jittery)

    startx = (1*cols)//10 + (random.randint(0, jitterx)//2)*2
    endx = (45*cols)//100 - (random.randint(0, jitterx)//2)*2

    # -------------
    # color 1

    killcounter = 0

    if valign:
        starty1 = starty
        endy1 = endy
    else:
        offset = (random.randint(-jittery, jittery)//2)*2
        starty1 = starty + offset
        endy1 = endy + offset
    yy = starty1

    offset = (random.randint(-jitterx, jitterx)//2)*2
    startx1 = startx + offset + 1
    endx1 = endx + offset
    xx = startx1

    while yy < endy1 and xx < endx1:
        for xx_ in range(xx, xx+dx+1):
            for yy_ in range(yy, yy+dy+1):
                if xx_ == xx:
                    team1_pattern[yy_][xx_] = "o"
                elif xx_==(xx+dx+1):
                    team1_pattern[yy_][xx_] = "o"
                else:
                    if xx_%2==yy_%2:
                        if random.random()<maxkillprob and killcounter != maxkillcounter:
                            killcounter += 1
                        else:
                            team1_pattern[yy_][xx_] = "o"
        yy += dy
        xx += dx

    # -------------
    # color 2

    killcounter = 0

    if valign:
        starty2 = starty
        endy2 = endy
    else:
        offset = (random.randint(-jittery, jittery)//2)*2
        starty2 = starty + offset
        endy2 = endy + offset
    yy = starty2

    offset = (random.randint(-jitterx, jitterx)//2)*2
    startx2 = startx + offset + 1
    endx2 = endx + offset
    xx = startx2

    while yy < endy2 and xx < endx2:
        for xx_ in range(xx, xx+dx+1):
            for yy_ in range(yy, yy+dy+1):
                if xx_ == xx:
                    team2_pattern[yy_][xx_] = "o"
                elif xx_==(xx+dx+1):
                    team2_pattern[yy_][xx_] = "o"
                else:
                    if xx_%2==yy_%2:
                        if random.random()<maxkillprob and killcounter != maxkillcounter:
                            killcounter += 1
                        else:
                            team2_pattern[yy_][xx_] = "o"
        yy += dy
        xx += dx

    # ---------------

    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    team2_pattern = hflip_pattern(team2_pattern)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)



def make_map2(seed=None):
    """
    Make horizontal rows of thick lines with criss-cross hole punches
    """
    rows = ROWS
    cols = COLS

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



def make_map1(seed=None):
    """
    Make two thick vertical bars of each color, with random holes punched
    """
    rows = ROWS
    cols = COLS

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


if __name__ == "__main__":
    make_map3()
