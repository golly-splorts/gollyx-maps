# gollyx-maps

Code for turning cellular automata patterns into GollyX maps (ListLife arrays).

## Install

Add this line to your `requirements.txt`, or to `dependencies` in `pyproject.toml`:

```
gollyx-maps @ git+https://github.com/golly-splorts/gollyx-maps.git@mainx
```

`mainx` is the release branch; `developx` is the development branch.

## Quick start

```
from gollyx_maps import maps

print(maps.get_all_map_patterns("ii"))

m = maps.get_map_realization("ii", "fourrabbits", seed=42)
print(m["mapName"])
print(m["url"])
```

`get_map_realization(cup, patternname, rows=None, columns=None, cell_size=None, seed=None)`
returns a dict:

```
{
    "patternName": "fourrabbits",
    "mapName": "Parking Garage",
    "mapStartSeason": 0,
    "initialConditions1": "[{\"70\":[55]},...]",
    "initialConditions2": "[{\"19\":[143]},...]",
    "url": "?s1=[...]&s2=[...]",
    "rows": 100,
    "columns": 200,
    "cellSize": 4
}
```

Each `initialConditionsN` string is a ListLife array: a list of `{row: [columns]}`
objects giving the live cells for team N. `url` is the query string that loads
the map in the GollyX simulator. Strings are readable by
[gollyx-python](https://github.com/golly-splorts/gollyx-python).

Some cups add fields:

- Hellmouth, Pseudo, Toroidal and Rainbow maps include `mapZone1Name` to `mapZone4Name`.
- Rainbow maps have four teams (`initialConditions1` to `initialConditions4`).
- Star maps may include `initialConditionsb1`, `initialConditionsb2`,
  `initialConditionsc1`, `initialConditionsc2` for cells in the dying states
  (`b` and `c` in pattern files).
- Dragon maps have no `mapStartSeason`.

Pass `seed` to get the same map every time; omit it for a new random placement.

## Cups

`registry.get_cup_maps(cup)` maps a cup name to its patterns, map metadata
and default grid size. Three kinds of cup name are accepted:

| Cup name | Examples | Maps |
|---|---|---|
| Legacy | `hellmouth`, `pseudo`, `toroidal`, `dragon`, `rainbow`, `star`, `klein` | that cup's own maps |
| Golly Union (roman numeral) | `ii`, `vi`, `xxi` | the newest registry entry at or below that number |
| Peninsula Union (`star-` + roman numeral) | `star-vii`, `star-xxi` | all registry entries at or below that number |

So `xxi` uses the VI maps, and `star-vii` uses the Star maps plus the Star VII maps.
See [PatternInheritance.md](PatternInheritance.md) for which patterns each cup
reuses and renames.

## Building maps from patterns

`patterns` loads pattern files and places them on a grid; `utils.pattern2url`
turns a grid into a ListLife array:

```
from gollyx_maps import patterns, utils

print(patterns.get_patterns())                      # all pattern names
rabbit = patterns.get_pattern("rabbit", rotdeg=90)  # list of rows, 'o' = live

grid = patterns.get_grid_pattern("rabbit", 20, 20, xoffset=10, yoffset=10, rotdeg=90)
print(utils.pattern2url(grid))
```

`xoffset` and `yoffset` give the position of the pattern's center.

Pattern files live in `src/gollyx_maps/`, one directory per rule:

- [b3s23_patterns](src/gollyx_maps/b3s23_patterns): Life (B3/S23)
- [b357s238_patterns](src/gollyx_maps/b357s238_patterns): Pseudo Life (B357/S238)
- [b2s345c4_patterns](src/gollyx_maps/b2s345c4_patterns): Star Wars (B2/S345/C4)

See [examples/](examples) for scripts that build each cup's maps.

## Adding maps for a new cup

1. Write the pattern functions in a new module under `src/gollyx_maps/`, with a
   `get_<cup>_pattern_function_map()` that returns `{pattern name: function}`.
2. Add the map names and descriptions to `src/gollyx_maps/data/<cup>.json`.
3. Add an entry to `GOLLY_REGISTRY` or `PENINSULA_REGISTRY` in
   `src/gollyx_maps/registry.py`.
4. Add tests and bump `__version__` in `src/gollyx_maps/__init__.py`.

[src/gollyx_maps/README.md](src/gollyx_maps/README.md) describes each module.

## Development

```
pip install -e ".[dev]"
pytest
```
