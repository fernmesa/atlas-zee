# -*- coding: utf-8 -*-
"""
Busca patrones: ¿hay correlaciones entre familia ZEE y posición galáctica?
"""
import csv, os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_FILE = os.path.join(ROOT, "data", "atlas_bodies.csv")
STARS_FILE = os.path.join(ROOT, "data", "host_stars.csv")

# Coordenadas galactocéntricas de estrellas (de host_stars.csv)
STAR_COORDS = {}

def load_star_coords():
    """Carga RA/Dec/distancia de host_stars.csv"""
    try:
        with open(STARS_FILE, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row.get("sistema", "").strip()
                ra_horas = float(row.get("ra_horas", 0))
                dec = float(row.get("dec_grados", 0))
                dist = float(row.get("dist_ly", 0))
                ra_deg = ra_horas * 15.0  # convertir horas a grados
                STAR_COORDS[name] = (ra_deg, dec, dist)
    except Exception as e:
        print(f"[aviso] no se pudieron cargar coordenadas: {e}", file=sys.stderr)

def get_star_coords(sistema):
    """Retorna (RA, Dec, dist_ly) o None si no existe"""
    return STAR_COORDS.get(sistema.strip())

def analyze():
    load_star_coords()

    # Leer datos
    bodies = {}
    with open(DATA_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nombre = row.get("nombre", "").strip()
            sistema = row.get("sistema", "").strip()
            familia = row.get("exp_familia", "").strip()
            if not familia:
                # Si no hay exp_familia, usa las primeras 2 de: A M O V C G X
                familia = "X"
            bodies[nombre] = {
                "sistema": sistema,
                "familia": familia,
                "coords": get_star_coords(sistema)
            }

    # Agrupar por familia
    por_familia = {}
    for nombre, data in bodies.items():
        fam = data["familia"]
        if fam not in por_familia:
            por_familia[fam] = []
        if data["coords"]:
            por_familia[fam].append((nombre, data["coords"]))

    print("\n=== ANÁLISIS DE PATRONES GALÁCTICOS ===\n")

    print("DISTRIBUCIÓN POR FAMILIA:")
    for fam in sorted(por_familia.keys()):
        count = len(por_familia[fam])
        print(f"  {fam}: {count} cuerpos")

    print("\n\nDISTANCIA PROMEDIO AL CENTRO GALÁCTICO (supuesto en 8 kly):")
    centro = (0, 0)  # en coordenadas galactocéntricas simplificadas

    for fam in sorted(por_familia.keys()):
        if not por_familia[fam]:
            continue
        # Convertir RA/Dec/dist a galactocéntrico (simplificado)
        distancias = []
        for nombre, (ra, dec, dist_ly) in por_familia[fam]:
            # Proyección cartesiana simple (no es exacta, pero indica tendencia)
            x = dist_ly * math.cos(math.radians(dec)) * math.cos(math.radians(ra))
            y = dist_ly * math.cos(math.radians(dec)) * math.sin(math.radians(ra))
            z = dist_ly * math.sin(math.radians(dec))
            dist_al_centro = math.sqrt(x**2 + y**2 + z**2)
            distancias.append((nombre, dist_al_centro))

        if distancias:
            promedio = sum(d[1] for d in distancias) / len(distancias)
            minimo = min(d[1] for d in distancias)
            maximo = max(d[1] for d in distancias)
            print(f"  {fam}: promedio {promedio:.1f} ly, "
                  f"rango [{minimo:.1f} - {maximo:.1f}]")

    print("\n\nCLUSTERING (¿cuerpos de la misma familia están juntos?):")
    for fam in sorted(por_familia.keys()):
        if len(por_familia[fam]) < 2:
            continue
        # Distancia promedio entre pares de la misma familia
        distancias_internas = []
        items = por_familia[fam]
        for i, (n1, c1) in enumerate(items):
            for n2, c2 in items[i+1:]:
                ra1, dec1, d1 = c1
                ra2, dec2, d2 = c2
                # Distancia euclidiana en proyección cartesiana
                x1 = d1 * math.cos(math.radians(dec1)) * math.cos(math.radians(ra1))
                y1 = d1 * math.cos(math.radians(dec1)) * math.sin(math.radians(ra1))
                z1 = d1 * math.sin(math.radians(dec1))
                x2 = d2 * math.cos(math.radians(dec2)) * math.cos(math.radians(ra2))
                y2 = d2 * math.cos(math.radians(dec2)) * math.sin(math.radians(ra2))
                z2 = d2 * math.sin(math.radians(dec2))
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
                distancias_internas.append(dist)

        if distancias_internas:
            prom_interno = sum(distancias_internas) / len(distancias_internas)
            print(f"  {fam}: separación promedio entre pares = {prom_interno:.1f} ly")

    print("\n")

if __name__ == "__main__":
    analyze()
