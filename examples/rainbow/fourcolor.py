import random
from operator import itemgetter
from gollyx_maps.patterns import (
    get_pattern_size,
    get_grid_pattern,
    pattern_union,
    get_pattern_livecount,
)
from gollyx_maps.utils import pattern2url


def randommethuselahs_fourcolor(rows=120, cols=200, seed=None):

    (
        team1_pattern,
        team2_pattern,
        team3_pattern,
        team4_pattern,
    ) = rainbow_methuselah_quadrants_pattern(rows, cols, seed)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)
    s3 = pattern2url(team3_pattern)
    s4 = pattern2url(team4_pattern)

    return s1, s2, s3, s4


def rainbow_methuselah_quadrants_pattern(
    rows, cols, seed=None, methuselah_counts=None, fixed_methuselah=None
):

    # set rng seed (optional)
    if seed is not None:
        random.seed(seed)

    small_methuselah_names = [
        "bheptomino",
        "cheptomino",
        "eheptomino",
        "piheptomino",
        "rpentomino",
    ]
    reg_methuselah_names = [
        "acorn",
        "bheptomino",
        "cheptomino",
        "eheptomino",
        "multuminparvo",
        "piheptomino",
        "rabbit",
        "rpentomino",
        #"timebomb",
        #"switchengine",
    ]

    mindim = min(rows, cols)

    # Basic checks
    BIGDIMLIMIT = 150
    mindim = min(rows, cols)
    if mindim < BIGDIMLIMIT:
        methuselah_counts = [3, 4, 9]
        if fixed_methuselah:
            methuselah_names = [fixed_methuselah]
        else:
            methuselah_names = reg_methuselah_names + small_methuselah_names
    else:
        methuselah_counts = [3, 4, 9, 16]
        if fixed_methuselah:
            methuselah_names = [fixed_methuselah]
        else:
            methuselah_names = small_methuselah_names

    valid_mc = [1, 2, 3, 4, 9, 16]
    for mc in methuselah_counts:
        if mc not in valid_mc:
            msg = "Invalid methuselah counts passed: must be in {', '.join(valid_mc)}\n"
            msg += "you specified {', '.join(methuselah_counts)}"
            raise GollyXPatternsError(msg)

    # Put a cluster of methuselahs in each quadrant,
    # one quadrant per team.

    # Procedure:
    # place random methuselah patterns in each quadrant corner

    # Store each quadrant and its upper left corner in (rows from top, cols from left) format
    quadrants = [
        (1, (0, cols // 2)),
        (2, (0, 0)),
        (3, (rows // 2, 0)),
        (4, (rows // 2, cols // 2)),
    ]

    rotdegs = [0, 90, 180, 270]

    all_methuselahs = []

    for iq, quad in enumerate(quadrants):
        count = random.choice(methuselah_counts)

        if count == 1:

            # Only one methuselah in this quadrant, so use the center

            jitterx = 8
            jittery = 8

            corner = quadrants[iq][1]

            y = corner[0] + rows // 4 + random.randint(-jittery, jittery)
            x = corner[1] + cols // 4 + random.randint(-jitterx, jitterx)

            meth = random.choice(methuselah_names)

            pattern = get_grid_pattern(
                meth,
                rows,
                cols,
                xoffset=x,
                yoffset=y,
                hflip=bool(random.getrandbits(1)),
                vflip=bool(random.getrandbits(1)),
                rotdeg=random.choice(rotdegs),
            )
            livecount = get_pattern_livecount(meth)
            all_methuselahs.append((livecount, pattern))

        elif count == 2 or count == 4:

            # Two or four methuselahs in this quadrant, so place at corners of a square
            # Form the square by cutting the quadrant into thirds

            if count == 4:
                jitterx = 2
                jittery = 2
            else:
                jitterx = 4
                jittery = 4

            corner = quadrants[iq][1]

            # Slices and partitions form the inside square
            nslices = 2
            nparts = nslices + 1

            posdiag = bool(random.getrandbits(1))

            for a in range(1, nparts):
                for b in range(1, nparts):

                    proceed = False
                    if count == 2:
                        if (posdiag and a == b) or (
                            not posdiag and a == (nslices - b + 1)
                        ):
                            proceed = True
                    elif count == 4:
                        proceed = True

                    if proceed:
                        y = (
                            corner[0]
                            + a * ((rows // 2) // nparts)
                            + random.randint(-jittery, jittery)
                        )
                        x = (
                            corner[1]
                            + b * ((cols // 2) // nparts)
                            + random.randint(-jitterx, jitterx)
                        )

                        meth = random.choice(methuselah_names)

                        try:
                            pattern = get_grid_pattern(
                                meth,
                                rows,
                                cols,
                                xoffset=x,
                                yoffset=y,
                                hflip=bool(random.getrandbits(1)),
                                vflip=bool(random.getrandbits(1)),
                                rotdeg=random.choice(rotdegs),
                            )
                        except GollyXPatternsError:
                            raise GollyXPatternsError(
                                f"Error with methuselah {meth}: cannot fit"
                            )
                        livecount = get_pattern_livecount(meth)
                        all_methuselahs.append((livecount, pattern))

        elif count == 3 or count == 9:

            # Three or nine methuselahs, place these on a square with three points per side
            # or eight points total
            if count == 9:
                jitterx = 2
                jittery = 2
            else:
                jitterx = 4
                jittery = 4

            corner = quadrants[iq][1]

            nslices = 4

            for a in range(1, nslices):
                for b in range(1, nslices):

                    proceed = False
                    if count == 3:
                        if a == b:
                            proceed = True
                    elif count == 9:
                        proceed = True

                    if proceed:
                        y = (
                            corner[0]
                            + a * ((rows // 2) // nslices)
                            + random.randint(-jittery, jittery)
                        )
                        x = (
                            corner[1]
                            + b * ((cols // 2) // nslices)
                            + random.randint(-jitterx, jitterx)
                        )

                        meth = random.choice(methuselah_names)

                        try:
                            pattern = get_grid_pattern(
                                meth,
                                rows,
                                cols,
                                xoffset=x,
                                yoffset=y,
                                hflip=bool(random.getrandbits(1)),
                                vflip=bool(random.getrandbits(1)),
                                rotdeg=random.choice(rotdegs),
                            )
                        except GollyXPatternsError:
                            raise GollyXPatternsError(
                                f"Error with methuselah {meth}: cannot fit"
                            )
                        livecount = get_pattern_livecount(meth)
                        all_methuselahs.append((livecount, pattern))

        elif count == 16:

            # Sixteen methuselahs, place these on a 4x4 square
            jitterx = 1
            jittery = 1

            corner = quadrants[iq][1]

            nslices = 5

            for a in range(1, nslices):
                for b in range(1, nslices):

                    y = (
                        corner[0]
                        + a * ((rows // 2) // nslices)
                        + random.randint(-jittery, jittery)
                    )
                    x = (
                        corner[1]
                        + b * ((cols // 2) // nslices)
                        + random.randint(-jitterx, jitterx)
                    )

                    meth = random.choice(methuselah_names)

                    try:
                        pattern = get_grid_pattern(
                            meth,
                            rows,
                            cols,
                            xoffset=x,
                            yoffset=y,
                            hflip=bool(random.getrandbits(1)),
                            vflip=bool(random.getrandbits(1)),
                            rotdeg=random.choice(rotdegs),
                        )
                    except GollyXPatternsError:
                        raise GollyXPatternsError(
                            f"Error with methuselah {meth}: cannot fit"
                        )
                    livecount = get_pattern_livecount(meth)
                    all_methuselahs.append((livecount, pattern))

    random.shuffle(all_methuselahs)

    # Sort by number of live cells
    all_methuselahs.sort(key=itemgetter(0), reverse=True)

    team1_patterns = []
    team2_patterns = []
    team3_patterns = []
    team4_patterns = []

    asc = [1, 2, 3, 4]
    ascrev = list(reversed(asc))
    serpentine_pattern = asc + ascrev

    for i, (_, methuselah_pattern) in enumerate(all_methuselahs):
        serpix = i % len(serpentine_pattern)
        serpteam = serpentine_pattern[serpix]
        if serpteam == 1:
            team1_patterns.append(methuselah_pattern)
        elif serpteam == 2:
            team2_patterns.append(methuselah_pattern)
        elif serpteam == 3:
            team3_patterns.append(methuselah_pattern)
        elif serpteam == 4:
            team4_patterns.append(methuselah_pattern)

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)
    team3_pattern = pattern_union(team3_patterns)
    team4_pattern = pattern_union(team4_patterns)

    return team1_pattern, team2_pattern, team3_pattern, team4_pattern


if __name__ == "__main__":
    s1, s2, s3, s4 = randommethuselahs_fourcolor()
    url = f"http://192.168.30.20:8888/simulator/index.html?s1={s1}&s2={s2}&s3={s3}&s4={s4}"
    print(url)
