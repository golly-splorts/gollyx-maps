from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def deuceswild():
    """
    guns in the middle, methuselahs at the corners
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    centerx = cols//2
    centery = rows//2

    # -------------
    # Guns, pew pew
    gun = 'gosper_gun'

    yw, xw = get_pattern_size(gun)

    xjitter = lambda: random.randint(xw//2, xw//2 + 10)
    x1 = centerx - xjitter()
    x2 = centerx + xjitter()

    yjitter = lambda: random.randint(-10, 10)
    y1 = centery - yjitter()
    y2 = centery + yjitter()

    flip = bool(random.randint(0, 1))

    team1_pattern = get_grid_pattern(gun, rows, cols, xoffset=x1, yoffset=y1, vflip=flip,     hflip=flip)
    team2_pattern = get_grid_pattern(gun, rows, cols, xoffset=x2, yoffset=y2, vflip=not flip, hflip=not flip)


    # -----------
    # Methuselahs

    methuselahs = ['multuminparvo', 'acorn', 'bunnies', 'twoglidermess']
    methuselah = random.choice(methuselahs)

    nw_x = cols//6 # random.randint(cols//6, cols//4)
    nw_y = rows//6 # random.randint(rows//6, rows//4)

    se_x = 5*cols//6 # random.randint(3*cols//4, 5*cols//6)
    se_y = 5*rows//6 # random.randint(3*rows//4, 5*rows//6)

    d = 15
    xjitter = lambda: random.randint(-d, d)
    yjitter = lambda: random.randint(0, 2*d)

    r = lambda: bool(random.randint(0,1))

    team1_pattern = pattern_union([team1_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=nw_x, yoffset=nw_y, vflip=r(), hflip=r())])
    team2_pattern = pattern_union([team2_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=se_x, yoffset=se_y, vflip=r(), hflip=r())])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)



if __name__=="__main__":
    deuceswild()
