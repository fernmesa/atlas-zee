# -*- coding: utf-8 -*-
"""
CAPA — Esquema de clasificación ZEE de 7 familias (ATLAS v0.1).

Familias: A acuática · M metánica · O océano interno · V volcánica ·
          C criogénica · G gaseosa · X desconocida.

Código = Familia + round(centralidad), donde centralidad = media(E, C, R) = CCE.

Si el cuerpo trae familia de experto (exp_familia) se respeta; si no, se deriva
del árbol de decisión sobre los observables. Cambiar de esquema (a 3 clases, a 16,
lo que sea) = escribir OTRO archivo como este y apuntarlo en la config. El núcleo
y la capa de índices no se enteran.
"""
from atlas_core.registry import scheme

FAMILIAS = {"A": "Acuática", "M": "Metánica", "O": "Océano interno",
            "V": "Volcánica", "C": "Criogénica", "G": "Gaseosa", "X": "Desconocida"}


def _familia_por_observables(b):
    """Árbol de decisión ATLAS §7 cuando no hay familia de experto."""
    agua = b.agua.lower(); atm = b.atmosfera.lower(); vul = b.vulcanismo.lower()
    masa = b.masa_Me or 0
    if agua.startswith("si") and "hielo" not in agua and "sub" not in agua:
        return "A"
    if "sub-hielo" in agua or "sub hielo" in agua:
        return "O"
    if ("metano" in atm or "ch4" in atm) and ("mares" in agua or "metano" in agua):
        return "M"
    if "activo" in vul or "extremo" in vul or "geiser" in vul:
        return "V"
    if masa > 10:
        return "G"
    # Congelado SOLO con evidencia real de hielo o atmósfera nula conocida.
    # Una atmósfera vacía ("") es FALTA DE DATOS, no frío: debe caer en X.
    if "hielo" in agua or atm in ("no", "negligible"):
        return "C"
    return "X"


@scheme("zee7")
def classify(body, indices, ctx):
    fam = body.exp_familia if body.exp_familia in FAMILIAS else _familia_por_observables(body)
    cce = sum(indices.values()) / len(indices) if indices else 0.0
    return {
        "clase": fam,
        "codigo": f"{fam}{round(cce)}",
        "centralidad": cce,
        "confianza": body.confianza,
        "notas": body.notas,
    }
