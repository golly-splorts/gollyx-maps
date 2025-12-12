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

    def flood_fill_check(current_path_tiles, rows_grid, cols_grid, x_min, x_max, y_min, y_max):
        # Create a grid representation
        grid = [[0 for _ in range(cols_grid)] for _ in range(rows_grid)]
        for r, c in current_path_tiles:
            if x_min <= r < x_max and y_min <= c < y_max: # Ensure path tiles are within the relevant bounds
                grid[c][r] = 1 # Mark path tiles as obstacles

        # Find an "outside" starting point for flood fill
        # This is tricky because the path might span the entire width/height.
        # A simple approach is to check corners or edges.
        # For now, let's assume (0,0) is always outside, if not a path tile.
        # A more robust check would involve iterating all cells and doing a fill from each unvisited empty cell
        # and checking if a visited component is completely enclosed.

        # For simplicity, we'll try to flood fill from all four corners
        # and then check if any empty cells within the search area (x_min, x_max, y_min, y_max)
        # remain unvisited.

        visited = set()
        q = []

        # Start flood fills from corners if they are empty
        start_points = []
        if grid[0][0] == 0: start_points.append((0,0))
        if grid[0][cols_grid - 1] == 0: start_points.append((0, cols_grid - 1))
        if grid[rows_grid - 1][0] == 0: start_points.append((rows_grid - 1, 0))
        if grid[rows_grid - 1][cols_grid - 1] == 0: start_points.append((rows_grid - 1, cols_grid - 1))

        # Add points along the boundary that are not part of the path
        for r_idx in range(rows_grid):
            if grid[r_idx][0] == 0: start_points.append((r_idx, 0))
            if grid[r_idx][cols_grid - 1] == 0: start_points.append((r_idx, cols_grid - 1))
        for c_idx in range(cols_grid):
            if grid[0][c_idx] == 0: start_points.append((0, c_idx))
            if grid[rows_grid - 1][c_idx] == 0: start_points.append((rows_grid - 1, c_idx))


        for start_r, start_c in set(start_points): # Use set to avoid duplicates
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

    def get_segment_props(max_len, is_horizontal, current_tile_x, current_tile_y, path_of_tiles, last_direction_x, last_direction_y):
        """Calculates the valid length and direction of a segment."""

        # Re-defining calculate_actual_length to return a list of tiles for the segment
        def calculate_actual_segment_tiles(direction_to_check):
            segment_tiles = []
            for step in range(1, max_len + 1):
                if is_horizontal:
                    next_x = current_tile_x + direction_to_check * step
                    current_proposed_tile = (next_x, current_tile_y)
                    if not (x_tile_min <= next_x < x_tile_max and current_proposed_tile not in path_of_tiles):
                        break

                    neighbor1 = (next_x, current_tile_y - 1)
                    neighbor2 = (next_x, current_tile_y + 1)
                    if (y_tile_min <= neighbor1[1] < y_tile_max and neighbor1 in path_of_tiles) or \
                       (y_tile_min <= neighbor2[1] < y_tile_max and neighbor2 in path_of_tiles):
                        break

                else:  # is_vertical
                    next_y = current_tile_y + direction_to_check * step
                    current_proposed_tile = (current_tile_x, next_y)
                    if not (y_tile_min <= next_y < y_tile_max and current_proposed_tile not in path_of_tiles):
                        break

                    neighbor1 = (current_tile_x - 1, next_y)
                    neighbor2 = (current_tile_x + 1, next_y)
                    if (x_tile_min <= neighbor1[0] < x_tile_max and neighbor1 in path_of_tiles) or \
                       (x_tile_min <= neighbor2[0] < x_tile_max and neighbor2 in path_of_tiles):
                        break
                segment_tiles.append(current_proposed_tile)
            return segment_tiles

        def count_empty_neighbors(tx, ty, current_path):
            count = 0
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]: # Include diagonals for openness
                nx, ny = tx + dx, ty + dy
                if x_tile_min <= nx < x_tile_max and y_tile_min <= ny < y_tile_max and (nx, ny) not in current_path:
                    count += 1
            return count

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
            segment_tiles = calculate_actual_segment_tiles(direction_to_try)
            final_length = len(segment_tiles)

            if final_length > 0:
                # Crucial loop check
                temporary_path = path_of_tiles.union(set(segment_tiles))
                if flood_fill_check(temporary_path, grid_tile_rows, grid_tile_cols, x_tile_min, x_tile_max, y_tile_min, y_tile_max):
                    continue # This segment creates a loop, discard it

                end_tile_x = segment_tiles[-1][0] if is_horizontal else current_tile_x
                end_tile_y = segment_tiles[-1][1] if not is_horizontal else current_tile_y

                openness_score = count_empty_neighbors(end_tile_x, end_tile_y, temporary_path)
                evaluated_options.append((final_length, openness_score, direction_to_try, segment_tiles))

        if not evaluated_options:
            return 0, 0, [] # No valid move found, return empty segment tiles

        evaluated_options.sort(key=lambda x: (x[0], x[1]), reverse=True)

        best_length = evaluated_options[0][0]
        best_openness = evaluated_options[0][1]
        top_options = [opt for opt in evaluated_options if opt[0] == best_length and opt[1] == best_openness]

        selected_option = random.choice(top_options)
        return selected_option[0], selected_option[2], selected_option[3] # Return actual_length, direction, and segment_tiles

    for _ in range(turns + 1):
        segment_generated = False

        if last_move_was_horizontal:  # Make a vertical segment
            max_len = max(1, int(random.uniform(0.7, 1.3) * avg_len_y))
            actual_length, direction, segment_tiles = get_segment_props(max_len, False, current_tile_x, current_tile_y, path_of_tiles, last_direction_x, last_direction_y)

            if actual_length > 0:
                for tile in segment_tiles:
                    path_of_tiles.add(tile)
                current_tile_y = segment_tiles[-1][1]
                last_direction_x = 0
                last_direction_y = direction
                last_move_was_horizontal = False
                segment_generated = True

            else:
                # If vertical move failed, try horizontal
                max_len = max(1, int(random.uniform(0.7, 1.3) * avg_len_x))
                actual_length, direction, segment_tiles = get_segment_props(max_len, True, current_tile_x, current_tile_y, path_of_tiles, last_direction_x, last_direction_y)

                if actual_length > 0:
                    for tile in segment_tiles:
                        path_of_tiles.add(tile)
                    current_tile_x = segment_tiles[-1][0]
                    last_direction_x = direction
                    last_direction_y = 0
                    last_move_was_horizontal = True
                    segment_generated = True

        else:  # Make a horizontal segment
            max_len = max(1, int(random.uniform(0.7, 1.3) * avg_len_x))
            actual_length, direction, segment_tiles = get_segment_props(max_len, True, current_tile_x, current_tile_y, path_of_tiles, last_direction_x, last_direction_y)

            if actual_length > 0:
                for tile in segment_tiles:
                    path_of_tiles.add(tile)
                current_tile_x = segment_tiles[-1][0]
                last_direction_x = direction
                last_direction_y = 0
                last_move_was_horizontal = True
                segment_generated = True
            else:
                # If horizontal move failed, try vertical
                max_len = max(1, int(random.uniform(0.7, 1.3) * avg_len_y))
                actual_length, direction, segment_tiles = get_segment_props(max_len, False, current_tile_x, current_tile_y, path_of_tiles, last_direction_x, last_direction_y)

                if actual_length > 0:
                    for tile in segment_tiles:
                        path_of_tiles.add(tile)
                    current_tile_y = segment_tiles[-1][1]
                    last_direction_x = 0
                    last_direction_y = direction
                    last_move_was_horizontal = False
                    segment_generated = True

        if not segment_generated:
            break # No valid segment could be generated in either orientation, path is stuck

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
