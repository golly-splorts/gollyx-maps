import json
import os
import random
from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern
from gollyx_maps.utils import pattern2url
from .toroidal import (
    donutmath_twocolor,
    porchlights_twocolor,
)


def get_vi_pattern_function_map():
    return {
        # Carbombs:
        "detroit_carbomb": detroit_carbomb,
        "jersey_carbomb": jersey_carbomb,
        "northdakota_carbomb": northdakota_carbomb,
        "elko_carbomb": elko_carbomb,

        # Crashes:
        "crunchy_crash": crunchy_crash,
        "tasty_crash": tasty_crash, 
        "butterfly_crash": butterfly_crash,
        "elephant_crash": elephant_crash,
        "sea_turtles": sea_turtles,
        "beach_crash": beach_crash,
        "cave_crash": cave_crash,
        "flotilla_crash": flotilla_crash,

        # Parties:
        "bunny_party": bunny_party,
        "domino_party": domino_party,
        "dove_party": dove_party,
        "multum_in_party": multum_in_party,

        # Quad:
        "quad_beatty": quad_beatty,
        "quad_barstow": quad_barstow,
        "quad_bakersfield": quad_bakersfield,

        # Spacetime complex:
        "spacetime_complex_north": complex_v,
        "spacetime_complex_east": complex_h,
        "bifurcating_spacetime_north": bifurcating_v,
        "bifurcating_spacetime_east": bifurcating_h,

        # Standoffs:
        "tacoma_standoff": tacoma_standoff,
        "tombstone_standoff": tombstone_standoff,
        "red_rock_standoff": red_rock_standoff,
        "cheyenne_showdown": cheyenne_showdown,
        "santa_fe_standoff": santa_fe_standoff,
        "caliente_standoff": caliente_standoff,
        "spaceport_standoff": spaceport_standoff,
        "suns_out_gosper_guns_out": suns_out_gosper_guns_out

        # West:
        "west_baltimore": west_baltimore,
        "west_cambridge": west_cambridge,
        "west_seattle": west_seattle,
        "west_salt_lake": west_salt_lake,
        "west_milwaukee": west_milwaukee,
        "west_detroit": west_detroit,

        # Wicks:
        "spider_cave": wick1,
        "dragon_cave": wick2,

        # Toroidal map patterns:
        "hellmath": donutmath_twocolor,
        "porchlights": porchlights_twocolor,
    }


############################################################
################### carbombs ###############################
############################################################


