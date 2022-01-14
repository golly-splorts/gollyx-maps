from gollyx_maps.patterns import pattern_union
from gollyx_maps.utils import pattern2url
import itertools
import random


def gaussian_pot_pie(rows, cols, seed=None):
    """12 closely-knit splotches of live cells"""
    team1_pattern, team2_pattern = _get_gaussian_grid(3, 4, rows, cols, seed=None, density_lim=[0.10, 0.12], blobby_lim=[12, 14])
    _print_patterns(rows, cols, team1_pattern, team2_pattern)


def gaussian_old_style(rows, cols, seed=None):
    """6-pack of gaussian cans"""
    team1_pattern, team2_pattern = _get_gaussian_grid(2, 3, rows, cols, seed=None, density_lim=[0.18, 0.20], blobby_lim=[8, 8])
    _print_patterns(rows, cols, team1_pattern, team2_pattern)


def gaussian_gliders(rows, cols, seed=None):
    """sparse gaussians make gliders"""
    team1_pattern, team2_pattern = _get_gaussian_grid(1, 2, rows, cols, seed=None, density_lim=[0.03, 0.08], blobby_lim=[2, 8])
    _print_patterns(rows, cols, team1_pattern, team2_pattern)


def gaussian_10and2(rows, cols, seed=None):
    """4 gaussians, densities and stddevs between 10 and 14 (2)"""
    team1_pattern, team2_pattern = _get_gaussian_grid(2, 2, rows, cols, seed=None, density_lim=[0.10, 0.14], blobby_lim=[10, 14])
    _print_patterns(rows, cols, team1_pattern, team2_pattern)


def gaussian_bimodal(rows, cols, seed=None):
    """bimodal gaussians"""
    team1_pattern, team2_pattern = _get_gaussian_grid(2, 2, rows, cols, seed=None, density_lim=[0.10, 0.14], blobby_lim=[10, 14])
    _print_patterns(rows, cols, team1_pattern, team2_pattern)


def _print_patterns(rows, cols, team1_pattern, team2_pattern):
    team1_pattern = ["".join(pattrow) for pattrow in team1_pattern]
    team2_pattern = ["".join(pattrow) for pattrow in team2_pattern]

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=3"
    print(url)


def _get_gaussian_grid(blobrows, blobcols, rows, cols, seed=None, density_lim=[0.10, 0.15], blobby_lim=[4, 8]):
    """
    create a grid of size rows x cols
    with blobrows x blobcols random Gaussian blobs
    """
    if seed is not None:
        random.seed(seed)

    if (blobrows*blobcols)%2!=0:
        err = "Error: product of blob rows/cols must be even overall: "
        err += f"{blobrows} x {blobcols} = {blobrows*blobcols} is not even"
        raise Exception(err)

    # Density = fraction of cells that are alive, of any color
    if len(density_lim) != 2:
        raise Exception(f"Error: density_lim variable should be a list of two numbers")
    if density_lim[0] > density_lim[1]:
        density_lim = reversed(density_lim)
    # Randomly sample from the uniform interval density_lim
    density = density_lim[0] + random.random()*(density_lim[1]-density_lim[0])

    # ----------------
    # Parameters

    stdx = cols//(blobcols*random.randint(*blobby_lim))
    stdy = cols//(blobcols*random.randint(*blobby_lim))

    jitter = 5

    apt = (blobcols*blobrows)//2
    team_assignments = [1,]*apt + [2,]*apt
    random.shuffle(team_assignments)

    dbcols = blobcols*2
    dbrows = blobrows*2

    centerxs = [(j+1)*cols//dbcols for j in range(0, dbcols, 2)]
    centerys = [(k+1)*rows//dbrows for k in range(0, dbrows, 2)]



    # Get number of live cells, and live per team (pt)
    ncells = rows * cols
    nlivecells = ((ncells * density)//2)*2
    nlivecellsperteam = nlivecells // 2
    nlivecellsperblob = nlivecellsperteam // (blobcols*blobrows)

    # Store two lists of team patterns, to be unionized at the end
    team_patterns = [[], []]

    # Each blob is assigned to a random team
    master_points = set()
    for i, (centerx, centery) in enumerate(itertools.product(centerxs, centerys)):

        team_ix = team_assignments[i]-1

        cx = centerx + random.randint(-jitter, jitter)
        cy = centery + random.randint(-jitter, jitter)

        team_points = set()
        while len(team_points) < nlivecellsperblob:
            randx = int(random.gauss(cx, stdx))
            randy = int(random.gauss(cy, stdy))
            if (randx >= 0 and randx < cols) and (randy >= 0 and randy < rows):
                if (randx, randy) not in master_points:
                    team_points.add((randx, randy))
                    master_points.add((randx, randy))

        # Assemble the circle dot diagram for team
        team_pattern = []
        for y in range(rows):
            this_row = []
            for x in range(cols):
                if (x, y) in team_points:
                    this_row.append("o")
                else:
                    this_row.append(".")
            this_rowstr = "".join(this_row)
            team_pattern.append(this_rowstr)

        team_patterns[team_ix].append(team_pattern)

    team1_pattern = pattern_union(team_patterns[0], flatten=False)
    team2_pattern = pattern_union(team_patterns[1], flatten=False)

    return team1_pattern, team2_pattern
