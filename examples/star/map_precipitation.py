from gollyx_maps import maps

rows = 160
cols = 240

m = maps.get_map_realization("star", "precipitation", rows=rows, columns=cols)
print(
    "https://star.vii.integration.golly456.life/simulator/index.html"
    + m["url"]
    + f"&rows={rows}&cols={cols}&cellSize=3"
)

