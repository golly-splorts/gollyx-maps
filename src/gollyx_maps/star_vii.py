import json
import os
import random
from .geom import hflip_pattern, vflip_pattern, rot_pattern
from .utils import pattern2url, retry_on_failure, pattern2url_char, pattern2url_chars
from .patterns import get_grid_empty, pattern_union, get_pattern, get_grid_pattern
from .error import GollyXGeomError
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
    """Returns a map of names to pattern generation functions."""
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
        "midnightexpress": midnightexpress,
        "spaceelevator": spaceelevator,
        #"ironhorse": ironhorse,
        #"faradaycage": faradaycage,
        #"deadendterminal": deadendterminal,
        #"bando": bando,
        #"ghosttrain": ghosttrain,
    }


def _points_to_url(points, rows, cols, char='o'):
    """Converts a set of points to a URL-encoded character string."""
    grid = get_grid_empty(rows, cols, flat=False)
    for x, y in points:
        if 0 <= y < rows and 0 <= x < cols:
            grid[y][x] = char
    grid_flat = ["".join(row) for row in grid]
    return pattern2url_char(grid_flat, char)

def _apply_random_transformation(points_set):
    """
    Applies a random transformation (hflip, vflip, or rotation) to a set of (x,y) points.
    Returns the new set of points.
    """
    if not points_set:
        return set()

    # Determine bounding box of the pattern
    min_x = min(p[0] for p in points_set)
    max_x = max(p[0] for p in points_set)
    min_y = min(p[1] for p in points_set)
    max_y = max(p[1] for p in points_set)

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    # Convert points to a grid (list of strings)
    pattern_grid = [['.' for _ in range(width)] for _ in range(height)]
    for x, y in points_set:
        pattern_grid[y - min_y][x - min_x] = 'o'

    pattern_list_str = ["".join(row) for row in pattern_grid]

    # Choose a random transformation
    transformation_choice = random.choice(['none', 'hflip', 'vflip', 'rot90', 'rot180', 'rot270'])

    transformed_pattern_list_str = pattern_list_str
    
    if transformation_choice == 'hflip':
        transformed_pattern_list_str = hflip_pattern(transformed_pattern_list_str)
    elif transformation_choice == 'vflip':
        transformed_pattern_list_str = vflip_pattern(transformed_pattern_list_str)
    elif transformation_choice == 'rot90':
        transformed_pattern_list_str = rot_pattern(transformed_pattern_list_str, 90)
    elif transformation_choice == 'rot180':
        transformed_pattern_list_str = rot_pattern(transformed_pattern_list_str, 180)
    elif transformation_choice == 'rot270':
        transformed_pattern_list_str = rot_pattern(transformed_pattern_list_str, 270)
    elif transformation_choice == 'none':
        pass # No transformation applied
    
    # Convert back to points, adjusting for new dimensions if rotated
    new_points_set = set()
    new_height = len(transformed_pattern_list_str)
    new_width = len(transformed_pattern_list_str[0]) if new_height > 0 else 0

    for r_idx, row_str in enumerate(transformed_pattern_list_str):
        for c_idx, char in enumerate(row_str):
            if char == 'o':
                # The new points are relative to their own new bounding box,
                # which effectively starts at (0,0).
                new_points_set.add((c_idx, r_idx))
    
    return new_points_set

def _flood_fill_check(current_path_tiles, rows_grid, cols_grid, x_min, x_max, y_min, y_max):
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
        if x_min <= r < x_max and y_min <= c < y_max: # Ensure path tiles are within the relevant bounds
            grid[c][r] = 1 # Mark path tiles as obstacles

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
                    if 0 <= nr < rows_grid and 0 <= nc < cols_grid and \
                        grid[nr][nc] == 0 and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        q.append((nr, nc))

    # After flood fill, check if any empty cell within the relevant search area is unvisited
    for r in range(rows_grid):
        for c in range(cols_grid):
            if grid[r][c] == 0 and (r,c) not in visited:
                # An empty cell within bounds was not visited, implying it's enclosed
                return True # Loop detected
    return False # No loop detected


def _count_empty_neighbors(tx, ty, current_path, x_tile_min, x_tile_max, y_tile_min, y_tile_max):
    """
    Counts the number of empty neighboring tiles around a specific tile.

    This includes diagonals and is used to calculate an "openness" score,
    preferring paths that lead to less constrained areas.
    """
    count = 0
    # Include diagonals for openness
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        nx, ny = tx + dx, ty + dy
        if x_tile_min <= nx < x_tile_max and y_tile_min <= ny < y_tile_max and (nx, ny) not in current_path:
            count += 1
    return count


