import roman
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
from .error import GollyXMapsError
from .dragon import get_dragon_pattern_function_map, MAX_PARTS
from . import registry


def get_pattern_function_map(cup):
    cm = registry.get_cup_maps(cup)
    return cm.pattern_function_map


########################
# High-level API methods


def get_all_map_patterns(cup):
    """Get a list of all pattern names for this cup"""
    cm = registry.get_cup_maps(cup)
    pattern_map = cm.pattern_function_map()
    return list(pattern_map.keys())


def remove_extra_map_keys(mapdat):
    # Remove these keys before returning realization for the API to serve up
    remove_keys = ["mapSeasonStart", "mapSeasonEnd", "mapDescription"]
    for remk in remove_keys:
        if remk in mapdat.keys():
            del mapdat[remk]
    return mapdat


def get_map_realization(cup, patternname, rows=None, columns=None, cell_size=None):
    """
    Return a JSON map with map names, zone names, and initial conditions.

    Non-Dragon Cup returns:
    {
        "patternName": y,
        "mapName": z,
        "url": e,
        "initialConditions1": f,
        "initialConditions2": g,
        "rows": i,
        "columns": j,
        "cellSize:" k
    }

    (some earlier cups had 4 zone names)

    Dragon Cup returns:
    {
        "patternName": (vector|matrix|starfield|supercritical|...),
        "mapName": (same as patternName, but with I/II/III/IV suffix),
        "initialConditions1": ...,
        "initialConditions2": ...,
        "url": ...,
        "rows": ...,
        "columns": ...,
        "cellSize": ...,
    }
    """
    cm = registry.get_cup_maps(cup)

    # Handle Dragon Cup differently
    if cm.type == "dragon":
        return get_dragon_realization(patternname, rows, columns, cell_size)

    # Handle Rainbow Cup differently too
    if cm.type == "rainbow":
        return get_rainbow_realization(patternname, rows, columns, cell_size)

    # Handle Star Cups
    if cm.type == "star":
        return get_star_realization(cm, patternname, rows, columns, cell_size)

    # Standard type

    # Set default sizes if none specified
    if rows is None and columns is None:
        rows = cm.default_rows
        columns = cm.default_columns

    # Get map data (pattern, name, zone names)
    mapdat = get_map_metadata(cup, patternname, zone_labels=cm.zone_labels)

    # Get the initial conditions for this map
    s1, s2 = render_map(cm, patternname, rows, columns)
    url = f"?s1={s1}&s2={s2}"
    mapdat["initialConditions1"] = s1
    mapdat["initialConditions2"] = s2
    mapdat["url"] = url

    # Include geometry info
    if cell_size is not None:
        cellSize = cell_size
    elif cm.default_cell_size is not None:
        cellSize = cm.default_cell_size
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

    return remove_extra_map_keys(mapdat)


def get_star_realization(cm, patternname, rows=None, columns=None, cell_size=None):
    """
    Assemble Star Map
    """
    # Set default sizes if none specified
    if rows is None and columns is None:
        rows = cm.default_rows
        columns = cm.default_columns

    # Get map data (pattern, name, zone names)
    mapdat = get_map_metadata_from_cup_maps(cm, patternname, zone_labels=False)

    # Get the initial condition strings
    s1, b1, c1, s2, b2, c2 = render_map(cm, patternname, rows, columns)

    # Always include s1 and s2
    mapdat['initialConditions1'] = s1
    mapdat['initialConditions2'] = s2
    url_params = [f"s1={s1}", f"s2={s2}"]

    # Conditionally add b1, b2, c1, c2
    if b1 != "[]":
        mapdat['initialConditionsb1'] = b1
        url_params.append(f"b1={b1}")
    if b2 != "[]":
        mapdat['initialConditionsb2'] = b2
        url_params.append(f"b2={b2}")
    if c1 != "[]":
        mapdat['initialConditionsc1'] = c1
        url_params.append(f"c1={c1}")
    if c2 != "[]":
        mapdat['initialConditionsc2'] = c2
        url_params.append(f"c2={c2}")

    mapdat['url'] = "?" + "&".join(url_params)

    if cell_size is not None:
        cellSize = cell_size
    elif cm.default_cell_size is not None:
        cellSize = cm.default_cell_size
    else:
        cellSize = 3  # Default for star-like

    mapdat["rows"] = rows
    mapdat["columns"] = columns
    mapdat["cellSize"] = cellSize

    return remove_extra_map_keys(mapdat)


