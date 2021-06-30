from .utils import pattern2url
from .patterns import get_grid_empty
import random


ALIVE_DENSITY = 0.5
MIN_STARS = 3
MAX_STARS = 9
MEAN_STREAK_SIZE = 5
MAX_PARTS = 8


##############
# Util Methods


def get_dragon_pattern_function_map():
    return {
        "starfield": starfield,
        "vector": vector,
        "matrix": matrix,
        "lake": lake,
        "waterfall": waterfall,
        "river": river,
        "lighthouse": lighthouse,
        "towers": towers,
        "isotropic": isotropic,
        "supercritical": supercritical,
    }


#############
# Map Methods


def empty_dragon_patterns(cols):
    """
    Return a line of 1D patterns filled with '.' (dead cells).
    Use 'o' to mark alive cells.
    This strips out the empty outer dimension,
    make sure to add it back in by surrounding the pattern
    with [] before you do anything with the pattern.
    """
    # Use [0] to remove the (empty) outer dimension and just get the row of interest
    team1_pattern = get_grid_empty(1, cols, flat=False)[0]
    team2_pattern = get_grid_empty(1, cols, flat=False)[0]
    patterns = [team1_pattern, team2_pattern]
    return patterns


def dragon_pattern_url(patterns):
    pattern1_url = pattern2url([patterns[0]])
    pattern2_url = pattern2url([patterns[1]])
    return pattern1_url, pattern2_url


####################
# Two-Color Patterns


def starfield(cols, nparts, seed=None):
    """
    Starfield: very sparse, one partition.
    This method does not use the nparts command,
    just there for consistent method signature.
    """

    if seed is not None:
        random.seed(seed)

    # Parameters:
    min_stars = MIN_STARS
    max_stars = MAX_STARS
    nstars = random.randint(min_stars, max_stars)

    patterns = empty_dragon_patterns(cols)

    # For each color, for each star, turn on one cell
    for color in range(2):
        for star in range(nstars):
            randloc = random.randint(0, cols - 1)
            while patterns[0][randloc] == "o" or patterns[1][randloc] == "o":
                randloc = random.randint(0, cols - 1)
            patterns[color][randloc] = "o"

    return dragon_pattern_url(patterns)


def waterfall(cols, nparts, seed=None):
    """
    Waterfall: two-color random streaks.
    This method does not use the nparts command,
    just there for consistent method signature.
    """
    if seed is not None:
        random.seed(seed)

    # Parameters:
    mean_size = MEAN_STREAK_SIZE

    patterns = empty_dragon_patterns(cols)

    ip = 0
    alivedeadsymbol = "."
    while ip < cols:

        # Flip the switch
        if alivedeadsymbol == ".":
            alivedeadsymbol = "o"
        elif alivedeadsymbol == "o":
            alivedeadsymbol = "."

        # Generate a new interval length
        interval = round(random.expovariate(1.0 / mean_size))
        if interval == 0:
            interval = 1

        # Loop over the interval, incrementing ip
        # and making cells alive as we go.
        for j in range(interval):
            color = random.choice([0, 1])
            patterns[color][ip] = alivedeadsymbol
            ip += 1
            if ip >= cols:
                break

    return dragon_pattern_url(patterns)


def river(cols, nparts, seed=None):
    """
    River: two-color big streaks.
    This method does not use the nparts command,
    just there for consistent method signature.
    """
    if seed is not None:
        random.seed(seed)

    # Parameters:
    mean_size = MEAN_STREAK_SIZE

    patterns = empty_dragon_patterns(cols)

    ip = 0
    alivedeadsymbol = "."
    lastcolor = random.choice([0, 1])
    while ip < cols:

        # Flip the switch
        if alivedeadsymbol == ".":
            alivedeadsymbol = "o"
            lastcolor = 1-lastcolor
        elif alivedeadsymbol == "o":
            alivedeadsymbol = "."

        # Generate a new interval length
        interval = round(random.expovariate(1.0 / mean_size))
        if interval == 0:
            interval = 1

        # Loop over the interval, incrementing ip
        # and making cells alive as we go.
        for j in range(interval):
            patterns[lastcolor][ip] = alivedeadsymbol
            ip += 1
            if ip >= cols:
                break

    return dragon_pattern_url(patterns)


