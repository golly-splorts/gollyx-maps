import os
from pprint import pprint
import json


def main():
    patterns = {
        "l_pentomino": '[{"30":[30,31],"31":[30],"32":[30],"33":[30]}]',
        "flower_pentomino": '[{"30":[31],"31":[30,31],"32":[32],"33":[31]}]',
        "kite_heptomino": '[{"30":[30,31],"31":[30],"32":[30,31],"33":[32]}]',
        "boomerang_heptomino": '[{"30":[30],"31":[30,31],"32":[30,31],"33":[33]}]',
        "t_heptomino": '[{"30":[30],"31":[30,31],"32":[30],"33":[31,32]}]',
        "lockpick_heptomino": '[{"30":[30],"31":[30],"32":[30,31,32],"33":[32]}]',
        "facade_heptomino": '[{"30":[30],"31":[30,32,33],"32":[30],"33":[33]}]',
        "raygun_heptomino": '[{"30":[30,32,33],"31":[30,31],"33":[30]}]',
        "broken_l_heptomino": '[{"30":[30],"31":[30],"32":[31,32,33],"33":[30]}]',
        "angel_heptomino": '[{"30":[30,33],"31":[30,31],"32":[32],"33":[31]}]',
        "sticky_heptomino": '[{"30":[30,33],"31":[30],"32":[31,32],"33":[31]}]',
        "reverse_f_heptomino": '[{"30":[30],"31":[31],"32":[30,31,33],"33":[31]}]',
        "swandive_octomino": '[{"30":[30,33],"31":[30],"32":[30,31,32],"33":[32,33]}]',
        "stretchydog_octomino": '[{"30":[30,32],"31":[30,31,33],"32":[30,32],"33":[33]}]',
        "capacitor_octomino": '[{"30":[30],"31":[30,33],"32":[30,31,33],"33":[31,33]}]',
        "brass_knuckles_nonomino": '[{"30":[31,32],"31":[30,31,33],"32":[30,32],"33":[31,32]}]',
        "mcnasty_nonomino": '[{"30":[30,32],"31":[31],"32":[30,31,32,33],"33":[31,32]}]',
        "octomino_oscillator": '[{"30":[30,32],"31":[32,33],"32":[30,31],"33":[31,33]}] ',
    }

    try:
        os.mkdir("output")
    except FileExistsError:
        pass

    for pattern_name, pattern in patterns.items():
        print(f"Exporting pattern {pattern_name}")
        s = convert(pattern)
        fname = pattern_name + ".txt"
        with open(os.path.join("output", fname), "w") as f:
            f.write(s)


def convert(s):

    t = ""

    points = []
    d = json.loads(s)[0]
    for y in d:
        for x in d[y]:
            points.append((x, int(y)))

    minx = min([p[0] for p in points])
    miny = min([p[1] for p in points])

    new_points = []
    for x, y in points:
        new_points.append((x - minx, y - miny))

    maxx = max([p[0] for p in new_points])
    maxy = max([p[1] for p in new_points])

    pattern = []
    for iy in range(maxy + 1):
        row = []
        for ix in range(maxx + 1):
            if (ix, iy) in new_points:
                row.append("o")
            else:
                row.append(".")
        pattern.append(row)

    for row in pattern:
        t += "".join(row)
        t += "\n"

    return t


if __name__ == "__main__":
    main()
