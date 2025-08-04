from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union, get_b3s23_patterns
from gollyx_maps.utils import pattern2url
import random

ROWS = 150
COLS = 240
SEED = 42

print("")
print("ii (toroidal + hellmouth) map pattern examples:")
print("")

patterns = sorted(get_b3s23_patterns())
for pattern in patterns:
    print(f"{pattern}:")
    #m = maps.get_map_realization('ii', pattern)
    #print(f"https://v.golly.life/simulator/index.html{m['url']}")

    rows = ROWS
    cols = COLS
    # set rng seed (optional)
    random.seed(SEED)

    centerx1 = cols//2 + cols//4
    centery1 = rows//2

    centerx2 = cols//4
    centery2 = rows//2

    pattern1 = get_grid_pattern(pattern, rows, cols, xoffset=centerx1+5, yoffset=centery1+5)
    pattern2 = get_grid_pattern(pattern, rows, cols, xoffset=centerx2,   yoffset=centery2, hflip=True)

    s1 = pattern2url(pattern1)
    s2 = pattern2url(pattern2)

    # url = f"https://v.golly.life/simulator/index.html?s1={s1}&s2={s2}"
    url = f"https://v.golly.life/simulator/index.html?s2={s2}"
    print(url)
    print()
