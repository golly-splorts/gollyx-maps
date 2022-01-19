from gollyx_maps import maps

rows = 160
cols = 240

def main():
    #m = maps.get_map_realization("star", "squarestar", rows=rows, columns=cols)
    m = maps.get_map_realization("star", "kitchensink", rows=rows, columns=cols)
    #m = maps.get_map_realization("star", "ricepudding", rows=rows, columns=cols)
    #m = maps.get_map_realization("star", "fishsoup", rows=rows, columns=cols)
    
    print(
        "http://192.168.30.20:8888/index.html"
        + m["url"]
        + f"&rows={rows}&cols={cols}&cellSize=3"
    )

if __name__=="__main__":
    #import cProfile
    #cProfile.run('main()')
    main()
