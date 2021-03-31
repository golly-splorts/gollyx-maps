import itertools
from gollyx_maps.utils import pattern2url
from gollyx_maps.patterns import segment_pattern, get_grid_empty
import random


rows = 100
cols = 120


def make_map(seed=None):

    if seed is not None:
        random.seed(seed)

    nsegments = 2
    thickness = random.randint(1, 3)

    team1_pattern = get_grid_empty(rows, cols, flat=False)
    team2_pattern = get_grid_empty(rows, cols, flat=False)

    jitterx = 4
    jittery = 10
    intersectys = [(j+1)*rows//(nsegments+1) + random.randint(-jittery, jittery) for j in range(nsegments)]
    random.shuffle(intersectys)

    def _get_bounds(z, dim):
        zstart = z - dim//2
        zend = z + (dim - dim//2)
        return zstart, zend

    # Add the string
    y1s = intersectys[:len(intersectys)//2]
    y2s = intersectys[len(intersectys)//2:]
    for ix in range(0, cols):

        for y1 in y1s:
            for iy in range(*_get_bounds(y1, thickness)):
                team1_pattern[iy][ix] = 'o'

        for y2 in y2s:
            for iy in range(*_get_bounds(y2, thickness)):
                team2_pattern[iy][ix] = 'o'

    # Add some lights to the string

    for y1 in y1s:
        b = _get_bounds(y1, thickness)
        maxy = max(b)
        miny = min(b)
        ylightstop = miny - random.randint(2, 3)
        ylightsbot = maxy + random.randint(2, 3)
        ix = random.randint(4, 12)
        while ix < cols:
            if random.random() < 0.50:
                team1_pattern[ylightsbot][ix] = 'o'
                team1_pattern[ylightsbot][ix+1] = 'o'
                team1_pattern[ylightsbot+1][ix] = 'o'
                team1_pattern[ylightsbot+1][ix+1] = 'o'
            else:
                team1_pattern[ylightstop][ix] = 'o'
                team1_pattern[ylightstop][ix+1] = 'o'
                team1_pattern[ylightstop-1][ix] = 'o'
                team1_pattern[ylightstop-1][ix+1] = 'o'
            ix += random.randint(10, 12) + random.randint(-jitterx, jitterx)

    for y2 in y2s:
        b = _get_bounds(y2, thickness)
        maxy = max(b)
        miny = min(b)
        ylightstop = miny - random.randint(2, 3)
        ylightsbot = maxy + random.randint(2, 3)
        ix = random.randint(4, 12)
        while ix < cols:
            if random.random() < 0.50:
                team2_pattern[ylightsbot][ix] = 'o'
                team2_pattern[ylightsbot][ix+1] = 'o'
                team2_pattern[ylightsbot+1][ix] = 'o'
                team2_pattern[ylightsbot+1][ix+1] = 'o'
            else:
                team2_pattern[ylightstop][ix] = 'o'
                team2_pattern[ylightstop][ix+1] = 'o'
                team2_pattern[ylightstop-1][ix] = 'o'
                team2_pattern[ylightstop-1][ix+1] = 'o'
            ix += random.randint(10, 12) + random.randint(-jitterx, jitterx)

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


if __name__ == "__main__":
    s1, s2 = make_map()
    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}"
    print(url)

