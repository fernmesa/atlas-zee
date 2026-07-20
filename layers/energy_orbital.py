# -*- coding: utf-8 -*-
"""
CAPA ANOTADORA — Energía orbital y resonancias (inspirado en orbital-simulator,
github.com/zakerias91/orbital-simulator).

No cambia la clasificación. Añade a cada Result una estimación física de:

  energia_especifica : energía orbital específica ε = -GM/(2a)  (proxy de "cuán
                        profundo" está el cuerpo en el pozo gravitatorio de su
                        estrella; más negativo = más ligado)
  velocidad_orbital   : velocidad circular aproximada v = sqrt(GM/a)  (km/s)
  periodo_dias        : periodo orbital vía Kepler III, T = 2*pi*sqrt(a^3/GM)
  resonancias         : lista de otros cuerpos del MISMO sistema cuyo periodo
                         forma una razón simple (1:2, 2:3, 1:3...) con el suyo,
                         señal de arquitectura orbital estable

Requiere dist_AU (semieje mayor, se asume ~circular). La masa estelar no está en
el modelo de Body; se asume 1 M_sol salvo que 'sistema' sea 'Solar' (exacto por
definición). Es una aproximación deliberada -- ver nota en indices_ecr.py sobre
"la fórmula es el primer sitio para que la comunidad mejore".

Requiere una lista completa de bodies del mismo sistema para detectar
resonancias; se pasa vía ctx["_all_bodies"] (lo rellena el pipeline si está
disponible) o, si no, la capa simplemente omite ese campo.
"""
import math
from atlas_core.registry import annotator

G_SI = 6.674e-11          # m^3 kg^-1 s^-2
M_SOL = 1.989e30          # kg
AU = 1.496e11             # m
DIA = 86400.0             # s

RATIOS_SIMPLES = [(1, 2), (2, 3), (1, 3), (3, 4), (2, 5), (1, 1)]
TOLERANCIA_RATIO = 0.05


def _masa_estrella_kg(body):
    # Aproximación: solo el Sol tiene masa estelar certera en este modelo.
    if body.sistema == "Solar":
        return M_SOL
    return M_SOL  # fallback: estrella tipo solar (mejorable con dato real)


def _periodo_dias(dist_AU, masa_estrella_kg):
    if not dist_AU or dist_AU <= 0:
        return None
    a = dist_AU * AU
    T = 2 * math.pi * math.sqrt(a ** 3 / (G_SI * masa_estrella_kg))
    return T / DIA


def _es_snapshot_temporal(tipo):
    # "_futuro"/"_historico" en atlas_bodies.csv son el MISMO cuerpo en otra
    # época (evolución estelar), no un vecino orbital real -> no cuenta como
    # resonancia.
    t = tipo.lower()
    return "futuro" in t or "historico" in t or "histórico" in t


def _resonancias(body, periodo, todos):
    if periodo is None or not todos or _es_snapshot_temporal(body.tipo):
        return []
    hallazgos = []
    for otro in todos:
        if otro is body or otro.sistema != body.sistema or not otro.dist_AU:
            continue
        if _es_snapshot_temporal(otro.tipo):
            continue
        M = _masa_estrella_kg(otro)
        T_otro = _periodo_dias(otro.dist_AU, M)
        if not T_otro or T_otro <= 0:
            continue
        ratio = periodo / T_otro
        for p, q in RATIOS_SIMPLES:
            objetivo = p / q
            if abs(ratio - objetivo) / objetivo < TOLERANCIA_RATIO:
                hallazgos.append(f"{otro.nombre} ({p}:{q})")
                break
    return hallazgos


@annotator("energy_orbital")
def annotate(body, clase, indices, ctx):
    if not body.dist_AU or body.dist_AU <= 0:
        return {"energia_disponible": None, "nota_energia": "sin semieje orbital (dist_AU)"}

    M = _masa_estrella_kg(body)
    a = body.dist_AU * AU

    energia_especifica = -G_SI * M / (2 * a)              # J/kg
    velocidad_orbital = math.sqrt(G_SI * M / a) / 1000.0   # km/s
    periodo = _periodo_dias(body.dist_AU, M)

    todos = ctx.get("_all_bodies") or []
    resonancias = _resonancias(body, periodo, todos)

    return {
        "energia_especifica_Jkg": round(energia_especifica, 1),
        "velocidad_orbital_kms": round(velocidad_orbital, 2),
        "periodo_dias": round(periodo, 2) if periodo else None,
        "resonancias": resonancias,
        "es_resonante": len(resonancias) > 0,
        "nota_energia": "asume estrella ~1 M_sol salvo sistema Solar" if body.sistema != "Solar" else "",
    }
