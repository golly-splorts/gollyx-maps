import itertools
import random

from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern, rot_pattern
from gollyx_maps.utils import pattern2url


ROWS = 150
COLS = 240
SEED = None


def west_baltimore():
    """west1 configuration, classic timebomb/aferimeter"""
    methuselahs = ['timebomb']
    oscillators = ['quadrupleburloaferimeter']
    _west1(methuselahs, oscillators)


def west_boston():
    """west1 configuration, wider variety of methuselahs and oscillators"""
    methuselahs = ['mustardseed', 'multuminparvo', 'twoglidermess']
    oscillators = ['koksgalaxy', 'ring64', 'switchbox']
    _west1(methuselahs, oscillators)


def west_seattle():
    """west2 configuration, classic timebomb/aferimeter"""
    methuselahs = ['timebomb']
    oscillators = ['quadrupleburloaferimeter']
    _west2(methuselahs, oscillators)


def west_salt_lake():
    """west2 configuration, wider variety of methuselahs and oscillators"""
    methuselahs = ['mustardseed', 'multuminparvo', 'twoglidermess']
    oscillators = ['koksgalaxy', 'ring64', 'switchbox']
    _west2(methuselahs, oscillators)


def west_milwaukee():
    """west3 with classic aferimeters"""
    oscillators = ['quadrupleburloaferimeter']
    _west3(oscillators)


def west_detroit():
    """west3 with classic aferimeters"""
    oscillators = ['koksgalaxy', 'ring64', 'switchbox', 'dinnertable']
    _west3(oscillators)


# --------------------


def _west1(methuselahs, oscillators):
    """
    o     o
      m m 
    o     o
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    centerx = cols//2
    centery = rows//2

    lengthscale = 30
    xjitter = lambda: random.randint(-lengthscale//2, lengthscale//2)
    yjitter = lambda: random.randint(-lengthscale//2, lengthscale//2)

    # --------------------
    # Oscillator locations

    team1_oscillators = []
    team2_oscillators = []

    nw_x = sw_x = cols//4
    ne_x = se_x = 3*cols//4

    nw_y = ne_y = rows//4
    sw_y = se_y = 3*rows//4

    mode = random.randint(0,1)
    if mode==0:
        team1_oscillators.append((nw_x, nw_y))
        team1_oscillators.append((sw_x, sw_y))
        team2_oscillators.append((ne_x, ne_y))
        team2_oscillators.append((se_x, se_y))
    else:
        team1_oscillators.append((nw_x, nw_y))
        team2_oscillators.append((sw_x, sw_y))
        team1_oscillators.append((ne_x, ne_y))
        team2_oscillators.append((se_x, se_y))

    oscillator = random.choice(oscillators)

    def _assemble_patterns(team_oscillators):
        team_pattern = []
        for i, (x_, y_) in enumerate(team_oscillators):
            xx = x_ + xjitter()
            yy = y_ + yjitter()
            vf = bool(random.randint(0,1))
            hf = bool(random.randint(0,1))
            if i==0:
                team_pattern = get_grid_pattern(oscillator, rows, cols, xoffset=xx, yoffset=yy, vflip=vf, hflip=hf)
            else:
                team_pattern = pattern_union([team_pattern, get_grid_pattern(oscillator, rows, cols, xoffset=xx, yoffset=yy, vflip=vf, hflip=hf)])
        return team_pattern

    team1_pattern = _assemble_patterns(team1_oscillators)
    team2_pattern = _assemble_patterns(team2_oscillators)

    # --------------------
    # Methuselah locations

    xx1 = cols//3 + xjitter()
    xx2 = 2*cols//3 + xjitter()
    yy = rows//2 + yjitter()

    m = ['grandpa_42100', 'timebomb', 'mustardseed', 'spaceshipgrower']
    methuselah = random.choice(m)

    vf = bool(random.randint(0,1))
    hf = bool(random.randint(0,1))
    team1_pattern = pattern_union([team1_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=xx1, yoffset=yy, vflip=vf, hflip=hf)])
    team2_pattern = pattern_union([team2_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=xx2, yoffset=yy, vflip=vf, hflip=hf)])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


def _west2(oscillators, methuselahs):
    """
    o m o
    o m o
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    centerx = cols//2
    centery = rows//2

    lengthscale = 40
    xjitter = lambda: random.randint(-lengthscale//2, lengthscale//2)
    yjitter = lambda: random.randint(-lengthscale//2, lengthscale//2)

    # --------------------
    # Oscillator locations

    team1_oscillators = []
    team2_oscillators = []

    nw_x = sw_x = cols//4
    ne_x = se_x = 3*cols//4

    nw_y = ne_y = rows//4
    sw_y = se_y = 3*rows//4

    mode = random.randint(0,1)
    if mode==0:
        team1_oscillators.append((nw_x, nw_y))
        team1_oscillators.append((sw_x, sw_y))
        team2_oscillators.append((ne_x, ne_y))
        team2_oscillators.append((se_x, se_y))
    else:
        team1_oscillators.append((nw_x, nw_y))
        team2_oscillators.append((sw_x, sw_y))
        team1_oscillators.append((ne_x, ne_y))
        team2_oscillators.append((se_x, se_y))

    oscillator = 'quadrupleburloaferimeter'

    def _assemble_patterns(team_oscillators):
        team_pattern = []
        for i, (x_, y_) in enumerate(team_oscillators):
            xx = x_ + xjitter()
            yy = y_ + yjitter()
            vf = bool(random.randint(0,1))
            hf = bool(random.randint(0,1))
            if i==0:
                team_pattern = get_grid_pattern(oscillator, rows, cols, xoffset=xx, yoffset=yy, vflip=vf, hflip=hf)
            else:
                team_pattern = pattern_union([team_pattern, get_grid_pattern(oscillator, rows, cols, xoffset=xx, yoffset=yy, vflip=vf, hflip=hf)])
        return team_pattern

    team1_pattern = _assemble_patterns(team1_oscillators)
    team2_pattern = _assemble_patterns(team2_oscillators)

    # --------------------
    # Methuselah locations

    xx = cols//2 + xjitter()
    yy1 = rows//4 + yjitter()
    yy2 = 3*rows//4 + yjitter()

    def _swap(a, b):
        temp = a
        a = b
        b = temp

    if bool(random.randint(0,1)):
        _swap(yy1, yy2)

    m = ['grandpa_42100', 'timebomb', 'mustardseed', 'spaceshipgrower']
    methuselah = random.choice(m)

    vf = bool(random.randint(0,1))
    hf = bool(random.randint(0,1))
    team1_pattern = pattern_union([team1_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=xx, yoffset=yy1, vflip=vf, hflip=hf)])
    team2_pattern = pattern_union([team2_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=xx, yoffset=yy2, vflip=vf, hflip=hf)])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


