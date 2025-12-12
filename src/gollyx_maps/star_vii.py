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


def choochoo(rows, cols, seed=None, turns=9):
    """
    Generates a "railroad track" of stars on one half of the grid,
    ensuring stars are touching arm-to-arm with no overlaps.
    The number of turns/bends in the track is configurable.
    """
    if seed is not None:
        random.seed(seed)

    points = set()
    star_shape = {(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)}
    margin = 2
    star_step = 3

    # 1. Choose half and define boundaries
    use_left_half = random.choice([True, False])
    half_width = cols // 2
    if use_left_half:
        x_min_boundary, x_max_boundary = 0, half_width
    else:
        x_min_boundary, x_max_boundary = half_width, cols
    y_min_boundary, y_max_boundary = 0, rows

    if (x_max_boundary - x_min_boundary) < margin * 2 or (
        y_max_boundary - y_min_boundary
    ) < margin * 2:
        return "23", "3", "{}", "[]", "[]", "[]"

    def can_stamp(x, y):
        for dx, dy in star_shape:
            if not (
                x_min_boundary <= x + dx < x_max_boundary
                and y_min_boundary <= y + dy < y_max_boundary
            ):
                return False
            if (x + dx, y + dy) in points:
                return False
        return True

    def stamp_star(x, y):
        for dx, dy in star_shape:
            points.add((x + dx, y + dy))

    # 2. Find start point
    x, y = -1, -1
    for _ in range(10):
        start_x = random.randint(x_min_boundary + margin, x_max_boundary - margin - 1)
        start_y = random.randint(y_min_boundary + margin, y_max_boundary - margin - 1)
        if can_stamp(start_x, start_y):
            x, y = start_x, start_y
            stamp_star(x, y)
            break

    if x == -1:
        return "23", "3", "{}", "[]", "[]", "[]"

    # 3. Generate path
    min_len, max_len = 5, 15
    last_move_was_horizontal = random.choice([True, False])
    center_x_of_half = (x_min_boundary + x_max_boundary) / 2
    center_y = (y_min_boundary + y_max_boundary) / 2

    for _ in range(turns + 1):  # +1 to generate 'turns' number of bends
        length = random.randint(min_len, max_len)

        if last_move_was_horizontal:
            last_move_was_horizontal = False
            # Smart direction for vertical movement
            direction = 1 if y < center_y else -1
            if random.random() < 0.2:  # 20% chance to move toward center
                direction *= -1

            last_successful_i = 0
            for i in range(1, length):
                ny = y + direction * i * star_step
                if can_stamp(x, ny):
                    stamp_star(x, ny)
                    last_successful_i = i
                else:
                    break
            y += direction * last_successful_i * star_step
        else:
            last_move_was_horizontal = True
            # Smart direction for horizontal movement
            direction = 1 if x < center_x_of_half else -1
            if random.random() < 0.2:  # 20% chance to move toward center
                direction *= -1

            last_successful_i = 0
            for i in range(1, length):
                nx = x + direction * i * star_step
                if can_stamp(nx, y):
                    stamp_star(nx, y)
                    last_successful_i = i
                else:
                    break
            x += direction * last_successful_i * star_step

    # --- String Serialization ---
    pattern_rows = []
    for y_coord in range(rows):
        row = []
        for x_coord in range(cols):
            if (x_coord, y_coord) in points:
                row.append("o")
            else:
                row.append(".")
        pattern_rows.append("".join(row))

    s1, b1, c1 = pattern2url_chars(pattern_rows)
    s2, b2, c2 = "[]", "[]", "[]"

    return s1, b1, c1, s2, b2, c2

