from gollyx_maps.utils import pattern2url
from gollyx_maps.geom import hflip_pattern, vflip_pattern
import random


rows = 100
cols = 120

SMOL = 1e-12


def make_map(seed=None):

    if seed is not None:
        random.seed(seed)

    ncells = rows * cols
    nlivecells = ncells * 0.10

    centerx = cols // 2
    centery = rows // 2

    team1_points = set()
    team2_points = set()

    while (
        len(team1_points) < nlivecells // 2
        and
        len(team2_points) < nlivecells // 2
    ):
        randx = int(random.gauss(centerx, centerx//2))
        randy = int(random.gauss(centery, centery//2))

        g = 2.5

        slope = (randy - centery)/(randx - centerx + SMOL)

        if slope > 0:

            if slope < 1/g:
                team2_points.add((randx, randy))
            elif slope < 1:
                team1_points.add((randx, randy))
            elif slope < g:
                team2_points.add((randx, randy))
            else:
                team1_points.add((randx, randy))

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
        team2_row_str = "".join(team2_row)
        team1_pattern.append(team1_row_str)
        team2_pattern.append(team2_row_str)

    if bool(random.getrandbits(1)):
        # swap
        temp = team1_pattern
        team1_pattern = team2_pattern
        team2_pattern = temp

    if bool(random.getrandbits(1)):
        team1_pattern = vflip_pattern(team1_pattern)
        team2_pattern = vflip_pattern(team2_pattern)

    s1 = pattern2url(hflip_pattern(team1_pattern))
    s2 = pattern2url(team2_pattern)

    return (s1, s2)


if __name__ == "__main__":
    s1, s2 = make_map()
    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


