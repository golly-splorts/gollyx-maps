from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.geom import hflip_pattern, vflip_pattern
from gollyx_maps.utils import pattern2url
from gollyx_maps.error import GollyXPatternsError
import random


ROWS = 150
COLS = 240
SEED = None


def wick1():
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    # Using wickstretcher pattern, mainly...
    wick_h, wick_w = get_pattern_size("wickstretcher")

    team1_pattern = None
    team2_pattern = None

    yjitter = lambda: random.randint(-int((1/7)*rows), int((1/7)*rows))

    # ----------------------------
    # Team 1 double wickstretchers

    for c in [1,2]:
        # Place at y = 1/3*rows and y = 2/3*rows
        team1_wickstretcher = get_grid_pattern(
            "wickstretcher",
            rows,
            cols,
            xoffset=cols//3,
            yoffset=c * rows // 3 + yjitter()
        )
        if team1_pattern is None:
            team1_pattern = team1_wickstretcher
        else:
            team1_pattern = pattern_union([team1_pattern, team1_wickstretcher])

        team2_wickstretcher = get_grid_pattern(
            "wickstretcher",
            rows,
            cols,
            xoffset=2*cols//3,
            yoffset=c * rows // 3 + yjitter(),
            hflip=True
        )
        if team2_pattern is None:
            team2_pattern = team2_wickstretcher
        else:
            team2_pattern = pattern_union([team2_pattern, team2_wickstretcher])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


def wick3():
    rows = ROWS
    cols = COLS
    if SEED is not None:
        random.seed(SEED)

    (wick_h, wick_w) = get_pattern_size("wickstretcher")

    (crab_h, crab_w) = get_pattern_size("crabstretcher")

    # Give ourselves a small margin on the edge of the map
    # (give the wickstretchers as much space as possible)
    margin = random.randint(2, 5)
    xbuff = wick_w // 2 + margin

    # Use this to jitter the vertical placement of both wickstretchers
    y_rel_jitter = wick_h // 2 - 2

    # Determine absolute y offset for both wickstretchers
    ybuff = y_rel_jitter
    y_abs_jitter = rows // 3 - 2 * wick_h
    y_abs_offset = random.randint(-y_abs_jitter, y_abs_jitter)

    # ---------------
    # Wickstretchers

    # Team 1 wickstretcher
    team1_yjitter_val = random.randint(-y_rel_jitter, y_rel_jitter)
    team1_wickstretcher = get_grid_pattern(
        "wickstretcher",
        rows,
        cols,
        xoffset=xbuff,
        yoffset=rows // 2 + y_abs_offset + team1_yjitter_val,
    )

    # Team 2 wickstretcher
    team2_yjitter_val = random.randint(-y_rel_jitter, y_rel_jitter)
    team2_wickstretcher = get_grid_pattern(
        "wickstretcher",
        rows,
        cols,
        xoffset=cols - xbuff,
        yoffset=rows // 2 + y_abs_offset + team2_yjitter_val,
        hflip=True,
        vflip=bool(random.getrandbits(1)),
    )

    # -----
    # Crabstretchers in the corners
    # Note that by default the crabstretcher goes up and to the left
    crab_margin = 20

    wickstretcher_bottom = y_abs_offset > 0
    if wickstretcher_bottom:
        # Crabs are at the top
        # Make crabs go down
        vflip_crabs = True
        # Down and still going to the left
        hflip_team1_crabs = False
        team1_xoffset = cols - 2*crab_w
        team1_yoffset = 2*crab_h
        team2_xoffset = 2*crab_w
        team2_yoffset = 2*crab_h
    else:
        # Crabs are at bottom
        # They should keep going up
        vflip_crabs = False
        team1_xoffset = cols - 2*crab_w
        team1_yoffset = rows - 2*crab_h
        team2_xoffset = 2*crab_w
        team2_yoffset = rows - 2*crab_h

    crab_jitter_max = 12
    crab1jitter = random.randint(0, crab_jitter_max)
    crab2jitter = random.randint(0, crab_jitter_max)

    team1_crab = get_grid_pattern(
        "crabstretcher",
        rows,
        cols,
        xoffset=team1_xoffset - crab1jitter,
        yoffset=team1_yoffset + crab1jitter,
        vflip=vflip_crabs,
    )

    team1_pattern = pattern_union([team1_wickstretcher, team1_crab])

    team2_crab = get_grid_pattern(
        "crabstretcher",
        rows,
        cols,
        xoffset=team2_xoffset + crab2jitter,
        yoffset=team2_yoffset - crab2jitter,
        vflip=vflip_crabs,
        hflip=True,
    )

    team2_pattern = pattern_union([team2_wickstretcher, team2_crab])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"
    print(url)


if __name__=="__main__":
    #wick1()
    wick3()
