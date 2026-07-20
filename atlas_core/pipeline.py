# -*- coding: utf-8 -*-
"""
Tubería (pipeline) del núcleo.

Orquesta el paso de cada cuerpo por las capas activas, en este orden:

    Body  ──▶  [gates]  ──▶  [index_provider]  ──▶  [scheme]  ──▶  Result

El pipeline no decide NADA científico: solo llama a las capas que la config indica.
Cambia la config y cambia el comportamiento, sin tocar este archivo ni el núcleo.
"""
import csv
from .model import Body, Result
from . import registry


def load_bodies(csv_path):
    """Lee data/atlas_bodies.csv y devuelve una lista de Body."""
    def num(s):
        s = (s or "").strip()
        try:
            return float(s)
        except ValueError:
            return None
    bodies = []
    with open(csv_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            exp = {}
            for k in ("E", "C", "R"):
                v = num(r.get(f"exp_{k}", ""))
                if v is not None:
                    exp[k] = v
            bodies.append(Body(
                nombre=r["nombre"], sistema=r.get("sistema", ""), tipo=r.get("tipo", ""),
                masa_Me=num(r.get("masa_Me")), radio_Re=num(r.get("radio_Re")),
                dist_AU=num(r.get("dist_AU")), insol_Wm2=num(r.get("insol_Wm2")),
                atmosfera=r.get("atmosfera", ""), agua=r.get("agua", ""),
                vulcanismo=r.get("vulcanismo", ""),
                exp_indices=exp, exp_familia=r.get("exp_familia", ""),
                confianza=r.get("confianza", ""),
                fuentes=[s for s in (r.get("fuentes", "") or "").split(";") if s],
                notas=r.get("notas", ""),
            ))
    return bodies


def run(bodies, config):
    """Aplica las capas de `config` a cada cuerpo y devuelve lista de Result."""
    prov_name = config["index_provider"]
    sch_name = config["scheme"]
    gate_names = config.get("gates", [])
    ctx = dict(config.get("params", {}))
    ctx["_all_bodies"] = bodies  # disponible para capas que necesiten el sistema completo

    provider = registry.INDEX_PROVIDERS[prov_name]
    scheme = registry.SCHEMES[sch_name]
    gates = [registry.GATES[g] for g in gate_names]
    annotators = [(a, registry.ANNOTATORS[a]) for a in config.get("annotators", [])]

    results = []
    for b in bodies:
        admitido, motivos = True, []
        for g in gates:
            ok, why = g(b, ctx)
            if not ok:
                admitido = False
                motivos += why
        indices, origen = provider(b, ctx)
        out = scheme(b, indices, ctx)
        clase = out.get("clase", "")
        anotaciones = {}
        for name, fn in annotators:
            anotaciones[name] = fn(b, clase, indices, ctx)
        results.append(Result(
            nombre=b.nombre, indices=indices, indices_origen=origen,
            clase=clase, codigo=out.get("codigo", ""),
            centralidad=out.get("centralidad"), confianza=out.get("confianza", b.confianza),
            admitido=admitido, motivos_filtro=motivos, esquema=sch_name,
            notas=out.get("notas", b.notas), anotaciones=anotaciones,
        ))
    return results
