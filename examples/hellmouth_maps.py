from gollyx_maps import maps

print("")
print("Hellmouth map pattern examples:")
print("")

for pattern in maps.get_all_map_patterns('hellmouth'):
    print(f"{pattern}:")
    m = maps.get_map_realization('hellmouth', pattern)
    print(f"https://v.golly.life/simulator/index.html{m['url']}")
