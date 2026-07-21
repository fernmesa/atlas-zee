# -*- coding: utf-8 -*-
"""
CAPA — Proveedor de índices E, C, R (modelo ATLAS v0.1).

Resuelve el eterno debate "¿mando el experto o mando la fórmula?" ofreciendo AMBOS:

  - Si el cuerpo trae valores de experto (exp_indices), se usan y se marca
    origen = "experto".
  - Si no, se calculan con una fórmula física aproximada y se marca
    origen = "formula".

Así los 90 cuerpos curados conservan el juicio experto (y pasan los 8 controles),
pero cualquier cuerpo nuevo importado de un catálogo (sin experto) obtiene igualmente
un E/C/R automático. La fórmula es DELIBERADAMENTE mejorable: este es el primer
sitio donde la comunidad querrá meter mano.

Parámetro de config (params):
  "preferir_formula": true  -> ignora el experto y usa siempre la fórmula
                               (útil para auditar el modelo automático).
"""
from atlas_core.registry import index_provider


def _E_formula(b):
    """Energía 0-9 desde insolación + pistas de calor interno."""
    ins = b.insol_Wm2 or 0.0
    if   ins >= 1000: e = 8
    elif ins >= 100:  e = 6
    elif ins >= 10:   e = 5
    elif ins >= 1:    e = 4
    else:             e = 2
    # bonus por energía interna (vulcanismo activo o agua bajo hielo => mareas/radiogénica)
    v = b.vulcanismo.lower()
    if "activo" in v or "extremo" in v or "geiser" in v or "criovulcanismo" in v:
        e += 2
    if "sub-hielo" in b.agua.lower() or "sub hielo" in b.agua.lower():
        e += 1
    return max(0, min(9, e))


def _C_formula(b):
    """Persistencia química 0-9 desde composición atmosférica y agua."""
    atm = b.atmosfera.lower()
    agua = b.agua.lower()
    c = 1
    if "o2" in atm and "n2" in atm:      c = 8          # atmósfera tipo Tierra
    elif "ch4" in atm or "metano" in atm: c = 5          # ciclos orgánicos
    elif "co2" in atm:                    c = 3
    elif "h2" in atm:                     c = 3
    elif atm in ("", "desconocida", "no", "negligible"): c = 2
    if agua.startswith("si") or "si " in agua or "sub-hielo" in agua:
        c += 1
    return max(0, min(9, c))


def _R_formula(b):
    """Resistencia 0-9. Con datos escasos (sin excentricidad) es la más incierta.

    Umbral de retención atmosférica: 0.8 R⊕, según Hill, Kane, Foley & Schaefer
    (2026), "Smaller Than Earth Habitability Model (STEHM): The Lower Size
    Limit for Atmosphere Retention in the Habitable Zone", Planetary Science
    Journal 7(6) -- ver REFERENCES.md. Reemplaza el corte previo por masa
    (0.1-10 M⊕), que no distinguía radio de composición. Si no hay radio
    conocido, cae de vuelta a la heurística de masa (peor proxy, pero mejor
    que nada). STEHM señala que el factor MÁS influyente es en realidad el
    inventario de carbono del manto, que ATLAS no modela -- ver
    layers/atmosphere_retention.py para el detalle completo del análisis.
    """
    r = 3
    if b.radio_Re is not None:
        if b.radio_Re >= 0.8:      # retiene atmósfera bajo condiciones tipo Tierra
            r += 1
        elif b.radio_Re >= 0.6:    # bajo el umbral, pero cerca -> posible con condiciones favorables
            r += 0
        else:                       # muy por debajo del umbral -> pérdida casi segura
            r -= 1
    elif b.masa_Me is not None and 0.1 <= b.masa_Me <= 10:
        r += 1  # sin radio conocido: heurística de masa como respaldo
    if "campo magn" in b.notas.lower() and "sin campo" not in b.notas.lower():
        r += 1
    # exoplanetas de enana M activa: penalización
    if "activ" in b.notas.lower() or "flare" in b.notas.lower():
        r -= 1
    return max(0, min(9, r))


@index_provider("ecr")
def provider(body, ctx):
    preferir_formula = ctx.get("preferir_formula", False)
    formula = {"E": _E_formula(body), "C": _C_formula(body), "R": _R_formula(body)}
    indices, origen = {}, {}
    for k in ("E", "C", "R"):
        if not preferir_formula and k in body.exp_indices:
            indices[k] = body.exp_indices[k]
            origen[k] = "experto"
        else:
            indices[k] = formula[k]
            origen[k] = "formula"
    return indices, origen
