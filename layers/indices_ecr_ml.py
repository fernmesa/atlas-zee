# -*- coding: utf-8 -*-
"""
CAPA — Proveedor de índices E, C, R con fallback ML (inspirado en el "hybrid
scoring system" de Real-Time Exoplanet Tracker, physics + ML con confianza,
github.com/Harshith-02/real-time-exoplanet-tracker).

indices_ecr.py ya cubre experto -> fórmula. Esta capa añade un TERCER escalón
para el caso límite: un cuerpo sin valor de experto Y sin ningún observable
físico/químico (masa, radio, insolación, atmósfera, agua todos vacíos), donde
la fórmula de indices_ecr.py solo puede devolver sus valores por defecto
(no informativos). En ese caso concreto, se estima E/C/R por k-vecinos-más-
cercanos sobre los cuerpos curados que SÍ tienen datos, en vez de un default
fijo.

Real-Time Tracker entrena RandomForest/MLP con scikit-learn sobre ~5900
exoplanetas de NASA. Aquí no hay ni sklearn (ATLAS es "sin dependencias
externas", ver README) ni ese volumen de datos -- solo 90 cuerpos curados,
insuficientes para una red neuronal seria. Por eso el fallback es KNN
ponderado por distancia, escrito a mano: mismo principio (aprender de casos
conocidos en vez de imputar un valor fijo), honesto sobre sus límites
(confianza siempre BAJA, nunca sustituye al experto ni a la fórmula cuando
hay algún dato real).

Parámetro de config (params):
  "usar_fallback_ml": true/false (def. true) -> activa el escalón KNN.
  "ml_k_vecinos": int (def. 5)
"""
import math
from atlas_core.registry import index_provider
from layers.indices_ecr import _E_formula, _C_formula, _R_formula

_FEATURES = ("masa_Me", "radio_Re", "dist_AU", "insol_Wm2")


def _sin_senal_fisica(b):
    """True si no hay NADA con lo que calcular la fórmula de forma informativa."""
    sin_numeros = all(getattr(b, f) is None for f in _FEATURES)
    atm = b.atmosfera.strip().lower()
    agua = b.agua.strip().lower()
    sin_quimica = atm in ("", "desconocida", "no", "negligible") and \
                  agua in ("", "no", "desconocida")
    return sin_numeros and sin_quimica


def _training_set(todos):
    """Cuerpos curados (con exp_indices completo) que sí tienen algún dato
    numérico, para servir de vecinos."""
    filas = []
    for b in todos:
        if not all(k in b.exp_indices for k in ("E", "C", "R")):
            continue
        vec = [getattr(b, f) for f in _FEATURES]
        if all(v is None for v in vec):
            continue
        filas.append((vec, b.exp_indices))
    return filas


def _stats(filas):
    """Media/desviación por feature, solo con los valores conocidos, para
    poder normalizar distancias entre magnitudes muy distintas (AU vs W/m2)."""
    stats = []
    for i in range(len(_FEATURES)):
        vals = [f[0][i] for f in filas if f[0][i] is not None]
        if not vals:
            stats.append((0.0, 1.0))
            continue
        media = sum(vals) / len(vals)
        var = sum((v - media) ** 2 for v in vals) / len(vals) if len(vals) > 1 else 1.0
        stats.append((media, math.sqrt(var) or 1.0))
    return stats


def _distancia(vec_a, vec_b, stats):
    """Distancia euclídea normalizada; features desconocidas en cualquiera de
    los dos lados se ignoran (no penalizan ni benefician)."""
    acc, n = 0.0, 0
    for i, (media, sd) in enumerate(stats):
        va, vb = vec_a[i], vec_b[i]
        if va is None or vb is None:
            continue
        acc += ((va - vb) / sd) ** 2
        n += 1
    if n == 0:
        return float("inf")
    return math.sqrt(acc)


def _knn_predict(body, todos, k):
    filas = _training_set(todos)
    if len(filas) < k:
        return None  # no hay suficientes vecinos para una estimación decente
    stats = _stats(filas)
    vec_b = [getattr(body, f) for f in _FEATURES]

    distancias = sorted(
        ((_distancia(vec_b, vec_a, stats), idx) for idx, (vec_a, _) in enumerate(filas)),
        key=lambda t: t[0],
    )[:k]

    pesos_totales = 0.0
    acumulado = {"E": 0.0, "C": 0.0, "R": 0.0}
    for dist, idx in distancias:
        if math.isinf(dist):
            continue  # ningún feature comparable con este vecino
        peso = 1.0 / (dist + 1e-6)
        pesos_totales += peso
        for key in acumulado:
            acumulado[key] += peso * filas[idx][1][key]

    if pesos_totales == 0:
        # Cero features numéricos en el cuerpo a predecir: no hay base para
        # distancia alguna. Único fallback honesto: media de TODO el
        # entrenamiento (equivale a "todos los vecinos son igual de (in)válidos").
        for _, kv in filas:
            for key in acumulado:
                acumulado[key] += kv[key]
        return {k_: round(acumulado[k_] / len(filas), 1) for k_ in acumulado}

    return {k_: round(acumulado[k_] / pesos_totales, 1) for k_ in acumulado}


@index_provider("ecr_ml")
def provider(body, ctx):
    """Igual que 'ecr' (experto -> fórmula), pero con un escalón adicional de
    fallback KNN para cuerpos sin ninguna señal física/química conocida."""
    preferir_formula = ctx.get("preferir_formula", False)
    usar_ml = ctx.get("usar_fallback_ml", True)
    k = int(ctx.get("ml_k_vecinos", 5))

    formula = {"E": _E_formula(body), "C": _C_formula(body), "R": _R_formula(body)}
    indices, origen = {}, {}

    if not preferir_formula and body.exp_indices:
        for kk in ("E", "C", "R"):
            if kk in body.exp_indices:
                indices[kk] = body.exp_indices[kk]
                origen[kk] = "experto"

    faltan = [kk for kk in ("E", "C", "R") if kk not in indices]
    if faltan and usar_ml and _sin_senal_fisica(body):
        todos = ctx.get("_all_bodies") or []
        pred = _knn_predict(body, [b for b in todos if b is not body], k)
        if pred:
            for kk in faltan:
                indices[kk] = pred[kk]
                origen[kk] = "ml_fallback"

    for kk in ("E", "C", "R"):
        if kk not in indices:
            indices[kk] = formula[kk]
            origen[kk] = "formula"

    return indices, origen
