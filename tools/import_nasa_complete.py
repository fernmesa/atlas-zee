# -*- coding: utf-8 -*-
"""
Importador avanzado de NASA Exoplanet Archive
Trae TODOS los exoplanetas confirmados con máxima información disponible.
Enriquece los datos existentes sin sobrescribir información curada.
"""
import csv, io, os, sys, urllib.parse, urllib.request, json
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
SOLAR_CONST = 1361.0  # W/m²

# Campos ricos disponibles en NASA Archive
COLS = ("pl_name,hostname,pl_bmasse,pl_rade,pl_orbsmax,pl_orbper,pl_insol,"
        "pl_eqt,pl_orbeccen,st_teff,st_spectype,sy_dist,sy_vmag,discoverymethod,"
        "disc_year,pl_pnum")

def fetch_nasa(limit=5000):
    """Descarga exoplanetas de NASA (sin límite de zona habitable)."""
    adql = (f"select top {limit} {COLS} from pscomppars "
            f"where pl_name is not null order by disc_year desc, pl_insol desc")
    url = TAP + "?" + urllib.parse.urlencode({"query": adql, "format": "csv"})
    print(f"Descargando hasta {limit} exoplanetas de NASA...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ATLAS-v0.2"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"Error: {e}")
        return None

def num(s):
    try:
        return float((s or "").strip()) if (s or "").strip() else None
    except:
        return None

def map_row(r):
    """Fila NASA → esquema ATLAS enriquecido."""
    masa = num(r.get("pl_bmasse"))
    radio = num(r.get("pl_rade"))
    insol_S = num(r.get("pl_insol"))
    temp_eq = num(r.get("pl_eqt"))
    periodo = num(r.get("pl_orbper"))
    dist = num(r.get("sy_dist"))
    teff = num(r.get("st_teff"))
    
    insol_W = insol_S * SOLAR_CONST if insol_S else None
    
    return {
        "nombre": (r.get("pl_name") or "").replace(" ", "_"),
        "sistema": r.get("hostname", ""),
        "tipo": "Exoplaneta_NASA_" + (r.get("discoverymethod", "unknown") or "unknown"),
        "masa_Me": masa,
        "radio_Re": radio,
        "dist_AU": num(r.get("pl_orbsmax")),
        "insol_Wm2": insol_W,
        "temp_eq_K": temp_eq,
        "periodo_dias": periodo,
        "excentricidad": num(r.get("pl_orbeccen")),
        "atmosfera": "",
        "agua": "",
        "vulcanismo": "",
        "exp_E": "", "exp_C": "", "exp_R": "",
        "exp_familia": "",
        "confianza": "MEDIA" if masa and radio else "BAJA",
        "fuentes": f"NASA_Archive;metodo={r.get('discoverymethod', '?')}",
        "notas": (f"Descubierto {r.get('disc_year', '?')}. "
                  f"Teff={teff}K, dist={dist}ly. "
                  f"Ref: https://exoplanetarchive.ipac.caltech.edu/"),
    }

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=5000, help="Máximo exoplanetas (default 5000)")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "atlas_bodies_nasa_complete.csv"))
    args = ap.parse_args()

    text = fetch_nasa(args.limit)
    if not text:
        print("No se pudieron obtener datos.")
        sys.exit(1)

    reader = csv.DictReader(io.StringIO(text))
    rows = [map_row(r) for r in reader if (r.get("pl_name") or "").strip()]
    
    if not rows:
        print("Sin filas procesadas.")
        sys.exit(1)

    cols = ["nombre","sistema","tipo","masa_Me","radio_Re","dist_AU","insol_Wm2",
            "temp_eq_K","periodo_dias","excentricidad","atmosfera","agua","vulcanismo",
            "exp_E","exp_C","exp_R","exp_familia","confianza","fuentes","notas"]
    
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"✅ Importados {len(rows)} exoplanetas → {args.out}")
    print(f"📊 Estadísticas:")
    print(f"  - Con masa: {sum(1 for r in rows if r['masa_Me'])}")
    print(f"  - Con radio: {sum(1 for r in rows if r['radio_Re'])}")
    print(f"  - En zona habitable (~0.25-4 W/m²): {sum(1 for r in rows if r['insol_Wm2'] and 0.25*1361 < r['insol_Wm2'] < 4*1361)}")
    print(f"\nPróximo: fusion con data/atlas_bodies.csv para obtener vista consolidada.")

if __name__ == "__main__":
    main()
