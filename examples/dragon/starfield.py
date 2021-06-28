from gollyx_maps.utils import pattern2url
from gollyx_maps.patterns import get_grid_empty
import random


name = 'vector 2'
COLS = 200


def make_map(seed=None):

    cols = COLS

    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # This will return a line of '.' (dead cells), use 'o' to mark cells alive
    # Use [0] to remove the (empty) outer dimension and just get the row of interest
    team1_pattern = get_grid_empty(1, cols, flat=False)[0]
    team2_pattern = get_grid_empty(1, cols, flat=False)[0]
    patterns = [team1_pattern, team2_pattern]


    # ---------
    # Starfield
    if name == 'starfield':

        # Parameters:
        min_stars = 3
        max_stars = 9
        nstars = random.randint(min_stars, max_stars)

        for color in range(2):
            for star in range(nstars):
                randloc = random.randint(0, cols-1)
                while (patterns[0][randloc]=='o' or patterns[1][randloc]=='o'):
                    randloc = random.randint(0, cols-1)
                patterns[color][randloc] = 'o'


    # ------
    # Vector
    elif name.startswith('vector'):

        # Parameters:
        nparts = 2
        alive_density = 0.20

        half = nparts//2
        alive_cells_each_color = (alive_density/2)*cols
        alive_cells_each_partition = round(alive_cells_each_color/half)
        partwidth = round(cols/nparts)
        colors = [0, 1]
        colorparts = [0,]*half + [1,]*half
        random.shuffle(colorparts)

        for i, part in enumerate(colorparts):
            color = part
            added = 0
            for j in range(alive_cells_each_partition):
                # Adjust for partition boundaries
                randloc = random.randint(i*partwidth, min((i+1)*partwidth - 1, cols - 1))
                while (patterns[0][randloc]=='o' or patterns[1][randloc]=='o'):
                    randloc = random.randint(i*partwidth, min((i+1)*partwidth - 1, cols - 1))
                patterns[color][randloc] = 'o'


    # Wrap in [] to re-insert the (empty) outer dimension
    s1 = pattern2url([patterns[0]])
    s2 = pattern2url([patterns[1]])

    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


if __name__ == "__main__":
    make_map()
