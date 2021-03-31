import itertools
from gollyx_maps.utils import pattern2url
from gollyx_maps.patterns import segment_pattern, get_grid_empty
import random


rows = 100
cols = 120


def make_map(seed=None):

    if seed is not None:
        random.seed(seed)

    thickness = random.randint(2, 4)

    #intersectx1 = cols//3 + random.randint(-jitterx, jitterx)
    #intersectx2 = 2*cols//3 + random.randint(-jitterx, jitterx)

    #intersecty1 = rows//3 + random.randint(-jittery, jittery)
    #intersecty2 = 2*rows//3 + random.randint(-jittery, jittery)

    #intersectxs = [intersectx1, intersectx2]
    #intersectys = [intersecty1, intersecty2]

    nsegments = random.choice([2, 4])

    jitterx = 0*(4//nsegments)
    jittery = 0*(4//nsegments)

    intersectxs = [(i+1)*cols//(nsegments+1) + random.randint(-jitterx, jitterx) for i in range(nsegments)]
    intersectys = [(j+1)*rows//(nsegments+1) + random.randint(-jittery, jittery) for j in range(nsegments)]

    random.shuffle(intersectxs)
    random.shuffle(intersectys)

    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    def _get_bounds(z, dim):
        zstart = z - dim//2
        zend = z + (dim - dim//2)
        return zstart, zend

    x1s = intersectxs[:len(intersectxs)//2]
    x2s = intersectxs[len(intersectxs)//2:]
    print(x1s)
    print(x2s)
    for iy in range(0, rows):
        
        for x1 in x1s:
            for ix in range(*_get_bounds(x1, thickness)):
                team1_pattern[iy][ix] = 'o'

        for x2 in x2s:
            for ix in range(*_get_bounds(x2, thickness)):
                team2_pattern[iy][ix] = 'o'

    y1s = intersectys[:len(intersectys)//2]
    y2s = intersectys[len(intersectys)//2:]
    for ix in range(0, cols):

        for y1 in y1s:
            for iy in range(*_get_bounds(y1, thickness)):
                team1_pattern[iy][ix] = 'o'

        for y2 in y2s:
            for iy in range(*_get_bounds(y2, thickness)):
                team2_pattern[iy][ix] = 'o'

    # Punch out squares at the intersections
    for (x, y) in itertools.product(intersectxs, intersectys):
        for ix in range(*_get_bounds(x, thickness)):
            for iy in range(*_get_bounds(y, thickness)):
                team1_pattern[iy][ix] = '.'
                team2_pattern[iy][ix] = '.'

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


if __name__ == "__main__":
    s1, s2 = make_map()
    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}"
    print(url)

