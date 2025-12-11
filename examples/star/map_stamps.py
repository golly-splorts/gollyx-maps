from gollyx_maps import maps
from gollyx_maps.patterns import get_pattern_size, get_grid_pattern, pattern_union
from gollyx_maps.utils import pattern2url

rows = 160
cols = 240

def maps():
    #m = maps.get_map_realization("star", "squarestar", rows=rows, columns=cols)
    m = maps.get_map_realization("star", "kitchensink", rows=rows, columns=cols)
    #m = maps.get_map_realization("star", "ricepudding", rows=rows, columns=cols)
    #m = maps.get_map_realization("star", "fishsoup", rows=rows, columns=cols)
    
    print(
        "?" + m["url"] + f"&rows={rows}&cols={cols}&cellSize=3"
    )


def stamps():

    centerx1 = cols//2 + cols//4
    centery1 = rows//2

    centerx2 = cols//4
    centery2 = rows//2

    pattern1 = get_grid_pattern('scaffoldunfusing', rows, cols, xoffset=centerx1+5, yoffset=centery1+5)
    pattern2 = get_grid_pattern('scaffoldunfusing', rows, cols, xoffset=centerx2,   yoffset=centery2, hflip=True)

    s1 = pattern2url(pattern1)
    s2 = pattern2url(pattern2)

    url = f"?s1={s1}&s2={s2}"
    print(url)


if __name__=="__main__":
    stamps()
