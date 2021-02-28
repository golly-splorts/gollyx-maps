from golly_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from golly_maps.utils import pattern2url
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

    # Place two wickstretchers at edge of map, facing each other
    # Small amount of vertical jitter relative to each other,
    # large amount of (coordinated) jitter

    (wick_h, wick_w) = get_pattern_size("wickstretcher")

    # Give ourselves a small margin on the edge of the map
    # (give the wickstretchers as much space as possible)
    margin = random.randint(2,5)
    xbuff = wick_w // 2 + margin

    # Use this to jitter the vertical placement of both wickstretchers
    y_rel_jitter = wick_h // 2 - 2

    # Determine absolute y offset for both wickstretchers
    ybuff = y_rel_jitter
    y_abs_jitter = rows // 3 - 2*wick_h
    y_abs_offset = random.randint(-y_abs_jitter, y_abs_jitter)

    team1_pattern = []
    team2_pattern = []

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

    roll = 0.30  # random.random()
    print(abs(y_abs_offset), "versus", wick_h)
    if roll < 0.15 and abs(y_abs_offset > wick_h):

        # -----
        # Double wickstretchers
        # Team 1 second wickstretcher
        team1_wickstretcher2 = get_grid_pattern(
            "wickstretcher",
            rows,
            cols,
            xoffset=xbuff,
            yoffset=rows // 2 - y_abs_offset - team1_yjitter_val,
        )

        # Team 2 second wickstretcher
        team2_wickstretcher2 = get_grid_pattern(
            "wickstretcher",
            rows,
            cols,
            xoffset=cols - xbuff,
            yoffset=rows // 2 - y_abs_offset - team2_yjitter_val,
            hflip=True,
            vflip=bool(random.getrandbits(1)),
        )
        team1_pattern = pattern_union([team1_wickstretcher, team1_wickstretcher2])
        team2_pattern = pattern_union([team2_wickstretcher, team2_wickstretcher2])

    elif roll < 0.40:
        # -----
        # Crabstretchers in the corners
        # Note that by default the crabstretcher goes up and to the left
        crab_margin = 15

        wickstretcher_bottom = y_abs_offset > 0
        if wickstretcher_bottom:
            # Crabs are at the top
            # Make crabs go down
            vflip_crabs = True
            # Down and still going to the left
            hflip_team1_crabs = False
            team1_xoffset = cols - crab_margin
            team1_yoffset = crab_margin
            team2_xoffset = crab_margin
            team2_yoffset = crab_margin
        else:
            # Crabs are at bottom
            # They should keep going up
            vflip_crabs = False
            team1_xoffset = cols - crab_margin
            team1_yoffset = rows - crab_margin
            team2_xoffset = crab_margin
            team2_yoffset = rows - crab_margin
        # Crabs are always going to the left, so team 1 never hflips, team 2 always hflips
        team1_crab = get_grid_pattern(
            "crabstretcher",
            rows,
            cols,
            xoffset=team1_xoffset,
            yoffset=team1_yoffset,
            vflip=vflip_crabs,
        )
        team1_pattern = pattern_union([team1_wickstretcher, team1_crab])

        team2_crab = get_grid_pattern(
            "crabstretcher",
            rows,
            cols,
            xoffset=team2_xoffset,
            yoffset=team2_yoffset,
            vflip=vflip_crabs,
            hflip=True,
        )
        team2_pattern = pattern_union([team2_wickstretcher, team2_crab])

    else:
        # -----
        # Spaceship escorts
        sschoices = [
            "lightweightspaceship",
            "middleweightspaceship",
            "heavyweightspaceship",
            "x66",
        ]
        top_ss = "lightweightspaceship" # random.choice(sschoices)
        bot_ss = "x66" # random.choice(sschoices)

        top_ssh, top_ssw = get_pattern_size(top_ss)
        top_ssjitter = top_ssh//2
        top_spaceship_y = (
            rows // 2
            + y_abs_offset
            - wick_h
            - top_ssh
            + random.randint(-top_ssjitter, top_ssjitter)
        )

        bot_ssh, bot_ssw = get_pattern_size(bot_ss)
        bot_ssjitter = bot_ssh//2
        bot_spaceship_y = (
            rows // 2
            + y_abs_offset
            + wick_h
            + bot_ssh
            + random.randint(-bot_ssjitter, bot_ssjitter)
        )

        xbuff_ss = max(top_ssw, bot_ssw)

        team1_top_ss = get_grid_pattern(
            top_ss,
            rows,
            cols,
            xoffset=xbuff_ss + random.randint(0, top_ssw),
            yoffset=top_spaceship_y + random.randint(-5, 0),
            hflip=True,
        )
        team1_bot_ss = get_grid_pattern(
            bot_ss,
            rows,
            cols,
            xoffset=xbuff_ss + random.randint(0, bot_ssw),
            yoffset=bot_spaceship_y + random.randint(-5, 0),
            hflip=True,
        )
        team1_pattern = pattern_union([team1_wickstretcher, team1_bot_ss, team1_top_ss])
        #team1_pattern = pattern_union([team1_wickstretcher, team1_top_ss])

        team2_top_ss = get_grid_pattern(
            top_ss,
            rows,
            cols,
            xoffset=cols - xbuff_ss - random.randint(0, top_ssw),
            yoffset=top_spaceship_y + random.randint(-5, 0),
        )
        team2_bot_ss = get_grid_pattern(
            bot_ss,
            rows,
            cols,
            xoffset=cols - xbuff_ss - random.randint(0, bot_ssw),
            yoffset=bot_spaceship_y + random.randint(-5, 0),
        )
        team2_pattern = pattern_union([team2_wickstretcher, team2_bot_ss, team2_top_ss])
        #team2_pattern = pattern_union([team2_wickstretcher, team2_top_ss])

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}&rows={rows}&cols={cols}&cellSize=5"
    print(url)


if __name__ == "__main__":
    make_map()
