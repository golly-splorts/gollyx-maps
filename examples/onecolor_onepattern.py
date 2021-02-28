from golly_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from golly_maps.utils import pattern2url


ROWS = 100
COLS = 120


def onepattern_onecolor(seed=None):
    """
    Generate a one-color map containing a pattern at the center.
    """
    rows = ROWS
    cols = COLS
    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    centerx = cols//2
    centery = rows//2

    #pattern1 = get_grid_pattern('heavyweightspaceship', rows, cols, xoffset=centerx, yoffset=centery)
    #pattern1 = get_grid_pattern('spaceshipgrower', rows, cols, xoffset=centerx, yoffset=centery)
    #pattern1 = get_grid_pattern('switchengine', rows, cols, xoffset=centerx, yoffset=centery)
    #pattern1 = get_grid_pattern('unidimensionalsixgliders', rows, cols, xoffset=centerx, yoffset=centery)
    #pattern1 = get_grid_pattern('unidimensionalinfinitegrowth', rows, cols, xoffset=centerx, yoffset=centery)
    #pattern1 = get_grid_pattern('ring64', rows, cols, xoffset=centerx, yoffset=centery)
    #pattern1 = get_grid_pattern('cthulhu', rows, cols, xoffset=centerx, yoffset=centery)
    #pattern1 = get_grid_pattern('78p70', rows, cols, xoffset=centerx, yoffset=centery)
    #pattern1 = get_grid_pattern('justyna', rows, cols, xoffset=centerx, yoffset=centery)
    #pattern1 = get_grid_pattern('crabstretcher', rows, cols, xoffset=centerx, yoffset=centery)
    pattern1 = get_grid_pattern('wickstretcher', rows, cols, xoffset=centerx, yoffset=centery)

    s1 = pattern2url(pattern1)
    url = f"?s1={s1}"
    print(url)


if __name__=="__main__":
    onepattern_onecolor()
