# -*- coding: utf-8 -*-
"""
Analisis de patrones galacticos expandido.
Busca correlaciones entre familia ZEE y posicion galactica en el dataset completo.
"""
import csv, os, sys, math, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_FILE = os.path.join(ROOT, "data", "atlas_bodies.csv")
STARS_FILE = os.path.join(ROOT, "data", "host_stars.csv")

STAR_COORDS = {}

def load_star_coords():
    """Carga RA/Dec/distancia"""
    if not os.path.exists(STARS_FILE):
        return 0
    try:
        with open(STARS_FILE, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row.get("sistema", "").strip()
                ra_h = float(row.get("ra_horas", 0))
                dec = float(row.get("dec_grados", 0))
                dist = float(row.get("dist_ly", 0))
                ra_deg = ra_h * 15.0
                STAR_COORDS[name] = (ra_deg, dec, dist)
        return len(STAR_COORDS)
    except Exception as e:
        print(f"WARNING: Error cargando coords: {e}", file=sys.stderr)
        return 0

def ra_dec_to_galactocentric(ra, dec, dist_ly):
    """Convierte RA/Dec/distancia a cartesianas."""
    ra_rad = math.radians(ra)
    dec_rad = math.radians(dec)
    x = dist_ly * math.cos(dec_rad) * math.cos(ra_rad)
    y = dist_ly * math.cos(dec_rad) * math.sin(ra_rad)
    z = dist_ly * math.sin(dec_rad)
    return x, y, z

def analyze():
    loaded_stars = load_star_coords()
    print("\n=== ATLAS PATTERN ANALYSIS ===\n")
    print(f"[*] Estrellas con coords: {loaded_stars}")

    # Leer datos
    bodies = {}
    families = set()
    with open(DATA_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nombre = row.get("nombre", "").strip()
            sistema = row.get("sistema", "").strip()
            familia = row.get("exp_familia", row.get("familia", "X")).strip()
            if not familia or familia == "":
                familia = "X"
            families.add(familia)
            coords = STAR_COORDS.get(sistema)
            bodies[nombre] = {
                "sistema": sistema,
                "familia": familia,
                "coords": coords,
                "ccm": float(row.get("exp_ccm", 0)) or 0
            }

    por_familia = {}
    for nombre, data in bodies.items():
        fam = data["familia"]
        if fam not in por_familia:
            por_familia[fam] = []
        if data["coords"]:
            por_familia[fam].append(data)

    print(f"\n[FAMILIAS]: {', '.join(sorted(families))}\n")

    print("DISTRIBUCION POR FAMILIA:")
    total_con_coords = sum(len(v) for v in por_familia.values())
    for fam in sorted(por_familia.keys()):
        count = len(por_familia[fam])
        pct = 100.0 * count / total_con_coords if total_con_coords > 0 else 0
        print(f"  {fam:2s}: {count:3d} cuerpos ({pct:5.1f}%)")

    print(f"\n[DISTANCIA AL CENTRO] (8 kly):")
    for fam in sorted(por_familia.keys()):
        if not por_familia[fam]:
            continue
        distancias = []
        for data in por_familia[fam]:
            if not data["coords"]:
                continue
            ra, dec, d = data["coords"]
            x, y, z = ra_dec_to_galactocentric(ra, dec, d)
            dist_centro = math.sqrt(x**2 + y**2 + z**2)
            distancias.append(dist_centro)
        if distancias:
            prom = sum(distancias) / len(distancias)
            minv = min(distancias)
            maxv = max(distancias)
            print(f"  {fam}: avg={prom:6.1f} ly  [min={minv:6.1f}, max={maxv:6.1f}]")

    print(f"\n[CLUSTERING] (separacion interna):")
    for fam in sorted(por_familia.keys()):
        if len(por_familia[fam]) < 2:
            continue
        items = por_familia[fam]
        distancias = []
        for i, d1 in enumerate(items):
            if not d1["coords"]:
                continue
            ra1, dec1, dist1 = d1["coords"]
            x1, y1, z1 = ra_dec_to_galactocentric(ra1, dec1, dist1)
            for d2 in items[i+1:]:
                if not d2["coords"]:
                    continue
                ra2, dec2, dist2 = d2["coords"]
                x2, y2, z2 = ra_dec_to_galactocentric(ra2, dec2, dist2)
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
                distancias.append(dist)
        if distancias:
            prom = sum(distancias) / len(distancias)
            print(f"  {fam}: separacion={prom:6.1f} ly (n={len(distancias)} pares)")

    print(f"\n[DESTACADOS] (CCM >= 5.0):")
    destacados = sorted(
        [(n, d["familia"], d["ccm"]) for n, d in bodies.items() if d["ccm"] >= 5.0],
        key=lambda x: -x[2]
    )
    for nombre, fam, ccm in destacados[:10]:
        print(f"  {fam} {ccm:5.1f}  {nombre}")

if __name__ == "__main__":
    analyze()