def get_rainbow_realization(patternname, rows=None, columns=None, cell_size=None):
    """
    Assemble Rainbow Map
    """
    # Set default sizes if none specified
    if rows is None and columns is None:
        rows = 120
        columns = 180

    # Get map data (pattern, name, zone names)
    mapdat = get_map_metadata('rainbow', patternname, zone_labels=True)

    # Get the initial condition strings
    cm = registry.get_cup_maps('rainbow')
    s1, s2, s3, s4 = render_map(cm, patternname, rows, columns)
    url = f"?s1={s1}&s2={s2}&s3={s3}&s4={s4}"

    mapdat['initialConditions1'] = s1
    mapdat['initialConditions2'] = s2
    mapdat['initialConditions3'] = s3
    mapdat['initialConditions4'] = s4
    mapdat['url'] = url

    mapdat["rows"] = rows
    mapdat["columns"] = columns
    mapdat["cellSize"] = 4

    return remove_extra_map_keys(mapdat)


def get_dragon_realization(patternname, rows=None, columns=None, cell_size=None):
    """
    Dragon Cup maps are assembled differently
    from Hellmouth, Toroidal, and Pseudo Cup maps.
    """

    # Set default sizes if none specified
    if rows is None and columns is None:
        rows = 500
        columns = 200

    # Map data: patternName, name

    # Some maps require choosing a number of partitions:
    # Vector
    # Matrix
    # Lake
    # Lighthouse
    # Isotropic
    chooseParts = ['starfield', 'supercritical', 'vector', 'matrix', 'lake', 'lighthouse', 'isotropic']
    if patternname in chooseParts:
        # Select a number of partitions
        nparts = random.randint(1, MAX_PARTS)
    else:
        nparts = 0

    # Assemble metadata (no zone data for Dragon Cup)

    # Add roman numeral suffix to map name if we specified partitions
    mapname = patternname.title()
    if nparts > 0:
        mapname += f" {roman.toRoman(nparts)}"

    m = {
        "patternName": patternname,
        "mapName": mapname
    }

    # Get the strings containing the listlife states for each color
    s1, s2 = render_dragon_map(patternname, rows, columns, nparts)
    url = f"?s1={s1}&s2={s2}"
    m['initialConditions1'] = s1
    m['initialConditions2'] = s2
    m['url'] = url

    # Find optimal cellsize
    if cell_size is not None:
        cellSize = cell_size
    elif columns < 50:
        cellSize = 5
    elif columns < 100:
        cellSize = 4
    else:
        cellSize = 3

    # Add geometry information
    m["rows"] = rows
    m["columns"] = columns
    m["cellSize"] = cellSize

    return m


##################
# Metadata methods


def _load_metadata_file(filename):
    """Load a single metadata JSON file from the data directory."""
    map_data_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", filename
    )
    if not os.path.exists(map_data_file):
        raise Exception(f"Could not find map metadata file: {filename}")
    with open(map_data_file, "r") as f:
        return json.load(f)


def get_map_metadata_from_cup_maps(cm, patternname, zone_labels=True):
    """
    Get map metadata using a CupMaps instance (merges cumulative metadata files).
    """
    all_metadata = []
    for filename in cm.metadata_files:
        all_metadata.extend(_load_metadata_file(filename))

    for m in all_metadata:
        if m['patternName'] == patternname:
            if not zone_labels:
                keys = [f'mapZone{i+1}Name' for i in range(4)]
                for key in keys:
                    if key in m:
                        del m[key]
            return m

    # If we reach this point, we didn't find the pattern in metadata
    if zone_labels:
        m = {
            "patternName": patternname,
            "mapName": "Anonymous Map",
            "mapZone1Name": "Zone 1",
            "mapZone2Name": "Zone 2",
            "mapZone3Name": "Zone 3",
            "mapZone4Name": "Zone 4",
        }
    else:
        m = {
            "patternName": patternname,
            "mapName": "Anonymous Map"
        }

    return m


def get_map_metadata(cup, patternname, zone_labels=True):
    """
    Get map metadata for the specified cup and pattern.
    """
    cm = registry.get_cup_maps(cup)
    return get_map_metadata_from_cup_maps(cm, patternname, zone_labels=zone_labels)


def get_all_map_metadata(cup, season=None):
    """
    Get metadata for all maps for the specified cup and season.
    """
    cm = registry.get_cup_maps(cup)
    mapdat = []
    for filename in cm.metadata_files:
        mapdat.extend(_load_metadata_file(filename))

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


def render_map(cm_or_cup, patternname, rows, columns, seed=None):
    if isinstance(cm_or_cup, str):
        cm = registry.get_cup_maps(cm_or_cup)
    else:
        cm = cm_or_cup
    pattern_map = cm.pattern_function_map()
    g = pattern_map[patternname]
    return g(rows, columns, seed=seed)


def render_dragon_map(patternname, rows, columns, nparts, seed=None):
    dragon_map = get_dragon_pattern_function_map()
    g = dragon_map[patternname]
    return g(columns, nparts, seed=seed)
