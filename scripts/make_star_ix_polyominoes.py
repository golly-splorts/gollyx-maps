"""
Generate src/gollyx_maps/data/star_ix_polyominoes.json: the free polyominoes of 7 to 10
cells that take off when played alone under the Star Wars rule (B2/S345/C4).

A shape takes off if it has more than 60 live cells at some point in generations 301 to
400 on a 160x160 board. Run from the repo root with gollyx-python installed:

    python scripts/make_star_ix_polyominoes.py
"""
import json
import os
from concurrent.futures import ProcessPoolExecutor

from gollyx_python import StarGOL

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(REPO_ROOT, "src", "gollyx_maps", "data", "star_ix_polyominoes.json")
SIZE = 160
GENERATIONS = 400


def normalize(cells):
    """
    Args:
        cells (iterable of (int, int)): polyomino cells.

    Returns:
        tuple: the cells moved to the origin and sorted.
    """
    mx, my = min(x for x, _ in cells), min(y for _, y in cells)
    return tuple(sorted((x - mx, y - my) for x, y in cells))


def canonical(cells):
    """
    Args:
        cells (iterable of (int, int)): polyomino cells.

    Returns:
        tuple: the same tuple for every rotation and reflection of a polyomino.
    """
    forms = []
    for _ in range(4):
        cells = [(y, -x) for x, y in cells]
        forms += [normalize(cells), normalize([(-x, y) for x, y in cells])]
    return min(forms)


def polyominoes(smallest, largest):
    """
    Args:
        smallest (int): fewest cells.
        largest (int): most cells.

    Returns:
        list of tuple: every free polyomino with that many cells.
    """
    found = []
    level = {canonical([(0, 0)])}
    for n in range(1, largest + 1):
        if n >= smallest:
            found += sorted(level)
        level = {
            canonical(p + ((x + dx, y + dy),))
            for p in level
            for x, y in p
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if (x + dx, y + dy) not in p
        }
    return found


def takes_off(cells):
    """
    Args:
        cells (tuple): polyomino cells.

    Returns:
        bool: True if the shape is still busy after 300 generations.
    """
    rows = {}
    for x, y in cells:
        rows.setdefault(SIZE // 2 + y, []).append(SIZE // 2 + x)
    gol = StarGOL(s1=[{str(y): xs} for y, xs in rows.items()], s2=[], rows=SIZE, columns=SIZE,
                  rule_b=[2], rule_s=[3, 4, 5], rule_c=4)
    gol.halt = False
    for generation in range(1, GENERATIONS + 1):
        live = gol.next_step()["liveCells"]
        if generation > 300 and live > 60:
            return True
    return False


def to_text(cells):
    """
    Args:
        cells (tuple): polyomino cells.

    Returns:
        str: rows of 'o' and '.' joined with '/'.
    """
    w, h = max(x for x, _ in cells) + 1, max(y for _, y in cells) + 1
    return "/".join("".join("o" if (x, y) in cells else "." for x in range(w)) for y in range(h))


def main():
    shapes = polyominoes(7, 10)
    with ProcessPoolExecutor() as pool:
        keep = [s for s, ok in zip(shapes, pool.map(takes_off, shapes, chunksize=20)) if ok]
    with open(DATA_FILE, "w") as f:
        json.dump([to_text(s) for s in keep], f, indent=0)
        f.write("\n")
    print(f"Wrote {len(keep)} of {len(shapes)} polyominoes to {DATA_FILE}")


if __name__ == "__main__":
    main()
