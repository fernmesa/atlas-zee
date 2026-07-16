# -*- coding: utf-8 -*-
"""Núcleo ATLAS: modelo de datos + registro de capas + tubería.

El núcleo es deliberadamente pequeño y estable. La ciencia vive en layers/.
"""
from .model import Body, Result
from . import registry, pipeline

__all__ = ["Body", "Result", "registry", "pipeline"]
__version__ = "0.2.0"
