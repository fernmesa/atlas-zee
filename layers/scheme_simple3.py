# -*- coding: utf-8 -*-
"""
CAPA — Esquema de clasificación alternativo de 3 clases (DEMOSTRACIÓN).

Existe para probar la tesis de la arquitectura: el MISMO núcleo y los MISMOS índices
E/C/R producen una taxonomía completamente distinta con solo cambiar esta capa.

Tres clases según la centralidad (media de E, C, R):
    H (Hospitalaria)   centralidad >= 6      — ecosistema físico robusto
    T (Transitoria)    3.5 <= centralidad < 6 — al borde de la zona
    E (Estéril)        centralidad < 3.5      — fuera de zona conocida

Alguien que prefiera 16 clases solo tiene que escribir scheme_zee16.py con la misma
firma y registrarlo con @scheme("zee16"). No se toca nada más.
"""
from atlas_core.registry import scheme


@scheme("simple3")
def classify(body, indices, ctx):
    cce = sum(indices.values()) / len(indices) if indices else 0.0
    if cce >= 6:      cls = "H"
    elif cce >= 3.5:  cls = "T"
    else:             cls = "E"
    return {
        "clase": cls,
        "codigo": f"{cls}{round(cce)}",
        "centralidad": cce,
        "confianza": body.confianza,
        "notas": body.notas,
    }
