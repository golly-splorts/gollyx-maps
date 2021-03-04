import itertools
from operator import itemgetter
import json
import os
import random
from .geom import hflip_pattern
from .patterns import (
    get_pattern_size,
    get_pattern_livecount,
    get_grid_pattern,
    segment_pattern,
    metheusela_quadrants_pattern,
    pattern_union,
    cloud_region,
)
from .utils import pattern2url, retry_on_failure
from .error import GollyPatternsError, GollyMapsError


##############
# Util methods


def _get_map_pattern_function_map():
    return {
        "bigsegment": bigsegment_twocolor,
        "eightpi": eightpi_twocolor,
        "eightr": eightr_twocolor,
        "fourrabbits": fourrabbits_twocolor,
        "orchard": orchard_twocolor,
        "quadjustyna": quadjustyna_twocolor,
        "rabbitfarm": rabbitfarm_twocolor,
        "random": random_twocolor,
        "randommetheuselas": randommetheuselas_twocolor,
        "randompartition": randompartition_twocolor,
        "randomsegment": randomsegment_twocolor,
        "spaceshipcluster": spaceshipcluster_twocolor,
        "spaceshipcrash": spaceshipcrash_twocolor,
        "spaceshipsegment": spaceshipsegment_twocolor,
        "switchengines": switchengines_twocolor,
        "timebomb": timebomb_oscillators_twocolor,
        "timebombredux": timebomb_randomoscillators_twocolor,
        "twoacorn": twoacorn_twocolor,
        "twomultum": twomultum_twocolor,
        "twospaceshipgenerators": twospaceshipgenerators_twocolor,
    }


########################
# High-level API methods


def get_all_map_patterns():
    patterns_map = _get_map_pattern_function_map()
    return list(patterns_map.keys())


def get_map_realization(patternname, rows=100, columns=120):
    """.
    Return a JSON dict with map name, zone names, and initial conditions.
    Returns:
    {
        "patternName": y,
        "mapName": z,
        "mapZone1Name": a,
        "mapZone2Name": b,
        "mapZone3Name": c,
        "mapZone4Name": d,
        "url": e,
        "initialConditions1": f,
        "initialConditions2": g,
        "rows": i,
        "columns": j,
        "cellSize:" k
    }
    """
    if rows < 100 or columns < 120:
        raise GollyMapsError(f"Error: you must have at least 100 rows and 120 columns")
    # Get map data (pattern, name, zone names)
    mapdat = get_map_metadata(patternname)

    # Get the initial conditions for this map
    s1, s2 = render_map(patternname, rows, columns)
    url = f"?s1={s1}&s2={s2}"
    mapdat["initialConditions1"] = s1
    mapdat["initialConditions2"] = s2
    mapdat["url"] = url

    # Include geometry info
    maxdim = max(rows, columns)
    if columns < 100:
        cellSize = 10

    elif columns < 125:
        cellSize = 8

    elif columns < 150:
        cellSize = 7

    elif columns < 175:
        cellSize = 5

    elif columns < 200:
        cellSize = 4

    elif columns < 275:
        cellSize = 3

    elif columns < 375:
        cellSize = 2

    else:
        cellSize = 1

    mapdat["rows"] = rows
    mapdat["columns"] = columns
    mapdat["cellSize"] = cellSize

    # Remove these keys before returning realization for the API to serve up
    remove_keys = ["mapSeasonStart", "mapSeasonEnd", "mapDescription"]
    for remk in remove_keys:
        if remk in mapdat.keys():
            del mapdat[remk]

    return mapdat


##################
# Metadata methods


def get_all_map_metadata(season=None):
    map_data_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", "maps.json"
    )
    with open(map_data_file, "r") as f:
        mapdat = json.load(f)

    # If the user does not specify a season, return every map's metadata
    if season is None:
        return mapdat

    # If the user specifies a season, return only the maps for that specified season
    keep_maps = []
    for this_map in mapdat:
        keep = False
        if "mapStartSeason" in this_map:
            if this_map["mapStartSeason"] <= season:
                keep = True
        if "mapEndSeason" in this_map:
            if this_map["mapEndSeason"] <= season:
                keep = False
        if keep:
            keep_maps.append(this_map)
    return keep_maps


def get_map_metadata(patternname):
    # Any patern must have a corresponding function to be valid
    patterns_map = _get_map_pattern_function_map()
    if patternname not in patterns_map:
        err = f"Error: map pattern {patternname} not found in valid patterns list: "
        err += ", ".join(list(patterns_map.keys()))
        raise GollyPatternsError(err)

    # Filter known patterns to find the specified pattern
    mapdat = get_all_map_metadata()
    for m in mapdat:
        if m["patternName"] == patternname:
            return m

    # If we reach this point, we didn't find labels in data/maps.json
    m = {
        "patternName": patternname,
        "mapName": "Unnamed Map",
        "mapZone1Name": "Zone 1",
        "mapZone2Name": "Zone 2",
        "mapZone3Name": "Zone 3",
        "mapZone4Name": "Zone 4",
    }
    return m


