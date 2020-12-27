from golly_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from golly_maps.utils import pattern2url
import random


ROWS = 100
COLS = 120


def make_map(seed=None):
    """
    Generate a two-color map with multiple patterns for each team.
    Four justyna metheuselas.
    """
    rows = ROWS
    cols = COLS
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    rotdegs = [0, 90, 180, 270]

    centerx1 = cols//4
    centerx1a = centerx1 + random.randint(-5, 30)
    centerx1b = centerx1 + random.randint(-5, 30)

    centery1a = rows//4 + random.randint(-10, 10)
    centery1b = rows//2 + rows//4 + random.randint(-10, 10)

    j1a = get_grid_pattern(
        'justyna',
        rows,
        cols,
        xoffset=centerx1a,
        yoffset=centery1a,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs)
    )
    j1b = get_grid_pattern(
        'justyna',
        rows,
        cols,
        xoffset=centerx1b,
        yoffset=centery1b,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs)
    )
    j1_pattern = pattern_union([j1a, j1b])

    centerx2 = cols//2 + cols//4
    centerx2a = centerx2 - random.randint(-5, 30)
    centerx2b = centerx2 - random.randint(-5, 30)

    centery2a = rows//4 + random.randint(-10, 10)
    centery2b = rows//2 + rows//4 + random.randint(-10, 10)

    j2a = get_grid_pattern(
        'justyna',
        rows,
        cols,
        xoffset=centerx2a,
        yoffset=centery2a,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs)
    )
    j2b = get_grid_pattern(
        'justyna',
        rows,
        cols,
        xoffset=centerx2b,
        yoffset=centery2b,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs)
    )
    j2_pattern = pattern_union([j2a, j2b])

    s1 = pattern2url(j1_pattern)
    s2 = pattern2url(j2_pattern)

    url = f"http://localhost:8888/simulator/index.html?s1={s1}&s2={s2}"
    #url = f"?s1={s1}"
    #url = f"?s2={s2}"
    print(url)


if __name__=="__main__":
    make_map()
