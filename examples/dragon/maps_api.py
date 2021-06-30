from gollyx_maps import maps

rows = 500
cols = 200

m = maps.get_map_realization("dragon", "starfield", rows=rows, columns=cols)
print(
    "http://192.168.30.20:8888/simulator/index.html"
    + m["url"]
    + f"&rows={rows}&cols={cols}"
)

