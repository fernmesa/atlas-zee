# -*- coding: utf-8 -*-
"""
CAPA — Validación de forma/rango contra data/atlas_body_schema.json.

Inspirada en la validación declarativa de Open Exoplanet Catalogue (oec.xsd +
cleanup.py, github.com/OpenExoplanetCatalogue/open_exoplanet_catalogue): un
esquema explícito que atrapa errores de FORMA (masa negativa, radio absurdo,
familia mal escrita) antes de que lleguen a la ciencia.

Distinto de gate_min_data.py: aquella capa decide si hay datos SUFICIENTES
para admitir el cuerpo al catálogo verificado; esta capa decide si los datos
que HAY son válidos (tipo y rango correctos). Un cuerpo puede pasar esta capa
sin pasar min_data (le faltan campos, pero los que tiene son correctos), o
fallar esta capa aunque tenga muchas fuentes (un dato corrupto).

ATLAS declara "sin dependencias externas" (ver README), así que este
validador es un subconjunto minimalista de JSON Schema escrito a mano
(type/minimum/maximum/exclusiveMinimum/enum/required) -- suficiente para un
esquema plano como el nuestro, sin tirar de la librería `jsonschema`.
"""
import json
import os
from atlas_core.registry import gate

_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "atlas_body_schema.json",
)
_SCHEMA = None


def _load_schema():
    global _SCHEMA
    if _SCHEMA is None:
        with open(_SCHEMA_PATH, encoding="utf-8") as f:
            _SCHEMA = json.load(f)
    return _SCHEMA


_TYPE_MAP = {"number": (int, float), "string": str, "null": type(None)}


def _check_type(value, tipos):
    if isinstance(tipos, str):
        tipos = [tipos]
    for t in tipos:
        py_t = _TYPE_MAP.get(t)
        if py_t and isinstance(value, py_t):
            # bool es subclase de int en Python; no lo aceptamos como number
            if py_t == (int, float) and isinstance(value, bool):
                continue
            return True
    return False


def _validate_field(nombre_campo, value, spec):
    errores = []
    if value is None:
        return errores  # los None se toleran; lo requerido se gestiona aparte
    if "type" in spec and not _check_type(value, spec["type"]):
        errores.append(f"{nombre_campo}: tipo inválido ({type(value).__name__})")
        return errores
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in spec and value < spec["minimum"]:
            errores.append(f"{nombre_campo}: {value} < mínimo {spec['minimum']}")
        if "exclusiveMinimum" in spec and value <= spec["exclusiveMinimum"]:
            errores.append(f"{nombre_campo}: {value} <= mínimo exclusivo {spec['exclusiveMinimum']}")
        if "maximum" in spec and value > spec["maximum"]:
            errores.append(f"{nombre_campo}: {value} > máximo {spec['maximum']}")
    if isinstance(value, str) and "enum" in spec and value not in spec["enum"]:
        errores.append(f"{nombre_campo}: '{value}' no está en {spec['enum']}")
    if isinstance(value, str) and "minLength" in spec and len(value) < spec["minLength"]:
        errores.append(f"{nombre_campo}: cadena vacía")
    return errores


def validate_body_dict(d):
    """Valida un dict crudo (p.ej. una fila de CSV ya parseada) contra el
    esquema. Devuelve lista de errores (vacía si es válido)."""
    schema = _load_schema()
    errores = []
    for campo in schema.get("required", []):
        if campo not in d or d[campo] in (None, ""):
            errores.append(f"{campo}: campo requerido ausente")
    for campo, spec in schema.get("properties", {}).items():
        if campo in d:
            errores += _validate_field(campo, d[campo], spec)
    return errores


def _body_to_schema_dict(body):
    """Traduce un Body del núcleo a las claves que espera el esquema."""
    return {
        "nombre": body.nombre, "sistema": body.sistema, "tipo": body.tipo,
        "masa_Me": body.masa_Me, "radio_Re": body.radio_Re,
        "dist_AU": body.dist_AU, "insol_Wm2": body.insol_Wm2,
        "atmosfera": body.atmosfera, "agua": body.agua,
        "vulcanismo": body.vulcanismo,
        "exp_E": body.exp_indices.get("E"), "exp_C": body.exp_indices.get("C"),
        "exp_R": body.exp_indices.get("R"), "exp_familia": body.exp_familia,
        "confianza": body.confianza, "notas": body.notas,
    }


@gate("quality_schema")
def check(body, ctx):
    errores = validate_body_dict(_body_to_schema_dict(body))
    return (len(errores) == 0, errores)
