from gollyx_maps import maps


# A list of all patterns ever
TOROIDAL_PATTERNS = [
    "crabdonuts",
    "randys",
    "porchlights",
    "donutmethuselahs",
    "donutpi",
    "doublegaussian",
    "donutcore",
    "quadjustyna",
    "donutrandom",
    "donutrandompartition",
    "donuttimebomb",
    "donuttimebombredux",
    "donutmultums",
    "bigsegment",
    "randomsegment",
    "donutmath",
]


rows = 40
cols = 240

for pattern in TOROIDAL_PATTERNS:

    print(f'Pattern: {pattern}')
    for i in range(25):
        m = maps.get_map_realization("toroidal", pattern, rows=rows, columns=cols)

    #print('---------------')
    #print(f'Pattern: {pattern}')
    #m = maps.get_map_realization("toroidal", pattern, rows=rows, columns=cols)
    #print(
    #    "http://192.168.30.20:8888/simulator/index.html"
    #    + m["url"]
    #    + f"&rows={rows}&cols={cols}&cellSize=3"
    #)

