from golly_maps import maps

rows = 200
cols = 240

m = maps.get_map_realization('spaceshipcrash', rows=rows, columns=cols)
print("http://192.168.30.20:8888/simulator/index.html" + m['url'] + f"&rows={rows}&cols={cols}&cellSize=4")

