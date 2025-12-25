import json
import os
import random
import itertools
from .geom import hflip_pattern, vflip_pattern, rot_pattern, hjiggle, vjiggle, apply_random_transformation
from .utils import pattern2url_chars, points_to_url
from .patterns import get_pattern, get_grid_pattern
from .error import GollyXGeomError
from .star import get_star_pattern_function_map


def get_star_vii_pattern_function_map():
    patterns = get_star_pattern_function_map()
    new_patterns = {
        "twochoochoo": twochoochoo,
        "midnightexpress": midnightexpress,
        "spaceelevator": spaceelevator,
        "faradaycage": faradaycage,
        # "ironhorse": ironhorse,
        # "deadendterminal": deadendterminal,
        # "bando": bando,
        # "ghosttrain": ghosttrain,
    }
    return patterns | new_patterns


################################################
# TODO 1: use star.txt pattern/stamp instead

STAR_3X3_PATTERN_STR = [".o.", "ooo", ".o."]
STAR_3X3_RELATIVE_POINTS = set()
for y_idx, row in enumerate(STAR_3X3_PATTERN_STR):
    for x_idx, char in enumerate(row):
        if char == "o":
            STAR_3X3_RELATIVE_POINTS.add((x_idx, y_idx))

# Calculate width and height of the STAR_3X3 stamp
min_x_star = min(p[0] for p in STAR_3X3_RELATIVE_POINTS)
max_x_star = max(p[0] for p in STAR_3X3_RELATIVE_POINTS)
min_y_star = min(p[1] for p in STAR_3X3_RELATIVE_POINTS)
max_y_star = max(p[1] for p in STAR_3X3_RELATIVE_POINTS)
STAR_STAMP_WIDTH = max_x_star - min_x_star + 1
STAR_STAMP_HEIGHT = max_y_star - min_y_star + 1

# END TODO 1
################################################


##############################################################################################
########################## utility functions #################################################


def _flood_fill_check(
    current_path_tiles, rows_grid, cols_grid, x_min, x_max, y_min, y_max
):
    """
    Checks if adding a new segment creates a closed loop in the path.

    It works by marking the path tiles as obstacles on a grid and then
    performing a flood fill from all boundary cells. If any empty cell
    remains unvisited after the fill, it implies it's inside an enclosed
    region, meaning a loop has been formed.
    """
    # Create a grid representation
    grid = [[0 for _ in range(cols_grid)] for _ in range(rows_grid)]
    for r, c in current_path_tiles:
        if (
            x_min <= r < x_max and y_min <= c < y_max
        ):  # Ensure path tiles are within the relevant bounds
            grid[c][r] = 1  # Mark path tiles as obstacles

    # Perform flood fill from all empty boundary cells to detect enclosed regions (loops).

    visited = set()
    q = []
    start_points = set()

    # Add all empty boundary cells to start_points
    for r in range(rows_grid):
        if grid[r][0] == 0:
            start_points.add((r, 0))
        if grid[r][cols_grid - 1] == 0:
            start_points.add((r, cols_grid - 1))
    for c in range(cols_grid):
        if grid[0][c] == 0:
            start_points.add((0, c))
        if grid[rows_grid - 1][c] == 0:
            start_points.add((rows_grid - 1, c))

    for start_r, start_c in start_points:
        if (start_r, start_c) not in visited and grid[start_r][start_c] == 0:
            q.append((start_r, start_c))
            visited.add((start_r, start_c))

            while q:
                r, c = q.pop(0)

                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < rows_grid
                        and 0 <= nc < cols_grid
                        and grid[nr][nc] == 0
                        and (nr, nc) not in visited
                    ):
                        visited.add((nr, nc))
                        q.append((nr, nc))

    # After flood fill, check if any empty cell within the relevant search area is unvisited
    for r in range(rows_grid):
        for c in range(cols_grid):
            if grid[r][c] == 0 and (r, c) not in visited:
                # Loop detected
                return True  # Loop detected

    # No loop detected
    return False


def _count_empty_neighbors(
    tx, ty, current_path, x_tile_min, x_tile_max, y_tile_min, y_tile_max
):
    """
    Counts the number of empty neighboring tiles around a specific tile.

    This includes diagonals and is used to calculate an "openness" score,
    preferring paths that lead to less constrained areas.
    """
    count = 0
    # Include diagonals for openness
    moves = [move for move in itertools.product((-1, 0, 1), repeat=2) if move != (0,0)]
    for dx, dy in moves:
        nx, ny = tx + dx, ty + dy
        if (
            x_tile_min <= nx < x_tile_max
            and y_tile_min <= ny < y_tile_max
            and (nx, ny) not in current_path
        ):
            count += 1
    return count


def _is_valid_tile_step(
    tx,
    ty,
    is_horizontal_step,
    current_path_tiles,
    x_tile_min,
    x_tile_max,
    y_tile_min,
    y_tile_max,
):
    """
    Validates a single tile step in a path.

    A step is valid if it is within the grid boundaries, does not land on
    an existing path tile, and does not run parallel to an adjacent path
    segment (which would create a "U-turn" or adjacent track).
    """
    # Check bounds and path overlap
    if is_horizontal_step:
        if not (x_tile_min <= tx < x_tile_max and (tx, ty) not in current_path_tiles):
            return False
        # Check for adjacent path segments (prevents U-turns and parallel tracks)
        neighbor1 = (tx, ty - 1)
        neighbor2 = (tx, ty + 1)
        if (
            y_tile_min <= neighbor1[1] < y_tile_max and neighbor1 in current_path_tiles
        ) or (
            y_tile_min <= neighbor2[1] < y_tile_max and neighbor2 in current_path_tiles
        ):
            return False
    else:  # is_vertical_step
        if not (y_tile_min <= ty < y_tile_max and (tx, ty) not in current_path_tiles):
            return False
        # Check for adjacent path segments (prevents U-turns and parallel tracks)
        neighbor1 = (tx - 1, ty)
        neighbor2 = (tx + 1, ty)
        if (
            x_tile_min <= neighbor1[0] < x_tile_max and neighbor1 in current_path_tiles
        ) or (
            x_tile_min <= neighbor2[0] < x_tile_max and neighbor2 in current_path_tiles
        ):
            return False
    return True


