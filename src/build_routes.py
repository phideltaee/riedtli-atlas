"""Pre-route a walking path from the Wohnsiedlung Riedtli (Kinkelstrasse 44) to every place on the board (OSRM foot). Cached.
Usage: python3 -I build_routes.py <content_json> <routes_json>"""
import json, math, sys, os, time, urllib.request
LAT0, LON0 = 47.388078, 8.544738
KX = 111320.0 * math.cos(math.radians(LAT0)); KY = 110574.0
HOME = (47.388078, 8.544738)    # Kinkelstrasse 44, 8006 Zürich (GWR EGID 153391)
content, out = sys.argv[1], sys.argv[2]
d = json.load(open(content))
cache = json.load(open(out)) if os.path.exists(out) else {}
todo = [p for p in d['pois'] if not p.get('out') and p['id'] not in cache]
print('to route', len(todo))
for i, p in enumerate(todo):
    lat, lon = LAT0 + p['y'] / KY, LON0 + p['x'] / KX
    url = f"https://routing.openstreetmap.de/routed-foot/route/v1/foot/{HOME[1]},{HOME[0]};{lon},{lat}?overview=full&geometries=geojson"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'riedtli-atlas/1.0'}), timeout=40) as r:
                rt = json.load(r)['routes'][0]
            pts = []
            for lo, la in rt['geometry']['coordinates']:
                x, y = (lo - LON0) * KX, (la - LAT0) * KY
                if not pts or math.hypot(x - pts[-1][0], y - pts[-1][1]) > 2:
                    pts.append([round(x, 1), round(y, 1)])
            cache[p['id']] = {'p': pts, 'd': round(rt['distance'])}
            break
        except Exception as ex:
            print('retry', p['id'], ex); time.sleep(3 + 3 * attempt)
    if i % 20 == 0:
        json.dump(cache, open(out, 'w'), separators=(',', ':')); print(i, p['id'])
    time.sleep(1.1)
json.dump(cache, open(out, 'w'), separators=(',', ':'))
print('done', len(cache), round(os.path.getsize(out) / 1024), 'KB')
# walking minutes on the place cards follow the routed distance (75 m per minute)
changed = 0
for p in d['pois']:
    r = cache.get(p['id'])
    if r and not p.get('out'):
        w = max(1, round(r['d'] / 75))
        if p.get('w') != w:
            p['w'] = w; changed += 1
d['pois'].sort(key=lambda r: (r['w'] if r['w'] is not None else 999))
json.dump(d, open(content, 'w'), ensure_ascii=False, separators=(',', ':'))
print('walking minutes updated from the routes:', changed)
