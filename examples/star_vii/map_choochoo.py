from gollyx_maps import maps

rows = 180
cols = 280

m = maps.get_map_realization("star_vii", "choochoo", rows=rows, columns=cols)

print(
    "http://localhost:8000/simulator/index.html"
    + m["url"]
    + f"&rows={rows}&cols={cols}&cellSize=3"
)

