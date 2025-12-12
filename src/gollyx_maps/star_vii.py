import json
import os
import random
from .geom import hflip_pattern, vflip_pattern
from .utils import pattern2url
from .patterns import get_grid_empty, pattern_union, get_pattern, get_grid_pattern
from .utils import pattern2url, retry_on_failure, pattern2url_char, pattern2url_chars
from .star import (
    random_2color,
    flyingv1,
    flyingv2,
    stlouis,
    newyork,
    chicago,
    combs,
    precipitation,
    evaporation,
    denaturation,
    gastank,
    rustytank,
    dinnerplate,
    dessertplate,
    squarestar,
    kitchensink,
    ricepudding,
    fishsoup,
)


def get_star_vii_pattern_function_map():
    return {
        ####################################
        ######### STAR CUP CLASSICS ########
        "random": random_2color,
        "flyingv1": flyingv1,
        "flyingv2": flyingv2,
        "stlouis": stlouis,
        "newyork": newyork,
        "chicago": chicago,
        "combs": combs,
        # containment lines
        "precipitation": precipitation,
        "evaporation": evaporation,
        "denaturation": denaturation,
        # containment rectangles
        "gastank": gastank,
        "rustytank": rustytank,
        "dinnerplate": dinnerplate,
        "dessertplate": dessertplate,
        # stamps
        "squarestar": squarestar,
        "kitchensink": kitchensink,
        "ricepudding": ricepudding,
        "fishsoup": fishsoup,
        #####################################
        ###### STAR VIII CUP NEW SHIT #######
        "choochoo": choochoo,
    }


def choochoo(rows, cols, seed=None):
    """
    Generates a map with a random walk pattern, creating "railroad tracks".
    """
    if seed is not None:
        random.seed(seed)

    points1 = set()

    # 1. Generate pattern with a random walk
    # Start the walk
    x = random.randint(0, cols - 1)
    y = random.randint(0, rows - 1)
    points1.add((x, y))

    # Number of steps for the walk
    num_steps = (rows + cols) * 2

    for _ in range(num_steps):
        # Move in a random direction
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

        nx, ny = x + dx, y + dy

        # Check boundaries for the grid
        if 0 <= nx < cols and 0 <= ny < rows:
            x, y = nx, ny
            points1.add((x, y))
        # if it hits a wall, it just stays put and tries a new direction next iteration.

    # --- String Serialization (GollyX Format) ---

    pattern1 = []

    for y_coord in range(rows):
        row1 = []
        for x_coord in range(cols):
            if (x_coord, y_coord) in points1:
                row1.append("o")
            else:
                row1.append(".")
        pattern1.append("".join(row1))

    # Convert to URL strings using the library's utility
    s1, b1, c1 = pattern2url_chars(pattern1)

    # Per user request, we do not generate a second pattern
    s2, b2, c2 = "[]", "[]", "[]"

    return s1, b1, c1, s2, b2, c2

