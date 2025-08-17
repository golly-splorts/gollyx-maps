from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def tacoma_standoff():
    methuselahs = ['acorn', 'mustardseed', 'rabbit', 'bunnies']
    _standoff(methuselahs)

def tombstone_standoff():
    methuselahs = ['acorn', 'mustardseed', 'rabbit', 'bunnies']
    _standoff(methuselahs, opposite_day=True)

def red_rock_standoff():
    methuselahs = ['cheptomino', 'rpentomino']
    _standoff(methuselahs)

def cheyenne_showdown():
    methuselahs = ['timebomb', 'multuminparvo', 'twoglidermess']
    _standoff(methuselahs)

def santa_fe_standoff():
    methuselahs = ['timebomb', 'multuminparvo', 'twoglidermess']
    _standoff(methuselahs, opposite_day=True)

def caliente_standoff():
    methuselahs = ['grandpa_42100', 'grandpa_13629876']
    _standoff(methuselahs)

def spaceport_standoff():
    methuselahs = ['bisectingpuffers']
    _standoff(methuselahs)

def suns_out_gosper_guns_out():
    # This makes for some deliciously long and tricky paths to victory
    methuselahs = ['gosper_gun']
    _standoff(methuselahs)


def _standoff(methuselahs, opposite_day=False):
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

    xjitter = lambda: random.randint(xw//2, xw//2 + 8)
    x1 = centerx - xjitter()
    x2 = centerx + xjitter()

    yjitter = lambda: random.randint(-8, 8)
    y1 = centery - yjitter()
    y2 = centery + yjitter()

    flip = bool(random.randint(0, 1))

    # The flip boolean logic ensures that the guns are always:
    # - next to each other
    # - pointing toward the same (NW/SE) corners
    # - outside of each others' range
    team1_pattern = get_grid_pattern(gun, rows, cols, xoffset=x1, yoffset=y1, vflip=flip,     hflip=flip)
    team2_pattern = get_grid_pattern(gun, rows, cols, xoffset=x2, yoffset=y2, vflip=not flip, hflip=not flip)


    # -----------
    # Methuselahs

    methuselah = random.choice(methuselahs)

    nw_x = cols//6
    nw_y = rows//6

    se_x = 5*cols//6
    se_y = 5*rows//6

    if opposite_day:
        # "nw" is actually ne
        nw_x = 5*cols//6
        # "se" is actually sw
        se_x = cols//6

    d = 11

    xjitter = lambda: random.randint(-d, d)
    yjitter = lambda: random.randint(0, d)

    r = lambda: bool(random.randint(0,1))

    # Put methuselahs in the NW/SE corners
    team1_pattern = pattern_union([team1_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=nw_x + xjitter(), yoffset=nw_y + yjitter(), vflip=r(), hflip=r())])
    team2_pattern = pattern_union([team2_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=se_x + xjitter(), yoffset=se_y + yjitter(), vflip=r(), hflip=r())])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


if __name__=="__main__":
    #garden_standoff()
    #domino_standoff()
    #small_standoff()
    #large_standoff()
    #garden_standoff2()
    #small_standoff2()
    #bisecting_standoff()
    #oops_all_standoff()
