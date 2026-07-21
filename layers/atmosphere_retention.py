# -*- coding: utf-8 -*-
"""
CAPA ANOTADORA — Retención atmosférica según STEHM.

Hill, M. L., Kane, S. R., Foley, B. J., & Schaefer, L. K. (2026).
"Smaller Than Earth Habitability Model (STEHM): The Lower Size Limit for
Atmosphere Retention in the Habitable Zone." The Planetary Science Journal,
7(6). https://iopscience.iop.org/article/10.3847/PSJ/ae6804 -- ver
REFERENCES.md.

STEHM modela, con un solar-analog XUV + escape de Jeans + degasificación de
manto, el radio mínimo (~0.8 R⊕ bajo condiciones tipo Tierra) por debajo del
cual un planeta pierde su atmósfera en escalas multi-gigaaño. El hallazgo más
importante del paper NO es el umbral en sí, sino que el factor que MÁS pesa es
el inventario inicial de carbono del manto -- por delante de la fracción del
núcleo, la temperatura inicial del manto, los elementos radiogénicos y la
posición dentro de la zona habitable.

ATLAS no modela ninguno de esos cuatro factores (no hay campos de composición
de manto en el modelo de Body). Esta capa es deliberadamente honesta sobre esa
laguna: da una estimación con el único dato que sí tenemos (radio_Re) y
etiqueta explícitamente qué factores decisivos según STEHM quedan sin
observar, en vez de fingir una precisión que no existe. Así, un mundo
pequeño no queda mal-descartado -- STEHM muestra que planetas por debajo del
umbral SÍ pueden retener (o recuperar) atmósfera con manto rico en carbono,
núcleo pequeño o mayor calor radiogénico; nada de eso lo sabemos todavía, así
que se marca como "incierto", no como "sin atmósfera".

No cambia la clasificación (como todo annotator); alimenta a observability.py
y a quien decida priorizar observación: un mundo con radio < 0.8 R⊕ y
composición de manto desconocida es exactamente el caso donde STEHM dice que
el dato que falta puede cambiarlo todo.
"""
from atlas_core.registry import annotator

UMBRAL_STEHM_RE = 0.8
UMBRAL_MARGINAL_RE = 0.6

FACTORES_NO_MODELADOS = [
    "inventario de carbono del manto (el más influyente según STEHM)",
    "fracción de radio del núcleo",
    "temperatura inicial del manto",
    "concentración de elementos radiogénicos (HPE)",
]


def _vulcanismo_activo(b):
    v = b.vulcanismo.lower()
    return any(p in v for p in ("activo", "extremo", "geiser", "criovulcanismo"))


def _posicion_relativa_zh(b, indices):
    """Proxy de 'cerca del borde interior de la ZH' usando el índice de energía
    (E alto = más insolación = más cerca del borde interior, donde STEHM dice
    que la retención es más difícil)."""
    e = indices.get("E")
    if e is None:
        return "desconocida"
    if e >= 7:
        return "cerca del borde interior (E alto) -- condición desfavorable"
    if e <= 3:
        return "lejos del borde interior (E bajo) -- condición favorable"
    return "intermedia"


@annotator("atmosphere_retention")
def annotate(body, clase, indices, ctx):
    if body.radio_Re is None:
        return {
            "estimacion": "desconocida",
            "motivo": "sin radio conocido; STEHM requiere R para el umbral",
        }

    r = body.radio_Re
    posicion = _posicion_relativa_zh(body, indices)
    vulcan_activo = _vulcanismo_activo(body)

    if r >= UMBRAL_STEHM_RE:
        estimacion = "probable"
        motivo = f"radio {r} R⊕ >= umbral STEHM ({UMBRAL_STEHM_RE} R⊕) bajo condiciones tipo Tierra"
    elif r >= UMBRAL_MARGINAL_RE:
        # Zona marginal: STEHM dice que aquí decide el manto (carbono, calor),
        # que no observamos. El vulcanismo activo es la única pista indirecta
        # de calor interno que sí tenemos.
        if vulcan_activo:
            estimacion = "incierta (favorable)"
            motivo = (f"radio {r} R⊕ bajo el umbral pero cerca; vulcanismo activo "
                       f"sugiere calor interno suficiente -- STEHM predice retención "
                       f"posible en este régimen")
        else:
            estimacion = "incierta"
            motivo = (f"radio {r} R⊕ en zona marginal STEHM ({UMBRAL_MARGINAL_RE}-"
                       f"{UMBRAL_STEHM_RE} R⊕); depende del manto, no observado")
    else:
        estimacion = "improbable (bajo condiciones por defecto)"
        motivo = f"radio {r} R⊕ muy por debajo del umbral STEHM ({UMBRAL_STEHM_RE} R⊕)"

    return {
        "estimacion": estimacion,
        "motivo": motivo,
        "posicion_zona_habitable": posicion,
        "factores_no_modelados": FACTORES_NO_MODELADOS,
        "nota": "STEHM permite recuperación atmosférica tardía en mundos pequeños "
                "con núcleo de baja fracción y manto rico en carbono, aun por "
                "debajo del umbral por defecto.",
    }
