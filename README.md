# Drishti

Interactive 2D + 3D maps of the KIET campus (roads, buildings, real terrain).

## Open the maps (double-click, no server needed)
- `kiet_3d_standalone.html` — 3D terrain world (roads, buildings, contours, click-for-elevation)
- Or serve the folder: `python3 -m http.server 8123` → http://localhost:8123/kiet_3d_standalone.html
- 2D: `kiet_road_map.html` (roads), `kiet_terrain_map.html` (roads + terrain)

## Data
- `data/` — GeoJSON + terrain overlays used by the maps
- `kiet_campus_map/` — campus boundary reconstruction from screenshot
- `kiet_terrain/` — Copernicus GLO-30 DEM package (raw 30m tile + derivatives)
- `report.md` — full experiment/build log

Sources: © OpenStreetMap contributors · Terrain © DLR/Airbus/Copernicus.
Terrain is 30m DSM ±4m — broad relief only, not survey-grade.
