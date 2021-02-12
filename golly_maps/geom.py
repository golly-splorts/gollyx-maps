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
        raise GollyGeomError(f"Invalid degree specified, must be one of: {', '.join(valid_deg)}")
    return newpattern
