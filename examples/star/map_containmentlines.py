from gollyx_maps import maps

rows = 160
cols = 240

#m = maps.get_map_realization("star", "precipitation", rows=rows, columns=cols)
m = maps.get_map_realization("star", "evaporation", rows=rows, columns=cols)
print(
    "http://192.168.30.20:8888/index.html"
    + m["url"]
    + f"&rows={rows}&cols={cols}&cellSize=3"
)

