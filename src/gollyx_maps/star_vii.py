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
        "candychoochoo": candychoochoo,
        "midnightexpress": midnightexpress,
        "spaceelevator": spaceelevator,
        "faradaycage": faradaycage,
        "housewithears": housewithears,
        "ironhorse": ironhorse,
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
max_x_star = max(p[0] for p in STAR_3X3_RELATIVE_POINTS)
max_y_star = max(p[1] for p in STAR_3X3_RELATIVE_POINTS)
STAR_STAMP_WIDTH = max_x_star + 1
STAR_STAMP_HEIGHT = max_y_star + 1

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
    alternating=False,
):
    """
    Evaluates and selects the best possible next segment for a path on a tile-based grid.

    This function attempts to extend a path from a given point (`current_tile_x`, `current_tile_y`)
    by adding a straight line segment, either horizontally or vertically. It is the core of the
    random "railroad track" generation logic.

    The selection process is opinionated to create aesthetically pleasing, non-looping paths:
    1.  **Direction**: It determines possible directions (e.g., right/left for horizontal). If
        the new segment has the same orientation as the previous one, this logic forces the path
        to continue straight, preventing 180-degree reversals. If the orientation is different,
        both perpendicular directions are considered.
    2.  **Validation**: For each direction, it generates the longest possible segment (up to `max_len`)
        that stays within the grid boundaries and doesn't violate path integrity rules defined in
        `_is_valid_tile_step` (no self-intersection, no parallel adjacent tracks).
    3.  **Loop Prevention**: It uses a flood-fill check (`_flood_fill_check`) to discard any segment
        that would form a closed loop in the path.
    4.  **Scoring**: Each valid potential segment is scored based on two criteria:
        a. `length`: The number of tiles in the segment. Longer is better.
        b. `openness_score`: The number of empty neighbors around the end tile of the segment.
           A higher score means the path is heading into a more open area, reducing the chance
           of getting trapped.
    5.  **Selection**: The function prioritizes the longest segments. Among segments of the same
        maximum length, it prioritizes those with the highest openness score. If multiple
        segments tie for the best score, one is chosen randomly.

    Args:
        max_len (int): The maximum allowed length for the new segment.
        is_horizontal (bool): If True, generate a horizontal segment; otherwise, a vertical one.
        current_tile_x (int): The starting X coordinate (in tiles) for the new segment.
        current_tile_y (int): The starting Y coordinate (in tiles) for the new segment.
        path_of_tiles (set): A set of (x, y) tuples representing the tiles already in the path.
        last_direction_x (int): The direction of the last horizontal move (1 for right, -1 for left, 0 if none).
        last_direction_y (int): The direction of the last vertical move (1 for down, -1 for up, 0 if none).
        grid_tile_rows (int): The total number of rows in the tile grid.
        grid_tile_cols (int): The total number of columns in the tile grid.
        x_tile_min (int): The minimum allowed X coordinate for a tile in the current region.
        x_tile_max (int): The maximum allowed X coordinate for a tile in the current region.
        y_tile_min (int): The minimum allowed Y coordinate for a tile in the current region.
        y_tile_max (int): The maximum allowed Y coordinate for a tile in the current region.
        alternating (bool): Unused parameter.

    Returns:
        tuple[int, int, list]: A tuple containing:
        - The length of the selected segment (0 if no valid segment was found).
        - The direction of the segment (1 or -1).
        - A list of (x, y) tile tuples that form the segment.
    """
    # Determine which directions to try. If the last move was in the same orientation,
    # this logic forces the path to continue straight. Otherwise, it allows turning.
    possible_directions = []
    if is_horizontal:
        if last_direction_x == 0:  # Previous move was vertical, can go left or right
            possible_directions = [1, -1]
        else:  # Previous move was horizontal, must continue in that direction
            possible_directions.append(last_direction_x)
    else:  # is_vertical
        if last_direction_y == 0:  # Previous move was horizontal, can go up or down
            possible_directions = [1, -1]
        else:  # Previous move was vertical, must continue in that direction
            possible_directions.append(last_direction_y)

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
                break  # Segment hits an invalid tile, stop extending it
            segment_tiles.append(current_proposed_tile)

        # If a valid segment of any length was created, evaluate it
        if segment_tiles:
            temporary_path = path_of_tiles.union(segment_tiles)

            # Discard segments that create closed loops
            if _flood_fill_check(
                temporary_path,
                grid_tile_rows,
                grid_tile_cols,
                x_tile_min,
                x_tile_max,
                y_tile_min,
                y_tile_max,
            ):
                continue

            # Score the segment based on length and "openness"
            end_tile = segment_tiles[-1]
            openness_score = _count_empty_neighbors(
                end_tile[0],
                end_tile[1],
                temporary_path,
                x_tile_min,
                x_tile_max,
                y_tile_min,
                y_tile_max,
            )
            evaluated_options.append(
                (len(segment_tiles), openness_score, direction_to_try, segment_tiles)
            )

    # If no valid segments were found, return empty
    if not evaluated_options:
        return 0, 0, []

    # Select the best option: sort by length then openness, descending
    evaluated_options.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # Find all options that are tied for the best score
    best_score = (evaluated_options[0][0], evaluated_options[0][1])
    top_options = [opt for opt in evaluated_options if (opt[0], opt[1]) == best_score]

    # Randomly choose one of the top options
    final_length, _, direction, segment_tiles = random.choice(top_options)
    return final_length, direction, segment_tiles