def _is_valid_tile_step(tx, ty, is_horizontal_step, current_path_tiles, x_tile_min, x_tile_max, y_tile_min, y_tile_max):
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
        if (y_tile_min <= neighbor1[1] < y_tile_max and neighbor1 in current_path_tiles) or \
            (y_tile_min <= neighbor2[1] < y_tile_max and neighbor2 in current_path_tiles):
            return False
    else: # is_vertical_step
        if not (y_tile_min <= ty < y_tile_max and (tx, ty) not in current_path_tiles):
            return False
        # Check for adjacent path segments (prevents U-turns and parallel tracks)
        neighbor1 = (tx - 1, ty)
        neighbor2 = (tx + 1, ty)
        if (x_tile_min <= neighbor1[0] < x_tile_max and neighbor1 in current_path_tiles) or \
            (x_tile_min <= neighbor2[0] < x_tile_max and neighbor2 in current_path_tiles):
            return False
    return True


def get_segment_props(
    max_len, is_horizontal, current_tile_x, current_tile_y, path_of_tiles,
    last_direction_x, last_direction_y, grid_tile_rows, grid_tile_cols,
    x_tile_min, x_tile_max, y_tile_min, y_tile_max
):
    """Calculates the valid length and direction of a segment."""
    possible_directions = []
    if is_horizontal:
        if last_direction_x != -1: possible_directions.append(1)
        if last_direction_x != 1: possible_directions.append(-1)
    else: # is_vertical
        if last_direction_y != -1: possible_directions.append(1)
        if last_direction_y != 1: possible_directions.append(-1)

    if not possible_directions: possible_directions = [1, -1]

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
                current_proposed_tile[0], current_proposed_tile[1], is_horizontal, path_of_tiles,
                x_tile_min, x_tile_max, y_tile_min, y_tile_max
            ):
                break
            segment_tiles.append(current_proposed_tile)
        final_length = len(segment_tiles)

        if final_length > 0:
            temporary_path = path_of_tiles.union(set(segment_tiles))
            if _flood_fill_check(
                temporary_path, grid_tile_rows, grid_tile_cols,
                x_tile_min, x_tile_max, y_tile_min, y_tile_max
            ):
                continue # This segment creates a loop, discard it

            end_tile_x = segment_tiles[-1][0] if is_horizontal else current_tile_x
            end_tile_y = segment_tiles[-1][1] if not is_horizontal else current_tile_y

            openness_score = _count_empty_neighbors(
                end_tile_x, end_tile_y, temporary_path,
                x_tile_min, x_tile_max, y_tile_min, y_tile_max
            )
            evaluated_options.append((final_length, openness_score, direction_to_try, segment_tiles))

    if not evaluated_options:
        return 0, 0, [] # No valid move found

    evaluated_options.sort(key=lambda x: (x[0], x[1]), reverse=True)

    best_length = evaluated_options[0][0]
    best_openness = evaluated_options[0][1]
    top_options = [opt for opt in evaluated_options if opt[0] == best_length and opt[1] == best_openness]

    selected_option = random.choice(top_options)
    return selected_option[0], selected_option[2], selected_option[3]


