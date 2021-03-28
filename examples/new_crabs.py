from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.utils import pattern2url
from gollyx_maps.geom import hflip_pattern, vflip_pattern
import random


ROWS = 200
COLS = 240


def make_map(seed=None):
    """
    Generate a two-color map with multiple patterns for each team.
    """
    rows = ROWS
    cols = COLS
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    # By default, crabs go up and to the left
    
    mindim = min(rows, cols)
    if mindim < 150:
        poss_ncrabs = [1]
    else:
        poss_ncrabs = [2, 3]

    ncrabs = random.choice(poss_ncrabs)

    # corners for quadrants 1 2 3 4
    quadrants = [
        (1, (0, cols // 2)),
        (2, (0, 0)),
        (3, (rows // 2, 0)),
        (4, (rows // 2, cols // 2)),
    ]
    do_hflip = [False, True, True,  False]
    do_vflip = [True, True,  False, False]
    parity = [1, -1, 1, -1]

    crabs = []

    for quadrant, (cornery, cornerx) in quadrants:
        k = quadrant - 1

        nslices = ncrabs + 1

        quadrant_crabs = []
        for a in range(1, nslices):
            for b in range(1, nslices):
                this_parity = parity[k]
                if this_parity > 0:
                    parity_check = (a == b)
                elif this_parity < 0:
                    parity_check = (a == (nslices-b))

                if parity_check:
                    y = cornery + a * ((rows // 2) // nslices)
                    x = cornerx + b * ((cols // 2) // nslices)

                    jitter = random.randint(-8, 8)

                    quadrant_crabs.append(
                        get_grid_pattern(
                            "crabstretcher",
                            rows,
                            cols,
                            xoffset=x + jitter,
                            yoffset=y + jitter,
                            hflip=do_hflip[k],
                            vflip=do_vflip[k],
                        )
                    )

        crabs.append(pattern_union(quadrant_crabs))

    # Use one quadrant to assemble the other quadrants
    random.shuffle(crabs)
    team1_pattern = pattern_union([crabs[0], crabs[1]])
    team2_pattern = pattern_union([crabs[2], crabs[3]])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=4"
    print(url)


if __name__ == "__main__":
    make_map()
