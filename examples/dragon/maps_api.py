from gollyx_maps import maps

rows = 500
cols = 200

patternNames = [
    "starfield",
    "supercritical",
    "vector",
    "lake",
    "lighthouse",
    "isotropic",
    "matrix",
    "waterfall",
    "river",
    "towers",
]

patternNames = ["towers"]

for patternName in patternNames:
    m = maps.get_map_realization("dragon", patternName, rows=rows, columns=cols)
    print("")
    print("Map: " + m['mapName'])
    print("State 1:", m["initialConditions1"])
    print("State 2:", m["initialConditions2"])
    print(
        "http://192.168.30.20:8888/simulator/index.html"
        + m["url"]
        + f"&rows={rows}&cols={cols}"
    )

