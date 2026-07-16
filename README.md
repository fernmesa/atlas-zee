# ATLAS — Clasificador modular de Zonas de Estabilidad Ecosistémica

**Adaptive Taxonomy of Life-compatible Astrophysical Systems** · v0.2 · Licencia CC-BY-4.0

Clasifica cuerpos planetarios (planetas, satélites, exoplanetas) no por "¿puede haber
vida?" sino por **¿qué ecosistema físico es estable aquí y durante cuánto tiempo?**.

> Este repositorio es un **motor abierto y mejorable**, no una verdad cerrada. El núcleo
> es pequeño y estable; toda la ciencia vive en capas que puedes reescribir, añadir o
> quitar. Clónalo y haz tu propia investigación.

---

## Filosofía: núcleo pequeño, capas intercambiables

```
   data/atlas_bodies.csv          ← fuente única de verdad (los observables)
            │
            ▼
   ┌──────────────────┐
   │   NÚCLEO          │  no sabe qué es "E" ni "familia A". Solo orquesta.
   │  atlas_core/      │
   └────────┬─────────┘
            │  pregunta a las CAPAS activas (elegidas en config/):
            ▼
   [ gate ] ──▶ [ index_provider ] ──▶ [ scheme ] ──▶ Resultado
   ¿datos          ¿qué índices          ¿qué clase
   suficientes?    numéricos?            y código?
```

La idea central: **si mañana alguien decide que hay que clasificar en 3 clases, o en 16,
o con índices distintos a E/C/R, no reescribe el motor — escribe una capa nueva.** El
núcleo no cambia. Cada persona ejecuta con las capas que quiera, o con todas.

### Las tres clases de capa (contratos)

| Capa | Pregunta que responde | Contrato de función |
|------|----------------------|---------------------|
| `index_provider` | ¿Qué índices numéricos tiene el cuerpo? | `(body, ctx) -> (indices, origen)` |
| `scheme` | ¿A qué clase/código pertenece? | `(body, indices, ctx) -> {clase, codigo, centralidad, ...}` |
| `gate` | ¿Tiene datos suficientes para el catálogo oficial? | `(body, ctx) -> (admitido, motivos)` |

Cada capa se auto-registra con un decorador (`@index_provider("ecr")`, etc.) y se activa
por nombre en la config. Añadir una capa = crear un archivo en `layers/`. **No se toca el núcleo.**

---

## Uso rápido

Sin dependencias externas. Solo Python 3.8+.

```bash
python run.py                         # clasifica con la config por defecto (ZEE-7)
python run.py --scheme simple3        # mismo núcleo, taxonomía de 3 clases
python run.py --provider ecr --scheme zee7 --out mi_investigacion.csv
python tests/test_controls.py         # los 8 controles deben pasar
```

Ejemplo de salida (extracto):

```
Cuerpo                 Código Central.  Admit.  Índices
Tierra                     A9     8.67      sí   E9 C9 R8
Europa                     O7     6.67      sí   E7 C7 R6
Titan                      M5     5.33      sí   E5 C5 R6
```

---

## Capas incluidas de serie

- **`indices_ecr`** — Índices E (energía), C (persistencia química), R (resistencia) del
  modelo ATLAS v0.1. Usa el valor del **experto** si el cuerpo lo trae; si no, aplica una
  **fórmula física** aproximada (marcada como tal). Así los cuerpos curados conservan el
  juicio experto y los importados de catálogos obtienen igualmente un valor automático.
  *La fórmula es el primer sitio pensado para que la comunidad la mejore.*
- **`scheme_zee7`** — Las 7 familias ZEE: A·M·O·V·C·G·X. Código = Familia + round(CCE).
- **`scheme_simple3`** — Esquema alternativo de 3 clases (H/T/E). Existe para **demostrar**
  que el mismo núcleo y los mismos índices dan otra taxonomía solo cambiando esta capa.
- **`gate_min_data`** — Exige datos mínimos y contraste de fuentes. No borra nada: marca
  cada cuerpo como `admitido` (catálogo verificado) o no (sandbox), con el motivo.

## Configuración (`config/default.json`)

```json
{
  "index_provider": "ecr",
  "scheme": "zee7",
  "gates": ["min_data"],
  "params": { "preferir_formula": false, "min_fuentes": 1, "exigir_radio": true }
}
```

Pon `"preferir_formula": true` para **auditar el modelo automático** ignorando al experto
y ver qué predice la fórmula sola. Cambia `"scheme"` a `"simple3"` para reclasificar.

---

## Cómo añadir tu propia capa (ejemplo: un esquema de 16 clases)

Crea `layers/scheme_zee16.py`:

```python
from atlas_core.registry import scheme

@scheme("zee16")
def classify(body, indices, ctx):
    cce = sum(indices.values()) / len(indices)
    # ...tu lógica de 16 clases...
    return {"clase": clase, "codigo": f"{clase}{round(cce)}",
            "centralidad": cce, "confianza": body.confianza, "notas": body.notas}
```

Y ejecuta `python run.py --scheme zee16`. Eso es todo. El núcleo lo descubre solo.

---

## Estructura del repo

```
atlas/
├── atlas_core/        # el núcleo estable (modelo + registro + tubería)
│   ├── model.py       # Body, Result
│   ├── registry.py    # decoradores y descubrimiento de capas
│   └── pipeline.py    # orquestación
├── layers/            # ← aquí vive toda la ciencia, y aquí se contribuye
│   ├── indices_ecr.py
│   ├── scheme_zee7.py
│   ├── scheme_simple3.py
│   └── gate_min_data.py
├── data/atlas_bodies.csv   # fuente única de verdad (90 cuerpos curados)
├── config/default.json
├── run.py
└── tests/test_controls.py  # contrato de calibración (8 controles)
```

## Estado y hoja de ruta

- **v0.2 (esto)** — núcleo modular, capas intercambiables, filtro de datos, 90 cuerpos.
- **Siguiente** — importar catálogos reales (NASA Exoplanet Archive), trayectorias
  temporales ±1 Ga, visor web y mapa galáctico. Ver `CONTRIBUTING.md`.

Cita: *ATLAS v0.2 (2026), CC-BY-4.0.*
