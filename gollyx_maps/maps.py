import itertools
from operator import itemgetter
import json
import os
import random
from .geom import hflip_pattern, vflip_pattern, rot_pattern
from .patterns import (
    get_pattern_size,
    get_pattern_livecount,
    get_grid_pattern,
    segment_pattern,
    methuselah_quadrants_pattern,
    pattern_union,
    cloud_region,
)
from .utils import pattern2url, retry_on_failure
from .error import GollyXPatternsError, GollyXMapsError
from .hellmouth import get_hellmouth_pattern_function_map
from .pseudo import get_pseudo_pattern_function_map
from .toroidal import get_toroidal_pattern_function_map


def get_pattern_function_map(cup):
    m = {
        'hellmouth': get_hellmouth_pattern_function_map,
        'pseudo': get_pseudo_pattern_function_map,
        'toroidal': get_toroidal_pattern_function_map,
    }
    return m[cup]


########################
# High-level API methods


def get_all_map_patterns(cup):
    """Get a list of all pattern names for this cup"""
    f = get_pattern_function_map(cup)
    pattern_map = f()
    return list(pattern_map.keys())


def get_map_realization(cup, patternname, rows=None, columns=None, cell_size=None):
    """
    Return a JSON map with map names, zone names, and initial conditions.

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

    # Set default sizes if none specified
    if rows is None and columns is None:
        if cup=="hellmouth" or cup=="pseudo":
            rows = 100
            columns = 120
        elif cup=="toroidal":
            rows = 40
            columns = 280

    # Get map data (pattern, name, zone names)
    mapdat = get_map_metadata(cup, patternname)

    # Get the initial conditions for this map
    s1, s2 = render_map(cup, patternname, rows, columns)
    url = f"?s1={s1}&s2={s2}"
    mapdat["initialConditions1"] = s1
    mapdat["initialConditions2"] = s2
    mapdat["url"] = url

    # Include geometry info
    maxdim = max(rows, columns)

    if cell_size is not None:
        cellSize = cell_size

    elif columns < 70:
        cellSize = 9

    elif columns < 100:
        cellSize = 7

    elif columns < 150:
        cellSize = 6

    elif columns < 170:
        cellSize = 5

    elif columns < 200:
        cellSize = 4

    elif columns < 300:
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


def get_map_metadata(cup, patternname):
    """
    Get map metadata for the specified cup and pattern
    """
    all_metadata = get_all_map_metadata(cup)
    for m in all_metadata:
        if m['patternName'] == patternname:
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


def get_all_map_metadata(cup, season=None):
    """
    Get metadata for all maps for the specified cup and season.
    """
    map_data_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", f"{cup}.json"
    )
    if not os.path.exists(map_data_file):
        raise Exception(f"Could not find map metadata for specified cup: {cup}")
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


####################################
# Render the map for the realization


def render_map(cup, patternname, rows, columns, seed=None):
    f = get_pattern_function_map(cup)
    pattern_map = f()
    g = pattern_map[patternname]
    return g(rows, columns, seed=seed)
