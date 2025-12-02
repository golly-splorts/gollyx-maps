import random
from gollyx_maps.patterns import get_grid_pattern, get_pattern, get_pattern_size
from gollyx_maps.utils import pattern2url

"""
WIP: two color gosper gun

one_gun creates a gosper gun where the two side squares are one color, the stuff in the middle (and gliders created) are another.

two_gun creates two versions of the two-color gosper gun, at the same y value and offset a bit from the center x.

the resulting matches take a really long time for the strings of gliders 
to cross the board, let alone do anything (50/50 on that).
needs methuselahs in the corners, tbh.
"""

def one_gun(reverse):

    # Define grid dimensions
    ROWS = 150
    COLS = 250

    # Get the raw pattern to determine its dimensions
    pattern_height, pattern_width = get_pattern_size("gosper_gun")

    # Place the Gosper glider gun in the center of the grid.
    # The script was calculating top-left offsets, but the library's
    # get_grid_pattern function expects center-based offsets.
    # We now calculate the correct center-based offsets to ensure the
    # pattern is placed where the script expects it to be.
    x_offset = (COLS - pattern_width) // 2
    y_offset = (ROWS - pattern_height) // 2
    
    x_center_arg = x_offset + (pattern_width // 2)
    y_center_arg = y_offset + (pattern_height // 2)

    base_pattern = get_grid_pattern("gosper_gun", ROWS, COLS, xoffset=x_center_arg, yoffset=y_center_arg)

    # Find all the alive cells in the pattern
    alive_cells = []
    for r, row_str in enumerate(base_pattern):
        for c, cell in enumerate(row_str):
            if cell == 'o':
                alive_cells.append((r, c))

    # The two 2x2 squares in the Gosper glider gun pattern, with (row, col)
    # coordinates relative to the pattern's top-left corner.
    square1_relative_rc = [(4, 0), (4, 1), (5, 0), (5, 1)]
    square2_relative_rc = [(2, 34), (2, 35), (3, 34), (3, 35)]
    squares_relative_rc = square1_relative_rc + square2_relative_rc

    # Calculate the absolute coordinates of the squares' cells on the grid
    squares_absolute_rc = set()
    for r_rel, c_rel in squares_relative_rc:
        squares_absolute_rc.add((r_rel + y_offset, c_rel + x_offset))

    # Split the alive cells into two teams: the squares, and the cells in between.
    team1_cells = []  # The squares
    team2_cells = []  # The "cells in between"
    for r, c in alive_cells:
        if (r, c) in squares_absolute_rc:
            team1_cells.append((r, c))
        else:
            team2_cells.append((r, c))

    # Create separate grid patterns for each team
    team1_grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]
    team2_grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]

    for r, c in team1_cells:
        team1_grid[r][c] = 'o'

    for r, c in team2_cells:
        team2_grid[r][c] = 'o'

    # Convert the character grids to a list of strings
    team1_pattern = ["".join(row) for row in team1_grid]
    team2_pattern = ["".join(row) for row in team2_grid]

    # Convert the patterns to URL-compatible strings
    if reverse:
        s2 = pattern2url(team1_pattern)
        s1 = pattern2url(team2_pattern)
    else:
        s1 = pattern2url(team1_pattern)
        s2 = pattern2url(team2_pattern)

    # Construct the final URL
    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"

    # Print the resulting URL
    print(url)


