# Riedtli Quartier-Atlas

An open 3D neighbourhood model of **Unterstrass and Oberstrass (Zürich, Kreis 6)** around the
**Wohnsiedlung Riedtli**, the City of Zürich's garden-city estate from 1911–1919. A plaster-white city on a model board
with the estate's houses set in as birch wood: explore places, take guided walks, see what's on, and add what is missing.

*Ein offenes 3D-Quartiermodell von Unterstrass und Oberstrass rund um die städtische Wohnsiedlung Riedtli. Orte
entdecken, Rundgänge machen, Anlässe finden und Fehlendes ergänzen.*

**Live:** https://phideltaee.github.io/riedtli-atlas/

**Author:** Fidel Esquivel ([@phideltaee](https://github.com/phideltaee))

> **Unofficial.** An independent neighbourhood project, not affiliated with the City of Zürich or Liegenschaften
> Stadt Zürich. The estate's official page is
> [stadt-zuerich.ch: Wohnsiedlung Riedtli](https://www.stadt-zuerich.ch/de/planen-und-bauen/portfolio/bauten-anlagen/wohnbauten/wohnsiedlung-riedtli.html).
> *Inoffiziell: ein unabhängiges Nachbarschaftsprojekt, nicht mit der Stadt Zürich verbunden.*

## What's in it

| | |
|---|---|
| 3D model | OpenStreetMap buildings (heights from OSM levels or type defaults), land use, streets, rail, tram and street trees within 1.45 km |
| The estate | All 66 houses (291 flats) of the Wohnsiedlung Riedtli, grouped by street, with storeys from the federal building register and schematic hipped roofs |
| Places | 157 in 10 groups (Kitas, kindergartens and schools, playgrounds, parks, sport, culture, food and shops, community, health, mobility), each with a walking time from the estate, German and English text and a source |
| Walking routes | 146 pre-routed footpaths (OSRM) from Kinkelstrasse 44 to every place on the board |
| Walks | 4 guided routes: Kita morning & commute to Oerlikon, Saturday in the quarter, green loop to Irchelpark, up to Rigiblick |
| Events | 35, November 2026 – October 2027, with a month strip and regular events |
| Layers | trees, place names, walking-time rings, stops, tram lines 7, 9 and 10, drinking fountains, recycling points, bike and car sharing |
| Contribute | ideas for the estate plus "Fehlt ein Ort?": drop a pin and get a record to copy |
| Terrain | swissALTI3D heights (© swisstopo) on a 15 m grid, shown 1.5× exaggerated; "Relief" switch in the layers menu |
| Modes | German/English, light and dark UI, day and night model, phone layout |

## How it's built

One static HTML page, no server and no build tools beyond Python 3 (standard library). three.js 0.170 loads from
jsDelivr. The GitHub Pages workflow runs `assemble.py --public` on every push to `main`.

```
src/app.html          UI + three.js engine (template with __SCENE__/__CONTENT__/__ROUTES__/__OVERLAY__ placeholders)
src/assemble.py       injects the data into the template -> one HTML file (--public: GitHub Pages build)
src/fetch_osm.sh      downloads the raw OpenStreetMap data with the queries in src/queries (Overpass, cached)
src/build_site.py     OSM outlines + federal building register points -> data/site.json (the estate's houses)
src/build_geo.py      Overpass JSON + site.json -> data/scene.json
src/build_content.py  research JSON -> data/content.json (places, events, routed walks, tram lines)
src/build_routes.py   OSRM walking routes from the estate -> data/routes.json (cached); sets the walking minutes
src/build_terrain.py  swisstopo profile service (swissALTI3D) -> data/terrain.json (height grid in model metres)
data/estate/          the estate's addresses and register points (GWR)
data/research/*.json  researched places, events and walk suggestions, each with a source
```

```bash
python3 -I src/assemble.py src/app.html data/scene.json data/content.json data/routes.json index.html --public
```

Rebuilding the 3D city needs the raw OpenStreetMap downloads (about 15 MB, not in the repo): `src/fetch_osm.sh <raw dir>`,
then `build_site.py` and `build_geo.py`. New or corrected places go into `data/research/*.json`, then
`build_content.py`, `build_routes.py` and `assemble.py`.

## How the estate was found

The city lists the estate's addresses (Goetzstrasse 4–12, Kinkelstrasse 44–60, Riedtlistrasse 65–85,
Röslibrunnenweg 1–10, Scheuchzerstrasse 82–102, Stolzestrasse 14–46, Winterthurerstrasse 27–55). The federal building
register (GWR, `api3.geo.admin.ch`, layer `ch.bfs.gebaeude_wohnungs_register`) has a point for each of the 66 houses,
with year of construction, number of flats (291 in total) and storeys. `build_site.py` takes every OpenStreetMap
building outline that contains one of those points; all 66 matched one to one. Heights use 3.15 m per storey; the
roofs are drawn as hipped roofs and are schematic.

## Credits and data

- Map data © OpenStreetMap contributors, ODbL. Routing: OSRM (routing.openstreetmap.de). Building points: GWR / swisstopo.
- Terrain: swissALTI3D, © swisstopo (geo.admin.ch profile service).
- Estate: City of Zürich, estate page and Siedlungsdokumentation Nr. 2 (2012).
- Places and events: City of Zürich open data, community centres, parishes and associations (each record has a `source`).
  Opening hours and dates change; check the source before you go.
- Code: MIT (see `LICENSE`), adapted from the [Binzmühle Quartier-Atlas](https://github.com/phideltaee/binzmuehle-atlas)
  and the [Koch-Quartier Atlas](https://github.com/phideltaee/koch-atlas).

Missing or wrong? Open an [issue](https://github.com/phideltaee/riedtli-atlas/issues) or use "Fehlt ein Ort?" in the map.
