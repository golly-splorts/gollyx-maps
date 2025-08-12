from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def quad():
    """
    four methuselahs in the four quadrant corners
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    centerx = cols//2
    centery = rows//2

    garden_methuselahs = ['acorn', 'mustardseed', 'rabbit', 'bunnies']
    small_methuselahs = ['timebomb', 'multuminparvo', 'twoglidermess']
    large_methuselahs = ['fred', 'wilma', 'grandpa_42100', 'grandpa_13629876']
    methuselah = random.choice(small_methuselahs)

    nw_x = sw_x = cols//4
    ne_x = se_x = 3*cols//4

    nw_y = ne_y = rows//4
    sw_y = se_y = 3*rows//4

    team1_locs = []
    team2_locs = []

    mode = random.randint(0,1)
    if mode==0:
        team1_locs.append((nw_x, nw_y))
        team1_locs.append((sw_x, sw_y))
        team2_locs.append((ne_x, ne_y))
        team2_locs.append((se_x, se_y))
    else:
        team1_locs.append((nw_x, nw_y))
        team2_locs.append((sw_x, sw_y))
        team1_locs.append((ne_x, ne_y))
        team2_locs.append((se_x, se_y))

    xjitter = lambda: random.randint( -int((1/6)*cols), int((1/6)*cols))
    yjitter = lambda: random.randint( -int((1/6)*rows), int((1/6)*rows))

    def _assemble_patterns(team_locs):
        team_pattern = []
        for i, (x_, y_) in enumerate(team_locs):
            xx = x_ + xjitter()
            yy = y_ + yjitter()
            vf = bool(random.randint(0,1))
            hf = bool(random.randint(0,1))
            if i==0:
                team_pattern = get_grid_pattern(methuselah, rows, cols, xoffset=xx, yoffset=yy, vflip=vf, hflip=hf)
            else:
                team_pattern = pattern_union([team_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=xx, yoffset=yy, vflip=vf, hflip=hf)])
        return team_pattern

    team1_pattern = _assemble_patterns(team1_locs)
    team2_pattern = _assemble_patterns(team2_locs)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


if __name__=="__main__":
    quad()
