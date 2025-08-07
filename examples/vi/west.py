from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern, rot_pattern
from gollyx_maps.utils import pattern2url
import random


ROWS = 150
COLS = 240
SEED = None


def main():
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
            vf = bool(random.randint(0,1))
            return get_grid_pattern(spaceship_pattern, rows, cols, xoffset=x, yoffset=yy, vflip=vf, hflip=orient_l2r)

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
    main()
