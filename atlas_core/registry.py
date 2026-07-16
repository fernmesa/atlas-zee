# -*- coding: utf-8 -*-
"""
Registro de capas.

Una "capa" es una pieza enchufable de tres tipos posibles:

  - index_provider : calcula índices numéricos a partir de un Body.
                     Contrato:  provider(body, ctx) -> (dict_indices, dict_origen)
  - scheme         : asigna clase y código a partir de índices.
                     Contrato:  scheme(body, indices, ctx) -> dict con
                                {clase, codigo, centralidad, confianza, notas}
  - gate           : decide si un cuerpo tiene datos suficientes para ser admitido.
                     Contrato:  gate(body, ctx) -> (admitido: bool, motivos: list[str])

Cada capa se registra con un decorador y un nombre. La config elige, por nombre,
qué capas están activas. Añadir una capa nueva = crear un archivo en layers/ que
llame a uno de estos decoradores. No hay que tocar el núcleo.
"""
import importlib, os, glob

INDEX_PROVIDERS = {}
SCHEMES = {}
GATES = {}
ANNOTATORS = {}


def index_provider(name):
    def deco(fn):
        INDEX_PROVIDERS[name] = fn
        return fn
    return deco


def scheme(name):
    def deco(fn):
        SCHEMES[name] = fn
        return fn
    return deco


def gate(name):
    def deco(fn):
        GATES[name] = fn
        return fn
    return deco


def annotator(name):
    """Capa opcional que se ejecuta DESPUÉS del esquema y enriquece el Result
    sin alterar la clasificación. Contrato:
        annotator(body, clase, indices, ctx) -> dict  (se fusiona en anotaciones)
    """
    def deco(fn):
        ANNOTATORS[name] = fn
        return fn
    return deco


def discover(layers_pkg="layers"):
    """Importa todos los módulos de layers/ para que se auto-registren."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for path in sorted(glob.glob(os.path.join(here, layers_pkg, "*.py"))):
        mod = os.path.splitext(os.path.basename(path))[0]
        if mod.startswith("_"):
            continue
        importlib.import_module(f"{layers_pkg}.{mod}")
