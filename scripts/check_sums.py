import json, csv
acc = json.load(open("data/campus_accurate.geojson"))
b = [f for f in acc["features"] if f["properties"].get("kind")=="sanctioned_building"]
s = sum(f["properties"].get("footprint_sqm",0) for f in b if "demolish" not in f["properties"].get("sanctioned_name",""))
print(f"buildings {len(b)} footprint sum {s:.2f}")
assert 8000 < s < 25000, f"footprint sum {s} outside sanity vs coverage 20801"
pk = [f for f in acc["features"] if f["properties"].get("kind")=="parking"]
ps = sum(f["properties"].get("area_sqm",0) for f in pk)
print(f"parking {len(pk)} area sum {ps:.2f} vs sanctioned 20232.12")
assert len(pk) >= 15, f"parking pockets {len(pk)} < 15"
assert 15000 < ps < 26000, f"parking sum {ps} outside tolerance vs 20232.12"
so = [f for f in acc["features"] if f["properties"].get("kind")=="solar"]
print(f"solar belts {len(so)}")
assert len(so) >= 8, "solar too few"
rd = [f for f in acc["features"] if f["properties"].get("kind")=="road_sanctioned"]
print(f"sanctioned roads {len(rd)}")
assert len(rd) >= 4, "roads too few"
rows = list(open("data/blocks_centroids.csv"))
assert len(rows) >= 15, "csv too few rows"
print("SUMS OK")
