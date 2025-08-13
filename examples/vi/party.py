from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def bunny_party():
    methuselahs = ['rabbit', 'bunnies']
    _party(methuselahs, (5, 25))

def domino_party():
    methuselahs = ['cheptomino', 'piheptomino', 'rpentomino']
    _party(methuselahs, (5, 16))

def dove_party():
    methuselahs = ['wing', 'dove']
    _party(methuselahs, (4, 13))

def multum_in_party():
    methuselahs = ['acorn', 'multuminparvo', 'mustardseed']
    _party(methuselahs, (5, 25))

def _party(methuselahs, spacing_range):
    """
    line of methuselahs thru the middle, with some vertical jitter
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    centerx = cols//2
    centery = rows//2

    methuselah = random.choice(methuselahs)

    yw, xw = get_pattern_size(methuselah)

    between = random.randint(*spacing_range)

    # Place one r omino every 10 grid spaces,
    # maximum number - 1
    maxshapes = centerx // (xw + between)

    # Set vertical jitter pattern
    if bool(random.getrandbits(1)):
        # identical between teams
        lo1, hi1 = -between, between
        lo2, hi2 = lo1, hi1
    else:
        # staggered (twice as high for one, twcie as low for other)
        if bool(random.getrandbits(1)):
            lo1, hi1 = -2*between, between
            lo2, hi2 = -between, 2*between
        else:
            lo1, hi1 = -between, 2*between
            lo2, hi2 = -2*between, between

    c1patterns = []
    c2patterns = []
    for i in range(maxshapes - 1):

        end = (i + 1) * (xw + between)
        start = end - xw//2
        pattern1 = get_grid_pattern(
            methuselah,
            rows,
            cols,
            xoffset=centerx - random.randint(start, end),
            yoffset=centery + random.randint(lo1, hi1),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c1patterns.append(pattern1)

        pattern2 = get_grid_pattern(
            methuselah,
            rows,
            cols,
            xoffset=centerx + random.randint(start, end),
            yoffset=centery + random.randint(lo2, hi2),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c2patterns.append(pattern2)

    c1 = pattern_union(c1patterns)
    c2 = pattern_union(c2patterns)

    s1 = pattern2url(c1)
    s2 = pattern2url(c2)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)

if __name__=="__main__":
    #bunny_party()
    #domino_party()
    #dove_party()
    multum_in_party()

