from patterns import get_grid_pattern, pattern_union
from maps import random_twocolor


def print_acorns():
    a1 = get_grid_pattern('acorn', 80, 80, xoffset=10, yoffset=20)
    a2 = get_grid_pattern('acorn', 80, 80, xoffset=30, yoffset=20)
    print("\n".join(pattern_union([a1, a2])))


def print_random_map():
    a1, a2 = random_twocolor(60,60)
    print("listlife for color 1:")
    print(a1)
    print("listlife for color 2:")
    print(a2)


if __name__=="__main__":
    print_random_map()
