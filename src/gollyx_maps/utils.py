import re
from .patterns import get_pattern, get_grid_empty
from .error import GollyXMapsError, GollyXPatternsError


def pattern2url(pattern, xoffset=0, yoffset=0):
    """
    Takes a pattern (list of lists, outer list is rows, inner list is characters)
    and returns a URL representation of it.

    This DOES NOT handle star dead-but-waiting states.

    Example input:
        [ [ '.', '.', 'o', '.'],
          [ '.', '.', '.', 'o'],
          [ '.', 'o', 'o', 'o'] ]

    Example output:
        [{"0":[2],"1":[3],"2":[1,2,3]}]
    """
    return pattern2url_char(pattern, "o", xoffset=xoffset, yoffset=yoffset)


def pattern2url_chars(pattern, xoffset=0, yoffset=0):
    """
    Takes a pattern (list of lists, outer list is rows, inner list is characters)
    and returns a URL representation of it for a given character.

    This correctly handles star dead-but-waiting states.
    """
    s_url = pattern2url_char(pattern, "o", xoffset=xoffset, yoffset=yoffset)
    b_url = pattern2url_char(pattern, "b", xoffset=xoffset, yoffset=yoffset)
    c_url = pattern2url_char(pattern, "c", xoffset=xoffset, yoffset=yoffset)
    return (s_url, b_url, c_url)


def pattern2url_char(pattern, char, xoffset=0, yoffset=0):
    """
    Takes a pattern (list of lists, outer list is rows, inner list is characters)
    and returns a URL representation of it for a given character.

    This correctly handles star dead-but-waiting states (specified by char).
    """
    rows = len(pattern)
    if rows == 0:
        return "[]"
    cols = len(pattern[0])
    listLife = []
    for i in range(rows):
        listLifeRow = {}
        for j in range(cols):
            if pattern[i][j] == char:
                y = str(i + yoffset)
                x = j + xoffset
                if y in listLifeRow.keys():
                    listLifeRow[y].append(x)
                else:
                    listLifeRow[y] = [x]
        if len(listLifeRow.keys()) > 0:
            listLife.append(listLifeRow)

    # Convert list of dicts to string using Python built-in repr func, trim spaces/quotes
    s = str(listLife)
    s = s.split(" ")
    listLife = "".join(s)
    listLife = re.sub("'", '"', listLife)
    return listLife


def retry_on_failure(func, *args, **kwargs):
    """
    Function wrapper to retry a function 10 times before giving up
    """
    def wrap(*args, **kwargs):
        done = False
        maxcount = 10
        count = 0
        while not done and count < maxcount:
            try:
                return func(*args, **kwargs)
            except GollyXPatternsError:
                count += 1
                continue
        raise GollyXMapsError(f"Error: retry failure for function {func.__name__}, tried {maxcount} times!")

    return wrap


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
            else transformed_pattern_list_str
        )
        pattern_list_str = (
            vflip_pattern(pattern_list_str)
            if random.getrandbits(1)
            else transformed_pattern_list_str
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


def points_to_url(points, rows, cols, char="o"):
    """Converts a set of points to a URL-encoded character string."""
    grid = get_grid_empty(rows, cols, flat=False)
    for x, y in points:
        if 0 <= y < rows and 0 <= x < cols:
            grid[y][x] = char
    grid_flat = ["".join(row) for row in grid]
    return pattern2url_char(grid_flat, char)

