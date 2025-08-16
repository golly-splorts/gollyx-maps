from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern, rot_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def st_v():
    m = ['backrake2']
    _spacetime_complex_v(m)


def st_h():
    m = ['backrake2']
    _spacetime_complex_h(m, rotdeg=90)


def b_v():
    m = ['bisectingpuffers']
    _spacetime_complex_v(m)


def b_h():
    m = ['bisectingpuffers']
    _spacetime_complex_h(m, rotdeg=90)


def _spacetime_complex_h(messmakers, rotdeg=None):
    """
            < mess-making
            < spaceships
    row of boxes . . . . . . .
            < mess-making
            < spaceships
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    # This is the messmaker pattern
    messmaker = random.choice(messmakers)

    if rotdeg is None:
        rotdeg = 0
    (xdim, ydim) = get_pattern_size(messmaker, rotdeg=rotdeg)

    # messmaker positions
    mm1y = rows // 4
    mm2y = rows // 2 + rows // 4

    # messmaker xwiggle
    xwiggle = 20
    xjitter = lambda: random.randint(-xwiggle//2, xwiggle//2)
    mmx = rows - 1 - xdim + xjitter()

    # messmaker ywiggle
    ywiggle = 8
    yjitter = lambda: random.randint(-ywiggle//2, ywiggle//2)
    mm1y += yjitter()
    mm2y += yjitter()

    r = random.randint(1,2)
    if True: # r == 1:
        # Orientation 1: both spaceship generators moving same direction
        generator1 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mmx, yoffset=mm1y, rotdeg=rotdeg, hflip=True
        )
        generator2 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mmx, yoffset=mm2y, rotdeg=rotdeg
        )
    else: # elif r==2:
        # Orientation 2: spaceship generators moving opposite direction
        generator1 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mmx, yoffset=mm1y, rotdeg=rotdeg, vflip=True, hflip=True
        )
        generator2 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mmx, yoffset=mm2y, rotdeg=rotdeg
        )

    stilllifes = ['block', 'donut', 'beehive']
    stilllife = random.choice(stilllifes)

    nboxes = random.randint(15, 25)
    box_patterns1 = []
    box_patterns2 = []
    for j in range(nboxes):
        box_y = rows // 2
        box_x = (j + 1) * (cols // (nboxes + 1))

        wiggle = 10
        box_x += random.randint(-wiggle//5, wiggle//5)
        box_y += random.randint(-wiggle//2, wiggle//2)

        box_pattern = get_grid_pattern(
            stilllife, rows, cols, xoffset=box_x, yoffset=box_y
        )

        # Alternating blocks
        if j % 2 == 0:
            box_patterns1.append(box_pattern)
        else:
            box_patterns2.append(box_pattern)

    c1 = pattern_union([generator1] + box_patterns1)
    c2 = pattern_union([generator2] + box_patterns2)

    s1 = pattern2url(c1)
    s2 = pattern2url(c2)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


def _spacetime_complex_v(messmakers, rotdeg=None):
    """

     ^ ^      .    ^ ^
     mess     .    mess
     makers   .    makers
              .
        row of boxes
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    # This is the messmaker pattern
    messmaker = random.choice(messmakers)

    (xdim, ydim) = get_pattern_size(messmaker)

    # messmaker positions
    mm1x = cols // 4
    mm2x = cols // 2 + cols // 4
    mmy = rows - 1 - ydim

    xwiggle = 12
    xjitter = lambda: random.randint(-xwiggle//2, xwiggle//2)

    mm1x += xjitter()
    mm2x += xjitter()

    r = random.randint(1,4)
    if True: #r in [1,2,3]:
        # Orientation 1: both spaceship generators moving same direction
        generator1 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mm1x, yoffset=mmy, hflip=True
        )
        generator2 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mm2x, yoffset=mmy
        )
    else: #elif r==4:
        # Orientation 2: spaceship generators moving opposite direction
        generator1 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mm1x, yoffset=mmy, rotdeg=rotdeg, vflip=True, hflip=True
        )
        generator2 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mm2x, yoffset=mmy, rotdeg=rotdeg
        )

    stilllifes = ['block', 'donut', 'beehive']
    stilllife = random.choice(stilllifes)

    ywiggle = 4
    yjitter = lambda: random.randint(-ywiggle//2, ywiggle//2)
    mmy += yjitter()

    nboxes = random.randint(10, 20)
    box_patterns1 = []
    box_patterns2 = []
    for i in range(nboxes):
        box_x = cols // 2
        box_y = (i + 1) * (rows // (nboxes + 1))

        wiggle = 10
        box_x += random.randint(-wiggle//2, wiggle//2)
        box_y += random.randint(-wiggle//5, wiggle//5)

        box_pattern = get_grid_pattern(
            stilllife, rows, cols, xoffset=box_x, yoffset=box_y
        )
        if i % 2 == 0:
            box_patterns1.append(box_pattern)
        else:
            box_patterns2.append(box_pattern)

    c1 = pattern_union([generator1] + box_patterns1)
    c2 = pattern_union([generator2] + box_patterns2)

    s1 = pattern2url(c1)
    s2 = pattern2url(c2)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


if __name__=="__main__":
    #st_v()
    #st_h()
    #b_v()
    b_h()

