h = open("kiet_terrain_map.html").read()
assert "campus_accurate" not in h, "terrain still wired to external labels"
t = open("kiet_3d_standalone.html", encoding="utf-8", errors="ignore").read()
assert "campus_accurate" in t, "3D lost accurate overlay"
print("ALLMAPS OK")