def _west3(oscillators):
    """
    o                     o
    o  bisecting puffers  o
    o                     o
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    centerx = cols//2
    centery = rows//2

    lengthscale = 30
    xjitter = lambda: random.randint(-lengthscale//2, lengthscale//2)
    yjitter = lambda: random.randint(-lengthscale//2, lengthscale//2)

    # --------------------
    # Oscillator locations

    team1_oscillators = []
    team2_oscillators = []

    xx1 = cols//6
    xx2 = 5*cols//6

    yy1 = rows//4
    yy2 = rows//2
    yy3 = 3*rows//4

    order = [1,]*3 + [0,]*3
    random.shuffle(order)

    points = itertools.product([xx1, xx2], [yy1, yy2, yy3])

    for o, p in zip(order, points):
        if o==0:
            team1_oscillators.append(p)
        elif o==1:
            team2_oscillators.append(p)

    oscillator = random.choice(oscillators)

    def _assemble_patterns(team_oscillators):
        team_pattern = []
        for i, (x_, y_) in enumerate(team_oscillators):
            xx = x_ + xjitter()
            yy = y_ + yjitter()
            vf = bool(random.randint(0,1))
            hf = bool(random.randint(0,1))
            if i==0:
                team_pattern = get_grid_pattern(oscillator, rows, cols, xoffset=xx, yoffset=yy, vflip=vf, hflip=hf)
            else:
                team_pattern = pattern_union([team_pattern, get_grid_pattern(oscillator, rows, cols, xoffset=xx, yoffset=yy, vflip=vf, hflip=hf)])
        return team_pattern

    team1_pattern = _assemble_patterns(team1_oscillators)
    team2_pattern = _assemble_patterns(team2_oscillators)

    # ----------------
    # Puffer locations

    xx = cols//2 + xjitter()
    yy1 = rows//4 + yjitter()
    yy2 = 3*rows//4 + yjitter()

    methuselah = 'bisectingpuffers'
    team1_pattern = pattern_union([team1_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=xx, yoffset=yy1, hflip=False)])
    team2_pattern = pattern_union([team2_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=xx, yoffset=yy2, hflip=True)])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)



if __name__=="__main__":
    # west1
    west_baltimore()
    west_boston()

    # west2
    west_seattle()
    west_salt_lake()

    # west3
    west_milwaukee()
    west_detroit()