def _place_oo_methuselah(region, occupied_points, rows, cols, n=1):
    x_start, y_start, x_end, y_end = region
    # Check if empty region
    if x_start >= x_end or y_start >= y_end:
        err = "Error: no region to place oo methuselah"
        raise GollyXMapsError(err)
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

    err = "Error: could not find anywhere to place oo methuselah"
    raise GollyXMapsError(err)


def _faraday_fill_region(target_points_set, region, rows, cols):
    rx_start, ry_start, rx_end, ry_end = region
    stamp_size = STAR_STAMP_WIDTH

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
###     # TODO: make use of star.txt pattern/stamp here
### 
###     tile_width  = 3
###     tile_height = 3
### 
###     # END TODO
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
###     # TODO: make use of star.txt pattern/stamp here
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
###     # END TODO 
###     ###############################################
### 
###     ###############################################
###     # TODO: see if there is a utility function to convert
###     # a list of alive cells (x, y) to url format. if not, add one to utils.py,
###     # import it at the top of this file, and use it below.
### 
###     # 5. Serialize to URL format
###     pattern_rows = [
###         "".join("o" if (x_coord, y_coord) in points else "." for x_coord in range(cols))
###         for y_coord in range(rows)
###     ]
### 
###     # END TODO
###     ###############################################
### 
###     # s1, b1, c1 form a pattern for color 1 on one side of the grid.
###     # Now horiz flip it, give it some vertical jiggle, and assign to color2
###     s1, b1, c1 = pattern2url_chars(pattern_rows)
###     s2, b2, c2 = pattern2url_chars(hflip_pattern(vjiggle(pattern_rows, 100)))
### 
###     return s1, b1, c1, s2, b2, c2


def twochoochoo(rows, cols, seed=None):
    """
    Split the grid in half. Use a flood fill algorithm to generate a random
    space filling curve of 90-degree railroad tracks (side-by-side crosses).
    Create two separate random tracks, one of each color. Number of cells for
    each team kept identical with a star stamps budget.
    """
    if seed is not None:
        random.seed(seed)

    tile_width  = STAR_STAMP_WIDTH
    tile_height = STAR_STAMP_HEIGHT

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
    # TODO: make use of star.txt pattern/stamp here

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

    # END TODO
    ###############################################

    ###############################################
    # TODO: see if there is a utility function to convert
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

    # END TODO
    ###############################################

    # s1, b1, c1 form a pattern for color 1 on one side of the grid.
    # Now horiz flip it, give it some vertical jiggle, and assign to color2
    s1, b1, c1 = pattern2url_chars(pattern_rows1)
    s2, b2, c2 = pattern2url_chars(pattern_rows2) 

    return s1, b1, c1, s2, b2, c2


