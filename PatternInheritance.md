# Pattern Inheritance: Legacy Cups → Numeric Cups

The numeric cups heavily reuse pattern functions from legacy cups, though some get renamed in the process.

## Hellmouth → II Cup

The II cup imports **18 patterns** from `hellmouth.py` and keeps them under the **same names**:

`bigsegment`, `eightpi`, `eightr`, `fourrabbits`, `quadjustyna`, `random`, `randompartition`, `randommethuselahs`, `randomsegment`, `spaceshipcluster`, `spaceshipcrash`, `spaceshipsegment`, `switchengines`, `spiders`, `crabs`, `twoacorn`, `twomultum`, `twospaceshipgenerators`

It also adds a few with new names (e.g., `timebomb_oscillators_twocolor` → `"classictimebomb"`).

## Toroidal → II Cup

5 toroidal patterns are imported into II, but **3 are renamed**:

| Toroidal name | II cup name |
|---|---|
| `donutmath` | `hellmath` |
| `donuttimebomb` | `helltimebomb` |
| `donuttimebombredux` | `helltimebombredux` |
| `doublegaussian` | `doublegaussian` (same) |
| `porchlights` | `porchlights` (same) |

## Toroidal → VI Cup

4 toroidal patterns imported, **2 renamed**:

| Toroidal name | VI cup name |
|---|---|
| `donutmath` | `hellmath` |
| `donutrandom` | `random` |
| `doublegaussian` | `gaussian` |
| `porchlights` | `porchlights` (same) |

## Star (legacy) → Star-VII (Peninsula)

**All 18** star patterns are inherited directly into star-vii via `get_star_pattern_function_map()`, keeping the same names. Star-vii then adds ~10 new patterns on top.

## How It Works

The sharing happens at the **code import level** (direct function imports in `ii.py`, `vi.py`, `star_vii.py`), not through the registry. The registry keeps legacy and numeric cups as separate entries, but the numeric cup modules pull in the actual generator functions from legacy modules and wire them into their own pattern maps.
