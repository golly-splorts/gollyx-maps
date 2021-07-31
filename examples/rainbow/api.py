from gollyx_maps.maps import render_map
from gollyx_maps.rainbow import get_rainbow_pattern_function_map


rows = 120
columns = 200


patternmap = get_rainbow_pattern_function_map()
patternnames = list(patternmap.keys())

for patternname in patternnames:

    print(f"\nURL for map {patternname}:")
    s1, s2, s3, s4 = render_map('rainbow', patternname, rows, columns)

    url = f"?s1={s1}&s2={s2}&s3={s3}&s4={s4}"
    print(f"http://192.168.30.20:8888/simulator/index.html{url}")

    # If you run these simulations,
    # you should see the exact same scores,
    # but assigned to different teams
    #url = f"?s1={s2}&s2={s3}&s3={s4}&s4={s1}"
    #print(f"http://192.168.30.20:8888/simulator/index.html{url}")

    #url = f"?s1={s2}&s2={s4}&s3={s3}&s4={s1}"
    #print(f"http://192.168.30.20:8888/simulator/index.html{url}")

    #url = f"?s1={s4}&s2={s3}&s3={s2}&s4={s1}"
    #print(f"http://192.168.30.20:8888/simulator/index.html{url}")

