def hflip_pattern(pattern):
    """Flip a pattern horizontally"""
    newpattern = ["".join(reversed(j)) for j in pattern]
    return newpattern


def vflip_pattern(pattern):
    """Flip a pattern vertically"""
    newpattern = [j for j in reversed(pattern)]
    return newpattern


def rot_pattern(pattern, deg):
    """Rotate a pattern 90, 180, or 270 degrees"""
    newpattern = pattern[:]
    if deg in [90, 180, 270]:
        for i in range(deg//90):
            newpattern_tup = zip(*list(reversed(newpattern)))
            newpattern = ["".join(j) for j in newpattern_tup]
    return newpattern
