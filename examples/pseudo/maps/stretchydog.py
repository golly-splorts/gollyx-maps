from gollyx_maps.utils import pattern2url
from gollyx_maps.patterns import methuselah_quadrants_pattern
import random


rows = 100
cols = 120


def make_map(seed=None):

    if seed is not None:
        random.seed(seed)

    all_meths = [
        "pseudo_angel_heptomino",
        "pseudo_boomerang_heptomino",
        "pseudo_brass_knuckles_nonomino",
        "pseudo_broken_l_heptomino",
        "pseudo_capacitor_octomino",
        "pseudo_facade_heptomino",
        "pseudo_flower_pentomino",
        "pseudo_kite_heptomino",
        "pseudo_l_pentomino",
        "pseudo_lockpick_heptomino",
        "pseudo_mcnasty_nonomino",
        "pseudo_octomino_oscillator",
        "pseudo_raygun_heptomino",
        "pseudo_reverse_f_heptomino",
        "pseudo_sticky_heptomino",
        "pseudo_stretchydog_octomino",
        "pseudo_swandive_octomino",
        "pseudo_t_heptomino",
    ]


    mc = [3]

    team1_pattern, team2_pattern = methuselah_quadrants_pattern(
        rows, cols, seed, methuselah_counts=mc, methuselah_names=["pseudo_stretchydog_octomino"]
    )

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)
    return pattern1_url, pattern2_url


if __name__ == "__main__":
    s1, s2 = make_map()
    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}"
    print(url)

