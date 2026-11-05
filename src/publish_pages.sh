#!/bin/bash
# Publish the public build to the gh-pages branch; GitHub Pages serves that branch (Settings > Pages > Deploy from a branch).
# Usage: src/publish_pages.sh   (from a clean checkout of main; builds with assemble.py --public, no personal overlay)
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d)
python3 -I src/assemble.py src/app.html data/scene.json data/content.json data/routes.json "$T/index.html" --public
touch "$T/.nojekyll"
git -C "$T" init -q -b gh-pages
git -C "$T" add -A
git -C "$T" commit -q -m "Public build from main $(git rev-parse --short HEAD)"
git -C "$T" push -q -f "$(git remote get-url origin)" gh-pages   # gh-pages holds only the latest build
rm -rf "$T"
echo "pushed gh-pages; https://phideltaee.github.io/riedtli-atlas/ updates in about a minute"
