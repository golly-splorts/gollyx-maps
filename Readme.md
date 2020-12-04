# golly-maps

Code for turning Game of Life patterns into Golly maps (ListLife arrays).

How to use golly-maps as a submodule:

From the repo of interest, add the golly-maps repo as a submodule named "gollymaps"
(no dash to make it simpler to import):

```
cd my-repo
git submodule add git@github.com:golly-splorts/golly-maps.git gollymaps
git submodule update --init
```

Note you can also:
* Vendor a copy of this repo by copying its contents into your own repo
* Do a git clone of this repo into your repo, cloning it to gollymaps as above,
  so that it can be imported as a submodule, but without adding it to your repo.

Whatever you want to do.

Now you will be able to import the gollymaps submodule from Python and start using it.
For example, to import the maps submodule:

```
from gollymaps import maps

s1, s2 = maps.twocolor_randommap(100,100)
print(s1)
print(s2)
```

See maps submodule below for explanation of s1 and s2.

## Submodules

### Maps Submodule

The maps submodule is intended to turn a pattern name
into a random, unique map. For example, the "fourrabbits"
pattern will place four rabbits on the board, but the
exact placement is random each time.

```
from gollymaps import maps

s1, s2 = maps.twocolor_randommap(100,100)
print(s1)
print(s2)
```

The s1 and s2 strings are readable/usable by both
[golly-python](https://github.com/golly-splorts/golly-python)
and [golly-js](https://github.com/golly-splorts/golly-js).

This makes it useful for both the front-end Javascript Golly
simulator, and for the backend Python Golly simulator.

However, there are a limited number of maps and this is not
gneerally useful, it is primarily for use by the Golly API
and the backend simulator.

(Note: this is where new maps are added for new seasons.)

## Pattern Submodule

Like the maps submodule, the patterns submodule provides patterns
that are usable by both golly-python and golly-js. But this
submodule provides more generally useful patterns.

For example, here is how we would get a rabbit pattern and
place it in the middle of a 20 x 20 grid:

```
from gollymaps import patterns

grid = get_grid_pattern('rabbit', 20, 20, xoffset=10, yoffset=10, rotdeg=90)
url = pattern2url(grid)
print(url)
```

Dot diagrams

```
from gollymaps import patterns
print(patterns.get_patterns())
rabbit = get_pattern('rabbit', rotdeg=90)
```

(Incomplete) list of patterns available:

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

