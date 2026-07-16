# -*- coding: utf-8 -*-
"""
Generador de SOLICITUDES DE OBSERVACIÓN.

Usa la capa 'observability' para rankear los cuerpos por valor de la información
(prioridad = ganancia potencial de CCE × plausibilidad) y redacta, para los N
mejores, una solicitud justificada de tiempo de telescopio.

Uso:
    python tools/observation_requests.py            # top 10 a stdout + Markdown
    python tools/observation_requests.py --top 15 --out solicitudes.md
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from atlas_core import registry, pipeline  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--out", default=os.path.join(ROOT, "solicitudes_observacion.md"))
    args = ap.parse_args()

    config = {"index_provider": "ecr", "scheme": "zee7", "gates": ["min_data"],
              "annotators": ["observability", "biochem"], "params": {}}
    registry.discover()
    bodies = pipeline.load_bodies(os.path.join(ROOT, "data", "atlas_bodies.csv"))
    results = pipeline.run(bodies, config)

    # candidatos: algo que observar + prioridad positiva
    cand = []
    for r in results:
        o = r.anotaciones["observability"]
        if o["prioridad"] > 0 and o["falta"]:
            cand.append((r, o))
    cand.sort(key=lambda x: x[1]["prioridad"], reverse=True)
    top = cand[:args.top]

    lines = ["# ATLAS — Solicitudes de observación priorizadas",
             "",
             "Objetivos donde un dato que falta cambiaría más la clasificación ZEE. "
             "Prioridad = ganancia potencial de CCE × plausibilidad de un resultado favorable.",
             ""]
    lines.append("| # | Objetivo | Actual | Potencial | Prioridad | Falta |")
    lines.append("|---|----------|--------|-----------|-----------|-------|")
    for i, (r, o) in enumerate(top, 1):
        pot_fam = r.clase
        lines.append(f"| {i} | {r.nombre} | {r.codigo} ({o['cce_actual']}) | "
                     f"{pot_fam}{round(o['cce_potencial'])} ({o['cce_potencial']}) | "
                     f"{o['prioridad']} | {', '.join(o['falta'])} |")
    lines.append("")

    for i, (r, o) in enumerate(top, 1):
        bio = r.anotaciones["biochem"]
        lines += [
            f"## {i}. Solicitud de observación — {r.nombre}",
            "",
            f"- **Clasificación actual:** {r.codigo}  ·  CCE {o['cce_actual']}  ·  "
            f"confianza {r.confianza}",
            f"- **Clasificación potencial:** {r.clase}{round(o['cce_potencial'])}  ·  "
            f"CCE ~{o['cce_potencial']} si el dato resulta favorable",
            f"- **Datos que faltan:** {', '.join(o['falta'])}",
            f"- **Método sugerido:** {o['metodo']}",
            f"- **Ganancia esperada (VOI):** +{o['upside']} de CCE × plausibilidad "
            f"{o['plausibilidad']} = **prioridad {o['prioridad']}**",
            "",
            f"**Justificación.** {_justificacion(r, o, bio)}",
            "",
        ]

    txt = "\n".join(lines)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(txt)

    print(f"{'#':>2}  {'Objetivo':<20}{'Actual':>8}{'Potenc.':>9}{'Prior.':>8}  Falta")
    for i, (r, o) in enumerate(top, 1):
        print(f"{i:>2}  {r.nombre:<20}{r.codigo:>8}"
              f"{r.clase + str(round(o['cce_potencial'])):>9}{o['prioridad']:>8}  "
              f"{', '.join(o['falta'])}")
    print(f"\nSolicitudes completas escritas en: {args.out}")


def _justificacion(r, o, bio):
    partes = []
    if o["rocoso"] and o["templado"]:
        partes.append("Cuerpo rocoso en régimen de energía templado")
    if r.clase == "A":
        partes.append("ya clasificado como acuático (familia A): el factor que limita "
                       "su centralidad es la persistencia química (C), no verificada")
    elif r.clase in ("O", "X"):
        partes.append(f"clasificado {r.clase} por falta de datos; confirmar atmósfera y "
                      "agua podría situarlo en la familia acuática")
    partes.append(f"si se confirma una química rica en ciclos redox, su código pasaría "
                  f"de {r.codigo} a ~{r.clase}{round(o['cce_potencial'])}, acercándolo a "
                  "los análogos terrestres más prometedores")
    partes.append(f"hipótesis biológica asociada: {bio['plausibilidad'].lower()} "
                  f"({bio['resumen'].split('.')[0]})")
    return ". ".join(p[0].upper() + p[1:] for p in partes) + "."


if __name__ == "__main__":
    main()
