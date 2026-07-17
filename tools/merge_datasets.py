# -*- coding: utf-8 -*-
"""
Fusiona datos curados con datos de NASA.
Prioridad: información curada + enriquecimiento de NASA (sin sobrescribir).
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def merge_datasets():
    """Fusiona atlas_bodies.csv + atlas_bodies_nasa_complete.csv."""
    curado_file = os.path.join(ROOT, "data", "atlas_bodies.csv")
    nasa_file = os.path.join(ROOT, "data", "atlas_bodies_nasa_complete.csv")
    output_file = os.path.join(ROOT, "data", "atlas_bodies_merged.csv")
    
    # Cargar curados (índice por nombre)
    curados = {}
    if os.path.exists(curado_file):
        with open(curado_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                curados[row.get("nombre", "").strip()] = row
    print(f"✅ Cargados {len(curados)} cuerpos curados")
    
    # Cargar NASA
    nasa_bodies = {}
    if os.path.exists(nasa_file):
        with open(nasa_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                nombre = row.get("nombre", "").strip()
                if nombre not in curados:  # Solo los nuevos
                    nasa_bodies[nombre] = row
    print(f"✅ Cargados {len(nasa_bodies)} exoplanetas nuevos de NASA")
    
    # Fusionar
    merged = []
    merged.extend(curados.values())
    merged.extend(nasa_bodies.values())
    
    # Guardar
    if merged:
        cols = list(merged[0].keys())
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(merged)
        print(f"✅ Fusión guardada: {len(merged)} total (curados: {len(curados)}, nuevos: {len(nasa_bodies)})")
        print(f"   → {output_file}")
        return len(merged)
    return 0

if __name__ == "__main__":
    merge_datasets()
