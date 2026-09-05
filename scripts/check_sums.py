import json, csv
acc = json.load(open("data/campus_accurate.geojson"))
b = [f for f in acc["features"] if f["properties"].get("kind")=="sanctioned_building"]
s = sum(f["properties"].get("footprint_sqm",0) for f in b if "demolish" not in f["properties"].get("sanctioned_name",""))
print(f"buildings {len(b)} footprint sum {s:.2f}")
assert 8000 < s < 25000, f"footprint sum {s} outside sanity vs coverage 20801"
rows = list(open("data/blocks_centroids.csv"))
assert len(rows) >= 15, "csv too few rows"
print("SUMS OK")