def _get_segment_props(
    max_len,
    is_horizontal,
    current_tile_x,
    current_tile_y,
    path_of_tiles,
    last_direction_x,
    last_direction_y,
    grid_tile_rows,
    grid_tile_cols,
    x_tile_min,
    x_tile_max,
    y_tile_min,
    y_tile_max,
):
    """Calculates the valid length and direction of a segment."""
    possible_directions = []
    if is_horizontal:
        if last_direction_x != -1:
            possible_directions.append(1)
        if last_direction_x != 1:
            possible_directions.append(-1)
    else:  # is_vertical
        if last_direction_y != -1:
            possible_directions.append(1)
        if last_direction_y != 1:
            possible_directions.append(-1)

    if not possible_directions:
        possible_directions = [1, -1]

    evaluated_options = []
    for direction_to_try in possible_directions:
        segment_tiles = []
        for step in range(1, max_len + 1):
            if is_horizontal:
                next_x = current_tile_x + direction_to_try * step
                current_proposed_tile = (next_x, current_tile_y)
            else:  # is_vertical
                next_y = current_tile_y + direction_to_try * step
                current_proposed_tile = (current_tile_x, next_y)

            if not _is_valid_tile_step(
                current_proposed_tile[0],
                current_proposed_tile[1],
                is_horizontal,
                path_of_tiles,
                x_tile_min,
                x_tile_max,
                y_tile_min,
                y_tile_max,
            ):
                break
            segment_tiles.append(current_proposed_tile)
        final_length = len(segment_tiles)

        if final_length > 0:
            temporary_path = path_of_tiles.union(set(segment_tiles))
            if _flood_fill_check(
                temporary_path,
                grid_tile_rows,
                grid_tile_cols,
                x_tile_min,
                x_tile_max,
                y_tile_min,
                y_tile_max,
            ):
                continue  # This segment creates a loop, discard it

            end_tile_x = segment_tiles[-1][0] if is_horizontal else current_tile_x
            end_tile_y = segment_tiles[-1][1] if not is_horizontal else current_tile_y

            openness_score = _count_empty_neighbors(
                end_tile_x,
                end_tile_y,
                temporary_path,
                x_tile_min,
                x_tile_max,
                y_tile_min,
                y_tile_max,
            )
            evaluated_options.append(
                (final_length, openness_score, direction_to_try, segment_tiles)
            )
    if not evaluated_options:
        # No valid move
        return 0, 0, []

    evaluated_options.sort(key=lambda x: (x[0], x[1]), reverse=True)

    best_length = evaluated_options[0][0]
    best_openness = evaluated_options[0][1]
    top_options = [
        opt
        for opt in evaluated_options
        if opt[0] == best_length and opt[1] == best_openness
    ]

    selected_option = random.choice(top_options)
    return selected_option[0], selected_option[2], selected_option[3]


def _place_oo_methuselah(region, occupied_points, rows, cols):
    x_start, y_start, x_end, y_end = region
    # Check if empty region
    if x_start >= x_end or y_start >= y_end:
        return set()
    for _ in range(100):  # max attempts to place
        px = random.randint(x_start, x_end - 1)
        py = random.randint(y_start, y_end - 1)
        potential_neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = px + dx, py + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                potential_neighbors.append((nx, ny))
        if not potential_neighbors:
            continue
        neighbor = random.choice(potential_neighbors)
        cell1 = (px, py)
        cell2 = neighbor
        if cell1 not in occupied_points and cell2 not in occupied_points:
            return {cell1, cell2}
    return set()  # Could not place


def _faraday_fill_region(target_points_set, region, stamp_size, rows, cols):
    rx_start, ry_start, rx_end, ry_end = region

    # Iterate through the region, placing stamp_size x stamp_size blocks
    # The loop range ensures that the entire stamp fits within the region bounds
    for y in range(ry_start, ry_end - stamp_size + 1, stamp_size):
        for x in range(rx_start, rx_end - stamp_size + 1, stamp_size):
            for dx, dy in STAR_3X3_RELATIVE_POINTS:
                # Ensure points are within the overall grid boundaries (rows, cols)
                if 0 <= (x + dx) < cols and 0 <= (y + dy) < rows:
                    target_points_set.add((x + dx, y + dy))


