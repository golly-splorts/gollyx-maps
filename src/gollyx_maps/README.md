# `gollyx-maps` Package Overview

This document provides an analysis of the `gollyx-maps` Python package, outlining the organization of its modules
and the functions they contain. The goal is to describe the current structure and identify logical groupings that
could inform future refactoring into submodules.

## Core API & Orchestration

The central entry point of the package.

- **`maps.py`**: This module acts as the primary interface for generating map realizations. The main function,
  `get_map_realization`, takes a "cup" name (e.g., `hellmouth`, `toroidal`) and a pattern name as input. It
  retrieves corresponding metadata (like map names and zone names) from the `data/` directory and calls the
  appropriate rendering function from the specialized map generation modules to produce the initial conditions for
  the cellular automata. It also handles calculating the appropriate `cellSize` for rendering.

## Map Generation Modules

These modules are responsible for creating the specific initial patterns for each cellular automata "cup." They all
expose a `get_<cup_name>_pattern_function_map()` function that returns a dictionary mapping human-readable pattern
names to their corresponding generator functions.

- **`hellmouth.py`**: Generates patterns for standard, two-color, bounded grids (B3/S23). It includes a wide
  variety of patterns, from random distributions (`random_twocolor`) to complex arrangements of oscillators,
  spaceships, and methuselahs (`spaceshipcrash_twocolor`, `timebomb_oscillators_twocolor`).

- **`toroidal.py`**: Generates patterns for two-color maps with toroidal (wrapping) boundary conditions. It
  features patterns designed for this topology, such as `donutmath_twocolor` which uses mathematical expressions
  that wrap around the grid.

- **`pseudo.py`**: Creates patterns for the B357/S238 rule. The patterns are built from a distinct set of
  methuselahs and oscillators suited for this rule, found in the `b357s238_patterns/` directory.

- **`dragon.py`**: Generates 1D, two-color patterns for the Dragon (B/S1) rule. Unlike other modules, its functions
  take the number of columns and partitions (`nparts`) as primary inputs.

- **`rainbow.py`**: The only module that generates four-color patterns. It includes unique multi-color designs like
  `sunburst_fourcolor` and `rainbowmath_fourcolor`.

- **`star.py`**: Creates patterns for the B2/S345c4 rule, also known as "Star Wars". It uses a specific set of
  patterns from the `b2s345c4_patterns/` directory.

- **`vi.py`**: Generates maps for the "VI" cup, which appears to be a mix of new, complex patterns
  (`detroit_carbomb`, `west_baltimore`) and patterns imported from other modules like `toroidal.py`.

- **`ii.py` & `klein.py`**: These modules are notable because they do not define their own pattern generation
  logic. Instead, they exclusively import and reuse functions from `hellmouth.py` and `toroidal.py`. This indicates
  a strong opportunity for consolidation, where a single module could provide base patterns that are reused across
  multiple cup configurations.

## Pattern Engine & Primitives

This group of modules and assets forms the foundation for building all map patterns.

- **`patterns.py`**: This is the core pattern-building engine. Its key responsibilities include:
    - Loading raw `.txt` pattern files from the various `*_patterns` directories (`get_pattern`).
    - Placing a named pattern onto a larger grid at a specific offset (`get_grid_pattern`).
    - Uniting multiple patterns into a single grid (`pattern_union`).
    - Procedurally generating complex structures like line segments (`segment_pattern`) and quadrant-based
      arrangements of methuselahs (`methuselah_quadrants_pattern`).

- **`*_patterns/` directories**: These folders (`b3s23_patterns`, `b357s238_patterns`, etc.) contain the raw `.txt`
  files that define the shape of the basic building blocks (oscillators, spaceships, etc.) used by the
  `patterns.py` module.

## Utilities

These modules provide essential, cross-cutting functionality.

- **`geom.py`**: Contains fundamental geometric transformation functions used throughout the package to manipulate
  patterns:
    - `hflip_pattern`: Flips a pattern horizontally.
    - `vflip_pattern`: Flips a pattern vertically.
    - `rot_pattern`: Rotates a pattern by 90, 180, or 270 degrees.

- **`utils.py`**:
    - `pattern2url`: A critical utility that converts a 2D grid of cells (`'o'` and `'.'`) into the compressed JSON
      list-of-coordinates format expected by the downstream application. This is the final step in generating the
      `initialConditions` strings.
    - `retry_on_failure`: A decorator used to automatically retry a map generation function if it fails due to a
      `GollyXPatternsError`, which can happen with procedurally generated patterns that don't fit the grid.

- **`error.py`**: Defines a set of custom exception classes (`GollyXMapsError`, `GollyXPatternNotFoundError`, etc.)
  for robust error handling.

## Proposed Submodule Structure

Based on this analysis, the code could be logically organized into the following submodules:

- **`gollyx_maps.maps`**: The high-level API, containing `maps.py` and the various map generation modules
  (`hellmouth`, `toroidal`, `pseudo`, etc.).
- **`gollyx_maps.patterns`**: The core pattern engine, containing `patterns.py` and the raw pattern assets.
- **`gollyx_maps.utils`**: A utilities module containing `geom.py`, `utils.py`, and `error.py`.
