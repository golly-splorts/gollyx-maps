import re
from .patterns import get_pattern


def pattern2url(pattern, xoffset=0, yoffset=0):
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