def candychoochoo(rows, cols, seed=None):
    """
    Generates a single space-filling "railroad track" of star stamps across the entire grid.
    The path is then divided between two teams using a 3x3 checkerboard pattern on the
    tile grid, where each 3x3 tile area is assigned to a team in an alternating fashion.
    """
    if seed is not None:
        random.seed(seed)

    tile_width  = STAR_STAMP_WIDTH
    tile_height = STAR_STAMP_HEIGHT

    grid_tile_rows = rows // tile_height
    grid_tile_cols = cols // tile_width

    turns = random.randint(7, 21)

    # Calculate average segment length for the whole grid
    num_h_segments = (turns + 1) // 2
    num_v_segments = (turns + 1) - num_h_segments
    avg_len_x = grid_tile_cols / (num_h_segments + 1) if num_h_segments > -1 else grid_tile_cols
    avg_len_y = grid_tile_rows / (num_v_segments + 1) if num_v_segments > -1 else grid_tile_rows

    max_moves = 2*random.randint(60, 180)

    # --- 1. Generate a single path across the whole grid ---
    path_of_tiles = set()
    x_tile_min, x_tile_max = 0, grid_tile_cols
    y_tile_min, y_tile_max = 0, grid_tile_rows

    current_tile_x = random.randint(x_tile_min, x_tile_max - 1)
    current_tile_y = random.randint(y_tile_min, y_tile_max - 1)
    path_of_tiles.add((current_tile_x, current_tile_y))

    last_move_was_horizontal = random.choice([True, False])
    last_direction_x = 0
    last_direction_y = 0

    nmoves = 0
    for _ in range(turns + 1):
        segment_generated = False

        if last_move_was_horizontal:
            primary_attempt = {"is_horizontal": False, "avg_len": avg_len_y}
            secondary_attempt = {"is_horizontal": True, "avg_len": avg_len_x}
        else:
            primary_attempt = {"is_horizontal": True, "avg_len": avg_len_x}
            secondary_attempt = {"is_horizontal": False, "avg_len": avg_len_y}

        for attempt in [primary_attempt, secondary_attempt]:
            max_len = max(1, int(random.uniform(0.7, 1.3) * attempt["avg_len"]))
            moves_budget = max_moves - nmoves
            max_len = min(max_len, moves_budget)

            actual_length, direction, segment_tiles = _get_segment_props(
                max_len,
                attempt["is_horizontal"],
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
            )

            if actual_length > 0:
                path_of_tiles.update(segment_tiles)
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
                nmoves += actual_length
                break

        if not segment_generated:
            break

    # --- 2. Split the path into two teams using a 3x3 checkerboard pattern ---
    path_of_tiles1 = set()
    path_of_tiles2 = set()
    for tile_x, tile_y in path_of_tiles:
        patch_x = tile_x // 3
        patch_y = tile_y // 3
        if (patch_x + patch_y) % 2 == 0:
            path_of_tiles1.add((tile_x, tile_y))
        else:
            path_of_tiles2.add((tile_x, tile_y))

    # --- 3. Translate tile paths to cell coordinates and stamp stars ---
    points1 = set()
    for tile_x, tile_y in path_of_tiles1:
        base_x = tile_x * tile_width
        base_y = tile_y * tile_height
        for dx, dy in STAR_3X3_RELATIVE_POINTS:
            points1.add((base_x + dx, base_y + dy))

    points2 = set()
    for tile_x, tile_y in path_of_tiles2:
        base_x = tile_x * tile_width
        base_y = tile_y * tile_height
        for dx, dy in STAR_3X3_RELATIVE_POINTS:
            points2.add((base_x + dx, base_y + dy))

    # --- 4. Serialize to URL format ---
    pattern_rows1 = [
        "".join("o" if (x_coord, y_coord) in points1 else "." for x_coord in range(cols))
        for y_coord in range(rows)
    ]
    pattern_rows2 = [
        "".join("o" if (x_coord, y_coord) in points2 else "." for x_coord in range(cols))
        for y_coord in range(rows)
    ]

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
    # TODO: Fix this to use common star.txt pattern
    star_shape = {(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)}  # 5-cell star stamp
    spacing = 3  # Spacing between star centers along the track, ensuring no overlap
    # END TODO
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

    chefs_choice = random.choice([1, 2, 3])
    # chefs_choice = 1
    # chefs_choice = 2
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
            if (x_end - x_start >= stamp_size) and (y_end - y_start >= stamp_size):
                region = (x_start, y_start, x_end, y_end)
                regions.append(region)

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
    # - Type 2: add N alive cells somewhere on the perimeter, N random locations

    chefs_choice = random.choice([1, 2])
    # chefs_choice = 1
    # chefs_choice = 2

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


