from gollyx_maps import maps


for rows, cols, cellsize in [(100, 120, 7), (200, 240, 4)]:

    print("")
    print("")
    print(f"Grid: {rows} x {cols}")
    print("")
    print("")

    print("-----------------")
    print("Original:")
    
    m = maps.get_map_realization("timebomb", rows=rows, columns=cols)
    print(
        "http://192.168.30.20:8888/simulator/index.html"
        + m["url"]
        + f"&rows={rows}&cols={cols}&cellSize={cellsize}"
    )
    
    print("-----------------")
    print("Redux:")
    
    m = maps.get_map_realization("timebombredux", rows=rows, columns=cols)
    print(
        "http://192.168.30.20:8888/simulator/index.html"
        + m["url"]
        + f"&rows={rows}&cols={cols}&cellSize={cellsize}"
    )