def choochoo(rows, cols, seed=None, turns=9):
    """
    Generates a final, correct, expansive, and resilient "railroad track"
    of stars, preventing loops and U-turns.
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

    if x_tile_min >= x_tile_max or y_tile_min >= y_tile_max:
        return "23", "3", "{}", "[]", "[]", "[]"

    current_tile_x = random.randint(x_tile_min, x_tile_max - 1)
    current_tile_y = random.randint(y_tile_min, y_tile_max - 1)
    path_of_tiles.add((current_tile_x, current_tile_y))

    # Calculate average segment length
    num_h_segments = (turns + 1) // 2
    num_v_segments = (turns + 1) - num_h_segments
    avg_len_x = ((x_tile_max - x_tile_min) / (num_h_segments + 1)) if num_h_segments > 0 else 0
    avg_len_y = ((y_tile_max - y_tile_min) / (num_v_segments + 1)) if num_v_segments > 0 else 0

    last_move_was_horizontal = random.choice([True, False])
    last_direction_x = 0
    last_direction_y = 0

    for _ in range(turns + 1):
        segment_generated = False
        
        # Define the primary and secondary attempts based on the last move
        if last_move_was_horizontal:
            # Last was horizontal, so try vertical first
            primary_attempt = {'is_horizontal': False, 'avg_len': avg_len_y}
            secondary_attempt = {'is_horizontal': True, 'avg_len': avg_len_x}
        else:
            # Last was vertical, so try horizontal first
            primary_attempt = {'is_horizontal': True, 'avg_len': avg_len_x}
            secondary_attempt = {'is_horizontal': False, 'avg_len': avg_len_y}

        for attempt in [primary_attempt, secondary_attempt]:
            max_len = max(1, int(random.uniform(0.7, 1.3) * attempt['avg_len']))
            actual_length, direction, segment_tiles = get_segment_props(
                max_len, attempt['is_horizontal'], current_tile_x, current_tile_y, path_of_tiles,
                last_direction_x, last_direction_y, grid_tile_rows, grid_tile_cols,
                x_tile_min, x_tile_max, y_tile_min, y_tile_max
            )

            if actual_length > 0:
                path_of_tiles.update(segment_tiles)
                if attempt['is_horizontal']:
                    current_tile_x = segment_tiles[-1][0]
                    last_direction_x = direction
                    last_direction_y = 0
                else:
                    current_tile_y = segment_tiles[-1][1]
                    last_direction_x = 0
                    last_direction_y = direction
                last_move_was_horizontal = attempt['is_horizontal']
                segment_generated = True
                break  # A segment was successfully generated, move to the next turn

        if not segment_generated:
            break  # No valid segment could be generated

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
    pattern_rows = [
        "".join("o" if (x_coord, y_coord) in points else "." for x_coord in range(cols))
        for y_coord in range(rows)
    ]

    s1, b1, c1 = pattern2url_chars(pattern_rows)
    s2, b2, c2 = "[]", "[]", "[]"

    return s1, b1, c1, s2, b2, c2


def midnightexpress(rows, cols, seed=None):
    """
    Creates two parallel tracks of stars with Methuselah patterns scattered
    between them, resembling a "midnight express" train scenario.
    """
    if seed is not None:
        random.seed(seed)

    # 1. Load ONE methuselah pattern to be used for all placements

    methuselah_names_numbers = [
        #("escapingsatellites",  (2, 4)),
        ("solarsail",  (1, 2)),
        #("scaffoldunfusing",    (1, 2)),
        #("backedupsink",        (1, 4)),
        #("spaceship2platform",  (1, 2)),
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
            p1 = (i + dx, track1_coord + dy) if is_horizontal_tracks else (track1_coord + dx, i + dy)
            team1_points.add(p1)
            # Point for track 2
            p2 = (i + dx, track2_coord + dy) if is_horizontal_tracks else (track2_coord + dx, i + dy)
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
    if meth_pattern_str and methuselah_bbox_min_x <= methuselah_bbox_max_x and \
       methuselah_bbox_min_y <= methuselah_bbox_max_y:

        meth_initial_relative_points = set()
        if meth_height > 0 and meth_width > 0:
            for r_idx, row_str in enumerate(meth_pattern_str):
                for c_idx, char in enumerate(row_str):
                    if char == 'o':
                        meth_initial_relative_points.add((c_idx, r_idx))

        if meth_initial_relative_points and \
           methuselah_bbox_min_x <= methuselah_bbox_max_x and \
           methuselah_bbox_min_y <= methuselah_bbox_max_y:

            num_methuselahs_per_team = random.randint(*chosen_meth_number)
            meth_to_place = [{'team': 1} for _ in range(num_methuselahs_per_team)] + \
                              [{'team': 2} for _ in range(num_methuselahs_per_team)]
            random.shuffle(meth_to_place)

            all_occupied_points = team1_points.copy()
            all_occupied_points.update(team2_points)

            for meth_info in meth_to_place:
                # Apply random transformation to the current methuselah instance
                transformed_meth_points_relative = _apply_random_transformation(meth_initial_relative_points)

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
                    continue # Skip if transformation resulted in an empty pattern (shouldn't happen with current transformations, but for robustness)

                # Define placement area for this specific transformed methuselah
                placement_min_x = methuselah_bbox_min_x
                placement_max_x = methuselah_bbox_max_x - current_meth_width + 1
                placement_min_y = methuselah_bbox_min_y
                placement_max_y = methuselah_bbox_max_y - current_meth_height + 1

                if placement_max_x < placement_min_x or placement_max_y < placement_min_y:
                    continue # No valid placement area for this transformed methuselah

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
                        if meth_info['team'] == 1:
                            team1_points.update(current_meth_absolute_points)
                        else:
                            team2_points.update(current_meth_absolute_points)
                        all_occupied_points.update(current_meth_absolute_points)
                        placed = True
                    attempts += 1

    # 4. Convert team points to URL format
    s1_output = _points_to_url(team1_points, rows, cols)
    s2_output = _points_to_url(team2_points, rows, cols)

    return s1_output, "[]", "[]", s2_output, "[]", "[]"


def spaceelevator(rows, cols, seed=None):
    """
    Creates a "space elevator" track of stars across the grid,
    with two adjacent Methuselah cells poised to interact with it.
    """
    if seed is not None:
        random.seed(seed)

    team1_points = set()
    team2_points = set()

    star_shape = {(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)} # 5-cell star stamp
    spacing = 3 # Spacing between star centers along the track, ensuring no overlap

    # 1. Determine track orientation and split the grid
    is_horizontal_split = False # Tracks are always vertical

    # Calculate jitter once, applied symmetrically to both tracks
    jitter_amount_rows = int(0.1 * rows * (random.random() * 2 - 1))
    jitter_amount_cols = int(0.1 * cols * (random.random() * 2 - 1))

    # Generate Track 1 (for team1_points)
    if is_horizontal_split:
        # Top half of the grid
        half_rows = rows // 2
        mid_row_half = half_rows // 2
        track1_row_center = max(1, min(rows - 2, mid_row_half + jitter_amount_rows)) # Ensure star fits
        for x_center in range(1, cols - 1, spacing):
            for dx, dy in star_shape:
                team1_points.add((x_center + dx, track1_row_center + dy))
    else: # Vertical split, left half of the grid
        half_cols = cols // 2
        mid_col_half = half_cols // 2
        track1_col_center = max(1, min(cols - 2, mid_col_half + jitter_amount_cols)) # Ensure star fits
        for y_center in range(1, rows - 1, spacing):
            for dx, dy in star_shape:
                team1_points.add((track1_col_center + dx, y_center + dy))

    # Generate Track 2 (for team2_points)
    if is_horizontal_split:
        # Bottom half of the grid
        half_rows = rows // 2
        mid_row_half = rows // 2 + half_rows // 2
        track2_row_center = max(1, min(rows - 2, mid_row_half + jitter_amount_rows)) # Ensure star fits
        for x_center in range(1, cols - 1, spacing):
            for dx, dy in star_shape:
                team2_points.add((x_center + dx, track2_row_center + dy))
    else: # Vertical split, right half of the grid
        half_cols = cols // 2
        mid_col_half = cols // 2 + half_cols // 2
        track2_col_center = max(1, min(cols - 2, mid_col_half + jitter_amount_cols)) # Ensure star fits
        for y_center in range(1, rows - 1, spacing):
            for dx, dy in star_shape:
                team2_points.add((track2_col_center + dx, y_center + dy))

    # Helper function to place a two-cell shape
    def place_two_cell_shape(all_occupied_points_so_far):
        while True:
            start_x = random.randint(0, cols - 1)
            start_y = random.randint(0, rows - 1)
            
            is_horizontal_shape = random.choice([True, False])

            if is_horizontal_shape:
                if start_x + 1 >= cols:
                    continue
                cell1 = (start_x, start_y)
                cell2 = (start_x + 1, start_y)
            else: # Vertical shape
                if start_y + 1 >= rows:
                    continue
                cell1 = (start_x, start_y)
                cell2 = (start_x, start_y + 1)
            
            if cell1 not in all_occupied_points_so_far and cell2 not in all_occupied_points_so_far:
                return {cell1, cell2}

    # Gather all points already occupied by tracks for overlap checking
    all_occupied_initial = team1_points.union(team2_points)

    # 2. Put one two-cell "oo" shape for color 1 (add to team1_points)
    shape1_cells = place_two_cell_shape(all_occupied_initial)
    team1_points.update(shape1_cells)
    all_occupied_initial.update(shape1_cells) # Update occupied points for next check

    # 3. Put one two-cell "oo" shape for color 2 (add to team2_points)
    shape2_cells = place_two_cell_shape(all_occupied_initial) 
    team2_points.update(shape2_cells)

    # Convert to URL format
    s1_output = _points_to_url(team1_points, rows, cols)
    s2_output = _points_to_url(team2_points, rows, cols)
    
    return s1_output, "[]", "[]", s2_output, "[]", "[]"


def ironhorse(rows, cols, seed=None):
    pass


def faradaycage(rows, cols, seed=None):
    pass


def deadendterminal(rows, cols, seed=None):
    pass


def bando(rows, cols, seed=None):
    pass


def ghosttrain(rows, cols, seed=None):
    pass
