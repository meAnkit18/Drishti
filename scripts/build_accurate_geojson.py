import json, math
# Anchors WGS84
A_LAT, A_LON = 28.75257, 77.49851
# Local ENU origin at A-Block SE corner; x=east(m), y=north(m)
# Control points: (e, n, lat, lon) - 6 pts from sanctioned dims + satellite
CONTROLS = [
    (0.0, 0.0, 28.752441, 77.49902),      # A-Block SE (gate)
    (-45.70, 0.0, 28.752441, 77.49855),   # A-Block SW (45.70m west)
    (-45.70, 45.00, 28.752845, 77.49855), # A-Block NW
    (0.0, 45.00, 28.752845, 77.49902),    # A-Block NE
    (-120.0, 180.0, 28.75406, 77.49775),  # Railway north edge approx
    (-200.0, 90.0, 28.75325, 77.49690),   # Girls hostel west approx
]
def solve_affine(pts):
    # Solve lon = ax*e + bx*n + cx, lat = ay*e + by*n + cy via least squares (normal eq, 3x3)
    import copy
    def lstsq(M, Y):
        # M Nx3, Y N -> 3 coeffs
        MtM = [[0.0]*3 for _ in range(3)]
        MtY = [0.0]*3
        for i in range(len(M)):
            for a in range(3):
                MtY[a] += M[i][a]*Y[i]
                for b in range(3):
                    MtM[a][b] += M[i][a]*M[i][b]
        # invert 3x3
        def inv3(m):
            det = (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
            assert abs(det) > 1e-18, "singular controls"
            adj = [[0.0]*3 for _ in range(3)]
            adj[0][0]=(m[1][1]*m[2][2]-m[1][2]*m[2][1])/det
            adj[0][1]=-(m[0][1]*m[2][2]-m[0][2]*m[2][1])/det
            adj[0][2]=(m[0][1]*m[1][2]-m[0][2]*m[1][1])/det
            adj[1][0]=-(m[1][0]*m[2][2]-m[1][2]*m[2][0])/det
            adj[1][1]=(m[0][0]*m[2][2]-m[0][2]*m[2][0])/det
            adj[1][2]=-(m[0][0]*m[1][2]-m[0][2]*m[1][0])/det
            adj[2][0]=(m[1][0]*m[2][1]-m[1][1]*m[2][0])/det
            adj[2][1]=-(m[0][0]*m[2][1]-m[0][1]*m[2][0])/det
            adj[2][2]=(m[0][0]*m[1][1]-m[0][1]*m[1][0])/det
            return adj
        inv = inv3(MtM)
        return [sum(inv[a][b]*MtY[b] for b in range(3)) for a in range(3)]
    M = [[e, n, 1.0] for e, n, la, lo in pts]
    clo = lstsq(M, [lo for e, n, la, lo in pts])
    cla = lstsq(M, [la for e, n, la, lo in pts])
    return clo, cla
CLO, CLA = solve_affine(CONTROLS)
def ENU_to_WGS84(e, n):
    lon = CLO[0]*e + CLO[1]*n + CLO[2]
    lat = CLA[0]*e + CLA[1]*n + CLA[2]
    return (round(lon, 5), round(lat, 5))
def rect(e0, n0, w, h):
    pts = [(e0,n0),(e0+w,n0),(e0+w,n0+h),(e0,n0+h),(e0,n0)]
    return [ENU_to_WGS84(e,n) for e,n in pts]
def build_accurate():
    feats = []
    # A-Block G+2 45.00x45.70 at origin
    feats.append({"type":"Feature","properties":{"kind":"sanctioned_building","sanctioned_name":"A","floors":"G+2","footprint_sqm":45.00*45.70,"confidence":"high","source":"11.jpeg 45.00x45.70"},"geometry":{"type":"Polygon","coordinates":[rect(-45.70,0.0,45.70,45.00)]}})
    # E-Block G+5 approx 40.23 frontage, 35m deep, 90m NW of A
    feats.append({"type":"Feature","properties":{"kind":"sanctioned_building","sanctioned_name":"E","floors":"G+5","footprint_sqm":1400,"confidence":"medium","source":"14.jpeg 40.23"},"geometry":{"type":"Polygon","coordinates":[rect(-140.0,90.0,40.23,35.0)]}})
    # Z-Block G+8 new compounding 748.31 sqm, 26.80 long
    feats.append({"type":"Feature","properties":{"kind":"sanctioned_building","sanctioned_name":"Z","floors":"G+8","footprint_sqm":748.31,"confidence":"high","source":"area chart row6"},"geometry":{"type":"Polygon","coordinates":[rect(-90.0,20.0,26.80,27.93)]}})
    # Y-Block G+5 compounding 28.70 wide
    feats.append({"type":"Feature","properties":{"kind":"sanctioned_building","sanctioned_name":"Y","floors":"G+5","footprint_sqm":748.31,"confidence":"medium","source":"14.jpeg 28.70"},"geometry":{"type":"Polygon","coordinates":[rect(-120.0,55.0,28.70,26.0)]}})
    # D-Lecture star G+2 (3-blade approx, centroid near -70,60)
    cx, cy = -70.0, 60.0
    star = [(cx+9.55,cy),(cx+4,cy+4),(cx-4,cy+9),(cx-9.55,cy),(cx-4,cy-4),(cx+4,cy-9),(cx+9.55,cy)]
    feats.append({"type":"Feature","properties":{"kind":"sanctioned_building","sanctioned_name":"D","floors":"G+2","footprint_sqm":900,"confidence":"medium","source":"14.jpeg star 9.55"},"geometry":{"type":"Polygon","coordinates":[[ENU_to_WGS84(e,n) for e,n in star]]}})
    # F-Boys G+3, S-Boys, B-Boys, J-Girls 40.17, L-TBI G+4, U G+4, V G+5 44.34, X, Pharmacy I/J, Canteen, C-1 demolish 41.76
    blocks = [("F","G+3",-160,140,24.51,20,"14.jpeg"),("S","G+? ",-175,150,30,18,"5.jpeg 534.10"),("B","G+3",-130,110,25,18,"5.jpeg 61.10"),("J","G+1",-210,100,40.17,22,"1.jpeg 40.17"),("L","G+4",-150,70,22,20,"14.jpeg"),("U","G+4",-135,70,20,18,"14.jpeg"),("V","G+5",-125,45,44.34,28,"5.jpeg 44.34"),("X","G+1",-230,160,28.95,18,"5.jpeg"),("I","G+4",-165,155,35.16,18,"14.jpeg 35.16"),("PharmaJ","G+2",-150,155,40.90,16,"14.jpeg 40.90"),("Canteen","G+2",-40,55,15,8,"8.jpeg 3.30"),("C1-demolish","G",-110,170,41.76,4.4,"demolish 41.76x184.78")]
    for nm, fl, e0, n0, w, h, src in blocks:
        feats.append({"type":"Feature","properties":{"kind":"sanctioned_building","sanctioned_name":nm,"floors":fl,"footprint_sqm":round(w*h,2),"confidence":"medium","source":src},"geometry":{"type":"Polygon","coordinates":[rect(e0,n0,w,h)]}})
    # Khasra boundary approx (KIET core 280-282 + 286 strip)
    bnd = [(-240,200),(-40,200),(-40,180),(0,180),(0,-10),(-60,-10),(-60,20),(-240,20),(-240,200)]
    feats.append({"type":"Feature","properties":{"kind":"boundary_khasra","sanctioned_name":"KIET-khasra-280-282-286","confidence":"medium","source":"13.jpeg khasra"},"geometry":{"type":"Polygon","coordinates":[[ENU_to_WGS84(e,n) for e,n in bnd]]}})
    # Labels with centroids
    for f in [x for x in feats if x["properties"]["kind"]=="sanctioned_building"]:
        ring = f["geometry"]["coordinates"][0]
        lon = sum(p[0] for p in ring[:-1])/ (len(ring)-1)
        lat = sum(p[1] for p in ring[:-1])/ (len(ring)-1)
        feats.append({"type":"Feature","properties":{"kind":"label_accurate","sanctioned_name":f["properties"]["sanctioned_name"],"floors":f["properties"]["floors"],"lat":round(lat,5),"lon":round(lon,5)},"geometry":{"type":"Point","coordinates":[round(lon,5),round(lat,5)]}})
    fc = {"type":"FeatureCollection","name":"KIET sanctioned accurate","features":feats}
    json.dump(fc, open("data/campus_accurate.geojson","w"), indent=1)
    print(f"Wrote {len(feats)} feats")
if __name__ == "__main__":
    build_accurate()
