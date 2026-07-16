# -*- coding: utf-8 -*-
"""
ATLAS — ejecutor de línea de comandos.

Uso:
    python run.py                        # config por defecto -> salida a stdout + CSV
    python run.py --config config/default.json
    python run.py --scheme simple3       # sobreescribe el esquema sin editar la config
    python run.py --out mi_salida.csv

Sin dependencias externas: solo Python 3.8+ de serie. Clona y ejecuta.
"""
import argparse, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # permite importar atlas_core y layers al ejecutar directamente

from atlas_core import registry, pipeline  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Clasificador modular ATLAS")
    ap.add_argument("--config", default=os.path.join(HERE, "config", "default.json"))
    ap.add_argument("--data", default=os.path.join(HERE, "data", "atlas_bodies.csv"))
    ap.add_argument("--scheme", default=None, help="sobreescribe el esquema de la config")
    ap.add_argument("--provider", default=None, help="sobreescribe el proveedor de índices")
    ap.add_argument("--out", default=os.path.join(HERE, "salida_clasificacion.csv"))
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config = json.load(f)
    if args.scheme:   config["scheme"] = args.scheme
    if args.provider: config["index_provider"] = args.provider

    registry.discover()                       # carga todas las capas de layers/
    bodies = pipeline.load_bodies(args.data)
    results = pipeline.run(bodies, config)

    # escribir CSV
    rows = [r.as_row() for r in results]
    cols = list(rows[0].keys())
    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)

    admitidos = sum(1 for r in results if r.admitido)
    print(f"Esquema activo    : {config['scheme']}")
    print(f"Proveedor índices : {config['index_provider']}")
    print(f"Cuerpos           : {len(results)}  ({admitidos} admitidos, "
          f"{len(results)-admitidos} en sandbox por datos insuficientes)")
    print(f"Salida            : {args.out}\n")
    print(f"{'Cuerpo':<22}{'Código':>7}{'Central.':>9}  {'Admit.':>6}  Índices")
    for r in results[:12]:
        idx = " ".join(f"{k}{int(v)}" for k, v in r.indices.items())
        print(f"{r.nombre:<22}{r.codigo:>7}{(r.centralidad or 0):>9.2f}  "
              f"{'sí' if r.admitido else 'NO':>6}  {idx}")
    print("...")


if __name__ == "__main__":
    main()
