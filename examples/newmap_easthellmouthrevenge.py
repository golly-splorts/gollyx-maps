from golly_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from golly_maps.utils import pattern2url
import random


ROWS = 100
COLS = 120


def make_map(seed=None):
    """
    Generate a two-color map with multiple patterns for each team.
    """
    rows = ROWS
    cols = COLS
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    ncells = rows*cols
    nlivecells = int(ncells*0.12)

    nhpartitions = random.choice([1, 2, 4, 5])
    nvpartitions = random.choice([2, 4, 8])

    w_vpartition = cols//nvpartitions
    h_hpartition = rows//nhpartitions

    team1_points = set()
    while len(team1_points)<nlivecells//2:
        randy = random.randint(0, rows-1)
        randx = random.randint(0, cols-1)
        if (randx//w_vpartition)%2==(randy//h_hpartition)%2:
            team1_points.add((randx, randy))

    team2_points = set()
    while len(team2_points)<nlivecells//2:
        randy = random.randint(0, rows-1)
        randx = random.randint(0, cols-1)
        if (randx//w_vpartition)%2!=(randy//h_hpartition)%2:
            team2_points.add((randx, randy))

    team1_pattern = []
    team2_pattern = []
    for y in range(rows):
        team1_row = []
        team2_row = []

        for x in range(cols):
            if (x,y) in team1_points:
                team1_row.append('o')
            else:
                team1_row.append('.')

            if (x,y) in team2_points:
                team2_row.append('o')
            else:
                team2_row.append('.')

        team1_row_str = "".join(team1_row)
        team2_row_str = "".join(team2_row)
        team1_pattern.append(team1_row_str)
        team2_pattern.append(team2_row_str)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8888/simulator/index.html?s1={s1}&s2={s2}"
    #url = f"?s1={s1}"
    #url = f"?s2={s2}"
    print(url)


if __name__=="__main__":
    make_map()
