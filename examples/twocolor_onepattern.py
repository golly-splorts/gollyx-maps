from golly_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from golly_maps.utils import pattern2url
import random


ROWS = 100
COLS = 120


def crashing_spaceships(seed=None):
    """
    Generate a two-color map with one pattern for each team.
    Two medium spaceships crashing into each other.
    """
    rows = ROWS
    cols = COLS
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    centerx1 = cols//2 + cols//4
    centery1 = rows//2

    centerx2 = cols//4
    centery2 = rows//2

    pattern1 = get_grid_pattern('heavyweightspaceship', rows, cols, xoffset=centerx1, yoffset=centery1)
    pattern2 = get_grid_pattern('heavyweightspaceship', rows, cols, xoffset=centerx2, yoffset=centery2, hflip=True)

    s1 = pattern2url(pattern1)
    s2 = pattern2url(pattern2)

    url = f"?s1={s1}&s2={s2}"
    print(url)


if __name__=="__main__":
    crashing_spaceships()
