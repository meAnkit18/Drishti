# KIET Terrain Integration — Experiment & Build Report

> Per `AGENT.md`: this file logs how the problem was solved, what was researched,
> what was tried, and what was built — so the full trail is preserved.

## 0. Request
User provided `kiet_real_terrain_package.zip` (Copernicus GLO-30 DSM + derivatives +
OSM boundary) and asked: use the terrain, run autonomous experiments/research,
and add an accurate terrain map on top of the existing road map.

## 1. Inventory of the terrain package (observed, not assumed)
- `data/terrain/raw/Copernicus_DSM_COG_10_N28_00_E077_00_DEM.tif` — 41,680,243 bytes,
  3600×3600 float32, 1 arc-sec (~30 m), tiepoint (0,0)→(77.0E, 29.0N), EPSG:4326.
  Pixel formula: `lon = 77 + col/3600`, `lat = 29 − row/3600`. Covers 77–78E, 28–29N.
- `data/terrain/clipped/*.tif` + `derived/*.tif` — all **20×13 px float32**,
  nodata −9999, 100 valid cells. Valid, but tiny (campus ≈ 500×400 m ≈ 16×13 cells).
- `derived/terrain_grid.json` — 13 rows × 20 cols = 260 cells, 100 valid elevations
  214.68–231.31 m, mean 219.22 m. **`slope_deg` is null for every cell** — slope grid
  exists only in `slope_degrees.tif`, not in the JSON.
- `derived/contours.geojson` — 13 lines at 4 levels (218.0, 221.33, 224.66, 227.98).
- `derived/low_points.geojson` — 10 cells ≤ p10 threshold 215.476 m.
- `derived/elevation_overlay.png` / `slope_overlay.png` — **20×13 px** direct grid renders.
- `derived/overlay_metadata.json` — raster bounds
  [[28.7506944, 77.4956944], [28.7543055, 77.50125]].
- `campus_osm.geojson` — 32-vertex OSM way 835252667 boundary (authoritative clip poly).
- Environment: **no GDAL, no rasterio** — PIL + numpy only. (Checked `gdalinfo` → missing,
  `import rasterio` → ModuleNotFound.)

## 2. Key accuracy judgment (research conclusion)
- 30 m DSM over a ~500 m campus gives ~100 usable cells. That resolves the
  broad SW→NE fall (~16 m across campus) but **cannot resolve individual roads,
  drains, or building pads**. Vertical LE90 <4 m is larger than most campus
  micro-relief. So: honest labels only — "broad fall direction + low pockets",
  never "flood depth" or "drainage engineering".
- DSM (surface) ≠ DTM (bare earth): cells over hostels/trees read high.
  The max 231.3 m cell is likely a building/vegetation hit, not ground.

## 3. Experiment log

### Exp1 — Verify raw DEM window vs package stats [DONE]
- Method: `PIL.Image.open` raw 3600×3600 float32 (~51 MB RAM, ok). Pixel math
  `col=(lon−77)*3600`, `row=(29−lat)*3600`. Window cols 1785:1805, rows 885:898
  for overlay bounds. Ray-cast point-in-polygon with the 32-vertex OSM boundary.
- Result: window 13×20=260 cells, min **214.6786** / max **231.3076** — exact match
  to package claim. Window mean 218.40 vs package polygon-masked 219.22.
  My independent polygon mask: n=101, mean 219.05, max 229.42 (package: n=100,
  mean 219.22, max 231.31). The 231.31 cell sits on the polygon edge — 1-cell
  masking difference, expected at 30 m resolution.
- Verdict: **package stats VERIFIED**. Pixel formula confirmed for all later work.
  Side-finding: max cell is an edge cell, likely a DSM building/vegetation hit.

### Exp2 — Recompute slope/hillshade, compare with package [DONE]
- Method: Horn's 3×3 slope on the 20×13 clipped grid, true metric cell size at
  28.7528°N (dx=27.11 m lon, dy=30.71 m lat). Hillshade az 315°/alt 45°.
  No GDAL/rasterio available — pure numpy.
