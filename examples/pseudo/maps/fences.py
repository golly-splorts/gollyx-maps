from gollyx_maps.utils import pattern2url
from gollyx_maps.patterns import (
    pattern_union,
    methuselah_quadrants_pattern,
    segment_pattern,
)
import random


rows = 100
cols = 120


def make_map(seed=None):

    if seed is not None:
        random.seed(seed)


    # Make the wabbits
    # -----------------
    mc = [4]

    team1_wabbits, team2_wabbits = methuselah_quadrants_pattern(
        rows, cols, seed, methuselah_counts=mc, methuselah_names=["pseudo_lockpick_heptomino"]
    )

    # Make the fence
    # -----------------

    # Always 1 horizontal segment, optional vertical segment
    nhseg = 1
    if random.random() < 0.33:
        nvseg = 0
    else:
        nvseg = 1

    # Set amount of jitter for placement of segments
    jitterx = 8
    jittery = 8

    # Color mode should be broken
    if random.random() < 0.33:
        colormode = "classicbroken"
    else:
        colormode = "randombroken"

    team1_fence, team2_fence = segment_pattern(
        rows,
        cols,
        seed,
        colormode=colormode,
        nhseg=nhseg,
        nvseg=nvseg,
        jitterx=jitterx,
        jittery=jittery,
    )

    team1_pattern = pattern_union([team1_wabbits, team1_fence])
    team2_pattern = pattern_union([team2_wabbits, team2_fence])

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url



if __name__ == "__main__":
    s1, s2 = make_map()
    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}"
    print(url)

