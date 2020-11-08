import os
from geom import (
    hflip_pattern,
    vflip_pattern,
    rot_pattern
)


def get_pattern(pattern_name, hflip=False, vflip=False, rotdeg=0):
    """
    For a given pattern, return the .o diagram
    as a list of strings, one string = one row
    """
    fname = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'patterns',
        pattern_name + '.txt'
    )
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            pattern = f.readlines()
        pattern = [r.strip() for r in pattern]
        if hflip:
            pattern = hflip_pattern(pattern)
        if vflip:
            pattern = vflip_pattern(pattern)
        if rotdeg:
            pattern = rot_pattern(pattern, rotdeg)
        return pattern
    else:
        raise Exception(f"Error: pattern {fname} does not exist!")


def get_pattern_size(pattern_name, **kwargs):
    """
    Returns: (nrows, ncols)
    """
    pattern = get_pattern(pattern_name, **kwargs)
    return (len(pattern), len(pattern[0]))


def get_grid_pattern(pattern_name, rows, columns, xoffset=0, yoffset=0, hflip=False, vflip=False, rotdeg=0):
    # convert list of strings to list of lists (for convenience)
    ogpattern = get_pattern(pattern_name, hflip=hflip, vflip=vflip, rotdeg=rotdeg)
    ogpattern = [list(j) for j in ogpattern]
    blank_row = ["."]*columns
    newpattern = [blank_row[:] for r in range(rows)]
    (pattern_h, pattern_w) = (len(ogpattern), len(ogpattern[0]))

    # given offset is offset for the center of the pattern,
    # so do some algebra to determine where we should start
    xstart = xoffset - pattern_w//2
    xend = xstart + pattern_w
    ystart = yoffset - pattern_h//2
    yend = ystart + pattern_h

    # iterate through the pattern and copy over the cells that are in the final grid
    for iy, y in enumerate(range(ystart, yend)):
        if y > 0 and y < len(newpattern):
            for ix, x in enumerate(range(xstart, xend)):
                if x > 0 and x < len(newpattern[iy]):
                    newpattern[y][x] = ogpattern[iy][ix]
    
    newpattern = ["".join(j) for j in newpattern]
    return newpattern


def pattern_union(patterns):
    for i in range(1, len(patterns)):
        axis0different = len(patterns[i-1]) != len(patterns[i])
        axis1different = len(patterns[i-1][0]) != len(patterns[i][0])
        if axis0different or axis1different:
            err = "Error: cannot perform pattern_union on patterns of dissimilar size"
            err += "\n"
            for i in range(patterns):
                err += "Pattern {i+1}: rows = {len(patterns[i])}, cols = {len(patterns[i][0]}\n"
            raise Exception(err)
    
    # Turn all patterns into lists of lists (for convenience)
    rows = len(patterns[0])
    cols = len(patterns[0][0])
    newpatterns = []
    for pattern in patterns:
        newpatterns.append([list(j) for j in pattern])
    patterns = newpatterns
    blank_row = ["."]*cols
    newpattern = [blank_row[:] for r in range(rows)]
    for iy in range(rows):
        for ix in range(cols):
            alive = False
            for ip, pattern in enumerate(patterns):
                if pattern[iy][ix] == 'o':
                    alive = True
                    break
            if alive:
                newpattern[iy][ix] = 'o'

    newpattern = ["".join(j) for j in newpattern]
    return newpattern

