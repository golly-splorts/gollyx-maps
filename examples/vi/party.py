from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def party():
    """
    line of methuselahs thru the middle, with some vertical jitter
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    centerx = cols//2
    centery = rows//2

    methuselahs = ['rabbit', 'bunnies', 'cheptomino', 'dove', 'multuminparvo', 'mustardseed', 'piheptomino', 'rpentomino', 'twoglidermess', 'wing']
    methuselah = random.choice(methuselahs)

    yw, xw = get_pattern_size(methuselah)

    between = random.randint(3, 20)

    # Place one r omino every 10 grid spaces,
    # maximum number - 1
    maxshapes = centerx // (xw + between)

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
            yoffset=centery + random.randint(-between, between),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c1patterns.append(pattern1)

        pattern2 = get_grid_pattern(
            methuselah,
            rows,
            cols,
            xoffset=centerx + random.randint(start, end),
            yoffset=centery + random.randint(-between, between),
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
    party()
