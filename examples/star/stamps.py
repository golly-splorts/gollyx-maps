from gollyx_maps.patterns import pattern_union
from gollyx_maps.utils import pattern2url
import itertools
import random
import os


def load_stamp(pattern_name):
    fpath = os.path.join('b2s345c4_patterns', f'{pattern_name}.txt')
    if not os.path.exists(fpath):
        raise Exception(f"Error: pattern file {fpath} does not exist")
    with open(fpath, "r") as f:
        pattern = f.readlines()
    pattern = [r.strip() for r in pattern]
    return pattern


def get_grid_stamp(pattern, rows, cols, xoffset=0, yoffset=0, flatten=True):
    ogpattern = [list(j) for j in pattern]
    blank_row = ["."] * cols
    newpattern = [blank_row[:] for r in range(rows)]
    (pattern_h, pattern_w) = (len(ogpattern), len(ogpattern[0]))

    # given offset is offset for the center of the pattern,
    # so do some algebra to determine where we should start
    xstart = xoffset - pattern_w // 2
    xend = xstart + pattern_w
    ystart = yoffset - pattern_h // 2
    yend = ystart + pattern_h

    # iterate through the pattern and copy over the cells that are in the final grid
    for iy, y in enumerate(range(ystart, yend)):
        if y > 0 and y < len(newpattern):
            for ix, x in enumerate(range(xstart, xend)):
                if x > 0 and x < len(newpattern[iy]):
                    newpattern[y][x] = ogpattern[iy][ix]

    if flatten:
        newpattern = ["".join(j) for j in newpattern]

    return newpattern


def stamps(rows, cols, seed=None):
    """
    Make horizontal rows of thick lines with criss-cross hole punches
    """
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    #stamp_name = 'backedupsink'
    #stamp_name = 'spaceship2platform'
    stamp_name = 'scaffoldunfusing'

    team1_pattern = pattern_union([
            get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=40, xoffset=38),
            ])
    team2_pattern = pattern_union([
            get_grid_stamp(load_stamp(stamp_name), rows, cols, yoffset=43, xoffset=141),
            ])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)