def detroit_carbomb(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['fred', 'wilma', 'grandpa_42100', 'grandpa_13629876']
    _carbomb(rows, cols, m, True)


def jersey_carbomb(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['timebomb', 'rabbit', 'bunnies', 'multuminparvo', 'acorn', 'twoglidermess', 'spaceshipgrower']
    _carbomb(rows, cols, m, False)


def northdakota_carbomb(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    p = [
        ('x66', 90),
        ('flotilla_14wss', 0),
        ('bisectingpuffers', 270),
    ]
    methuselah, rotdeg = random.choice(p)
    _carbomb(rows, cols, [methuselah], True, rotdeg=rotdeg)


def elko_carbomb(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['crabstretcher']
    _carbomb(rows, cols, m, True)


def _carbomb(rows, cols, methuselahs, are_methuselahs_large, rotdeg=None):
    """
    top half/third: wicks
    bottom half/third: methuselahs
    """
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

    return s1, s2


############################################################
################### crashes ################################
############################################################


def crunchy_crash(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    # Nice solid crunch
    s = ['heavyweightspaceship', 'middleweightspaceship', 'lightweightspaceship']
    o = ['ring64']
    _crash(rows, cols, s, o, are_spaceships_large=False, vspace=random.randint(20, 35))

def tasty_crash(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    # Large methuselahs and large spaceships
    s = ['x66']
    o = ['fred', 'wilma', 'grandpa_305230', 'grandpa_42100', 'ring64']
    _crash(rows, cols, s, o, are_spaceships_large=True, vspace=random.randint(35, 50))

def butterfly_crash(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    # Big spaceships, tiny methuselahs
    s = ['tagalong']
    o = ['bunnies', 'timebomb', 'multuminparvo', 'mustardseed']
    _crash(rows, cols, s, o, are_spaceships_large=True, vspace=random.randint(25, 35))

def elephant_crash(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    # Big spaceships, big oscillators and methuselahs
    s = ['tagalong']
    o = ['pulsar25', '13on30', 'ring64', 'fred', 'wilma']
    _crash(rows, cols, s, o, are_spaceships_large=True, vspace=random.randint(32, 35))

def sea_turtles(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    # Sea turtles vs simple methuselahs
    s = ['x66']
    o = ['rpentomino', 'piheptomino']
    _crash(rows, cols, s, o, are_spaceships_large=True, vspace=random.randint(30, 35))

def beach_crash(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    # Spaceships vs simple methuselahs
    s = ['heavyweightspaceship', 'middleweightspaceship', 'lightweightspaceship']
    o = ['rpentomino', 'bunnies', 'timebomb', 'multuminparvo']
    _crash(rows, cols, s, o, are_spaceships_large=False, vspace=random.randint(25, 35))

def cave_crash(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    # Spaceships vs simple methuselahs, with plenty of room for the methuselahs to grow
    s = ['heavyweightspaceship', 'middleweightspaceship', 'lightweightspaceship', 'x66']
    o = ['rpentomino', 'bunnies', 'timebomb', 'multuminparvo', 'mustardseed']
    _crash(rows, cols, s, o, are_spaceships_large=False, vspace=random.randint(31, 50))


def flotilla_crash(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    # Spaceships vs simple methuselahs, with plenty of room for the methuselahs to grow
    s = ['flotilla_14wss']
    o = ['bunnies', 'timebomb', 'multuminparvo', 'mustardseed']
    _crash(rows, cols, s, o, are_spaceships_large=False, vspace=random.randint(31, 50), rotate_spaceships=True)


def _crash(rows, cols, spaceships, oscillators, are_spaceships_large=False, vspace=None, rotate_spaceships=False):
    """
    fix the y-values
    fix the y-jitter (minimal)
    set the x-values
    fix the x-jitter (main source of variation)
    """
    # Assemble tuples of points
    team1_points = []
    team2_points = []

    if vspace is None or vspace < 0:
        vspace = random.randint(20, 35)

    n_placements = ROWS//vspace
    n_placements_even = (n_placements//2)*2

    placements = [1,]*(n_placements_even//2) + [0,]*(n_placements_even//2)
    random.shuffle(placements)

    team1_spaceships  = []
    team1_oscillators = []

    team2_spaceships  = []
    team2_oscillators = []

    spaceship_pattern  = random.choice(spaceships)
    oscillator_pattern = random.choice(oscillators)

    if not are_spaceships_large:
        nspaceships = random.randint(1, 3)
    else:
        nspaceships = 1

    for i, p in enumerate(placements):

        # Wider x-jitter
        xjitter = lambda: random.randint(0, vspace)
        centerx1 = int(cols//6)   + xjitter()
        centerx2 = int(5*cols//6) - xjitter()
        
        orient_l2r = i%2==0

        if orient_l2r:
            xxs, xxo = centerx1, centerx2
        else:
            xxo, xxs = centerx1, centerx2

        # Limited y-jitter
        if not are_spaceships_large:
            yjitter = lambda: random.randint(-9, 9)
        else:
            yjitter = lambda: random.randint(-3, 3)
        yys = int(((i+1)/(n_placements_even+1))*rows) + yjitter()
        yyo = int(((i+1)/(n_placements_even+1))*rows) + yjitter()

        def gen_spaceship(x, y):
            yy = int(((i+1)/(n_placements_even+1))*rows) + yjitter()
            if rotate_spaceships:
                rdeg = 90
                hf = False
                vf = False
            else:
                rdeg = 0
                hf = orient_l2r
                vf = bool(random.randint(0,1))
            return get_grid_pattern(spaceship_pattern, rows, cols, xoffset=x, yoffset=yy, vflip=vf, hflip=hf, rotdeg=rdeg)

        if p==0:
            hf = bool(random.randint(0,1))
            team1_oscillators.append(                                                                
                get_grid_pattern(oscillator_pattern, rows, cols, xoffset=xxo, yoffset=yyo, hflip=hf)
            )
            team1_spaceships.append(gen_spaceship(xxs, yys))
            if nspaceships > 1:
                # Second spaceship
                team1_spaceships.append(gen_spaceship(xxs-20, yys))
                if nspaceships > 2:
                    # Third spaceship
                    team1_spaceships.append(gen_spaceship(xxs+20, yys))
        else:
            hf = bool(random.randint(0,1))
            team2_oscillators.append(                                                                
                get_grid_pattern(oscillator_pattern, rows, cols, xoffset=xxo, yoffset=yyo, hflip=hf)
            )
            team2_spaceships.append(gen_spaceship(xxs, yys))
            if nspaceships > 1:
                # Second spaceship
                team2_spaceships.append(gen_spaceship(xxs-20, yys))
                if nspaceships > 2:
                    # Third spaceship
                    team2_spaceships.append(gen_spaceship(xxs+20, yys))

    team1_pattern = pattern_union(team1_spaceships + team1_oscillators)
    team2_pattern = pattern_union(team2_spaceships + team2_oscillators)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return s1, s2


############################################################
################### parties ################################
############################################################


def bunny_party(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['rabbit', 'bunnies']
    _party(rows, cols, methuselahs, (5, 25))


def domino_party(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['cheptomino', 'piheptomino', 'rpentomino']
    _party(rows, cols, methuselahs, (5, 16))


def dove_party(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['wing', 'dove']
    _party(rows, cols, methuselahs, (4, 13))


def multum_in_party(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['acorn', 'multuminparvo', 'mustardseed']
    _party(rows, cols, methuselahs, (5, 25))


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

    return s1, s2


############################################################
################### quad ###################################
############################################################


def quad_beatty(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['acorn', 'mustardseed', 'rabbit', 'bunnies']
    _quad(rows, cols, m)


def quad_barstow(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['timebomb', 'multuminparvo', 'twoglidermess']
    _quad(rows, cols, m)


def quad_bakersfield(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['fred', 'wilma', 'grandpa_42100', 'grandpa_13629876']
    _quad(rows, cols, m)


def _quad(rows, cols, methuselahs):
    """
    four methuselahs in the four quadrant corners
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    centerx = cols//2
    centery = rows//2

    methuselah = random.choice(methuselahs)

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

    return s1, s2


############################################################
################### spacetime complex ######################
############################################################


def complex_v(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['backrake2']
    _spacetime_complex_v(m)


def complex_h(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['backrake2']
    _spacetime_complex_h(m, rotdeg=90)


def bifurcating_v(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['bisectingpuffers']
    _spacetime_complex_v(m, rotdeg=90)


def bifurcating_h(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    m = ['bisectingpuffers']
    _spacetime_complex_h(m)


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
    mmx = rows - 1 - xdim

    # messmaker xwiggle
    xwiggle = 20
    xjitter = lambda: random.randint(-xwiggle//2, xwiggle//2)
    mmx += xjitter()

    # messmaker ywiggle
    ywiggle = 8
    yjitter = lambda: random.randint(-ywiggle//2, ywiggle//2)
    mm1y += yjitter()
    mm2y += yjitter()

    r = random.randint(1,4)
    if r in [1,2,3]:
        # Orientation 1: both spaceship generators moving same direction
        generator1 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mmx, yoffset=mm1y, rotdeg=rotdeg, hflip=bool(random.randint(0,1))
        )
        generator2 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mmx, yoffset=mm2y, rotdeg=rotdeg
        )
    elif r in [4]:
        # Orientation 2: spaceship generators moving opposite direction
        generator1 = get_grid_pattern(
            messmaker, rows, cols, xoffset=mmx, yoffset=mm1y, rotdeg=rotdeg, vflip=True, hflip=bool(random.randint(0,1)) 
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

    # s1 = pattern2url(c1)
    # s2 = pattern2url(c2)

    if bool(random.randint(0,1)):
        s1 = pattern2url(c1)
        s2 = pattern2url(c2)
    else:
        s1 = pattern2url(c2)
        s2 = pattern2url(c1)

    return s1, s2


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

    if rotdeg is None:
        rotdeg = 0
    (xdim, ydim) = get_pattern_size(messmaker, rotdeg=rotdeg)

    # messmaker positions
    mm1x = cols // 4
    mm2x = cols // 2 + cols // 4
    mmy = rows - 1 - ydim

    # messmaker xwiggle
    xwiggle = 12
    xjitter = lambda: random.randint(-xwiggle//2, xwiggle//2)
    mm1x += xjitter()
    mm2x += xjitter()

    # messmaker ywiggle
    ywiggle = 4
    yjitter = lambda: random.randint(-ywiggle//2, ywiggle//2)
    mmy += yjitter()

    r = random.randint(1,4)
    if r in [1,2,3]:
        # Orientation 1: both spaceship generators moving same direction
        generator1 = get_grid_pattern(
            messmaker, rows, cols, rotdeg=rotdeg, xoffset=mm1x, yoffset=mmy, hflip=True # bool(random.randint(0,1))
        )
        generator2 = get_grid_pattern(
            messmaker, rows, cols, rotdeg=rotdeg, xoffset=mm2x, yoffset=mmy
        )
    elif r in [4]:
        # Orientation 2: spaceship generators moving opposite direction
        generator1 = get_grid_pattern(
            messmaker, rows, cols, rotdeg=rotdeg, xoffset=mm1x, yoffset=mmy, hflip=True, vflip=bool(random.randint(0,1))
        )
        generator2 = get_grid_pattern(
            messmaker, rows, cols, rotdeg=rotdeg, xoffset=mm2x, yoffset=mmy
        )

    stilllifes = ['block', 'donut', 'beehive']
    stilllife = random.choice(stilllifes)

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

    if bool(random.randint(0,1)):
        s1 = pattern2url(c1)
        s2 = pattern2url(c2)
    else:
        s1 = pattern2url(c2)
        s2 = pattern2url(c1)

    return s1, s2


############################################################
################### standoffs ##############################
############################################################


def tacoma_standoff(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['acorn', 'mustardseed', 'rabbit', 'bunnies']
    _standoff(rows, cols, methuselahs)


def tombstone_standoff(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['acorn', 'mustardseed', 'rabbit', 'bunnies']
    _standoff(rows, cols, methuselahs, opposite_day=True)


def red_rock_standoff(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['cheptomino', 'rpentomino']
    _standoff(rows, cols, methuselahs)


def cheyenne_showdown(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['timebomb', 'multuminparvo', 'twoglidermess']
    _standoff(rows, cols, methuselahs)


def santa_fe_standoff(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['timebomb', 'multuminparvo', 'twoglidermess']
    _standoff(rows, cols, methuselahs, opposite_day=True)


def caliente_standoff(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['grandpa_42100', 'grandpa_13629876']
    _standoff(rows, cols, methuselahs)


def spaceport_standoff(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    methuselahs = ['bisectingpuffers']
    _standoff(rows, cols, methuselahs)


def suns_out_gosper_guns_out(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    # This makes for some deliciously long and tricky paths to victory
    methuselahs = ['gosper_gun']
    _standoff(rows, cols, methuselahs)


def _standoff(rows, cols, methuselahs, opposite_day=False):
    """
    guns in the middle, methuselahs at the corners
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    centerx = cols//2
    centery = rows//2

    # -------------
    # Guns, pew pew
    gun = 'gosper_gun'

    yw, xw = get_pattern_size(gun)

    xjitter = lambda: random.randint(xw//2, xw//2 + 8)
    x1 = centerx - xjitter()
    x2 = centerx + xjitter()

    yjitter = lambda: random.randint(-8, 8)
    y1 = centery - yjitter()
    y2 = centery + yjitter()

    flip = bool(random.randint(0, 1))

    # The flip boolean logic ensures that the guns are always:
    # - next to each other
    # - pointing toward the same (NW/SE) corners
    # - outside of each others' range
    team1_pattern = get_grid_pattern(gun, rows, cols, xoffset=x1, yoffset=y1, vflip=flip,     hflip=flip)
    team2_pattern = get_grid_pattern(gun, rows, cols, xoffset=x2, yoffset=y2, vflip=not flip, hflip=not flip)


    # -----------
    # Methuselahs

    methuselah = random.choice(methuselahs)

    nw_x = cols//6
    nw_y = rows//6

    se_x = 5*cols//6
    se_y = 5*rows//6

    if opposite_day:
        # "nw" is actually ne
        nw_x = 5*cols//6
        # "se" is actually sw
        se_x = cols//6

    d = 11

    xjitter = lambda: random.randint(-d, d)
    yjitter = lambda: random.randint(0, d)

    r = lambda: bool(random.randint(0,1))

    # Put methuselahs in the NW/SE corners
    team1_pattern = pattern_union([team1_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=nw_x + xjitter(), yoffset=nw_y + yjitter(), vflip=r(), hflip=r())])
    team2_pattern = pattern_union([team2_pattern, get_grid_pattern(methuselah, rows, cols, xoffset=se_x + xjitter(), yoffset=se_y + yjitter(), vflip=r(), hflip=r())])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return s1, s2


############################################################
################### west ###################################
############################################################


def west_baltimore(rows, cols, seed=None):
    """west1 configuration, classic timebomb/aferimeter"""
    if seed is not None:
        random.seed(seed)
    methuselahs = ['timebomb']
    oscillators = ['quadrupleburloaferimeter']
    _west1(rows, cols, methuselahs, oscillators)


def west_cambridge(rows, cols, seed=None):
    """west1 configuration, wider variety of methuselahs and oscillators"""
    if seed is not None:
        random.seed(seed)
    methuselahs = ['mustardseed', 'multuminparvo', 'twoglidermess']
    oscillators = ['koksgalaxy', 'ring64', 'switchbox']
    _west1(rows, cols, methuselahs, oscillators)


def west_seattle(rows, cols, seed=None):
    """west2 configuration, classic timebomb/aferimeter"""
    if seed is not None:
        random.seed(seed)
    methuselahs = ['timebomb']
    oscillators = ['quadrupleburloaferimeter']
    _west2(rows, cols, methuselahs, oscillators)


def west_salt_lake(rows, cols, seed=None):
    """west2 configuration, wider variety of methuselahs and oscillators"""
    if seed is not None:
        random.seed(seed)
    methuselahs = ['mustardseed', 'multuminparvo', 'twoglidermess']
    oscillators = ['koksgalaxy', 'ring64', 'switchbox']
    _west2(rows, cols, methuselahs, oscillators)


def west_milwaukee(rows, cols, seed=None):
    """west3 with classic aferimeters"""
    if seed is not None:
        random.seed(seed)
    oscillators = ['quadrupleburloaferimeter']
    _west3(rows, cols, oscillators)


def west_detroit(rows, cols, seed=None):
    """west3 with classic aferimeters"""
    if seed is not None:
        random.seed(seed)
    oscillators = ['koksgalaxy', 'ring64', 'switchbox', 'dinnertable']
    _west3(rows, cols, oscillators)


def _west1(rows, cols, methuselahs, oscillators):
    """
    o     o
      m m 
    o     o
    """
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

    return s1, s2


def _west2(rows, cols, oscillators, methuselahs):
    """
    o m o
    o m o
    """
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

    return s1, s2


def _west3(oscillators):
    """
    o                     o
    o  bisecting puffers  o
    o                     o
    """
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

    return s1, s2

############################################################
################### wicks ##################################
############################################################

def spider_cave(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)

    # Using wickstretcher pattern, mainly...
    wick_h, wick_w = get_pattern_size("wickstretcher")

    team1_pattern = None
    team2_pattern = None

    yjitter = lambda: random.randint(-int((1/7)*rows), int((1/7)*rows))

    # ----------------------------
    # Team 1 double wickstretchers

    for c in [1,2]:
        # Place at y = 1/3*rows and y = 2/3*rows
        team1_wickstretcher = get_grid_pattern(
            "wickstretcher",
            rows,
            cols,
            xoffset=cols//3,
            yoffset=c * rows // 3 + yjitter()
        )
        if team1_pattern is None:
            team1_pattern = team1_wickstretcher
        else:
            team1_pattern = pattern_union([team1_pattern, team1_wickstretcher])

        team2_wickstretcher = get_grid_pattern(
            "wickstretcher",
            rows,
            cols,
            xoffset=2*cols//3,
            yoffset=c * rows // 3 + yjitter(),
            hflip=True
        )
        if team2_pattern is None:
            team2_pattern = team2_wickstretcher
        else:
            team2_pattern = pattern_union([team2_pattern, team2_wickstretcher])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return s1, s2


def wick2(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)

    (wick_h, wick_w) = get_pattern_size("wickstretcher")

    (crab_h, crab_w) = get_pattern_size("crabstretcher")

    # Give ourselves a small margin on the edge of the map
    # (give the wickstretchers as much space as possible)
    margin = random.randint(2, 5)
    xbuff = wick_w // 2 + margin

    # Use this to jitter the vertical placement of both wickstretchers
    y_rel_jitter = wick_h // 2 - 2

    # Determine absolute y offset for both wickstretchers
    ybuff = y_rel_jitter
    y_abs_jitter = rows // 3 - 2 * wick_h
    y_abs_offset = random.randint(-y_abs_jitter, y_abs_jitter)

    # ---------------
    # Wickstretchers

    # Team 1 wickstretcher
    team1_yjitter_val = random.randint(-y_rel_jitter, y_rel_jitter)
    team1_wickstretcher = get_grid_pattern(
        "wickstretcher",
        rows,
        cols,
        xoffset=xbuff,
        yoffset=rows // 2 + y_abs_offset + team1_yjitter_val,
    )

    # Team 2 wickstretcher
    team2_yjitter_val = random.randint(-y_rel_jitter, y_rel_jitter)
    team2_wickstretcher = get_grid_pattern(
        "wickstretcher",
        rows,
        cols,
        xoffset=cols - xbuff,
        yoffset=rows // 2 + y_abs_offset + team2_yjitter_val,
        hflip=True,
        vflip=bool(random.getrandbits(1)),
    )

    # -----
    # Crabstretchers in the corners
    # Note that by default the crabstretcher goes up and to the left
    crab_margin = 20

    wickstretcher_bottom = y_abs_offset > 0
    if wickstretcher_bottom:
        # Crabs are at the top
        # Make crabs go down
        vflip_crabs = True
        # Down and still going to the left
        hflip_team1_crabs = False
        team1_xoffset = cols - 2*crab_w
        team1_yoffset = 2*crab_h
        team2_xoffset = 2*crab_w
        team2_yoffset = 2*crab_h
    else:
        # Crabs are at bottom
        # They should keep going up
        vflip_crabs = False
        team1_xoffset = cols - 2*crab_w
        team1_yoffset = rows - 2*crab_h
        team2_xoffset = 2*crab_w
        team2_yoffset = rows - 2*crab_h

    crab_jitter_max = 12
    crab1jitter = random.randint(0, crab_jitter_max)
    crab2jitter = random.randint(0, crab_jitter_max)

    team1_crab = get_grid_pattern(
        "crabstretcher",
        rows,
        cols,
        xoffset=team1_xoffset - crab1jitter,
        yoffset=team1_yoffset + crab1jitter,
        vflip=vflip_crabs,
    )

    team1_pattern = pattern_union([team1_wickstretcher, team1_crab])

    team2_crab = get_grid_pattern(
        "crabstretcher",
        rows,
        cols,
        xoffset=team2_xoffset + crab2jitter,
        yoffset=team2_yoffset - crab2jitter,
        vflip=vflip_crabs,
        hflip=True,
    )

    team2_pattern = pattern_union([team2_wickstretcher, team2_crab])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return s1, s2