def towers(cols, nparts, seed=None):
    """
    Towers: two-color one cell.
    This method does not use the nparts command,
    just there for consistent method signature.
    """
    if seed is not None:
        random.seed(seed)

    patterns = empty_dragon_patterns(cols)

    for color in [0, 1]:
        loc = cols//2 + round(random.normalvariate(0, cols//6))
        while (patterns[0][loc] == "o" or patterns[1][loc] == "o"):
            loc = cols//2 + round(random.normalvariate(0, cols//6))
        patterns[color][loc] = "o"

    return dragon_pattern_url(patterns)


def supercritical(cols, nparts, seed=None):
    """
    Supercritical: two-color sparse.
    Each live cell of color 1 or 2 occurs next to
    one cell of the opposite color.
    """
    if seed is not None:
        random.seed(seed)

    # Parameters:
    min_stars = MIN_STARS
    max_stars = MAX_STARS
    nstars = random.randint(min_stars, max_stars)

    patterns = empty_dragon_patterns(cols)

    for i in range(nstars):
        loc = random.randint(0, cols-2)
        while (patterns[0][loc] == "o" or patterns[1][loc] == "o" or patterns[0][loc+1] == "o" or patterns[1][loc+1] == "o"):
            loc = random.randint(pstart, pend-1)
        color = random.choice([0, 1])
        patterns[color][loc] = "o"
        patterns[1-color][loc+1] = "o"

    return dragon_pattern_url(patterns)


####################
# One-Color Patterns


def vector(cols, nparts, seed=None):
    """
    Vector: one-color random split
    """
    if seed is not None:
        random.seed(seed)

    assert nparts > 0

    if nparts % 2 == 1:
        nparts += 1

    # We require minimum of 2 partitions
    if nparts < 2:
        nparts = 2

    # Parameters:
    alive_density = ALIVE_DENSITY

    patterns = empty_dragon_patterns(cols)

    if nparts % 2 == 0:

        # If even number of partitions,
        # split them 50/50 between color1/color2
        half = nparts // 2
        alive_cells_each_color = (alive_density / 2) * cols
        alive_cells_each_partition = round(alive_cells_each_color / half)
        partwidth = round(cols / nparts)
        colorparts = [0,] * half + [
            1,
        ] * half
        random.shuffle(colorparts)

    for i, color in enumerate(colorparts):

        for j in range(alive_cells_each_partition):
            # Adjust for partition boundaries
            randloc = random.randint(
                i * partwidth, min((i + 1) * partwidth - 1, cols - 1)
            )
            while patterns[0][randloc] == "o" or patterns[1][randloc] == "o":
                randloc = random.randint(
                    i * partwidth, min((i + 1) * partwidth - 1, cols - 1)
                )
            patterns[color][randloc] = "o"

    return dragon_pattern_url(patterns)


def matrix(cols, nparts, seed=None):
    """
    Matrix: two-color random split
    """
    if seed is not None:
        random.seed(seed)

    # Parameters:
    alive_density = ALIVE_DENSITY

    # total, not per color
    alive_cells_each_partition = round((alive_density * cols) / nparts)
    partwidth = round(cols / nparts)

    patterns = empty_dragon_patterns(cols)

    if nparts % 2 == 0:

        # If even number of partitions,
        # leave one totally dead, and the rest
        # two-color random split
        alivedead = [0] + [
            1,
        ] * (nparts - 1)
        random.shuffle(alivedead)

    else:

        # If odd number of partitions,
        # every other partition is dead
        alivedead = []
        for k in range(nparts):
            alivedead.append((k + 1) % 2)

    for i, ald in enumerate(alivedead):
        if ald != 0:
            for j in range(alive_cells_each_partition):
                randloc = random.randint(
                    i * partwidth, min((i + 1) * partwidth - 1, cols - 1)
                )
                while patterns[0][randloc] == "o" or patterns[1][randloc] == "o":
                    randloc = random.randint(
                        i * partwidth, min((i + 1) * partwidth - 1, cols - 1)
                    )
                # Split 50/50 between colors
                color = j % 2
                patterns[color][randloc] = "o"

    return dragon_pattern_url(patterns)


