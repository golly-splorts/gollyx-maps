from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def standoff():
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

    garden_methuselahs = ['acorn', 'mustardseed', 'rabbit', 'bunnies']
    small_methuselahs = ['timebomb', 'multuminparvo', 'twoglidermess']
    large_methuselahs = ['fred', 'wilma', 'grandpa_42100', 'grandpa_13629876']

    methuselah = random.choice(garden_methuselahs)

    nw_x = cols//6
    nw_y = rows//6

    se_x = 5*cols//6
    se_y = 5*rows//6

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
    standoff()
