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
    Generates an expansive, non-looping "railroad track" of stars by
    adding directional momentum to a scaled, segment-based, self-avoiding
    path generation algorithm on a conceptual tile grid.
    """
    if seed is not None:
        random.seed(seed)

    tile_width = 3
    tile_height = 3

    # 1. Define the tile grid dimensions
    grid_tile_rows = rows // tile_height
    grid_tile_cols = cols // tile_width

    # 2. Choose half and define tile boundaries
    use_left_half = random.choice([True, False])
    half_tile_cols = grid_tile_cols // 2
    if use_left_half:
        x_tile_min, x_tile_max = 0, half_tile_cols
    else:
        x_tile_min, x_tile_max = half_tile_cols, grid_tile_cols

    y_tile_min, y_tile_max = 0, grid_tile_rows

    # 3. Path Generation
    path_of_tiles = set()

    # Start point
    if x_tile_min >= x_tile_max or y_tile_min >= y_tile_max:
        return "23", "3", "{}", "[]", "[]", "[]"

    current_tile_x = random.randint(x_tile_min, x_tile_max - 1)
    current_tile_y = random.randint(y_tile_min, y_tile_max - 1)
    path_of_tiles.add((current_tile_x, current_tile_y))

    # Calculate average segment length
    num_h_segments = (turns + 1) // 2
    num_v_segments = (turns + 1) - num_h_segments
    avg_len_x = (x_tile_max - x_tile_min) / (num_h_segments + 1) if num_h_segments > 0 else 0
    avg_len_y = (y_tile_max - y_tile_min) / (num_v_segments + 1) if num_v_segments > 0 else 0

    # Initialize path generation state
    last_move_was_horizontal = random.choice([True, False])
    last_h_dir = random.choice([-1, 1])
    last_v_dir = random.choice([-1, 1])

    for _ in range(turns + 1):
        if last_move_was_horizontal:  # Make a vertical segment
            last_move_was_horizontal = False
            length = max(1, int(random.uniform(0.5, 1.5) * avg_len_y))
            
            # Use momentum for direction
            direction = last_v_dir
            if random.random() < 0.2: # Chance to reverse general direction
                last_v_dir *= -1

            actual_length = 0
            for step in range(1, length + 1):
                next_y = current_tile_y + direction * step
                if not (y_tile_min <= next_y < y_tile_max and (current_tile_x, next_y) not in path_of_tiles):
                    break
                actual_length = step
            
            for step in range(1, actual_length + 1):
                path_of_tiles.add((current_tile_x, current_tile_y + direction * step))
            current_tile_y += direction * actual_length

        else:  # Make a horizontal segment
            last_move_was_horizontal = True
            length = max(1, int(random.uniform(0.5, 1.5) * avg_len_x))

            # Use momentum for direction
            direction = last_h_dir
            if random.random() < 0.2: # Chance to reverse general direction
                last_h_dir *= -1

            actual_length = 0
            for step in range(1, length + 1):
                next_x = current_tile_x + direction * step
                if not (x_tile_min <= next_x < x_tile_max and (next_x, current_tile_y) not in path_of_tiles):
                    break
                actual_length = step

            for step in range(1, actual_length + 1):
                path_of_tiles.add((current_tile_x + direction * step, current_tile_y))
            current_tile_x += direction * actual_length
    
    # 4. Translate tile path to cell coordinates and stamp stars
    points = set()
    star_shape = {(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)}

    def stamp_star(center_x, center_y):
        for dx, dy in star_shape:
            points.add((center_x + dx, center_y + dy))

    for tile_x, tile_y in path_of_tiles:
        center_x = tile_x * tile_width + (tile_width // 2)
        center_y = tile_y * tile_height + (tile_height // 2)
        stamp_star(center_x, center_y)

    # 5. Serialize to URL format
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