def housewithears(rows, cols, seed=None):
    """
    Make a house with ears (similar to Faraday cage, but slightly different)
    """
    if seed is not None:
        random.seed(seed)

    team1_points = set()
    team2_points = set()

    team1_b = set()
    team2_b = set()

    team1_c = set()
    team2_c = set()

    pbuff = 2

    # --------------------------------
    # The House

    # Calculate valid house regions
    N = random.choice(list(range(16, 20)))
    x_divs = [i * (cols // N) for i in range(N + 1)]
    y_divs = [i * (rows // N) for i in range(N + 1)]

    valid = []
    for j in range(N):
        for i in range(N):
            x_start = x_divs[i]
            y_start = y_divs[j]
            x_end = x_divs[i + 1] if i < N - 1 else cols
            y_end = y_divs[j + 1] if j < N - 1 else rows
            if x_start > pbuff and x_end < cols - pbuff:
                if y_start > pbuff and y_end < rows - pbuff:
                    region = (x_start, y_start, x_end, y_end)
                    valid.append(region)

    chosen = random.sample(valid, 2)
    team1_faraday_region = chosen[0]
    team2_faraday_region = chosen[1]

    _faraday_fill_region(
        team1_points, team1_faraday_region, rows, cols
    )
    _faraday_fill_region(
        team2_points, team2_faraday_region, rows, cols
    )

    # --------------------------------
    # The Ears

    all_occupied_points = team1_points.union(team2_points)

    # Add ears/horns/etc
    regions = random.sample(valid, 3)
    for (team_points, team_points_b, team_points_c, region1, region2) in [
            (team1_points, team1_b, team1_c, regions[0], regions[1]),
            (team2_points, team2_b, team2_c, regions[1], regions[2])
    ]:
        min_x = min(p[0] for p in team_points)
        max_x = max(p[0] for p in team_points)
        min_y = min(p[1] for p in team_points)
        max_y = max(p[1] for p in team_points)

        if random.getrandbits(1)==1:

            # Top and bottom perimeters
            top_perimeter_candidates = set()
            y = min_y - 1
            if pbuff <= y < rows-pbuff:
                for x in range(min_x, max_x + 1):
                    if pbuff <= x < cols-pbuff:
                        top_perimeter_candidates.add((x, y))
            top_perimeter_points = {p for p in top_perimeter_candidates if p not in all_occupied_points}

            bot_perimeter_candidates = set()
            y = max_y + 1
            if pbuff <= y < rows-pbuff:
                for x in range(min_x, max_x + 1):
                    if pbuff <= x < cols-pbuff:
                        bot_perimeter_candidates.add((x, y))
            bot_perimeter_points = {p for p in bot_perimeter_candidates if p not in all_occupied_points}

            if len(top_perimeter_points)==0 or len(bot_perimeter_points)==0:
                err = "Error: no perimeter points found"
                raise GollyXMapsError(err)

            # Top ears
            (x_, y_) = random.choice(list(top_perimeter_points))
            p = (x_, y_)
            pb = (x_-1, y_-1)
            pc = (x_-2, y_-1)
            team_points.update([p])
            team_points_b.update([pb])
            team_points_c.update([pc])
            all_occupied_points.update([p, pb, pc])

            # Bottom ears
            (x_, y_) = random.choice(list(bot_perimeter_points))
            p = (x_, y_)
            pb = (x_-1, y_+1)
            pc = (x_-2, y_+1)
            team_points.update([p])
            team_points_b.update([pb])
            team_points_c.update([pc])
            all_occupied_points.update([p, pb, pc])

        else:

            # Left and right perimeters
            # "top" is actually left
            top_perimeter_candidates = set()
            x = min_x - 1
            if pbuff <= x < cols-pbuff:
                for y in range(min_y, max_y + 1):
                    if pbuff <= y < rows-pbuff:
                        top_perimeter_candidates.add((x, y))
            top_perimeter_points = {p for p in top_perimeter_candidates if p not in all_occupied_points}

            # "bot" is actually right
            bot_perimeter_candidates = set()
            x = max_x + 1
            if pbuff <= x < cols-pbuff:
                for y in range(min_y, max_y + 1):
                    if pbuff <= y < cols-pbuff:
                        bot_perimeter_candidates.add((x, y))
            bot_perimeter_points = {p for p in bot_perimeter_candidates if p not in all_occupied_points}

            if len(top_perimeter_points)==0 or len(bot_perimeter_points)==0:
                err = "Error: no perimeter points found"
                raise GollyXMapsError(err)

            # Top ears
            (x_, y_) = random.choice(list(top_perimeter_points))
            p = (x_, y_)
            pb = (x_-1, y_-1)
            pc = (x_-1, y_-2)
            team_points.update([p])
            team_points_b.update([pb])
            team_points_c.update([pc])
            all_occupied_points.update([p, pb, pc])

            # Bottom ears
            (x_, y_) = random.choice(list(bot_perimeter_points))
            p = (x_, y_)
            pb = (x_+1, y_+1)
            pc = (x_+1, y_+2)
            team_points.update([p])
            team_points_b.update([pb])
            team_points_c.update([pc])
            all_occupied_points.update([p, pb, pc])

        for region in [region1, region2]:
            methuselah_points = _place_oo_methuselah(
                region, all_occupied_points, rows, cols
            )
            team_points.update(methuselah_points)
            all_occupied_points.update(methuselah_points)

    s1 = points_to_url(team1_points, rows, cols)
    s2 = points_to_url(team2_points, rows, cols)

    b1 = points_to_url(team1_b, rows, cols, char="b")
    b2 = points_to_url(team2_b, rows, cols, char="b")

    c1 = points_to_url(team1_c, rows, cols, char="c")
    c2 = points_to_url(team2_c, rows, cols, char="c")

    return s1, b1, c1, s2, b2, c2


def ironhorse(rows, cols, seed=None):
    """
    Create a line of crosses, randomly add satellites to some, "o" or "ob" or "bc"

    Set them up so they are facing off

    Pick a random y-value level, add at y+25 and y-25

    Add some x-jiggle +/-10
    """
    # ----------------------------
    # Input parameters
    nstamps_range = [22, 44]
    orbiter_prob = 0.70
    # (min, max)
    xjit = (-15, 15)
    yjit = (25, 75)

    # ----------------------------
    # 5 x 5 star pattern
    STAR_5X5_PATTERN_STR = [".....", "..o..", ".ooo.", "..o..", "....."]
    STAR_5X5_RELATIVE_POINTS = set()
    for y_idx, row in enumerate(STAR_5X5_PATTERN_STR):
        for x_idx, char in enumerate(row):
            if char == "o":
                STAR_5X5_RELATIVE_POINTS.add((x_idx, y_idx))
    stamp_size = len(STAR_5X5_PATTERN_STR[0])

    # ---------------------------
    # Add the lineup of stars

    team1_points = set()
    team2_points = set()

    team1_b = set()
    team2_b = set()

    team1_c = set()
    team2_c = set()

    nstamps = random.randint(nstamps_range[0], nstamps_range[1])

    xcenter, ycenter = cols//2, rows//2
    ytop, ybot = ycenter - random.randint(*yjit), ycenter + random.randint(*yjit)
    xofftop, xoffbot = random.randint(*xjit), random.randint(*xjit)
    rx_start, rx_end = xcenter - stamp_size*(nstamps//2+1), xcenter + stamp_size*(nstamps//2+1)

    def _add_orbiter(team_points, team_b, team_c, stamp_size, x, y, p=orbiter_prob):
        add_orbiter = random.random() < p
        if add_orbiter:
            point_choice = random.randint(1, 4)
            if point_choice==1:
                dx = 1
                dy = stamp_size-1
                ghost = 'y'
            elif point_choice==2:
                dx = stamp_size-1
                dy = 1
                ghost = 'x'
            elif point_choice==3:
                dx = 0
                dy = 1
                ghost = 'x'
            elif point_choice==4:
                dx = 1
                dy = 0
                ghost = 'y'
            team_points.add((x + dx,  y + dy))

            add_ghost = random.random() < p
            if add_ghost:
                rand_sign = random.choice([1, -1])
                if ghost=='y':
                    team_b.add((x + dx + rand_sign*1, y + dy))
                    team_c.add((x + dx + rand_sign*2, y + dy))
                elif ghost=='x':
                    team_b.add((x + dx, y + dy + rand_sign*1))
                    team_c.add((x + dx, y + dy + rand_sign*2))

    # Top row
    for y in range(ytop, ytop + stamp_size - 1, stamp_size):
        for x in range(rx_start, rx_end + stamp_size - 1, stamp_size):
            for dx, dy in STAR_5X5_RELATIVE_POINTS:
                # Ensure points are within the overall grid boundaries (rows, cols)
                if 0 <= (x + dx) < cols and 0 <= (y + dy) < rows:
                    team1_points.add((x + dx, y + dy))

            # Optionally, add an orbiter
            _add_orbiter(team1_points, team1_b, team1_c, stamp_size, x, y)

    # Bot row
    for y in range(ybot, ybot + stamp_size - 1, stamp_size):
        for x in range(rx_start, rx_end + stamp_size - 1, stamp_size):
            for dx, dy in STAR_5X5_RELATIVE_POINTS:
                # Ensure points are within the overall grid boundaries (rows, cols)
                if 0 <= (x + dx) < cols and 0 <= (y + dy) < rows:
                    team2_points.add((x + dx, y + dy))

            # Optionally, add an orbiter
            _add_orbiter(team2_points, team2_b, team2_c, stamp_size, x, y)

    if random.getrandbits(1)==1:
        s1 = points_to_url(team1_points, rows, cols)
        s2 = points_to_url(team2_points, rows, cols)

        b1 = points_to_url(team1_b, rows, cols)
        b2 = points_to_url(team2_b, rows, cols)

        c1 = points_to_url(team1_c, rows, cols)
        c2 = points_to_url(team2_c, rows, cols)

    else:
        s2 = points_to_url(team1_points, rows, cols)
        s1 = points_to_url(team2_points, rows, cols)

        b2 = points_to_url(team1_b, rows, cols, char="b")
        b1 = points_to_url(team2_b, rows, cols, char="b")

        c2 = points_to_url(team1_c, rows, cols, char="c")
        c1 = points_to_url(team2_c, rows, cols, char="c")

    return s1, b1, c1, s2, b2, c2


def deadendterminal(rows, cols, seed=None):
    pass


def bando(rows, cols, seed=None):
    pass


def ghosttrain(rows, cols, seed=None):
    pass
