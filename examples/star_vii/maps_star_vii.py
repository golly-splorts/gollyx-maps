from gollyx_maps import maps

rows = 180
cols = 280

#m = maps.get_map_realization("star_vii", "twochoochoo", rows=rows, columns=cols)
#m = maps.get_map_realization("star_vii", "candychoochoo", rows=rows, columns=cols)
#m = maps.get_map_realization("star_vii", "midnightexpress", rows=rows, columns=cols)
#m = maps.get_map_realization("star_vii", "spaceelevator", rows=rows, columns=cols)
#m = maps.get_map_realization("star_vii", "faradaycage", rows=rows, columns=cols)
#m = maps.get_map_realization("star_vii", "housewithears", rows=rows, columns=cols)
m = maps.get_map_realization("star_vii", "horsewithears", rows=rows, columns=cols)
#m = maps.get_map_realization("star_vii", "ironhorse", rows=rows, columns=cols)


print(
    "http://localhost:8000/simulator/index.html"
    + m["url"]
    + f"&rows={rows}&cols={cols}&cellSize=3"
)

