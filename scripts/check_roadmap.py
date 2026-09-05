h = open("kiet_road_map.html").read()
assert "campus_accurate.geojson" not in h, "external labels still wired"
assert "renderAccurate" not in h, "renderAccurate still present"
assert "Esri" in h or "World_Imagery" in h, "satellite missing"
print("ROADMAP WIRED OK")
