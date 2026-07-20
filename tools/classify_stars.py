# -*- coding: utf-8 -*-
"""
CLASIFICADOR DE ESTRELLAS ANFITRIONAS (por los planetas que hospedan).

Pregunta que responde: "de las estrellas del catálogo, ¿cuáles merece más la
pena mirar, a la vista de lo que ya sabemos de sus planetas?"

data/host_stars.csv es HOY un archivo curado a mano (ver README: "15 estrellas
con coordenadas verificadas"); no existe ni ha existido una fórmula que derive
su columna 'indice_anfitrion' desde atlas_bodies.csv. Este script propone una:

    índice_anfitrión = media ponderada de la centralidad (CCE) de los planetas
    admitidos del sistema, tomando como mucho los 3 mejores con pesos
    decrecientes (0.5 / 0.3 / 0.2, renormalizados si hay menos de 3).

Así una estrella con UN mundo excelente puntúa cerca de ese mundo, pero una
con VARIOS mundos buenos puntúa más alto que una con uno solo igual de bueno
-- relevante para priorizar observación de sistema completo, no solo de
planeta individual. Es, como la fórmula de indices_ecr.py, DELIBERADAMENTE
mejorable: un punto de partida transparente, no una verdad cerrada. Al correrlo contra host_stars.csv, coincide EXACTO en 5 de 9 sistemas con
solapamiento (Proxima Centauri, Epsilon Eridani, Tau Ceti, Wolf 1061, Gliese
581, LHS 1140) y queda cerca en el resto. El mayor desvío es TRAPPIST-1 (4.17
automático vs 5.08 curado): con 7 planetas, el tope de "solo los 3 mejores"
se queda corto frente al criterio original, que premiaba más la riqueza de
sistemas con muchos mundos. Limitación conocida, no corregida a propósito
--otro sitio donde la comunidad puede mejorar la fórmula (subir el tope o
hacerlo dependiente de n_admitidos).

Sistemas binarios/múltiples: el modelo de datos ATLAS no tiene una entidad
"Estrella" separada del campo Body.sistema (string). Siguiendo la convención
del propio NASA Exoplanet Archive (host_star_flag: si el planeta orbita una
componente concreta, se nombra esa componente), 'sistema' YA actúa como el
nombre de la estrella (o baricentro) principal -- p.ej. "Gliese 667C" nombra
la componente C, no el sistema triple completo. No hace falta modelar el
baricentro aparte: se usa el nombre tal cual aparece en 'sistema'.
Referencia de campos NASA: data/reference/nasa_exoplanet_archive_parameter_template.csv

Distingue PLANETAS (orbitan la estrella) de SATÉLITES (orbitan un planeta,
Body.sistema = nombre del planeta, no de la estrella) por Body.tipo, y excluye
los "snapshots" temporales (_futuro/_historico) igual que layers/energy_orbital.py.

Uso:
    python tools/classify_stars.py                  # tabla a stdout + CSV
    python tools/classify_stars.py --out salida_estrellas.csv
"""
import argparse, csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from atlas_core import registry, pipeline  # noqa: E402

PESOS_TOP3 = [0.5, 0.3, 0.2]


def _es_snapshot_temporal(tipo):
    t = tipo.lower()
    return "futuro" in t or "historico" in t or "histórico" in t


def _es_planeta_directo(tipo):
    """Orbita la estrella directamente (no es luna de otro cuerpo). Cubre
    tanto 'Planeta' (Sistema Solar) como 'Exoplaneta' (resto del catálogo)."""
    t = tipo.lower()
    return (t.startswith("planeta") or t.startswith("exoplaneta")) and not _es_snapshot_temporal(t)


def _indice_anfitrion(centralidades):
    """Media ponderada de hasta los 3 mejores, pesos decrecientes renormalizados."""
    top = sorted(centralidades, reverse=True)[:3]
    pesos = PESOS_TOP3[:len(top)]
    total_peso = sum(pesos)
    return round(sum(c * p for c, p in zip(top, pesos)) / total_peso, 2)


def classify_stars(bodies, results):
    por_nombre = {r.nombre: r for r in results}
    sistemas = {}
    for b in bodies:
        if not _es_planeta_directo(b.tipo):
            continue
        r = por_nombre.get(b.nombre)
        if r is None:
            continue
        sistemas.setdefault(b.sistema, []).append(r)

    filas = []
    for sistema, rs in sistemas.items():
        admitidos = [r for r in rs if r.admitido and r.centralidad is not None]
        if not admitidos:
            continue
        mejor = max(admitidos, key=lambda r: r.centralidad)
        filas.append({
            "sistema": sistema,
            "n_planetas": len(rs),
            "n_admitidos": len(admitidos),
            "fam_mejor": mejor.clase,
            "codigo_mejor": mejor.codigo,
            "indice_anfitrion": _indice_anfitrion([r.centralidad for r in admitidos]),
        })
    filas.sort(key=lambda f: f["indice_anfitrion"], reverse=True)
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(ROOT, "config", "default.json"))
    ap.add_argument("--data", default=os.path.join(ROOT, "data", "atlas_bodies.csv"))
    ap.add_argument("--out", default=os.path.join(ROOT, "salida_estrellas.csv"))
    args = ap.parse_args()

    import json
    config = json.load(open(args.config, encoding="utf-8"))
    registry.discover()
    bodies = pipeline.load_bodies(args.data)
    results = pipeline.run(bodies, config)

    filas = classify_stars(bodies, results)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["sistema", "n_planetas", "n_admitidos",
                                           "fam_mejor", "codigo_mejor", "indice_anfitrion"])
        w.writeheader()
        w.writerows(filas)

    print(f"{'Sistema':<20}{'Planetas':>10}{'Admit.':>8}{'Mejor':>8}{'Índice':>9}")
    for fl in filas:
        print(f"{fl['sistema']:<20}{fl['n_planetas']:>10}{fl['n_admitidos']:>8}"
              f"{fl['codigo_mejor']:>8}{fl['indice_anfitrion']:>9}")
    print(f"\n{len(filas)} sistemas clasificados. Salida: {args.out}")


if __name__ == "__main__":
    main()
