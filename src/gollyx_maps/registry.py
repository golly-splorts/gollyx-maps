import roman
from .error import GollyXMapsError
from .hellmouth import get_hellmouth_pattern_function_map
from .pseudo import get_pseudo_pattern_function_map
from .toroidal import get_toroidal_pattern_function_map
from .dragon import get_dragon_pattern_function_map
from .rainbow import get_rainbow_pattern_function_map
from .star import get_star_pattern_function_map
from .klein import get_klein_pattern_function_map
from .ii import get_ii_pattern_function_map
from .vi import get_vi_pattern_function_map
from .star_vii import get_star_vii_new_pattern_function_map


# =============================================================================
# Legacy cups — exact backward compat, no changes
# =============================================================================

LEGACY_CUPS = {
    "hellmouth": {
        "func": get_hellmouth_pattern_function_map,
        "type": "standard",
        "zone_labels": True,
        "rows": 100,
        "columns": 120,
        "cell_size": None,
        "metadata_files": ["hellmouth.json"],
    },
    "pseudo": {
        "func": get_pseudo_pattern_function_map,
        "type": "standard",
        "zone_labels": True,
        "rows": 100,
        "columns": 120,
        "cell_size": None,
        "metadata_files": ["pseudo.json"],
    },
    "toroidal": {
        "func": get_toroidal_pattern_function_map,
        "type": "standard",
        "zone_labels": True,
        "rows": 40,
        "columns": 280,
        "cell_size": None,
        "metadata_files": ["toroidal.json"],
    },
    "dragon": {
        "func": get_dragon_pattern_function_map,
        "type": "dragon",
        "zone_labels": False,
        "rows": 500,
        "columns": 200,
        "cell_size": None,
        "metadata_files": ["dragon.json"],
    },
    "rainbow": {
        "func": get_rainbow_pattern_function_map,
        "type": "rainbow",
        "zone_labels": True,
        "rows": 120,
        "columns": 180,
        "cell_size": None,
        "metadata_files": ["rainbow.json"],
    },
    "star": {
        "func": get_star_pattern_function_map,
        "type": "star",
        "zone_labels": False,
        "rows": 160,
        "columns": 240,
        "cell_size": 3,
        "metadata_files": ["star.json"],
    },
    "klein": {
        "func": get_klein_pattern_function_map,
        "type": "standard",
        "zone_labels": False,
        "rows": 100,
        "columns": 200,
        "cell_size": 4,
        "metadata_files": ["klein.json"],
    },
}


# =============================================================================
# Numeric cup registries
# Sorted by cup number. Maps accumulate: cup N gets all entries where
# cup_number <= N.  Each entry is:
#   (cup_number, pattern_func, config_dict, metadata_filename)
# =============================================================================

GOLLY_REGISTRY = [
    (2, get_ii_pattern_function_map, {"rows": 100, "columns": 200, "cell_size": 4}, "ii.json"),
    (6, get_vi_pattern_function_map, {"rows": 150, "columns": 240, "cell_size": 3}, "vi.json"),
]

PENINSULA_REGISTRY = [
    (1, get_star_pattern_function_map,        {"rows": 160, "columns": 240, "cell_size": 3}, "star.json"),
    (7, get_star_vii_new_pattern_function_map, {"rows": 180, "columns": 280, "cell_size": 3}, "star_vii.json"),
]

# Defaults applied to numeric cups when no registry entry overrides them
GOLLY_DEFAULTS = {"type": "standard", "zone_labels": False, "rows": 150, "columns": 240, "cell_size": 3}
PENINSULA_DEFAULTS = {"type": "star", "zone_labels": False, "rows": 180, "columns": 280, "cell_size": 3}


# =============================================================================
# CupMaps — returned by the getter factory
# =============================================================================