- Result: my slope max **10.75°** / mean 4.54° vs package 14.36° / 5.21°.
  On 47 interior full-3×3 cells: mean abs diff 1.10°, max 4.87° (one edge cell).
  30 m-square-cell assumption barely changes it (max 10.95°).
- Verdict: **broad agreement, method-dependent details**. Package probably GDAL
  with different edge/nodata handling. Both say: gentle campus, a few moderate
  DSM-artifact cells at edges. Safe for 3-class visualization
  (flat <3° / gentle 3–8° / moderate >8°); unsafe for drainage engineering.
### Exp3 — High-res display overlays + smooth contours [DONE]
- Method: scipy `zoom(order=1)` ×40 → 800×520. Hillshade recomputed on the dense
  grid (az 315/alt 45), multiplied over a green→brown elevation ramp; nodata →
  transparent alpha. Slope classified flat <3° / gentle 3–8° / moderate >8°.
  Contours every 2 m via matplotlib on the dense grid, thinned 1:2, tagged
  "bilinear display smoothing — not survey".
- Result: `data/terrain_elevation_hillshade.png` (154 KB),
  `data/terrain_slope_class.png` (11 KB), `data/terrain_contours_smooth.geojson`
  (25 lines, 107 KB), `data/terrain_overlay_meta.json` (bounds + honesty note).
- Verdict: **display-quality good, source-truth preserved**. The 30 m blockiness
  is still faintly visible — deliberately kept, so nobody mistakes smoothing
  for accuracy. Pattern: high ground SW/center (~231 m), fall toward NE low
  pockets (~215 m) near the FC playground/SSB side.

## 4. What was built
- `scripts/` + `data/roads.geojson` + `data/campus.geojson` + `kiet_road_map.html`
  (earlier road map — untouched).
- **Exp3 outputs:** `data/terrain_elevation_hillshade.png` (800×520, hillshade-blended,
  transparent outside grid), `data/terrain_slope_class.png`,
  `data/terrain_contours_smooth.geojson` (25 lines @ 2 m, honesty-tagged),
  `data/terrain_overlay_meta.json`, plus staged copies `data/terrain_grid.json`
  (13×20, 100 valid), `data/terrain_low_points.geojson` (10),
  `data/terrain_contours_pkg.geojson` (13 package lines, kept for reference).
- **`kiet_terrain_map.html`** — Leaflet 1.9.4, same road hierarchy styling as the road
  map plus: elevation+hillshade overlay (on), slope class (off), smooth 2 m contours
  (on), low pockets (on), **click-anywhere elevation query** (nearest valid 30 m cell
  within ~25 m, popup shows `~X m ±4m`), combined layer control + legend, OSM and
  Copernicus attribution, `file://` fallback alert.
