from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern, rot_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def crunchy_crash():

    # Nice solid crunch
    s = ['heavyweightspaceship', 'middleweightspaceship', 'lightweightspaceship']
    o = ['ring64']
    _crash(s, o, are_spaceships_large=False, vspace=random.randint(20, 35))

def spaceship_crash():

    # Large methuselahs and large spaceships
    s = ['x66']
    o = ['fred', 'wilma', 'grandpa_305230', 'grandpa_42100', 'ring64']
    _crash(s, o, are_spaceships_large=True, vspace=random.randint(35, 50))

def spaceship_crash2():

    # Big spaceships, tiny methuselahs
    s = ['tagalong']
    o = ['bunnies', 'timebomb', 'multuminparvo', 'mustardseed']
    _crash(s, o, are_spaceships_large=True, vspace=random.randint(25, 35))

def big_crash():

    # Big spaceships, big oscillators and methuselahs
    s = ['tagalong']
    o = ['pulsar25', '13on30', 'ring64', 'fred', 'wilma']
    _crash(s, o, are_spaceships_large=True, vspace=random.randint(32, 35))

def sea_turtles():

    # Sea turtles vs simple methuselahs
    s = ['x66']
    o = ['rpentomino', 'piheptomino']
    _crash(s, o, are_spaceships_large=True, vspace=random.randint(30, 35))

def beach_crash():

    # Spaceships vs simple methuselahs
    s = ['heavyweightspaceship', 'middleweightspaceship', 'lightweightspaceship']
    o = ['rpentomino', 'bunnies', 'timebomb', 'multuminparvo']
    _crash(s, o, are_spaceships_large=False, vspace=random.randint(25, 35))

def mountain_crash():

    # Spaceships vs simple methuselahs, with plenty of room for the methuselahs to grow
    s = ['heavyweightspaceship', 'middleweightspaceship', 'lightweightspaceship', 'x66']
    o = ['rpentomino', 'bunnies', 'timebomb', 'multuminparvo', 'mustardseed']
    _crash(s, o, are_spaceships_large=False, vspace=random.randint(31, 50))


def flotilla_crash():

    # Spaceships vs simple methuselahs, with plenty of room for the methuselahs to grow
    s = ['flotilla_14wss']
    o = ['bunnies', 'timebomb', 'multuminparvo', 'mustardseed']
    _crash(s, o, are_spaceships_large=False, vspace=random.randint(31, 50), rotate_spaceships=True)


def _crash(spaceships, oscillators, are_spaceships_large=False, vspace=None, rotate_spaceships=False):
    """
    fix the y-values
    fix the y-jitter (minimal)
    set the x-values
    fix the x-jitter (main source of variation)
    """
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

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
        
        #orient_l2r = bool(random.randint(0,1))
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

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


if __name__=="__main__":
    #crunchy_crash()
    #spaceship_crash()
    #spaceship_crash2()
    #big_crash()
    #sea_turtles()
    #beach_crash()
    #mountain_crash()
    flotilla_crash()
