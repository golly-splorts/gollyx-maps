from golly_maps.patterns import get_pattern_livecount, get_grid_pattern


def count_example():
    rows = 100
    cols = 120
    pattern1 = get_grid_pattern('78p70', rows, cols, xoffset=centerx, yoffset=centery)
    print(get_pattern_livecount(pattern1))


if __name__=="__main__":
    count_example()
