h = open("kiet_road_map.html").read()
assert "campus_accurate.geojson" in h, "accurate not wired"
assert "Esri" in h or "World_Imagery" in h, "satellite missing"
assert "Sanctioned" in h, "layers missing"
print("ROADMAP WIRED OK")
