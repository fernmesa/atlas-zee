# -*- coding: utf-8 -*-
"""
CAPA ANOTADORA — Prioridad de observación (valor de la información).

Responde: "¿en qué cuerpos merece la pena pedir tiempo de telescopio?"

Idea: un mundo puede estar mal clasificado NO porque sea malo, sino porque le
faltan datos. Si un planeta rocoso en zona templada saliera acuático (familia A)
en cuanto confirmáramos su atmósfera, ese dato vale oro. Esta capa cuantifica esa
ganancia potencial (VOI, value of information) y sugiere el método observacional.

Por cada cuerpo calcula:
  falta        : qué datos críticos faltan (radio, atmósfera, contraste de fuentes)
  cce_actual   : centralidad con lo que sabemos hoy
  cce_potencial: centralidad si el dato que falta resultara FAVORABLE
  upside       : cce_potencial - cce_actual
  plausibilidad: probabilidad (0-1) de que el resultado sea favorable
  prioridad    : upside * plausibilidad  ← ranking de solicitudes
  metodo       : técnica observacional sugerida

No cambia la clasificación; solo la anota. El generador de solicitudes
(tools/observation_requests.py) usa 'prioridad' para ordenar y justificar.
"""
from atlas_core.registry import annotator


def _es_rocoso(b):
    if b.radio_Re is not None:
        return b.radio_Re <= 1.8
    if b.masa_Me is not None:
        return b.masa_Me <= 8
    return False


def _templado(indices):
    # energía ni estéril ni abrasadora: la ventana donde la química interesa
    return 4 <= indices.get("E", 0) <= 7


def _falta(b):
    faltan = []
    if b.radio_Re is None:
        faltan.append("radio/densidad")
    atm = b.atmosfera.strip().lower()
    if atm in ("", "desconocida", "especulativa", "posible"):
        faltan.append("composición atmosférica")
    agua = b.agua.strip().lower()
    if agua in ("", "desconocida", "especulativa", "posible"):
        faltan.append("presencia de agua")
    if b.n_fuentes < 2:
        faltan.append("contraste de fuentes (>=2)")
    return faltan


@annotator("observability")
def annotate(body, clase, indices, ctx):
    cce_actual = sum(indices.values()) / len(indices) if indices else 0.0
    faltan = _falta(body)
    rocoso = _es_rocoso(body)
    templado = _templado(indices)

    # Escenario favorable: si es rocoso y templado, confirmar atmósfera rica en
    # ciclos redox llevaría C hasta ~8 (química tipo terrestre).
    ind_pot = dict(indices)
    if rocoso and templado:
        ind_pot["C"] = max(ind_pot.get("C", 0), 8)
        ind_pot["R"] = max(ind_pot.get("R", 0), min(9, ind_pot.get("R", 0) + 1))
    cce_potencial = sum(ind_pot.values()) / len(ind_pot) if ind_pot else 0.0
    upside = round(cce_potencial - cce_actual, 2)

    # Plausibilidad de que el escenario favorable se cumpla
    if not rocoso or not templado:
        plaus = 0.15
    elif clase == "A":
        plaus = 0.70          # ya parece acuático, solo falta confirmar
    elif clase in ("O", "X"):
        plaus = 0.50          # rocoso templado sin clasificar bien
    else:
        plaus = 0.30
    prioridad = round(upside * plaus, 2)

    # Método observacional según lo que falte
    metodos = []
    if "composición atmosférica" in faltan or "presencia de agua" in faltan:
        metodos.append("espectroscopía de transmisión/emisión (JWST NIRSpec/MIRI, ELT)")
    if "radio/densidad" in faltan:
        metodos.append("fotometría de tránsito de precisión (masa+radio→densidad)")
    if not metodos:
        metodos.append("monitorización adicional para contraste")

    return {
        "falta": faltan,
        "cce_actual": round(cce_actual, 2),
        "cce_potencial": round(cce_potencial, 2),
        "upside": upside,
        "plausibilidad": plaus,
        "prioridad": prioridad,
        "metodo": "; ".join(metodos),
        "rocoso": rocoso, "templado": templado,
    }
