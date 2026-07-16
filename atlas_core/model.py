# -*- coding: utf-8 -*-
"""
Modelo de datos del núcleo ATLAS.

El núcleo NO sabe nada de "E, C, R" ni de "familias ZEE". Solo conoce dos cosas:

  1. Body  -> un cuerpo con sus observables (masa, radio, insolación, atmósfera...)
              y, opcionalmente, valores aportados por un experto.
  2. Result -> el resultado de pasar un Body por las capas activas: unos índices
               numéricos con nombre, una clase, un código y metadatos.

Todo lo demás (qué índices existen, cuántas clases hay, qué se exige para admitir
un cuerpo) vive en las CAPAS, no aquí. Así el núcleo permanece estable mientras la
comunidad reescribe las capas.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Body:
    """Un cuerpo planetario. Los campos observacionales pueden faltar (None/"")."""
    nombre: str
    sistema: str = ""
    tipo: str = ""
    masa_Me: Optional[float] = None      # masas terrestres
    radio_Re: Optional[float] = None     # radios terrestres
    dist_AU: Optional[float] = None      # distancia orbital (AU)
    insol_Wm2: Optional[float] = None    # insolación (W/m²)
    atmosfera: str = ""
    agua: str = ""
    vulcanismo: str = ""
    # --- valores aportados por un experto (capa de override opcional) ---
    exp_indices: dict = field(default_factory=dict)   # p.ej. {"E":9,"C":9,"R":8}
    exp_familia: str = ""
    confianza: str = ""
    fuentes: list = field(default_factory=list)        # para el filtro de datos
    notas: str = ""

    @property
    def n_fuentes(self) -> int:
        return len([s for s in self.fuentes if s.strip()])


@dataclass
class Result:
    """Salida de la tubería para un cuerpo."""
    nombre: str
    indices: dict = field(default_factory=dict)   # {"E":9,"C":9,"R":8}
    indices_origen: dict = field(default_factory=dict)  # {"E":"experto","C":"formula"}
    clase: str = ""          # p.ej. "A"  (familia/categoría según el esquema activo)
    codigo: str = ""         # p.ej. "A9"
    centralidad: Optional[float] = None   # media de índices (CCE en ZEE), si aplica
    confianza: str = ""
    admitido: bool = True    # ¿supera el filtro de datos mínimos?
    motivos_filtro: list = field(default_factory=list)
    esquema: str = ""
    notas: str = ""
    anotaciones: dict = field(default_factory=dict)  # salida de las capas anotadoras

    def as_row(self) -> dict:
        return {
            "nombre": self.nombre,
            **{f"idx_{k}": v for k, v in self.indices.items()},
            "clase": self.clase,
            "codigo": self.codigo,
            "centralidad": None if self.centralidad is None else round(self.centralidad, 2),
            "confianza": self.confianza,
            "admitido": self.admitido,
            "esquema": self.esquema,
            "motivos_filtro": "; ".join(self.motivos_filtro),
            "notas": self.notas,
        }
