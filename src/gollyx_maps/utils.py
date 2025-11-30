import re
from .patterns import get_pattern
from .error import GollyXMapsError, GollyXPatternsError


def pattern2url(pattern, xoffset=0, yoffset=0):
    """
    Takes a pattern (list of lists, outer list is rows, inner list is characters)
    and returns a URL representation of it.

    Example input:
        [ [ '.', '.', 'o', '.'],
          [ '.', '.', '.', 'o'],
          [ '.', 'o', 'o', 'o'] ]

    Example output:
        [{"0":[2],"1":[3],"2":[1,2,3]}]
    """
    rows = len(pattern)
    cols = len(pattern[0])
    listLife = []
    for i in range(rows):
        listLifeRow = {}
        for j in range(cols):
            if pattern[i][j] == "o":
                y = str(i + yoffset)
                x = j + xoffset
                if y in listLifeRow.keys():
                    listLifeRow[y].append(x)
                else:
                    listLifeRow[y] = [x]
        if len(listLifeRow.keys()) > 0:
            listLife.append(listLifeRow)

    # This is a list of dictionaries.
    # Use the built-in Python representation to convert to string.
    # Trim spaces and fix quotes.
    s = str(listLife)
    s = s.split(" ")
    listLife = "".join(s)
    listLife = re.sub("'", '"', listLife)
    return listLife


def print_pattern_url(
    p1=None,
    p2=None,
    xoff=[0, 0],
    yoff=[0, 0],
    hflip=[False, False],
    vflip=[False, False],
    rot=[0, 0],
):
    url = ""
    for ip, pattern_name in enumerate([p1, p2]):
        if pattern_name is not None:
            pattern = get_pattern(pattern_name)

            if hflip[ip]:
                pattern = [j for j in reversed(pattern)]

            if vflip[ip]:
                pattern = ["".join(reversed(j)) for j in pattern]

            if rot[ip] in [90, 180, 270]:
                for i in range(rot[ip] // 90):
                    pattern_tup = zip(*list(reversed(pattern)))
                    pattern = ["".join(j) for j in pattern_tup]

            listLife = pattern2url(pattern)

            if len(url) > 0:
                url += "&"
            url += f"s{ip+1}={listLife}"
    print(url)


def retry_on_failure(func, *args, **kwargs):
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