- `preview_terrain_map.png` — static combined render (this report's proof).
- Validation: all 4 road-map checks + terrain shell/content checks + `node --check`
  pass; bundle ≈ 550 KB.

## 5. How to run
```
cd /home/devdevil/development/drishti
python3 -m http.server 8000
# open http://localhost:8000/kiet_terrain_map.html
```

## 6. Honest limits (do not remove)
30 m DSM, ±4 m vertical, DSM≠bare earth, smoothing is display-only. Good for
"high SW → low NE + watch the 10 low pockets in monsoon". Not for drainage
design, flood depth, or construction — needs LiDAR/RTK survey.

## 7. 3D terrain view [DONE]
- Request: use ALL data, max effort, very accurate 3D terrain view.
- **Payload `data/terrain_3d.json` (323 KB):** 160×104 bilinear-sampled mesh
  (16,640 nodes) from the verified 20×13 source grid + validity mask; 45 in-bounds
  OSM roads with per-vertex sampled elevations; 31 building footprints with base
  elevation (min corner sample) and estimated heights (12 m default, 18 m for
  Saraswati/staff quarters); 25 smoothed 2 m contours with elevations; 12 labels
  + 10 low pockets with elevations.
- **Page `kiet_3d_terrain.html` (Three.js 0.160 via CDN):** vertex-colored terrain
  mesh (invalid faces dropped), extruded buildings, draped roads
  (orange/white/blue by class), purple contours, blue low-pocket spheres, HTML
  labels, sun + hemisphere lighting, orbit controls, **exaggeration slider 1–6×**,
  per-layer toggles, auto-rotate, reset view, **click-terrain elevation query**.
  Data smoothness verified first (max neighbor step 1.42 m — an early scary
  matplotlib preview was proven to be a NaN-triangulation artifact, not data).
- **Verified with real headless-Chrome renders** (3 iterations for camera framing):
  `preview_3d_browser.png` is an actual screenshot of the page, not a mockup.
- Run: `python3 -m http.server 8123` → `http://localhost:8123/kiet_3d_terrain.html`
  (needs internet once for the Three.js CDN).

## 8. file:// fix — standalone page [DONE]
- Symptom (user-reported): `Could not load data/terrain_3d.json` alert.
- Reproduced via headless Chrome on `file:///.../kiet_3d_terrain.html` — browsers
  block `fetch()` on file:// (CORS), so the data never loads. Root cause confirmed.
- Fix: `scripts/build_standalone_3d.py` embeds the payload into
  **`kiet_3d_standalone.html`** (293 KB, no fetch). Also upgraded the server
  version's error text to distinguish file:// (points to standalone) from bad
  server root. Verified: file:// screenshot of standalone is **pixel-identical**
  (md5 match) to the verified server render. User fix: double-click
  `kiet_3d_standalone.html` — no server needed (internet still needed once for
  the Three.js CDN).

## 9. Remove thin "tree" towers [DONE]
- Symptom (user-reported): tree-like objects in the 3D view.
- Diagnosis: small OSM structures (9 m² "big treat" kiosk, 25 m² "amul" shop,
  guard room, etc.) were all extruded to the 12 m default height, producing tall
  thin pillars that read as trees/poles.
- Fix: footprint-based heights (≤100 m²→4 m kiosk, ≤400 m²→8 m, default 12 m,
  hostels 18 m) written into `data/terrain_3d.json` (+`area_m2` per building),
  standalone rebuilt, verified by headless-Chrome screenshot — poles gone, low
  flat kiosks remain.

## 10. Remove floating "stick" lines at terrain edges [DONE]
- Symptom (user-reported): tree-like sticks into/out of the ground, still visible
  after §9. Zoomed headless-Chrome crops showed thin white lines floating past
  the terrain edge and lying on the dark base box — road/contour vertices inside
  the bounding box but OUTSIDE the valid DEM mask, floating in air like poles.
- Fix: clipped every road/contour polyline to the valid source-cell mask
  (all-4-neighbors-valid + half-cell edge erosion), splitting into valid runs
  (roads 45→30 segments, contour pts −33%). Before/after crops verified clean.

## 11. Static-hosting compat + deploy (Vercel & Render) [DONE]
- Compat: added `index.html` landing (root 404 otherwise), fixed `render.yaml`
  (dropped empty buildCommand), added `vercel.json` + `.vercelignore` (keeps the
  40 MB raw DEM out of Vercel deploys), verified zero absolute-path refs and all
  15 pages/assets return 200 locally.
- Vercel: imported meAnkit18/Drishti via dashboard (preset Other/static), production
  domain `https://drishti-sand.vercel.app` (plain `drishti.vercel.app` was taken by
  an older project). Note: hashed deployment URLs sit behind Vercel SSO login;
  the production domain is public. Verified 200s for /, 3D page, JSON.
- Render: new Static Site from repo, name Drishti, branch main, no build command,
  publish dir `.` — first deploy 21.7s, live at `https://drishti-cl8r.onrender.com`
  (verified 200s). Both hosts auto-redeploy on `main` pushes.