def two_guns(reverse):

    # Define grid dimensions
    ROWS = 150
    COLS = 250

    # Get the raw pattern to determine its dimensions
    pattern_height, pattern_width = get_pattern_size("gosper_gun")

    # Center y-offset is same for both guns
    y_offset = (ROWS - pattern_height) // 2
    y_center_arg = y_offset + (pattern_height // 2)

    # --- Gun 1 (left) ---
    # The right edge of the left pattern should be at (COLS // 2) - 10.
    # So, its center will be at ((COLS // 2) - 10) - (pattern_width // 2).
    x_center_arg1 = (COLS // 2) - random.randint(8,30) - (pattern_width // 2)
    base_pattern1 = get_grid_pattern("gosper_gun", ROWS, COLS, xoffset=x_center_arg1, yoffset=y_center_arg)

    # top-left offset for gun 1
    x_offset1 = x_center_arg1 - (pattern_width // 2)
    
    # Find all the alive cells in pattern 1
    alive_cells1 = []
    for r, row_str in enumerate(base_pattern1):
        for c, cell in enumerate(row_str):
            if cell == 'o':
                alive_cells1.append((r, c))

    # --- Gun 2 (right) ---
    # The left edge of the right pattern should be at (COLS // 2) + 10.
    # So, its center will be at ((COLS // 2) + 10) + (pattern_width // 2).
    x_center_arg2 = (COLS // 2) + random.randint(8,30) + (pattern_width // 2)
    base_pattern2 = get_grid_pattern("gosper_gun", ROWS, COLS, xoffset=x_center_arg2, yoffset=y_center_arg)
    
    # top-left offset for gun 2
    x_offset2 = x_center_arg2 - (pattern_width // 2)

    # Find all the alive cells in pattern 2
    alive_cells2 = []
    for r, row_str in enumerate(base_pattern2):
        for c, cell in enumerate(row_str):
            if cell == 'o':
                alive_cells2.append((r, c))

    # The two 2x2 squares in the Gosper glider gun pattern, with (row, col)
    # coordinates relative to the pattern's top-left corner.
    square1_relative_rc = [(4, 0), (4, 1), (5, 0), (5, 1)]
    square2_relative_rc = [(2, 34), (2, 35), (3, 34), (3, 35)]
    squares_relative_rc = square1_relative_rc + square2_relative_rc

    # --- Gun 1 cell separation ---
    squares_absolute_rc1 = set()
    for r_rel, c_rel in squares_relative_rc:
        squares_absolute_rc1.add((r_rel + y_offset, c_rel + x_offset1))

    gun1_team1_cells = []  # The squares
    gun1_team2_cells = []  # The "cells in between"
    for r, c in alive_cells1:
        if (r, c) in squares_absolute_rc1:
            gun1_team1_cells.append((r, c))
        else:
            gun1_team2_cells.append((r, c))

    # --- Gun 2 cell separation ---
    squares_absolute_rc2 = set()
    for r_rel, c_rel in squares_relative_rc:
        squares_absolute_rc2.add((r_rel + y_offset, c_rel + x_offset2))

    gun2_team1_cells = []  # The squares
    gun2_team2_cells = []  # The "cells in between"
    for r, c in alive_cells2:
        if (r, c) in squares_absolute_rc2:
            gun2_team1_cells.append((r, c))
        else:
            gun2_team2_cells.append((r, c))
    
    # --- Combine cells into final teams ---
    # Gun 1: squares are team 1, other are team 2
    # Gun 2: squares are team 2, other are team 1 (inverted)
    team1_cells = gun1_team1_cells + gun2_team2_cells
    team2_cells = gun1_team2_cells + gun2_team1_cells

    # Create separate grid patterns for each team
    team1_grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]
    team2_grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]

    for r, c in team1_cells:
        team1_grid[r][c] = 'o'

    for r, c in team2_cells:
        team2_grid[r][c] = 'o'

    # Convert the character grids to a list of strings
    team1_pattern = ["".join(row) for row in team1_grid]
    team2_pattern = ["".join(row) for row in team2_grid]

    # Convert the patterns to URL-compatible strings
    if reverse:
        s2 = pattern2url(team1_pattern)
        s1 = pattern2url(team2_pattern)
    else:
        s1 = pattern2url(team1_pattern)
        s2 = pattern2url(team2_pattern)

    # Construct the final URL
    url = f"http://localhost:8000/simulator/index.html?s1={s1}&s2={s2}"

    # Print the resulting URL
    print(url)


if __name__ == "__main__":
    one_gun(False)
    two_guns(True)

