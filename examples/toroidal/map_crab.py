from gollyx_maps import maps

rows = 40
cols = 240

m = maps.get_map_realization("toroidal", "crabdonuts", rows=rows, columns=cols)
print(
    "http://192.168.30.20:8888/simulator/index.html"
    + m["url"]
    + f"&rows={rows}&cols={cols}&cellSize=3"
)

