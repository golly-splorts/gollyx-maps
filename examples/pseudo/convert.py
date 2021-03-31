from pprint import pprint
import json


s = '[{"30":[30,31],"31":[30],"32":[30],"33":[30]}]'

points = []
d = json.loads(s)[0]
for y in d:
    for x in d[y]:
        points.append((x, int(y)))

minx = min([p[0] for p in points])
miny = min([p[1] for p in points])

new_points = []
for x, y in points:
    new_points.append((x-minx, y-miny))

maxx = max([p[0] for p in new_points])
maxy = max([p[1] for p in new_points])

pattern = []
for iy in range(maxy+1):
    row = []
    for ix in range(maxx+1):
        if (ix, iy) in new_points:
            row.append('o')
        else:
            row.append('.')
    pattern.append(row)

for row in pattern:
    print("".join(row))
