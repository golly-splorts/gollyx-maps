from gollyx_maps.utils import pattern2url
import random


rows = 100
cols = 120


def make_map(seed=None):

    if seed is not None:
        random.seed(seed)
    ncells = rows * cols
    nlivecells = ncells * 0.15
    points = set()
    centerx = cols//2
    centery = rows//2
    while len(points) < nlivecells:
        randx = int(random.gauss(centerx, centerx//2))
        randy = int(random.gauss(centery, centery//2))
        if (randx > 0 and randx < cols) and (randy > 0 and randy < rows):
            points.add((randx, randy))

    points = list(points)
    points1 = set(points[: len(points) // 2])  # noqa
    points2 = set(points[len(points) // 2 :])  # noqa
    pattern1 = []
    pattern2 = []
    for y in range(rows):
        row1 = []
        row2 = []

        # team 1 row
        for x in range(cols):
            if (x, y) in points1:
                row1.append("o")
            else:
                row1.append(".")
        row1str = "".join(row1)
        pattern1.append(row1str)

        # team 2 row
        for x in range(cols):
            if (x, y) in points2:
                row2.append("o")
            else:
                row2.append(".")
        row2str = "".join(row2)
        pattern2.append(row2str)

    pattern1_url = pattern2url(pattern1)
    pattern2_url = pattern2url(pattern2)

    return pattern1_url, pattern2_url



if __name__ == "__main__":
    s1, s2 = make_map()
    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}"
    print(url)
