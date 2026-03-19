from gollyx_maps import maps

rows = 160
cols = 240

m = maps.get_map_realization("star", "newyork", rows=rows, columns=cols)
print(
    "http://localhost:8000/simulator/index.html"
    + m["url"]
    + f"&rows={rows}&cols={cols}&cellSize=3"
)
