# -*- coding: utf-8 -*-
"""
CAPA — Filtro de datos mínimos y contraste de fuentes.

"Debemos exigir un mínimo de datos y de contraste de los mismos para incorporarlos
a nuestra base de datos." — Este filtro implementa exactamente eso.

Importante: NO borra ni bloquea nada. Marca cada cuerpo con admitido=True/False y el
motivo. Quien se descarga el repo puede jugar con TODO (admitidos o no); el filtro
solo distingue lo que entra en el catálogo "verificado" oficial de lo que queda en
zona de pruebas (sandbox) esperando más datos. Umbrales configurables en params.

Parámetros (params):
  "min_fuentes"      : nº mínimo de fuentes independientes (def. 1)
  "exigir_radio"     : requiere radio conocido (def. true)
  "exigir_energia"   : requiere insolación o (masa+distancia) (def. true)
"""
from atlas_core.registry import gate


@gate("min_data")
def check(body, ctx):
    min_fuentes = ctx.get("min_fuentes", 1)
    exigir_radio = ctx.get("exigir_radio", True)
    exigir_energia = ctx.get("exigir_energia", True)

    motivos = []
    if body.n_fuentes < min_fuentes:
        motivos.append(f"fuentes insuficientes ({body.n_fuentes}<{min_fuentes})")
    if exigir_radio and body.radio_Re is None:
        motivos.append("radio desconocido")
    if exigir_energia and body.insol_Wm2 is None and (
            body.masa_Me is None or body.dist_AU is None):
        motivos.append("energía no derivable (falta insolación y masa/distancia)")

    return (len(motivos) == 0, motivos)
