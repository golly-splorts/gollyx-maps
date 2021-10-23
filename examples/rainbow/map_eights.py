from gollyx_maps import maps

rows = 120
cols = 180

m = maps.get_map_realization("rainbow", "eights", rows=rows, columns=cols)
print(
    "http://192.168.30.20:8888/simulator/index.html"
    + m["url"]
    + f"&rows={rows}&cols={cols}&cellSize=3"
)