def lake(cols, nparts, seed=None):
    """
    Lake: one-color streak
    This method does not use the nparts command,
    just there for consistent method signature.
    """
    if seed is not None:
        random.seed(seed)

    if nparts % 2 == 1:
        nparts += 1

    # Parameters:
    mean_size = MEAN_STREAK_SIZE

    patterns = empty_dragon_patterns(cols)

    half = nparts // 2
    partwidth = round(cols / nparts)
    colorparts = [0,] * half + [
        1,
    ] * half
    random.shuffle(colorparts)

    for i, color in enumerate(colorparts):
        pstart = i * partwidth
        # end of partition (exclusive of the end)
        pend = min((i + 1) * partwidth, cols)
        ip = pstart
        alivedeadsymbol = "."
        while ip < pend:

            # Flip the switch
            if alivedeadsymbol == ".":
                alivedeadsymbol = "o"
            elif alivedeadsymbol == "o":
                alivedeadsymbol = "."

            # Generate a new interval length
            interval = round(random.expovariate(1.0 / mean_size))
            if interval == 0:
                interval = 1

            # Loop over the interval, incrementing ip
            # and making cells alive as we go.
            for j in range(interval):
                patterns[color][ip] = alivedeadsymbol
                ip += 1
                if ip >= pend:
                    break

    return dragon_pattern_url(patterns)


def lighthouse(cols, nparts, seed=None):
    """
    Lighthouse: one-color one cell.
    """
    if seed is not None:
        random.seed(seed)

    assert nparts > 0

    if nparts % 2 == 1:
        nparts += 1

    patterns = empty_dragon_patterns(cols)

    half = nparts // 2
    partwidth = round(cols / nparts)
    colorparts = [0,] * half + [
        1,
    ] * half
    random.shuffle(colorparts)

    for i, color in enumerate(colorparts):
        pstart = i * partwidth
        # end of partition (exclusive of the end)
        pend = min((i + 1) * partwidth, cols)
        pmid = pstart + (pend-pstart)//2
        loc = pmid + round(random.normalvariate(0, partwidth//4))
        while (patterns[0][loc] == "o" or patterns[1][loc] == "o"):
            loc = pmid + round(random.normalvariate(0, partwidth//4))
        patterns[color][loc] = "o"

    return dragon_pattern_url(patterns)


def isotropic(cols, nparts, seed=None):
    """
    Isotropic: one-color sparse.
    """
    if seed is not None:
        random.seed(seed)

    assert nparts > 0

    if nparts < 3:
        nparts = 4
    if nparts % 2 == 1:
        nparts += 1

    # Parameters:
    min_stars = MIN_STARS
    max_stars = MAX_STARS
    nstars = random.randint(min_stars, max_stars)

    patterns = empty_dragon_patterns(cols)

    half = nparts // 2
    partwidth = round(cols / nparts)
    colorparts = [0,] * half + [
        1,
    ] * half
    random.shuffle(colorparts)

    for i, color in enumerate(colorparts):
        pstart = i * partwidth
        pend = min((i + 1) * partwidth, cols)

        for j in range(nstars):
            loc = random.randint(pstart, pend-1)
            while (patterns[0][loc] == "o" or patterns[1][loc] == "o"):
                loc = random.randint(pstart, pend-1)
            patterns[color][loc] = "o"

    return dragon_pattern_url(patterns)