def _get_adjacent_placement_coords(region, stamp_width, stamp_height, rows, cols):
    """
    Returns a list of (x, y) coordinates for the top-left corner of a stamp
    of size stamp_width x stamp_height such that it is adjacent to the region
    (touches but does not overlap) and is within the grid boundaries.
    """
    rx_start, ry_start, rx_end, ry_end = region
    potential_coords = set()

    # Iterate along the top side (stamp directly above the region)
    sy = ry_start - stamp_height
    if 0 <= sy < rows:
        for sx in range(
            max(0, rx_start - stamp_width + 1), min(cols - stamp_width + 1, rx_end)
        ):
            if 0 <= sx < cols and 0 <= sx + stamp_width - 1 < cols:
                potential_coords.add((sx, sy))

    # Iterate along the bottom side (stamp directly below the region)
    sy = ry_end
    if 0 <= sy < rows:
        for sx in range(
            max(0, rx_start - stamp_width + 1), min(cols - stamp_width + 1, rx_end)
        ):
            if 0 <= sx < cols and 0 <= sx + stamp_width - 1 < cols:
                potential_coords.add((sx, sy))

    # Iterate along the left side (stamp directly to the left of the region)
    sx = rx_start - stamp_width
    if 0 <= sx < cols:
        for sy in range(
            max(0, ry_start - stamp_height + 1), min(rows - stamp_height + 1, ry_end)
        ):
            if 0 <= sy < rows and 0 <= sy + stamp_height - 1 < rows:
                potential_coords.add((sx, sy))

    # Iterate along the right side (stamp directly to the right of the region)
    sx = rx_end
    if 0 <= sx < cols:
        for sy in range(
            max(0, ry_start - stamp_height + 1), min(rows - stamp_height + 1, ry_end)
        ):
            if 0 <= sy < rows and 0 <= sy + stamp_height - 1 < rows:
                potential_coords.add((sx, sy))


##############################################################################################
########################## map functions #####################################################


### def choochoo2(rows, cols, seed=None, turns=9):
###     """
###     Generates a final, correct, expansive, and resilient "railroad track"
###     of stars, preventing loops and U-turns.
###     """
###     if seed is not None:
###         random.seed(seed)
### 
###     ###############################################
###     # TODO 2: make use of star.txt pattern/stamp here
### 
###     tile_width  = 3
###     tile_height = 3
### 
###     # END TODO 2
###     ###############################################
### 
###     # 1. Define the tile grid dimensions
###     grid_tile_rows = rows // tile_height
###     grid_tile_cols = cols // tile_width
### 
###     # 2. Choose half and define tile boundaries
###     use_left_half = random.choice([True, False])
###     half_tile_cols = grid_tile_cols // 2
###     if use_left_half:
###         x_tile_min, x_tile_max = 0, half_tile_cols
###     else:
###         x_tile_min, x_tile_max = half_tile_cols, grid_tile_cols
### 
###     y_tile_min, y_tile_max = 0, grid_tile_rows
### 
###     # 3. Path Generation
###     path_of_tiles = set()
### 
###     current_tile_x = random.randint(x_tile_min, x_tile_max - 1)
###     current_tile_y = random.randint(y_tile_min, y_tile_max - 1)
###     path_of_tiles.add((current_tile_x, current_tile_y))
### 
###     # Calculate average segment length
###     num_h_segments = (turns + 1) // 2
###     num_v_segments = (turns + 1) - num_h_segments
###     avg_len_x = (((x_tile_max - x_tile_min) / (num_h_segments + 1)))
###     avg_len_y = (((y_tile_max - y_tile_min) / (num_v_segments + 1)))
### 
###     last_move_was_horizontal = random.choice([True, False])
###     last_direction_x = 0
###     last_direction_y = 0
### 
###     for _ in range(turns + 1):
###         segment_generated = False
### 
###         # Define the primary and secondary attempts based on the last move
###         if last_move_was_horizontal:
###             # Last was horizontal, so try vertical first
###             primary_attempt = {"is_horizontal": False, "avg_len": avg_len_y}
###             secondary_attempt = {"is_horizontal": True, "avg_len": avg_len_x}
###         else:
###             # Last was vertical, so try horizontal first
###             primary_attempt = {"is_horizontal": True, "avg_len": avg_len_x}
###             secondary_attempt = {"is_horizontal": False, "avg_len": avg_len_y}
### 
###         for attempt in [primary_attempt, secondary_attempt]:
###             max_len = max(1, int(random.uniform(0.7, 1.3) * attempt["avg_len"]))
###             actual_length, direction, segment_tiles = _get_segment_props(
###                 max_len,
###                 attempt["is_horizontal"],
###                 current_tile_x,
###                 current_tile_y,
###                 path_of_tiles,
###                 last_direction_x,
###                 last_direction_y,
###                 grid_tile_rows,
###                 grid_tile_cols,
###                 x_tile_min,
###                 x_tile_max,
###                 y_tile_min,
###                 y_tile_max,
###             )
### 
###             if actual_length > 0:
###                 path_of_tiles.update(segment_tiles)
###                 if attempt["is_horizontal"]:
###                     current_tile_x = segment_tiles[-1][0]
###                     last_direction_x = direction
###                     last_direction_y = 0
###                 else:
###                     current_tile_y = segment_tiles[-1][1]
###                     last_direction_x = 0
###                     last_direction_y = direction
###                 last_move_was_horizontal = attempt["is_horizontal"]
###                 segment_generated = True
###                 break
### 
###         if not segment_generated:
###             break
### 
###     ###############################################
###     # TODO 3: make use of star.txt pattern/stamp here
### 
###     # 4. Translate tile path to cell coordinates and stamp stars
###     points = set()
###     star_shape = {(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)}
### 
###     def stamp_star(center_x, center_y):
###         for dx, dy in star_shape:
###             points.add((center_x + dx, center_y + dy))
### 
###     for tile_x, tile_y in path_of_tiles:
###         center_x = tile_x * tile_width + (tile_width // 2)
###         center_y = tile_y * tile_height + (tile_height // 2)
###         stamp_star(center_x, center_y)
### 
###     # END TODO 3
###     ###############################################
### 
###     ###############################################
###     # TODO 4: see if there is a utility function to convert
###     # a list of alive cells (x, y) to url format. if not, add one to utils.py,
###     # import it at the top of this file, and use it below.
### 
###     # 5. Serialize to URL format
###     pattern_rows = [
###         "".join("o" if (x_coord, y_coord) in points else "." for x_coord in range(cols))
###         for y_coord in range(rows)
###     ]
### 
###     # END TODO 4
###     ###############################################
### 
###     # s1, b1, c1 form a pattern for color 1 on one side of the grid.
###     # Now horiz flip it, give it some vertical jiggle, and assign to color2
###     s1, b1, c1 = pattern2url_chars(pattern_rows)
###     s2, b2, c2 = pattern2url_chars(hflip_pattern(vjiggle(pattern_rows, 100)))
### 
###     return s1, b1, c1, s2, b2, c2


