# gollyx-maps

[![Travis](https://travis-ci.com/golly-splorts/gollyx-maps.svg?branch=main)](https://travis-ci.com/golly-splorts/gollyx-maps.svg?branch=main)

Code for turning cellular autonoma patterns into GollyX maps (ListLife arrays).

To use gollyx-maps, install it directly from the git repo by adding the following
to your `requirements.txt` file:

```
git+git://github.com/golly-splorts/gollyx-maps@develop#egg=gollyx_maps
```

(replace `develop` with the appropriate branch name.)

Once you have the `gollyx-maps` package installed into your Python environment,
you can start using it like this:

```
from gollyx_maps import maps

s1, s2 = maps.twocolor_randommap(100,100)
print(s1)
print(s2)
```

See maps submodule below for explanation of s1 and s2.

## Rules

(This is intended for use with CA rules other than the classic Game of Life.)

## Submodules

### Maps Submodule

The maps submodule is intended to turn a pattern name
into a random, unique map. For example, the "fourrabbits"
pattern will place four rabbits on the board, but the
exact placement is random each time.

```
from gollyx_maps import maps

s1, s2 = maps.twocolor_randommap(100,100)
print(s1)
print(s2)
```

The s1 and s2 strings are readable/usable by
[gollyx-python](https://github.com/golly-splorts/gollyx-python).

(Note: this is where new maps are added for new seasons.)

## Pattern Submodule

Like the maps submodule, the patterns submodule provides patterns
that are usable by both golly-python and golly-js. But this
submodule provides more generally useful patterns.

For example, here is how we would get a rabbit pattern and
place it in the middle of a 20 x 20 grid:

```
from gollyx_maps import patterns

grid = get_grid_pattern('rabbit', 20, 20, xoffset=10, yoffset=10, rotdeg=90)
url = pattern2url(grid)
print(url)
```

Dot diagrams

```
from gollyx_maps import patterns
print(patterns.get_patterns())
rabbit = get_pattern('rabbit', rotdeg=90)
```

## List of Patterns

### B3/S23 - Classic Life

Incomplete list of patterns from the classic Game of Life,
rule B3/S23:

* 78p70
* acorn
* backrake2
* bheptomino
* block
* cheptomino
* coespaceship
* cthulhu
* dinnertable
* dinnertablecenter
* dinnertableedges
* eheptomino
* heavyweightspaceship
* justyna
* koksgalaxy
* lightweightspaceship
* middleweightspaceship
* multuminparvo
* piheptomino
* quadrupleburloaferimeter
* rabbit
* rpentomino
* spaceshipgrower
* switchengine
* tagalong
* timebomb
* twoglidermess
* unidimensionalinfinitegrowth
* unidimensionalsixgliders
* x66

# Todo

Need to fix up nomenclature - maps, patterns, pattern-mappings, it is very confusing.

