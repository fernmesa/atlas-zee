# -*- coding: utf-8 -*-
"""
Test de regresión: los 8 cuerpos de control DEBEN dar su código canónico.

Este test es el contrato del modelo: cualquier cambio en las capas que rompa uno
de estos 8 códigos debe fallar el CI y bloquear el Pull Request. Es lo que impide
que "mejorar el motor" degrade silenciosamente la calibración.

Ejecutar:  python tests/test_controls.py     (o con pytest)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from atlas_core import registry, pipeline  # noqa: E402

CONTROLES = {
    "Tierra": "A9", "Titan": "M5", "Europa": "O7", "Luna": "C2",
    "Io": "V5", "Jupiter": "G6", "Venus": "G4", "Marte": "C4",
}

CONFIG = {"index_provider": "ecr", "scheme": "zee7", "gates": [], "params": {}}


def test_controls():
    registry.discover()
    bodies = pipeline.load_bodies(os.path.join(ROOT, "data", "atlas_bodies.csv"))
    results = {r.nombre: r for r in pipeline.run(bodies, CONFIG)}
    fallos = []
    for nombre, esperado in CONTROLES.items():
        got = results[nombre].codigo
        if got != esperado:
            fallos.append(f"{nombre}: esperado {esperado}, obtenido {got}")
    assert not fallos, "Controles rotos:\n  " + "\n  ".join(fallos)


if __name__ == "__main__":
    test_controls()
    print("OK — los 8 controles pasan.")
