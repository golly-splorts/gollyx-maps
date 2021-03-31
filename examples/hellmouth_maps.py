from gollyx_maps import maps

print("")
print("Hellmouth map pattern examples:")
print("")

for pattern in maps.get_all_map_patterns('hellmouth'):
    print(f"{pattern}:")
    m = maps.get_map_realization('hellmouth', pattern)
    print(f"http://192.168.30.20:8888/simulator/index.html{m['url']}")
