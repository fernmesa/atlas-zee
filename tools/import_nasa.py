# -*- coding: utf-8 -*-
"""
Importador del NASA Exoplanet Archive -> data/atlas_bodies_imported.csv

Trae exoplanetas confirmados vía la API TAP (ADQL sobre la tabla `pscomppars`,
"Planetary Systems Composite Parameters"), los mapea al esquema de ATLAS y los
deja LISTOS para pasar por el pipeline con el proveedor de fórmula (sin experto).

Filosofía honesta:
  - El archivo NO trae composición atmosférica, agua ni vulcanismo para casi ningún
    planeta. Por eso importamos lo medible (masa, radio, insolación, parámetros
    estelares) y dejamos atmósfera/agua/vulcanismo en blanco -> la mayoría caerá en X
    con confianza BAJA. Es correcto: el catálogo entra en bruto y la comunidad
    (o el telescopio) rellena lo que falta.
  - Insolación del archivo viene en S_tierra (flujo relativo). La pasamos a W/m²
    multiplicando por la constante solar (1361 W/m²) para casar con nuestro esquema.

Uso:
    python tools/import_nasa.py                 # zona habitable (por defecto)
    python tools/import_nasa.py --all --limit 500
    python tools/import_nasa.py --offline muestra.csv   # usa un CSV ya descargado

Requiere solo la librería estándar (urllib). Sin dependencias externas.
"""
import argparse, csv, io, os, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
SOLAR_CONST = 1361.0  # W/m² a 1 AU de una estrella tipo Sol

# columnas del archivo -> significado
COLS = ("pl_name,hostname,pl_bmasse,pl_rade,pl_orbsmax,pl_insol,"
        "pl_orbeccen,st_teff,st_spectype,sy_dist")


def build_query(where, limit):
    adql = (f"select top {limit} {COLS} from pscomppars "
            f"where {where} order by pl_insol desc")
    return TAP + "?" + urllib.parse.urlencode({"query": adql, "format": "csv"})


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "ATLAS-importer/0.2"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def num(s):
    s = (s or "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def map_row(r):
    """Fila del archivo -> fila del esquema atlas_bodies.csv (sin valores de experto)."""
    ins_S = num(r.get("pl_insol"))                       # en S_tierra
    ins_W = round(ins_S * SOLAR_CONST, 1) if ins_S is not None else ""
    masa = num(r.get("pl_bmasse"))
    radio = num(r.get("pl_rade"))
    # nº de "fuentes": el archivo es una fuente; si hay masa Y radio medidos, contamos 2
    fuentes = "NASA_Exoplanet_Archive"
    if masa is not None and radio is not None:
        fuentes += ";transito+RV"
    return {
        "nombre": (r.get("pl_name") or "").replace(" ", "_"),
        "sistema": r.get("hostname", ""),
        "tipo": "Exoplaneta_importado",
        "masa_Me": masa if masa is not None else "",
        "radio_Re": radio if radio is not None else "",
        "dist_AU": num(r.get("pl_orbsmax")) or "",
        "insol_Wm2": ins_W,
        "atmosfera": "",          # el archivo no lo trae
        "agua": "",
        "vulcanismo": "",
        "exp_E": "", "exp_C": "", "exp_R": "",   # sin juicio experto -> usará fórmula
        "exp_familia": "",
        "confianza": "BAJA",
        "fuentes": fuentes,
        "notas": (f"Importado NASA Archive. Teff={r.get('st_teff','?')}K, "
                  f"tipo={r.get('st_spectype','?')}, ecc={r.get('pl_orbeccen','?')}. "
                  "Sin datos de atmósfera/agua: clasificación provisional."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="todos, no solo zona habitable")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--offline", help="ruta a un CSV ya descargado del archivo")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "atlas_bodies_imported.csv"))
    args = ap.parse_args()

    if args.offline:
        text = open(args.offline, encoding="utf-8").read()
    else:
        # zona habitable aproximada: insolación entre 0.2 y 2 veces la terrestre
        where = ("pl_insol between 0.2 and 2 and pl_rade < 2.5"
                 if not args.all else "pl_insol is not null")
        url = build_query(where, args.limit)
        print("Consultando NASA Exoplanet Archive...")
        try:
            text = fetch(url)
        except Exception as e:
            print(f"[ERROR] no se pudo consultar el archivo ({e}).")
            print("Sugerencia: descarga el CSV manualmente y usa --offline archivo.csv")
            sys.exit(2)

    reader = csv.DictReader(io.StringIO(text))
    rows = [map_row(r) for r in reader if (r.get("pl_name") or "").strip()]
    if not rows:
        print("[aviso] la consulta no devolvió filas.")
        sys.exit(1)

    cols = ["nombre","sistema","tipo","masa_Me","radio_Re","dist_AU","insol_Wm2",
            "atmosfera","agua","vulcanismo","exp_E","exp_C","exp_R","exp_familia",
            "confianza","fuentes","notas"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
    print(f"Importados {len(rows)} exoplanetas -> {args.out}")
    print("Siguiente: fusiónalo con data/atlas_bodies.csv o pásalo directo al pipeline.")


if __name__ == "__main__":
    main()
