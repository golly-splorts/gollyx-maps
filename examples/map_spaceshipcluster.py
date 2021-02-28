from golly_maps import maps

m = maps.get_map_realization('spaceshipcluster', rows=200, columns=240)
print("http://192.168.30.20:8888/simulator/index.html" + m['url'] + "&rows=200&cols=240&cellSize=4")