####################################
# Render the map for the realization


def render_map(patternname, rows, columns, seed=None):
    patterns_map = _get_map_pattern_function_map()
    f = patterns_map[patternname]
    return f(rows, columns, seed=seed)


def random_twocolor(rows, cols, seed=None):
    """
    Generate a random two-color list life initialization.

    Returns: two listlife strings, state1 and state2,
    with the random initializations.
    (12% of all cells are alive).

    Strategy: generate a set of (x,y) tuples,
    convert to list, split in half. Use those
    point sets to create listLife URL strings.
    """
    if seed is not None:
        random.seed(seed)
    ncells = rows * cols
    nlivecells = ncells * 0.12
    points = set()
    while len(points) < nlivecells:
        randy = random.randint(0, rows - 1)
        randx = random.randint(0, cols - 1)
        points.add((randx, randy))

    points = list(points)
    points1 = set(points[: len(points) // 2])  # noqa
    points2 = set(points[len(points) // 2 :])  # noqa
    pattern1 = []
    pattern2 = []
    for y in range(rows):
        row1 = []
        row2 = []

        # team 1 row
        for x in range(cols):
            if (x, y) in points1:
                row1.append("o")
            else:
                row1.append(".")
        row1str = "".join(row1)
        pattern1.append(row1str)

        # team 2 row
        for x in range(cols):
            if (x, y) in points2:
                row2.append("o")
            else:
                row2.append(".")
        row2str = "".join(row2)
        pattern2.append(row2str)

    pattern1_url = pattern2url(pattern1)
    pattern2_url = pattern2url(pattern2)

    return pattern1_url, pattern2_url


def randompartition_twocolor(rows, cols, seed=None):
    """
    Generate a two-color map with multiple patterns for each team.
    """
    if seed is not None:
        random.seed(seed)
    ncells = rows * cols
    nlivecells = int(ncells * 0.12)

    nhpartitions = random.choice([1, 2, 4, 5])
    nvpartitions = random.choice([2, 4, 8])

    w_vpartition = cols // nvpartitions
    h_hpartition = rows // nhpartitions

    team1_points = set()
    while len(team1_points) < nlivecells // 2:
        randy = random.randint(0, rows - 1)
        randx = random.randint(0, cols - 1)
        if (randx // w_vpartition) % 2 == (randy // h_hpartition) % 2:
            team1_points.add((randx, randy))

    team2_points = set()
    while len(team2_points) < nlivecells // 2:
        randy = random.randint(0, rows - 1)
        randx = random.randint(0, cols - 1)
        if (randx // w_vpartition) % 2 != (randy // h_hpartition) % 2:
            team2_points.add((randx, randy))

    team1_pattern = []
    team2_pattern = []
    for y in range(rows):
        team1_row = []
        team2_row = []

        for x in range(cols):
            if (x, y) in team1_points:
                team1_row.append("o")
            else:
                team1_row.append(".")

            if (x, y) in team2_points:
                team2_row.append("o")
            else:
                team2_row.append(".")

        team1_row_str = "".join(team1_row)
        team2_row_str = "".join(team2_row)
        team1_pattern.append(team1_row_str)
        team2_pattern.append(team2_row_str)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return (s1, s2)


def quadjustyna_twocolor(rows, cols, seed=None):
    """
    Four justyna metheuselas.
    """
    if seed is not None:
        random.seed(seed)

    rotdegs = [0, 90, 180, 270]

    centerx1 = cols // 4
    centerx1a = centerx1 + random.randint(-5, 30)
    centerx1b = centerx1 + random.randint(-5, 30)

    centery1a = rows // 4 + random.randint(-10, 10)
    centery1b = rows // 2 + rows // 4 + random.randint(-10, 10)

    j1a = get_grid_pattern(
        "justyna",
        rows,
        cols,
        xoffset=centerx1a,
        yoffset=centery1a,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs),
    )
    j1b = get_grid_pattern(
        "justyna",
        rows,
        cols,
        xoffset=centerx1b,
        yoffset=centery1b,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs),
    )
    j1_pattern = pattern_union([j1a, j1b])

    centerx2 = cols // 2 + cols // 4
    centerx2a = centerx2 - random.randint(-5, 30)
    centerx2b = centerx2 - random.randint(-5, 30)

    centery2a = rows // 4 + random.randint(-10, 10)
    centery2b = rows // 2 + rows // 4 + random.randint(-10, 10)

    j2a = get_grid_pattern(
        "justyna",
        rows,
        cols,
        xoffset=centerx2a,
        yoffset=centery2a,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs),
    )
    j2b = get_grid_pattern(
        "justyna",
        rows,
        cols,
        xoffset=centerx2b,
        yoffset=centery2b,
        hflip=(random.random() < 0.5),
        vflip=(random.random() < 0.5),
        rotdeg=random.choice(rotdegs),
    )
    j2_pattern = pattern_union([j2a, j2b])

    s1 = pattern2url(j1_pattern)
    s2 = pattern2url(j2_pattern)

    return (s1, s2)


def spaceshipcrash_twocolor(rows, cols, seed=None):
    """
    Clouds of spaceships in each quadrant crashing into each other at the origin.
    """
    if seed is not None:
        random.seed(seed)

    # Decide on how to distribute shapes among quadrants
    ss_quadrant_assignments = [1, 2]
    random.shuffle(ss_quadrant_assignments)
    quadrant_clouds = []

    osc_quadrant_assignments = [1, 2]
    random.shuffle(osc_quadrant_assignments)
    quadrant_osc = []

    # Assemble parameters needed to create a cloud region
    left_xlim = (0, cols // 2)
    right_xlim = (cols // 2, cols)
    top_ylim = (0, rows // 2)
    bot_ylim = (rows // 2, rows)

    jitter = [3, 3]

    # This will turn better-spaced grids on/off
    distancing = True  # random.getrandbits(1)

    # Use margins to shift the cloud forward/backward (how depends on which quadrant)
    lo_value = max(min(rows, cols) // 20, 1)
    hi_value = max(min(rows, cols) // 10, 5)

    # quadrant 1
    if random.random() < 0.50:
        # Slide cloud forward by padding north and east
        q1margin = [hi_value, hi_value, lo_value, lo_value]
    else:
        # Slide cloud backward by padding south and west
        q1margin = [lo_value, lo_value, hi_value, hi_value]
    q1flip = [True, False]

    quadrant_clouds.append(
        cloud_region(
            "glider",
            (rows, cols),
            right_xlim,
            top_ylim,
            q1margin,
            jitter,
            q1flip,
            distancing,
        )
    )

    # quadrant 2
    if random.random() < 0.50:
        # Slide cloud forward by padding north and west
        q2margin = [hi_value, lo_value, lo_value, hi_value]
    else:
        # Slide cloud backward by padding south and east
        q2margin = [lo_value, hi_value, hi_value, lo_value]
    q2flip = [False, False]

    quadrant_clouds.append(
        cloud_region(
            "glider",
            (rows, cols),
            left_xlim,
            top_ylim,
            q2margin,
            jitter,
            q2flip,
            distancing,
        )
    )

    mindim = min(rows, cols)

    osc_names = ["vring64", "quadrupleburloaferimeter"]
    osc_jitter = 10

    # quadrant 3
    if mindim < 200:
        # bottom left oscillator
        quadrant_osc.append(
            get_grid_pattern(
                random.choice(osc_names),
                rows,
                cols,
                xoffset=cols // 4,
                yoffset=rows // 2 + rows // 4,
            )
        )
        # bottom right oscillator
        quadrant_osc.append(
            get_grid_pattern(
                random.choice(osc_names),
                rows,
                cols,
                xoffset=cols // 2 + cols // 4,
                yoffset=rows // 2 + rows // 4,
            )
        )

    else:
        # bottom left oscillators: located in upper left corner and bottom right corner of quadrant
        left_oscillators = []
        left_oscillators.append(
            get_grid_pattern(
                random.choice(osc_names),
                rows,
                cols,
                xoffset=cols // 4 + random.randint(-osc_jitter, osc_jitter),
                yoffset=rows // 2 + rows // 4 - rows // 8,
            )
        )
        left_oscillators.append(
            get_grid_pattern(
                random.choice(osc_names),
                rows,
                cols,
                xoffset=cols // 4 + random.randint(-osc_jitter, osc_jitter),
                yoffset=rows // 2 + rows // 4 + rows // 6,
            )
        )
        quadrant_osc.append(pattern_union(left_oscillators))

        # bottom right oscillators:
        right_oscillators = []
        right_oscillators.append(
            get_grid_pattern(
                random.choice(osc_names),
                rows,
                cols,
                xoffset=cols // 2 + cols // 4 + random.randint(-osc_jitter, osc_jitter),
                yoffset=rows // 2 + rows // 4 - rows // 8,
            )
        )
        right_oscillators.append(
            get_grid_pattern(
                random.choice(osc_names),
                rows,
                cols,
                xoffset=cols // 2 + cols // 4 + random.randint(-osc_jitter, osc_jitter),
                yoffset=rows // 2 + rows // 4 + rows // 6,
            )
        )
        quadrant_osc.append(pattern_union(right_oscillators))

    team1_patterns = []
    team2_patterns = []

    for k, (ss_qa, osc_qa) in enumerate(
        zip(ss_quadrant_assignments, osc_quadrant_assignments)
    ):
        # Deal with spaceships
        if ss_qa == 1:
            team1_patterns.append(quadrant_clouds[k])
        else:
            team2_patterns.append(quadrant_clouds[k])

        # Deal with oscillators
        if osc_qa == 1:
            team1_patterns.append(quadrant_osc[k])
        else:
            team2_patterns.append(quadrant_osc[k])

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return (s1, s2)


def spaceshipcluster_twocolor(rows, cols, seed=None):
    """
    Clouds of spaceships in the upper quadrants crashing into burloaferimeters below.
    """
    if seed is not None:
        random.seed(seed)

    # Decide on how to distribute spaceships among quadrants
    quadrant_assignments = [1, 1, 2, 2]
    random.shuffle(quadrant_assignments)

    # Assemble parameters needed to create a cloud region in each quadrant
    left_xlim = (0, cols // 2)
    right_xlim = (cols // 2, cols)
    top_ylim = (0, rows // 2)
    bot_ylim = (rows // 2, rows)

    jitter = [3, 3]

    # Use margins to shift the cloud forward/backward (how depends on which quadrant)
    lo_value = max(min(rows, cols) // 20, 1)
    hi_value = max(min(rows, cols) // 10, 5)

    # This will hold four items: one glider cloud pattern for each quadrant
    quadrant_clouds = []

    # This will turn better-spaced grids on/off
    distancing = True  # random.getrandbits(1)

    # quadrant 1
    if random.random() < 0.50:
        # Slide cloud forward by padding north and east
        q1margin = [hi_value, hi_value, lo_value, lo_value]
    else:
        # Slide cloud backward by padding south and west
        q1margin = [lo_value, lo_value, hi_value, hi_value]
    q1flip = [True, False]

    quadrant_clouds.append(
        cloud_region(
            "glider",
            (rows, cols),
            right_xlim,
            top_ylim,
            q1margin,
            jitter,
            q1flip,
            distancing,
        )
    )

    # quadrant 2
    if random.random() < 0.50:
        # Slide cloud forward by padding north and west
        q2margin = [hi_value, lo_value, lo_value, hi_value]
    else:
        # Slide cloud backward by padding south and east
        q2margin = [lo_value, hi_value, hi_value, lo_value]
    q2flip = [False, False]

    quadrant_clouds.append(
        cloud_region(
            "glider",
            (rows, cols),
            left_xlim,
            top_ylim,
            q2margin,
            jitter,
            q2flip,
            distancing,
        )
    )

    # quadrant 3
    if random.random() < 0.50:
        # Slide cloud forward by padding south and west
        q3margin = [lo_value, lo_value, hi_value, hi_value]
    else:
        # Slide cloud backward by padding north and east
        q3margin = [hi_value, hi_value, lo_value, lo_value]
    q3flip = [False, True]

    quadrant_clouds.append(
        cloud_region(
            "glider",
            (rows, cols),
            left_xlim,
            bot_ylim,
            q3margin,
            jitter,
            q3flip,
            distancing,
        )
    )

    # quadrant 4
    if random.random() < 0.50:
        # Slide cloud forward by padding south and east
        q4margin = [lo_value, hi_value, hi_value, lo_value]
    else:
        # Slide cloud backward by padding north and west
        q4margin = [hi_value, lo_value, lo_value, hi_value]
    q4flip = [True, True]

    quadrant_clouds.append(
        cloud_region(
            "glider",
            (rows, cols),
            right_xlim,
            bot_ylim,
            q4margin,
            jitter,
            q4flip,
            distancing,
        )
    )

    team1_patterns = []
    team2_patterns = []

    for k, qa in enumerate(quadrant_assignments):
        if qa == 1:
            team1_patterns.append(quadrant_clouds[k])
        else:
            team2_patterns.append(quadrant_clouds[k])

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    s1 = pattern2url(team1_pattern)
    s2 = pattern2url(team2_pattern)

    return (s1, s2)


def twoacorn_twocolor(rows, cols, seed=None):
    """
    Generate a map wth an acorn on the top and an acorn on the bottom.

    Returns: two listlife strings, state1 and state2,
    with the acorn initializations.

    Strategy:
    - grid size doesn't matter when getting pattern
    - use grid size to determine centerpoints
    - get size of acorn pattern
    - ask for acorn at particular offset
    """
    if seed is not None:
        random.seed(seed)

    die1 = random.randint(1, 3)
    if die1 == 1:
        # zone 1
        centerx1 = cols // 2 + cols // 4
        centery1 = rows // 4
    elif die1 == 2:
        # zone 2
        centerx1 = cols // 4
        centery1 = rows // 4
    else:
        # middle of zone 1 and 2
        centerx1 = cols // 2
        centery1 = rows // 4

    centerx1 += random.randint(-5, 5)

    die2 = random.randint(1, 3)
    if die2 == 1:
        # zone 3
        centerx2 = cols // 4
        centery2 = rows // 2 + rows // 4
    elif die2 == 2:
        # zone 4
        centerx2 = cols // 2 + cols // 4
        centery2 = rows // 2 + rows // 4
    else:
        # middle of zone 3 and 4
        centerx2 = cols // 2
        centery2 = rows // 2 + rows // 4

    centerx2 += random.randint(-5, 5)

    pattern1 = get_grid_pattern(
        "acorn", rows, cols, xoffset=centerx1, yoffset=centery1, vflip=True
    )
    pattern2 = get_grid_pattern("acorn", rows, cols, xoffset=centerx2, yoffset=centery2)

    pattern1_url = pattern2url(pattern1)
    pattern2_url = pattern2url(pattern2)

    return pattern1_url, pattern2_url


def timebomb_oscillators_twocolor(rows, cols, seed=None):
    return _timebomb_oscillators_twocolor(rows, cols, revenge=False, seed=seed)


def timebomb_randomoscillators_twocolor(rows, cols, seed=None):
    return _timebomb_oscillators_twocolor(rows, cols, revenge=True, seed=seed)


def _timebomb_oscillators_twocolor(rows, cols, revenge, seed=None):

    if seed is not None:
        random.seed(seed)

    mindim = min(rows, cols)

    # Geometry
    lengthscale = 28
    centerx = cols // 2
    centery = rows // 2

    if mindim < 200:
        # Three oscillators versus one timebomb

        # Timebomb locations
        timebomb_x = [centerx]
        timebomb_y = [centery + lengthscale]
        hflip_timebomb = bool(random.getrandbits(1))

        # Oscillator locations
        osc_x = [centerx - lengthscale, centerx, centerx + lengthscale]
        osc_y = [centery - lengthscale]

    else:
        # Six oscillators versus two timebombs

        # Timebomb locations
        timebomb_x = [centerx, centerx]
        timebomb_y = [centery + lengthscale, centery - lengthscale]
        hflip_timebomb = [False, True]

        # Bottom oscillator locations
        osc_x = [centerx - lengthscale, centerx, centerx + lengthscale]
        osc_y = [
            timebomb_y[0] + lengthscale,
        ] * 3

        # Top oscillator locations
        osc_x += [centerx - lengthscale, centerx, centerx + lengthscale]
        osc_y += [
            timebomb_y[1] - lengthscale,
        ] * 3

    def _get_oscillator_name():
        if revenge:
            oscillators = ["airforce", "koksgalaxy", "dinnertable", "vring64", "harbor"]
            which_oscillator = random.choice(oscillators)
        else:
            which_oscillator = "quadrupleburloaferimeter"
        return which_oscillator

    # jitter for patterns
    osc_jitter_x = lengthscale // 8
    osc_jitter_y = lengthscale // 4
    timebomb_jitter_x = lengthscale // 2
    timebomb_jitter_y = lengthscale // 4

    # Decide whether this is an even matchup (each team has 1 timebomb and 3 oscillators)
    # or a lopsided matchup (one team has both timebombs)
    if random.random() < 0.25:
        # Even
        osc_team_ass = [1, 1, 1, 2, 2, 2]
        timebomb_team_ass = [2, 1]
    else:
        # Lopsided
        osc_team_ass = [1, 1, 1, 1, 1, 1]
        timebomb_team_ass = [2, 2]

    # Assemble the team patterns
    team1_patterns = []
    team2_patterns = []

    # Assemble the oscillator patterns
    for k, (oscxx, oscyy, team_ass) in enumerate(zip(osc_x, osc_y, osc_team_ass)):
        pattern = get_grid_pattern(
            _get_oscillator_name(),
            rows,
            cols,
            xoffset=oscxx + random.randint(-osc_jitter_x, osc_jitter_x),
            yoffset=oscyy + random.randint(-osc_jitter_y, 0),
        )
        if team_ass == 1:
            team1_patterns.append(pattern)
        else:
            team2_patterns.append(pattern)

    # Assemble the timebomb patterns
    for k, (timebombxx, timebombyy, team_ass, do_hflip) in enumerate(zip(timebomb_x, timebomb_y, timebomb_team_ass, hflip_timebomb)):
        do_hflip = k == 1
        pattern = get_grid_pattern(
            "timebomb",
            rows,
            cols,
            xoffset=timebombxx
            + random.randint(-timebomb_jitter_x, timebomb_jitter_x),
            yoffset=timebombyy + random.randint(0, timebomb_jitter_y),
            hflip=do_hflip,
        )
        if team_ass == 1:
            team1_patterns.append(pattern)
        else:
            team2_patterns.append(pattern)

    team1_pattern = pattern_union(team1_patterns)
    team2_pattern = pattern_union(team2_patterns)

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


# def timebomb_randomoscillators_twocolor(rows, cols, seed=None):
#
#    if seed is not None:
#        random.seed(seed)
#
#    oscillators = ["airforce", "koksgalaxy", "dinnertable", "vring64", "harbor"]
#
#    # Flip a coin to decide on random oscillators or all the same oscillators
#    random_oscillators = False
#    if random.random() < 0.33:
#        random_oscillators = True
#
#    oscillator_name = random.choice(oscillators)
#
#    centerxs = [
#        (cols // 2) + (cols // 4) + random.randint(-4, 4),
#        cols // 4 + random.randint(-4, 4),
#        cols // 2 + random.randint(-4, 4),
#    ]
#    centerys = [
#        (rows // 3),
#    ] * 3
#    centerys = [j + random.randint(-4, 4) for j in centerys]
#
#    osc_patterns = []
#    for centerx, centery in zip(centerxs, centerys):
#        if random_oscillators:
#            oscillator_name = random.choice(oscillators)
#        osc = get_grid_pattern(
#            oscillator_name, rows, cols, xoffset=centerx, yoffset=centery
#        )
#        osc_patterns.append(osc)
#
#    osc_pattern = pattern_union(osc_patterns)
#
#    centerx2 = cols // 2
#    centery2 = 2 * rows // 3
#
#    centerx2 += random.randint(-12, 12)
#    centery2 += random.randint(-8, 8)
#
#    vflipopt = bool(random.getrandbits(1))
#    hflipopt = bool(random.getrandbits(1))
#    rotdegs = [0, 90, 180, 270, 0]
#    timebomb = get_grid_pattern(
#        "timebomb",
#        rows,
#        cols,
#        xoffset=centerx2,
#        yoffset=centery2,
#        hflip=hflipopt,
#        vflip=vflipopt,
#        rotdeg=random.choice(rotdegs),
#    )
#
#    pattern1_url = pattern2url(osc_pattern)
#    pattern2_url = pattern2url(timebomb)
#
#    return pattern1_url, pattern2_url


def fourrabbits_twocolor(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)

    mindim = min(rows, cols)

    if mindim < 200:
        rabbit_x_loc = [cols // 4, cols // 2 + cols // 4]
        rabbit_y_loc = [rows // 4, rows // 2 + rows // 4]

    else:
        rabbit_x_loc = [
            cols // 4 - cols // 8,
            cols // 4 + cols // 8,
            cols // 2 + cols // 4 + cols // 8,
            cols // 2 + cols // 4 - cols // 8,
        ]
        rabbit_y_loc = [
            rows // 4 - rows // 8,
            rows // 4 + rows // 8,
            rows // 2 + rows // 4 + rows // 8,
            rows // 2 + rows // 4 - rows // 8,
        ]

    npoints = len(rabbit_x_loc) * len(rabbit_y_loc)
    team_assignments = [
        1,
    ] * (npoints // 2)
    team_assignments += [
        2,
    ] * (npoints - npoints // 2)
    random.shuffle(team_assignments)

    team1_patterns = []
    team2_patterns = []
    for i, (x, y) in enumerate(itertools.product(rabbit_x_loc, rabbit_y_loc)):
        do_vflip = bool(random.getrandbits(1))
        do_hflip = bool(random.getrandbits(1))
        xjitter = 5
        yjitter = 5
        rabbit = get_grid_pattern(
            "rabbit",
            rows,
            cols,
            xoffset=x + random.randint(-xjitter, xjitter),
            yoffset=y + random.randint(-yjitter, yjitter),
            vflip=do_vflip,
            hflip=do_hflip,
        )
        if team_assignments[i] == 1:
            team1_patterns.append(rabbit)
        else:
            team2_patterns.append(rabbit)

    p1 = pattern_union(team1_patterns)
    p2 = pattern_union(team2_patterns)

    pattern1_url = pattern2url(p1)
    pattern2_url = pattern2url(p2)

    return pattern1_url, pattern2_url


def twospaceshipgenerators_twocolor(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)

    # backrake 2 laying trail of glider ships
    # both backrakes start at very bottom
    # squares in middle, of alternating colors
    (xdim, ydim) = get_pattern_size("backrake2")

    spaceship1x = cols // 4
    spaceship2x = cols // 2 + cols // 4
    spaceshipy = rows - 1 - ydim

    spaceship1x += random.randint(-5, 5)
    spaceship2x += random.randint(-5, 5)

    generator1 = get_grid_pattern(
        "backrake2", rows, cols, xoffset=spaceship1x, yoffset=spaceshipy, hflip=True
    )
    generator2 = get_grid_pattern(
        "backrake2", rows, cols, xoffset=spaceship2x, yoffset=spaceshipy
    )

    nboxes = 15
    box_patterns1 = []
    box_patterns2 = []
    for i in range(nboxes):
        box_x = cols // 2
        box_y = (i + 1) * (rows // (nboxes + 1))

        box_x += random.randint(-5, 5)
        box_y += random.randint(-1, 1)

        box_pattern = get_grid_pattern(
            "block", rows, cols, xoffset=box_x, yoffset=box_y
        )
        if i % 2 == 0:
            box_patterns1.append(box_pattern)
        else:
            box_patterns2.append(box_pattern)

    boxship_pattern1 = pattern_union([generator1] + box_patterns1)
    boxship_pattern2 = pattern_union([generator2] + box_patterns2)

    pattern1_url = pattern2url(boxship_pattern1)
    pattern2_url = pattern2url(boxship_pattern2)

    return pattern1_url, pattern2_url


def eightr_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    centerx = cols // 2
    centery = rows // 2

    # Place one r omino every 10 grid spaces,
    # maximum number - 1
    maxshapes = centerx // 10
    c1patterns = []
    c2patterns = []
    for i in range(maxshapes - 1):
        end = (i + 1) * 10
        start = end - 5
        pattern1 = get_grid_pattern(
            "rpentomino",
            rows,
            cols,
            xoffset=centerx - random.randint(start, end),
            yoffset=centery + random.randint(-10, 10),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c1patterns.append(pattern1)

        pattern2 = get_grid_pattern(
            "rpentomino",
            rows,
            cols,
            xoffset=centerx + random.randint(start, end),
            yoffset=centery + random.randint(-10, 10),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c2patterns.append(pattern2)

    s1 = pattern_union(c1patterns)
    s2 = pattern_union(c2patterns)

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


def eightpi_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    centerx = cols // 2
    centery = rows // 2

    # Place one pi omino every 10 grid spaces,
    # maximum number - 1
    maxshapes = centerx // 10
    c1patterns = []
    c2patterns = []
    for i in range(maxshapes - 1):
        end = (i + 1) * 10
        start = end - 5
        pattern1 = get_grid_pattern(
            "piheptomino",
            rows,
            cols,
            xoffset=centerx - random.randint(start, end),
            yoffset=centery + random.randint(-10, 10),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c1patterns.append(pattern1)

        pattern2 = get_grid_pattern(
            "piheptomino",
            rows,
            cols,
            xoffset=centerx + random.randint(start, end),
            yoffset=centery + random.randint(-10, 10),
            hflip=bool(random.getrandbits(1)),
            vflip=bool(random.getrandbits(1)),
        )
        c2patterns.append(pattern2)

    s1 = pattern_union(c1patterns)
    s2 = pattern_union(c2patterns)

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


def twomultum_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    mindim = min(rows, cols)
    if mindim < 200:
        L = 15
        multum_x_loc = [cols // 2]
        multum_y_loc = [rows // 2 - L, rows // 2 + L]

    else:
        L = 25
        multum_x_loc = [cols // 2 - L, cols // 2 + L]
        multum_y_loc = [rows // 2 - L, rows // 2 + L]

    npoints = len(multum_x_loc) * len(multum_y_loc)
    team_assignments = [
        1,
    ] * (npoints // 2)
    team_assignments += [
        2,
    ] * (npoints - npoints // 2)
    random.shuffle(team_assignments)

    jitter = 5

    team1_patterns = []
    team2_patterns = []
    for i, (x, y) in enumerate(itertools.product(multum_x_loc, multum_y_loc)):
        m = get_grid_pattern(
            "multuminparvo",
            rows,
            cols,
            xoffset=x + random.randint(-jitter, jitter),
            yoffset=y + random.randint(-jitter, jitter),
            vflip=(y < rows // 2 or random.random() < 0.25),
        )
        if team_assignments[i] == 1:
            team1_patterns.append(m)
        else:
            team2_patterns.append(m)

    s1 = pattern_union(team1_patterns)
    s2 = pattern_union(team2_patterns)

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


def bigsegment_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    nhseg = 0
    nvseg = 0
    while (nhseg == 0 and nvseg == 0) or (nhseg % 2 != 0 and nvseg == 0):
        nhseg = random.choice([0, 1, 3])
        nvseg = random.choice([0, 1, 3])

    jitterx = 15
    jittery = 15

    team1_pattern, team2_pattern = segment_pattern(
        rows,
        cols,
        seed,
        colormode="classicbroken",
        nhseg=nhseg,
        nvseg=nvseg,
        jitterx=jitterx,
        jittery=jittery,
    )

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


def randomsegment_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    nhseg = 0
    nvseg = 0
    while nhseg == 0 and nvseg == 0:
        nhseg = random.choice(list(range(4)))
        nvseg = random.choice(list(range(4)))

    jitterx = 0
    jittery = 12

    colormode = "random"
    if random.random() < 0.50:
        colormode = "randombroken"

    team1_pattern, team2_pattern = segment_pattern(
        rows,
        cols,
        seed,
        colormode=colormode,
        nhseg=nhseg,
        nvseg=nvseg,
        jitterx=jitterx,
        jittery=jittery,
    )

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url


def spaceshipsegment_twocolor(rows, cols, seed=None):

    if seed is not None:
        random.seed(seed)

    nhseg = 1
    nvseg = 0

    jitterx = 0
    jittery = 5

    team1_segment, team2_segment = segment_pattern(
        rows,
        cols,
        seed,
        colormode="random",
        nhseg=nhseg,
        nvseg=nvseg,
        jitterx=jitterx,
        jittery=jittery,
    )

    ss_name = "lightweightspaceship"
    ssh, ssw = get_pattern_size(ss_name)

    hbuff = 10
    vbuff = 3
    ssjitterx = ssw

    remaining_height = rows // 2
    nspaceships = ((remaining_height - vbuff) // (ssh + vbuff)) - 1

    # Team 1 has a fleet of lightweight spaceships in upper right corner
    team1_spaceships = []
    for i in range(nspaceships):
        # find center y, starting from top
        y = 0 + vbuff + i * (ssh + vbuff) + ssh // 2
        # find center x, starting from far right
        x = (
            cols
            - hbuff
            - 2 * i * (ssw)
            - ssw // 2
            + random.randint(-ssjitterx, ssjitterx)
        )
        p = get_grid_pattern(
            ss_name, rows, cols, xoffset=x, yoffset=y, check_overflow=True
        )
        team1_spaceships.append(p)

    # Team 2 has a fleet of lightweight spaceships in lower left corner
    team2_spaceships = []
    for i in range(nspaceships):
        # find center y, starting from bottom
        y = rows - vbuff - i * (ssh + vbuff) - ssh // 2
        # find center x, starting from far left
        x = 0 + hbuff + 2 * i * ssw + ssw // 2 + random.randint(-ssjitterx, ssjitterx)
        p = get_grid_pattern(
            ss_name, rows, cols, xoffset=x, yoffset=y, hflip=True, check_overflow=True
        )
        team2_spaceships.append(p)

    s1 = pattern_union([team1_segment] + team1_spaceships)
    s2 = pattern_union([team2_segment] + team2_spaceships)

    pattern1_url = pattern2url(s1)
    pattern2_url = pattern2url(s2)

    return pattern1_url, pattern2_url


@retry_on_failure
def switchengines_twocolor(rows, cols, seed=None):
    team1_pattern, team2_pattern = metheusela_quadrants_pattern(
        rows, cols, seed, metheusela_counts=[2, 4], fixed_metheusela="switchengine"
    )
    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)
    return pattern1_url, pattern2_url


@retry_on_failure
def orchard_twocolor(rows, cols, seed=None):
    count = random.choice([4, 9])
    team1_pattern, team2_pattern = metheusela_quadrants_pattern(
        rows, cols, seed, metheusela_counts=[count], fixed_metheusela="acorn"
    )
    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)
    return pattern1_url, pattern2_url


@retry_on_failure
def randommetheuselas_twocolor(rows, cols, seed=None):
    team1_pattern, team2_pattern = metheusela_quadrants_pattern(rows, cols, seed)
    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)
    return pattern1_url, pattern2_url


def rabbitfarm_twocolor(rows, cols, seed=None):

    # Make the wabbits
    # -----------------
    count = 4  # random.choice([4, 9])
    team1_wabbits, team2_wabbits = metheusela_quadrants_pattern(
        rows, cols, seed, metheusela_counts=[count], fixed_metheusela="rabbit"
    )

    # Make the fence
    # -----------------

    # Always 1 horizontal segment, optional vertical segment
    nhseg = 1
    if random.random() < 0.33:
        nvseg = 0
    else:
        nvseg = 1

    # Set amount of jitter for placement of segments
    jitterx = 8
    jittery = 8

    # Color mode should be broken
    if random.random() < 0.33:
        colormode = "classicbroken"
    else:
        colormode = "randombroken"

    team1_fence, team2_fence = segment_pattern(
        rows,
        cols,
        seed,
        colormode=colormode,
        nhseg=nhseg,
        nvseg=nvseg,
        jitterx=jitterx,
        jittery=jittery,
    )

    team1_pattern = pattern_union([team1_wabbits, team1_fence])
    team2_pattern = pattern_union([team2_wabbits, team2_fence])

    pattern1_url = pattern2url(team1_pattern)
    pattern2_url = pattern2url(team2_pattern)

    return pattern1_url, pattern2_url
