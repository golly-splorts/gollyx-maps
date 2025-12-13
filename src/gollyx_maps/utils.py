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


def points_to_url(points, rows, cols, char="o"):
    """Converts a set of points to a URL-encoded character string."""
    grid = get_grid_empty(rows, cols, flat=False)
    for x, y in points:
        if 0 <= y < rows and 0 <= x < cols:
            grid[y][x] = char
    grid_flat = ["".join(row) for row in grid]
    return pattern2url_char(grid_flat, char)

