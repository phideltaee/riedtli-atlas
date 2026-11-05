"""Pick the houses of the Wohnsiedlung Riedtli out of the OpenStreetMap buildings and write them as the estate.

Usage: python3 -I build_site.py <raw_dir> <estate_gwr_json> <out_json>

The estate is not new (1911-1919), so nothing is drawn from a plan: every OSM building outline that contains one of
the estate's points in the federal building register (data/estate/riedtli-gwr.json) becomes a house of the estate,
grouped by street. Its height comes from the register (storeys above ground: GASTW minus cellar and attic, 2-4) and
the roof is drawn as a hipped roof over the outline. The OSM ids are listed so build_geo.py leaves them out of the
plaster city.
"""
import json, math, sys, os, glob

LAT0, LON0 = 47.388078, 8.544738          # Kinkelstrasse 44, 8006 Zürich (GWR EGID 153391)
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 110574.0

# street -> row of the estate in the explorer (z1 ... z5)
GROUPS = {'Kinkelstrasse': 1, 'Stolzestrasse': 2, 'Winterthurerstrasse': 3, 'Riedtlistrasse': 4, 'Scheuchzerstrasse': 4,
          'Röslibrunnenweg': 5, 'Goetzstrasse': 5}


def proj(lat, lon):
    return ((lon - LON0) * KX, (lat - LAT0) * KY)


def pip(pt, ring):
    x, y = pt; inside = False
    for i in range(len(ring)):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % len(ring)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1:
            inside = not inside
    return inside


def area(ring):
    return sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring))) / 2.0


def main():
    raw, gwr, out = sys.argv[1:4]
    houses = json.load(open(gwr))['houses']
    for h in houses:
        h['xy'] = proj(h['lat'], h['lon'])
    seen, pieces, ids, hit = set(), [], [], {}
    for f in sorted(glob.glob(os.path.join(raw, 't[0-9][0-9].json'))):
        for el in json.load(open(f)).get('elements', []):
            if el['type'] != 'way' or (el['type'], el['id']) in seen or 'building' not in el.get('tags', {}):
                continue
            seen.add((el['type'], el['id']))
            ring = [proj(p['lat'], p['lon']) for p in el.get('geometry') or []]
            if len(ring) < 4:
                continue
            if ring[0] == ring[-1]:
                ring = ring[:-1]
            if abs(area(ring)) < 25:
                continue
            inside = [h for h in houses if pip(h['xy'], ring)]
            t = el['tags']
            if not inside:   # fall back to the address on the outline
                a = f"{t.get('addr:street', '')} {t.get('addr:housenumber', '')}"
                inside = [h for h in houses if h['adr'] == a]
            if not inside:
                continue
            if area(ring) < 0:
                ring = ring[::-1]
            st = max(2, min(4, max((h['storeys'] or 6) for h in inside) - 2))
            street = inside[0]['adr'].rsplit(' ', 1)[0]
            pieces.append({'z': GROUPS.get(street, 5), 'e': 1, 'k': 'h', 'fl': st, 'a': ', '.join(h['adr'] for h in inside),
                           'year': min(h['year'] for h in inside), 'flats': sum(h['flats'] or 0 for h in inside),
                           'ring': [[round(x, 2), round(y, 2)] for x, y in ring]})
            ids.append(el['id'])
            for h in inside:
                hit[h['adr']] = el['id']
    missing = [h['adr'] for h in houses if h['adr'] not in hit]
    pieces.sort(key=lambda p: (p['z'], p['a']))
    for i, p in enumerate(pieces):
        p['i'] = i
    site = {'source': 'OSM building outlines containing the GWR points of the Wohnsiedlung Riedtli (data/estate/riedtli-gwr.json)',
            'pieces': pieces, 'gaps': [], 'osm_ids': ids, 'missing': missing}
    json.dump(site, open(out, 'w'), ensure_ascii=False, indent=0)
    print('estate houses', len(pieces), 'flats', sum(p['flats'] for p in pieces), 'missing', missing)
    for z in range(1, 6):
        print('  z%d' % z, sum(1 for p in pieces if p['z'] == z), 'outlines')


if __name__ == '__main__':
    main()
