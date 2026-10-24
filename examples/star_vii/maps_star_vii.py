from gollyx_maps import maps

rows = 180
cols = 280

#m = maps.get_map_realization("star-vii", "twochoochoo", rows=rows, columns=cols)
#m = maps.get_map_realization("star-vii", "candychoochoo", rows=rows, columns=cols)
#m = maps.get_map_realization("star-vii", "midnightexpress", rows=rows, columns=cols)
#m = maps.get_map_realization("star-vii", "spaceelevator", rows=rows, columns=cols)
#m = maps.get_map_realization("star-vii", "faradaycage", rows=rows, columns=cols)
#m = maps.get_map_realization("star-vii", "housewithears", rows=rows, columns=cols)
#m = maps.get_map_realization("star-vii", "horsewithears", rows=rows, columns=cols)
#m = maps.get_map_realization("star-vii", "ironhorse", rows=rows, columns=cols)
m = maps.get_map_realization("star-vii", "deadendterminal", rows=rows, columns=cols)
#m = maps.get_map_realization("star-vii", "bando", rows=rows, columns=cols)


print(
    "http://localhost:8000/simulator/index.html"
    + m["url"]
    + f"&rows={rows}&cols={cols}&cellSize=3"
)