class CupMaps:
    """Represents the maps configuration for a given cup."""

    def __init__(self, pattern_funcs, cup_type, zone_labels, default_rows, default_columns, default_cell_size, metadata_files):
        self._pattern_funcs = pattern_funcs
        self.type = cup_type
        self.zone_labels = zone_labels
        self.default_rows = default_rows
        self.default_columns = default_columns
        self.default_cell_size = default_cell_size
        self.metadata_files = metadata_files

    def pattern_function_map(self):
        """Return the cumulative {pattern_name: function} dict."""
        result = {}
        for func in self._pattern_funcs:
            result.update(func())
        return result


# =============================================================================
# Getter factory
# =============================================================================

def _parse_cup_name(cup_name):
    """
    Parse a cup identifier string.

    Returns:
        ("legacy", cup_name)      for word-name legacy cups
        ("golly", int)            for roman numeral cups (golly union)
        ("peninsula", int)        for star-prefixed roman numeral cups
    """
    if not isinstance(cup_name, str):
        raise GollyXMapsError(f"Cup name must be a string, but got {type(cup_name)}")
    if cup_name in LEGACY_CUPS:
        return ("legacy", cup_name)

    if cup_name.startswith("star-"):
        numeral = cup_name[5:]  # strip "star-"
        try:
            num = roman.fromRoman(numeral.upper())
        except roman.InvalidRomanNumeralError:
            raise GollyXMapsError(f"Invalid peninsula cup name: {cup_name!r}")
        return ("peninsula", num)

    # Try as a golly union roman numeral
    try:
        num = roman.fromRoman(cup_name.upper())
    except roman.InvalidRomanNumeralError:
        raise GollyXMapsError(f"Unknown cup name: {cup_name!r}")
    return ("golly", num)


def get_cup_maps(cup_name):
    """
    Getter factory: takes a cup identifier string and returns a CupMaps
    instance representing the maps configuration for that cup.

    Handles three cases:
      - Legacy word-name cups (hellmouth, dragon, star, etc.)
      - Golly Union roman numeral cups (ii, vi, xxi, etc.)
      - Peninsula Union star-prefixed cups (star-ii, star-vii, star-xxi, etc.)
    """
    kind, value = _parse_cup_name(cup_name)

    if kind == "legacy":
        entry = LEGACY_CUPS[value]
        return CupMaps(
            pattern_funcs=[entry["func"]],
            cup_type=entry["type"],
            zone_labels=entry["zone_labels"],
            default_rows=entry["rows"],
            default_columns=entry["columns"],
            default_cell_size=entry.get("cell_size"),
            metadata_files=entry["metadata_files"],
        )

    if kind == "golly":
        return _build_numeric_cup_maps(value, GOLLY_REGISTRY, GOLLY_DEFAULTS, all_prior=False)

    if kind == "peninsula":
        return _build_numeric_cup_maps(value, PENINSULA_REGISTRY, PENINSULA_DEFAULTS, all_prior=True)


def _build_numeric_cup_maps(cup_number, registry, defaults, all_prior):
    """
    Build a CupMaps for a numeric cup by accumulating all registry entries
    with cup_number <= the requested number.
    """
    pattern_funcs = []
    metadata_files = []
    config = dict(defaults)

    matched = False
    for entry_cup, entry_func, entry_config, entry_metadata in registry:
        if (all_prior and entry_cup <= cup_number) or (entry_cup == cup_number):
            pattern_funcs.append(entry_func)
            metadata_files.append(entry_metadata)
            config.update(entry_config)
            matched = True

    if not matched:
        min_cup = registry[0][0] if registry else "?"
        raise GollyXMapsError(
            f"No maps registered for cup number {cup_number}. "
            f"Minimum registered cup is {min_cup}."
        )

    return CupMaps(
        pattern_funcs=pattern_funcs,
        cup_type=config["type"],
        zone_labels=config["zone_labels"],
        default_rows=config["rows"],
        default_columns=config["columns"],
        default_cell_size=config.get("cell_size"),
        metadata_files=metadata_files,
    )
