#!/bin/bash
# Download the raw OpenStreetMap data for the board (Overpass, one query at a time with pauses).
# Usage: src/fetch_osm.sh <raw_dir>   (skips files that already exist)
set -u
Q="$(cd "$(dirname "$0")" && pwd)/queries"; RAW="$1"; mkdir -p "$RAW"
get() { # $1 query file, $2 output
  [ -s "$RAW/$2" ] && python3 -I -c "import json,sys;json.load(open(sys.argv[1]))" "$RAW/$2" 2>/dev/null && { echo "have $2"; return; }
  for try in 1 2 3 4; do
    curl -s -A "riedtli-atlas/1.0" --max-time 300 --data-urlencode "data@$Q/$1" https://overpass-api.de/api/interpreter -o "$RAW/$2.tmp"
    if python3 -I -c "import json,sys;d=json.load(open(sys.argv[1]));print(len(d['elements']))" "$RAW/$2.tmp" 2>/dev/null; then mv "$RAW/$2.tmp" "$RAW/$2"; echo "ok $2"; sleep 4; return; fi
    echo "retry $2 ($try)"; sleep $((15 * try))
  done
  echo "FAILED $2"
}
for i in $(seq -w 0 15); do get "qt$i.txt" "t$i.json"; done
get q_land.txt land.json
get q_points.txt points.json
get q_routes.txt routes_geom.json
