from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def detroit_carbomb():
    m = ['fred', 'wilma', 'grandpa_42100', 'grandpa_13629876']
    carbomb(m, True)


def jersey_carbomb():
    m = ['timebomb', 'rabbit', 'bunnies', 'multuminparvo', 'acorn', 'twoglidermess', 'spaceshipgrower']
    carbomb(m, False)


def northdakota_carbomb():
    p = [
        ('x66', 90),
        ('flotilla_14wss', 0),
        ('bisectingpuffers', 270),
    ]
    methuselah, rotdeg = random.choice(p)
    carbomb([methuselah], True, rotdeg=rotdeg)


def elko_carbomb():
    m = ['crabstretcher']
    carbomb(m, True)


def carbomb(methuselahs, are_methuselahs_large, rotdeg=None):
    """
    top half/third: wicks
    bottom half/third: methuselahs
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    # Assemble tuples of points
    team1_points = []
    team2_points = []

    # Main input parameter:
    spacing = random.randint(8,18)

    # Additional random parameters
    start_y = random.randint(1, spacing)
    end_y = rows//2 - random.randint(spacing, 2*spacing)
    color_mode = random.randint(1,2)

    n_placements = ROWS//spacing

    if color_mode == 1:

        # Color mode 1: single colored wicks

        n_placements_even = (n_placements//2)*2
        start_xs = [int(((i+1)/n_placements_even)*cols) for i in range(n_placements_even)]

        for y in range(start_y, end_y):

            for j, start_x in enumerate(start_xs):

                x = start_x + y

                xx = (x+cols)%cols
                yy = (y+rows)%rows

                xxp1 = (x+1+cols)%cols
                yym1 = (y-1+rows)%rows

                if j%2==0:
                    team1_points.append((xx, yy))
                    team1_points.append((xxp1, yym1))
                else:
                    team2_points.append((xx, yy))
                    team2_points.append((xxp1, yym1))

    elif color_mode == 2:

        # Color mode 2: multi colored wicks

        start_xs = [int(((i+1)/n_placements)*cols) for i in range(n_placements)]

        for y in range(start_y, end_y):

            for j, start_x in enumerate(start_xs):

                x = start_x + y

                xx = (x+cols)%cols
                yy = (y+rows)%rows

                if yy%2==0:
                    team1_points.append((xx, yy))
                else:
                    team2_points.append((xx, yy))

                xxp1 = (x+1+cols)%cols
                yym1 = (y-1+rows)%rows

                if yym1%2==0:
                    team1_points.append((xxp1, yym1))
                else:
                    team2_points.append((xxp1, yym1))

    # Convert points list to pattern
    team1_pattern = []
    team2_pattern = []
    for y in range(rows):
        team1_row = []
        team2_row = []

        for x in range(cols):
            if (x, y) in team1_points:
                team1_row.append("o")
            else:
                team1_row.append(".")

            if (x, y) in team2_points:
                team2_row.append("o")
            else:
                team2_row.append(".")

        team1_row_str = "".join(team1_row)
        team1_pattern.append(team1_row_str)

        team2_row_str = "".join(team2_row)
        team2_pattern.append(team2_row_str)

    # Combine wicks pattern with methuselahs
    xjitter = lambda: random.randint(-2*spacing, 2*spacing)

    centerx1 = cols//3 + xjitter()
    centerx2 = 2*cols//3 + xjitter()

    if are_methuselahs_large:
        # Place in bottom 2/3 and y-jitter up or down
        yjitter = lambda: random.randint(-spacing, spacing)
        centery1 = 2*rows//3 + yjitter()
        centery2 = 2*rows//3 + yjitter()
    else:
        # Place in bottom 1/2 and y-jitter down
        yjitter = lambda: random.randint(0, 2*spacing)
        centery1 = rows//2 + yjitter()
        centery2 = rows//2 + yjitter()

    methuselah = random.choice(methuselahs)

    if rotdeg is None:
        # Random orientation (vlips/hflips)
        team1_pattern = pattern_union([team1_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=centerx1,   yoffset=centery1, vflip=bool(random.randint(0,1)), hflip=bool(random.randint(0,1)))])
        team2_pattern = pattern_union([team2_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=centerx2,   yoffset=centery2, vflip=bool(random.randint(0,1)), hflip=bool(random.randint(0,1)))])
    else:
        # specific orientation
        team1_pattern = pattern_union([team1_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=centerx1,   yoffset=centery1, rotdeg=rotdeg)])
        team2_pattern = pattern_union([team2_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=centerx2,   yoffset=centery2, rotdeg=rotdeg)])

    if bool(random.randint(0,1)):
        team1_pattern = hflip_pattern(team1_pattern)
        team2_pattern = hflip_pattern(team2_pattern)

    if bool(random.randint(0,1)):
        team1_pattern = vflip_pattern(team1_pattern)
        team2_pattern = vflip_pattern(team2_pattern)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


if __name__=="__main__":
    #detroit_carbomb()
    #jersey_carbomb()
    northdakota_carbomb()
    #elko_carbomb()


