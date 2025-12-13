import random


def hflip_pattern(pattern):
    """Flip a pattern horizontally"""
    newpattern = ["".join(reversed(j)) for j in pattern]
    return newpattern


def vflip_pattern(pattern):
    """Flip a pattern vertically"""
    newpattern = [j for j in reversed(pattern)]
    return newpattern


def rot_pattern(pattern, deg):
    """Rotate a pattern 0, 90, 180, 270, or 360 degrees"""
    newpattern = pattern[:]
    valid_deg = [0, 90, 180, 270, 360]
    if deg in valid_deg:
        for i in range(deg//90):
            newpattern_tup = zip(*list(reversed(newpattern)))
            newpattern = ["".join(j) for j in newpattern_tup]
    else:
        raise GollyXGeomError(f"Invalid degree specified, must be one of: {', '.join(valid_deg)}")
    return newpattern


def vjiggle(pattern_rows, ncells: int):
    r = 0
    while r == 0:
        r = random.randint(-ncells, ncells)
    new_pattern_rows = pattern_rows[r:] + pattern_rows[:r]
    return new_pattern_rows


def hjiggle(pattern_rows, ncells: int):
    c = 0
    while c == 0:
        c = random.randint(-ncells, ncells)
    new_pattern_rows = []
    for i in range(len(pattern_rows)):
        new_pattern_rows.append(pattern_rows[i][c:] + pattern_rows[i][:c])
    return new_pattern_rows


def apply_random_transformation(points_set):
    """
    Applies a random transformation (hflip, vflip, or rotation) to a set of (x,y) points.
    Returns the new set of points.
    Does NOT handle dead-but-waiting states.
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
    pattern_grid = [["." for _ in range(width)] for _ in range(height)]
    for x, y in points_set:
        pattern_grid[y - min_y][x - min_x] = "o"

    pattern_list_str = ["".join(row) for row in pattern_grid]

    if random.getrandbits(1):
        # Random hflip/vflip
        pattern_list_str = (
            hflip_pattern(pattern_list_str)
            if random.getrandbits(1)
            else pattern_list_str
        )
        pattern_list_str = (
            vflip_pattern(pattern_list_str)
            if random.getrandbits(1)
            else pattern_list_str
        )
    else:
        # Random rotation
        a = random.choice([0, 90, 180, 270])
        pattern_list_str = rot_pattern(pattern_list_str, a)

    # Convert back to points, adjusting for new dimensions if rotated
    new_points_set = set()
    new_height = len(pattern_list_str)
    new_width = len(pattern_list_str[0])

    for r_idx, row_str in enumerate(pattern_list_str):
        for c_idx, char in enumerate(row_str):
            if char == "o":
                new_points_set.add((c_idx, r_idx))

    return new_points_set


