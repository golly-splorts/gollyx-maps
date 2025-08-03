from gollyx_maps import maps

print("")
print("ii (toroidal + hellmouth) map pattern examples:")
print("")

for pattern in maps.get_all_map_patterns('ii'):
    print(f"{pattern}:")
    m = maps.get_map_realization('ii', pattern)
    print(f"https://v.golly.life/simulator/index.html{m['url']}")