def twochoochoo(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)
    tile_width  = 3
    tile_height = 3

    grid_tile_rows = rows // tile_height
    grid_tile_cols = cols // tile_width
    half_tile_cols = grid_tile_cols // 2

    turns = random.randint(4, 12)

    # Calculate average segment length
    num_h_segments = (turns + 1) // 2
    num_v_segments = (turns + 1) - num_h_segments
    avg_len_x = half_tile_cols / (num_h_segments + 1)
    avg_len_y = grid_tile_rows / (num_v_segments + 1)

    approved = False
    while not approved:

        max_moves = random.randint(35,120)

        #########################################
        ####### COLOR 1 RAILROAD TRACKS #########

        # left half
        x_tile_min, x_tile_max = 0, half_tile_cols
        y_tile_min, y_tile_max = 0, grid_tile_rows
        path_of_tiles1 = set()

        current_tile_x = random.randint(x_tile_min, x_tile_max - 1)
        current_tile_y = random.randint(y_tile_min, y_tile_max - 1)
        path_of_tiles1.add((current_tile_x, current_tile_y))

        last_move_was_horizontal = random.choice([True, False])
        last_direction_x = 0
        last_direction_y = 0

        nmoves1 = 0
        for _ in range(turns + 1):
            segment_generated = False

            # Define the primary and secondary attempts based on the last move
            if last_move_was_horizontal:
                # Last was horizontal, so try vertical first
                primary_attempt = {"is_horizontal": False, "avg_len": avg_len_y}
                secondary_attempt = {"is_horizontal": True, "avg_len": avg_len_x}
            else:
                # Last was vertical, so try horizontal first
                primary_attempt = {"is_horizontal": True, "avg_len": avg_len_x}
                secondary_attempt = {"is_horizontal": False, "avg_len": avg_len_y}

            for attempt in [primary_attempt, secondary_attempt]:
                max_len = max(1, int(random.uniform(0.7, 1.3) * attempt["avg_len"]))
                moves_budget = max_moves - nmoves1
                max_len = min(max_len, moves_budget)
                actual_length, direction, segment_tiles = _get_segment_props(
                    max_len,
                    attempt["is_horizontal"],
                    current_tile_x,
                    current_tile_y,
                    path_of_tiles1,
                    last_direction_x,
                    last_direction_y,
                    grid_tile_rows,
                    grid_tile_cols,
                    x_tile_min,
                    x_tile_max,
                    y_tile_min,
                    y_tile_max,

                )
                if actual_length > 0:
                    path_of_tiles1.update(segment_tiles)
                    if attempt["is_horizontal"]:
                        current_tile_x = segment_tiles[-1][0]
                        last_direction_x = direction
                        last_direction_y = 0
                    else:
                        current_tile_y = segment_tiles[-1][1]
                        last_direction_x = 0
                        last_direction_y = direction
                    last_move_was_horizontal = attempt["is_horizontal"]
                    segment_generated = True
                    nmoves1 += actual_length
                    break

            if not segment_generated:
                break

        #########################################
        ####### COLOR 2 RAILROAD TRACKS #########

        # right half
        x_tile_min, x_tile_max = half_tile_cols, grid_tile_cols
        y_tile_min, y_tile_max = 0, grid_tile_rows
        path_of_tiles2 = set()

        current_tile_x = random.randint(x_tile_min, x_tile_max - 1)
        current_tile_y = random.randint(y_tile_min, y_tile_max - 1)
        path_of_tiles2.add((current_tile_x, current_tile_y))

        last_move_was_horizontal = random.choice([True, False])
        last_direction_x = 0
        last_direction_y = 0

        nmoves2 = 0
        for _ in range(turns + 1):
            segment_generated = False

            # Define the primary and secondary attempts based on the last move
            if last_move_was_horizontal:
                # Last was horizontal, so try vertical first
                primary_attempt = {"is_horizontal": False, "avg_len": avg_len_y}
                secondary_attempt = {"is_horizontal": True, "avg_len": avg_len_x}
            else:
                # Last was vertical, so try horizontal first
                primary_attempt = {"is_horizontal": True, "avg_len": avg_len_x}
                secondary_attempt = {"is_horizontal": False, "avg_len": avg_len_y}

            for attempt in [primary_attempt, secondary_attempt]:
                max_len = max(1, int(random.uniform(0.7, 1.3) * attempt["avg_len"]))
                moves_budget = max_moves - nmoves2
                max_len = min(max_len, moves_budget)
                actual_length, direction, segment_tiles = _get_segment_props(
                    max_len,
                    attempt["is_horizontal"],
                    current_tile_x,
                    current_tile_y,
                    path_of_tiles2,
                    last_direction_x,
                    last_direction_y,
                    grid_tile_rows,
                    grid_tile_cols,
                    x_tile_min,
                    x_tile_max,
                    y_tile_min,
                    y_tile_max,

                )
                if actual_length > 0:
                    path_of_tiles2.update(segment_tiles)
                    if attempt["is_horizontal"]:
                        current_tile_x = segment_tiles[-1][0]
                        last_direction_x = direction
                        last_direction_y = 0
                    else:
                        current_tile_y = segment_tiles[-1][1]
                        last_direction_x = 0
                        last_direction_y = direction
                    last_move_was_horizontal = attempt["is_horizontal"]
                    segment_generated = True
                    nmoves2 += actual_length
                    break

            if not segment_generated:
                break

        if nmoves1 == nmoves2:
            approved = True

    ###############################################
    # TODO 3: make use of star.txt pattern/stamp here

    # 4. Translate tile path to cell coordinates and stamp stars
    star_shape = {(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)}

    def stamp_star(center_x, center_y, points):
        for dx, dy in star_shape:
            points.add((center_x + dx, center_y + dy))

    points1 = set()
    for tile_x, tile_y in path_of_tiles1:
        center_x = tile_x * tile_width + (tile_width // 2)
        center_y = tile_y * tile_height + (tile_height // 2)
        stamp_star(center_x, center_y, points1)

    points2 = set()
    for tile_x, tile_y in path_of_tiles2:
        center_x = tile_x * tile_width + (tile_width // 2)
        center_y = tile_y * tile_height + (tile_height // 2)
        stamp_star(center_x, center_y, points2)

    # END TODO 3
    ###############################################

    ###############################################
    # TODO 4: see if there is a utility function to convert
    # a list of alive cells (x, y) to url format. if not, add one to utils.py,
    # import it at the top of this file, and use it below.

    # 5. Serialize to URL format
    pattern_rows1 = [
        "".join("o" if (x_coord, y_coord) in points1 else "."
        for x_coord in range(cols))
        for y_coord in range(rows)
    ]

    pattern_rows2 = [
        "".join("o" if (x_coord, y_coord) in points2 else "." 
        for x_coord in range(cols))
        for y_coord in range(rows)
    ]

    # END TODO 4
    ###############################################

    # s1, b1, c1 form a pattern for color 1 on one side of the grid.
    # Now horiz flip it, give it some vertical jiggle, and assign to color2
    s1, b1, c1 = pattern2url_chars(pattern_rows1)
    s2, b2, c2 = pattern2url_chars(pattern_rows2) 

    return s1, b1, c1, s2, b2, c2

def midnightexpress(rows, cols, seed=None):
    """
    Creates two parallel tracks of stars with Methuselah patterns scattered between them
    """
    if seed is not None:
        random.seed(seed)

    # 1. Load ONE methuselah pattern to be used for all placements

    methuselah_names_numbers = [
        ("escapingsatellites", (2, 4)),
        ("solarsail", (1, 3)),
        ("squarepair", (1, 1)),
        ("ylingrow96", (1, 3)),
        ("scaffoldunfusing", (1, 2)),
        ("backedupsink", (1, 4)),
        ("spaceship2platform", (1, 2)),
    ]

    chosen_meth = random.choice(methuselah_names_numbers)
    chosen_meth_name = chosen_meth[0]
    chosen_meth_number = chosen_meth[1]
    meth_pattern_str = get_pattern(chosen_meth_name)

    meth_height = 0
    meth_width = 0

    if meth_pattern_str:
        meth_height = len(meth_pattern_str)
        if meth_height > 0:
            meth_width = len(meth_pattern_str[0])

    # Initialize sets for points for Team 1 ('o') and Team 2 ('o')
    team1_points = set()
    team2_points = set()

    # 2. Determine Track Orientation and generate tracks
    is_horizontal_tracks = random.choice([True, False])
    star_shape = {(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)}
    spacing = 3

    # Abstract dimensions based on orientation
    w, h = (cols, rows) if is_horizontal_tracks else (rows, cols)

    # Determine track length and start position based on primary dimension 'w'
    min_len = w // 3
    max_len = (2 * w) // 3
    track_len = random.randint(min_len, max_len)
    start_pos = random.randint(0, w - track_len)
    end_pos = start_pos + track_len

    # Determine track coordinates based on secondary dimension 'h'
    track1_coord = (h // 4) + random.randint(-h // 8, h // 8)
    track1_coord = max(1, min(h - 2, track1_coord))

    track2_coord = (3 * h // 4) + random.randint(-h // 8, h // 8)
    track2_coord = max(1, min(h - 2, track2_coord))

    # Generate points for both tracks
    for i in range(start_pos, end_pos, spacing):
        for dx, dy in star_shape:
            # Point for track 1
            p1 = (
                (i + dx, track1_coord + dy)
                if is_horizontal_tracks
                else (track1_coord + dx, i + dy)
            )
            team1_points.add(p1)
            # Point for track 2
            p2 = (
                (i + dx, track2_coord + dy)
                if is_horizontal_tracks
                else (track2_coord + dx, i + dy)
            )
            team2_points.add(p2)

    # Define the bounding box for Methuselah placement
    if is_horizontal_tracks:
        methuselah_bbox_min_y = min(track1_coord, track2_coord) + 6
        methuselah_bbox_max_y = max(track1_coord, track2_coord) - 6
        methuselah_bbox_min_x = start_pos
        methuselah_bbox_max_x = end_pos - 1
    else:  # Vertical tracks
        methuselah_bbox_min_x = min(track1_coord, track2_coord) + 6
        methuselah_bbox_max_x = max(track1_coord, track2_coord) - 6
        methuselah_bbox_min_y = start_pos
        methuselah_bbox_max_y = end_pos - 1

    # 3. Place Methuselahs if there is a valid pattern and space
    if (
        meth_pattern_str
        and methuselah_bbox_min_x <= methuselah_bbox_max_x
        and methuselah_bbox_min_y <= methuselah_bbox_max_y
    ):

        meth_initial_relative_points = set()
        if meth_height > 0 and meth_width > 0:
            for r_idx, row_str in enumerate(meth_pattern_str):
                for c_idx, char in enumerate(row_str):
                    if char == "o":
                        meth_initial_relative_points.add((c_idx, r_idx))

        if (
            meth_initial_relative_points
            and methuselah_bbox_min_x <= methuselah_bbox_max_x
            and methuselah_bbox_min_y <= methuselah_bbox_max_y
        ):

            num_methuselahs_per_team = random.randint(*chosen_meth_number)
            meth_to_place = [{"team": 1} for _ in range(num_methuselahs_per_team)] + [
                {"team": 2} for _ in range(num_methuselahs_per_team)
            ]
            random.shuffle(meth_to_place)

            all_occupied_points = team1_points.copy()
            all_occupied_points.update(team2_points)

            for meth_info in meth_to_place:
                transformed_meth_points_relative = apply_random_transformation(
                    meth_initial_relative_points
                )

                # Recalculate meth_width and meth_height based on the transformed pattern for this instance
                current_meth_width = 0
                current_meth_height = 0
                if transformed_meth_points_relative:
                    min_x = min(p[0] for p in transformed_meth_points_relative)
                    max_x = max(p[0] for p in transformed_meth_points_relative)
                    min_y = min(p[1] for p in transformed_meth_points_relative)
                    max_y = max(p[1] for p in transformed_meth_points_relative)
                    current_meth_width = max_x - min_x + 1
                    current_meth_height = max_y - min_y + 1

                if current_meth_width == 0 or current_meth_height == 0:
                    continue  # Skip if transformation resulted in an empty pattern (shouldn't happen with current transformations, but for robustness)

                # Define placement area for this specific transformed methuselah
                placement_min_x = methuselah_bbox_min_x
                placement_max_x = methuselah_bbox_max_x - current_meth_width + 1
                placement_min_y = methuselah_bbox_min_y
                placement_max_y = methuselah_bbox_max_y - current_meth_height + 1

                if (
                    placement_max_x < placement_min_x
                    or placement_max_y < placement_min_y
                ):
                    continue  # No valid placement area for this transformed methuselah

                placed = False
                attempts = 0
                max_attempts = 100

                while not placed and attempts < max_attempts:
                    start_x = random.randint(placement_min_x, placement_max_x)
                    start_y = random.randint(placement_min_y, placement_max_y)

                    current_meth_absolute_points = set()
                    overlap_detected = False
                    for rel_x, rel_y in transformed_meth_points_relative:
                        abs_x, abs_y = start_x + rel_x, start_y + rel_y
                        if (abs_x, abs_y) in all_occupied_points:
                            overlap_detected = True
                            break
                        current_meth_absolute_points.add((abs_x, abs_y))

                    if not overlap_detected:
                        if meth_info["team"] == 1:
                            team1_points.update(current_meth_absolute_points)
                        else:
                            team2_points.update(current_meth_absolute_points)
                        all_occupied_points.update(current_meth_absolute_points)
                        placed = True
                    attempts += 1

    # 4. Convert team points to URL format
    s1_output = points_to_url(team1_points, rows, cols)
    s2_output = points_to_url(team2_points, rows, cols)

    return s1_output, "[]", "[]", s2_output, "[]", "[]"


def spaceelevator(rows, cols, seed=None):
    """
    Creates a "space elevator" track of stars across the grid,
    with two adjacent methuselah cells poised to interact with it.
    """
    if seed is not None:
        random.seed(seed)

    team1_points = set()
    team2_points = set()
    all_occupied_points = set()

    #################################################
    # TODO 1: Fix this to use common star.txt pattern
    star_shape = {(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)}  # 5-cell star stamp
    spacing = 3  # Spacing between star centers along the track, ensuring no overlap
    # END TODO 1
    #################################################

    # 1. Track orientation, grid split
    is_horizontal_split = False  # Tracks are always vertical

    xjitter = random.randint(-12, 12)

    # Generate Track 1 (for team1_points)
    half_cols = cols // 2
    mid_col_half = half_cols // 2
    track1_xloc = max(
        1, min(cols - 2, mid_col_half + xjitter)
    )
    for y_center in range(1, rows - 1, spacing):
        for dx, dy in star_shape:
            p = (track1_xloc + dx, y_center + dy)
            team1_points.add(p)
            all_occupied_points.add(p)

    # Generate Track 2 (for team2_points)
    half_cols = cols // 2
    mid_col_half = cols // 2 + half_cols // 2
    track2_xloc = max(
        1, min(cols - 2, mid_col_half + xjitter)
    )  # Ensure star fits
    for y_center in range(1, rows - 1, spacing):
        for dx, dy in star_shape:
            p = (track2_xloc + dx, y_center + dy)
            team2_points.add(p)
            all_occupied_points.add(p)

    # -------------------------------------
    # Chef's choice:
    # - Type 1: 1 oo methuselah somewhere on the grid
    # - Type 2: add one extra star stamp of opp color, somewhere on the perimeter
    # - Type 3: add N alive cells somewhere on the perimeter, N random locations

    # chefs_choice = random.choice([1, 2, 3])
    # chefs_choice = 1
    chefs_choice = 2
    # chefs_choice = 3

    if chefs_choice == 1:
        buffer = 3
        team1_methuselah_region = 0+buffer, 0+buffer, cols-buffer, rows-buffer
        team2_methuselah_region = 0+buffer, 0+buffer, cols-buffer, rows-buffer 

        # Place methuselah for team 1
        methuselah1_points = _place_oo_methuselah(
            team1_methuselah_region, all_occupied_points, rows, cols
        )
        if methuselah1_points:
            team1_points.update(methuselah1_points)
            all_occupied_points.update(
                methuselah1_points
            )  # Update occupied points for next placement

        # Place methuselah for team 2
        methuselah2_points = _place_oo_methuselah(
            team2_methuselah_region, all_occupied_points, rows, cols
        )
        if methuselah2_points:
            team2_points.update(methuselah2_points)

    elif chefs_choice == 2:
        # Add some 3x3 star stamps that are DIRECT neighbors of the space elevator track
        nstars = random.randint(3, 10)
        buffer = 3

        star_points1 = set()
        star_points2 = set()

        for _ in range(nstars):
            xloc = track1_xloc
            xjitter = random.choice([-3, 3])
            yloc = random.randint(0+buffer, rows-buffer) 
            p = (xloc + xjitter - 1, yloc)
            star_points1.add(p)

        for _ in range(nstars):
            xloc = track2_xloc
            xjitter = random.choice([-3, 3])
            yloc = random.randint(0+buffer, rows-buffer) 
            p = (xloc + xjitter -1, yloc)
            star_points2.add(p)

        for (x, y) in star_points1:
            for dx, dy in STAR_3X3_RELATIVE_POINTS:
                # Ensure points are within the overall grid boundaries (rows, cols)
                if 0 <= (x + dx) < cols and 0 <= (y + dy) < rows:
                    team1_points.add((x + dx, y + dy))

        for (x, y) in star_points2:
            for dx, dy in STAR_3X3_RELATIVE_POINTS:
                # Ensure points are within the overall grid boundaries (rows, cols)
                if 0 <= (x + dx) < cols and 0 <= (y + dy) < rows:
                    team2_points.add((x + dx, y + dy))

    elif chefs_choice == 3:
        # Add random points around the perimeter of the elevators
        ncells = random.randint(15, 35)
        buffer = 3

        for _ in range(ncells):
            xloc = track1_xloc
            xjitter = random.choice([-2, 2])
            yloc = random.randint(0+buffer, rows-buffer) 
            p = (xloc + xjitter, yloc)
            team1_points.add(p)

        for _ in range(ncells):
            xloc = track2_xloc
            xjitter = random.choice([-2, 2])
            yloc = random.randint(0+buffer, rows-buffer) 
            p = (xloc + xjitter, yloc)
            team2_points.add(p)

    # Convert to URL format
    s1_output = points_to_url(team1_points, rows, cols)
    s2_output = points_to_url(team2_points, rows, cols)

    return s1_output, "[]", "[]", s2_output, "[]", "[]"


def faradaycage(rows, cols, seed=None):
    """
    Generates a map with two randomly selected segments of the grid
    filled with a tiled 3x3 grid with 2x2 empty square in the middle.
    """
    if seed is not None:
        random.seed(seed)

    team1_points = set()
    team2_points = set()

    stamp_size = STAR_STAMP_WIDTH

    # Define the N x N regions of the grid
    regions = []

    # Calculate division points
    N = random.choice(list(range(7, 11)))
    x_divs = [i * (cols // N) for i in range(N + 1)]
    y_divs = [i * (rows // N) for i in range(N + 1)]

    for j in range(N):
        for i in range(N):
            x_start = x_divs[i]
            y_start = y_divs[j]
            x_end = x_divs[i + 1] if i < N - 1 else cols
            y_end = y_divs[j + 1] if j < N - 1 else rows

            region = (x_start, y_start, x_end, y_end)
            regions.append(region)

    valid = []
    for region in regions:
        x_start, y_start, x_end, y_end = region
        # Check if the region is large enough to fit at least one stamp
        if (x_end - x_start >= stamp_size) and (y_end - y_start >= stamp_size):
            valid.append(region)

    # -------------------
    # Faraday region:

    # Select four regions to fill with stamps and ...something else
    chosen = random.sample(valid, 4)
    team1_faraday_region = chosen[0]
    team2_faraday_region = chosen[1]

    # Fill Faraday cage regions with stamps
    _faraday_fill_region(
        team1_points, team1_faraday_region, stamp_size, rows, cols
    )
    _faraday_fill_region(
        team2_points, team2_faraday_region, stamp_size, rows, cols
    )

    # -------------------------------------
    # Chef's choice:
    # - Type 1: 1 oo methuselah somewhere on the grid
    # - Type 2: add one extra star stamp of opp color, somewhere on the perimeter
    # - Type 3: add N alive cells somewhere on the perimeter, N random locations

    # chefs_choice = random.choice([1, 2, 3])
    # chefs_choice = 1
    # chefs_choice = 2
    chefs_choice = 3

    # Initial occupied points after filling Faraday cages
    all_occupied_points = team1_points.union(team2_points)

    if chefs_choice == 1:
        team1_methuselah_info = chosen[2]
        team2_methuselah_info = chosen[3]

        # Place methuselah for team 1
        methuselah1_points = _place_oo_methuselah(
            team1_methuselah_info["region"], all_occupied_points, rows, cols
        )
        if methuselah1_points:
            team1_points.update(methuselah1_points)
            all_occupied_points.update(
                methuselah1_points
            )  # Update occupied points for next placement

        # Place methuselah for team 2
        methuselah2_points = _place_oo_methuselah(
            team2_methuselah_info["region"], all_occupied_points, rows, cols
        )
        if methuselah2_points:
            team2_points.update(methuselah2_points)

    elif chefs_choice == 2:
        # TODO:
        # - determine the perimeter of the faraday cage, the tiled 3x3 star stamp
        # - add one 3x3 star stamp that is a DIRECT neighbor of the faraday cage, at a random location on the perimeter.
        pass

    elif chefs_choice == 3:
        # This choice is made AFTER team1_points and team2_points have been filled
        # with their respective Faraday cage stamps.

        # Ensure an equal number of cells are added to the perimeter of each team's cage.
        num_cells_to_add_per_team = random.randint(1, 5)

        # --- Process Team 1's perimeter ---
        final_perimeter_points_team1 = set()
        if team1_points:
            min_x_t1 = min(p[0] for p in team1_points)
            max_x_t1 = max(p[0] for p in team1_points)
            min_y_t1 = min(p[1] for p in team1_points)
            max_y_t1 = max(p[1] for p in team1_points)

            perimeter_candidates_t1 = set()
            # Top perimeter
            y = min_y_t1 - 1
            if 0 <= y < rows:
                for x in range(min_x_t1, max_x_t1 + 1):
                    if 0 <= x < cols:
                        perimeter_candidates_t1.add((x, y))
            # Bottom perimeter
            y = max_y_t1 + 1
            if 0 <= y < rows:
                for x in range(min_x_t1, max_x_t1 + 1):
                    if 0 <= x < cols:
                        perimeter_candidates_t1.add((x, y))
            # Left perimeter
            x = min_x_t1 - 1
            if 0 <= x < cols:
                for y in range(min_y_t1, max_y_t1 + 1):
                    if 0 <= y < rows:
                        perimeter_candidates_t1.add((x, y))
            # Right perimeter
            x = max_x_t1 + 1
            if 0 <= x < cols:
                for y in range(min_y_t1, max_y_t1 + 1):
                    if 0 <= y < rows:
                        perimeter_candidates_t1.add((x, y))

            final_perimeter_points_team1 = {
                p for p in perimeter_candidates_t1 if p not in all_occupied_points
            }

        # Add cells to team 1
        if final_perimeter_points_team1:
            num_to_place_t1 = min(
                num_cells_to_add_per_team, len(final_perimeter_points_team1)
            )
            cells_to_add_t1 = random.sample(
                list(final_perimeter_points_team1), num_to_place_t1
            )
            team1_points.update(cells_to_add_t1)

        # --- Process Team 2's perimeter ---
        current_all_occupied_points = team1_points.union(team2_points)
        final_perimeter_points_team2 = set()
        if team2_points:
            min_x_t2 = min(p[0] for p in team2_points)
            max_x_t2 = max(p[0] for p in team2_points)
            min_y_t2 = min(p[1] for p in team2_points)
            max_y_t2 = max(p[1] for p in team2_points)

            perimeter_candidates_t2 = set()
            # Top perimeter
            y = min_y_t2 - 1
            if 0 <= y < rows:
                for x in range(min_x_t2, max_x_t2 + 1):
                    if 0 <= x < cols:
                        perimeter_candidates_t2.add((x, y))
            # Bottom perimeter
            y = max_y_t2 + 1
            if 0 <= y < rows:
                for x in range(min_x_t2, max_x_t2 + 1):
                    if 0 <= x < cols:
                        perimeter_candidates_t2.add((x, y))
            # Left perimeter
            x = min_x_t2 - 1
            if 0 <= x < cols:
                for y in range(min_y_t2, max_y_t2 + 1):
                    if 0 <= y < rows:
                        perimeter_candidates_t2.add((x, y))
            # Right perimeter
            x = max_x_t2 + 1
            if 0 <= x < cols:
                for y in range(min_y_t2, max_y_t2 + 1):
                    if 0 <= y < rows:
                        perimeter_candidates_t2.add((x, y))

            final_perimeter_points_team2 = {
                p
                for p in perimeter_candidates_t2
                if p not in current_all_occupied_points
            }

        # Add cells to team 2
        if final_perimeter_points_team2:
            num_to_place_t2 = min(
                num_cells_to_add_per_team, len(final_perimeter_points_team2)
            )
            cells_to_add_t2 = random.sample(
                list(final_perimeter_points_team2), num_to_place_t2
            )
            team2_points.update(cells_to_add_t2)

    s1 = points_to_url(team1_points, rows, cols)
    s2 = points_to_url(team2_points, rows, cols)

    return s1, "[]", "[]", s2, "[]", "[]"


def ironhorse(rows, cols, seed=None):
    pass


def deadendterminal(rows, cols, seed=None):
    pass


def bando(rows, cols, seed=None):
    pass


def ghosttrain(rows, cols, seed=None):
    pass
