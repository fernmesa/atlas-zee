# Cómo contribuir a ATLAS

Hay dos formas de contribuir, y las dos importan: **aportar datos** (cuerpos nuevos o
correcciones) y **aportar capas** (nuevos índices, esquemas o filtros).

---

## 1. Aportar datos de cuerpos

La fuente única de verdad es `data/atlas_bodies.csv`. Para añadir o corregir un cuerpo,
edita ese archivo y abre un Pull Request. El CI ejecutará automáticamente la clasificación
y los 8 controles, y comentará en el PR el código ATLAS resultante.

### Filtro de datos mínimos (calidad y contraste)

Para entrar en el **catálogo verificado** (no en la zona de pruebas), un cuerpo debe
superar `gate_min_data`. Por defecto exige:

- **Radio conocido** (`radio_Re`).
- **Energía derivable**: insolación conocida, o bien masa + distancia para calcularla.
- **Contraste de fuentes**: al menos `min_fuentes` fuentes independientes en la columna
  `fuentes` (separadas por `;`).

Un cuerpo que no supere el filtro **no se rechaza** — se incorpora marcado como no admitido
(`admitido=False`) y queda visible en la sandbox para que se complete con más datos. Así
nadie pierde información, pero el catálogo oficial mantiene un mínimo de rigor.

> Regla de oro: **un dato sin fuente no es un dato.** Si añades un cuerpo, cita de dónde
> sale cada observable (misión, catálogo, paper) en la columna `fuentes`.

### Columnas del CSV

`nombre, sistema, tipo, masa_Me, radio_Re, dist_AU, insol_Wm2, atmosfera, agua,
vulcanismo, exp_E, exp_C, exp_R, exp_familia, confianza, fuentes, notas`

Los campos `exp_*` son **opcionales**: si los rellenas, aportas juicio experto; si los
dejas vacíos, el motor calculará E/C/R con su fórmula. Marca siempre `confianza` como
ALTA / MEDIA / BAJA con honestidad.

---

## 2. Aportar capas (mejorar el motor)

El motor está hecho para ser mejorado. Una idea nueva puede cambiarlo todo.

- **Nuevo índice** → `layers/indices_*.py` con `@index_provider("nombre")`.
- **Nuevo esquema** (3, 16, N clases) → `layers/scheme_*.py` con `@scheme("nombre")`.
- **Nuevo filtro** → `layers/gate_*.py` con `@gate("nombre")`.

Requisitos para aceptar una capa:

1. Respeta el contrato de su tipo (ver `atlas_core/registry.py`).
2. No modifica el núcleo (`atlas_core/`).
3. Si tu capa pretende sustituir a `zee7` como oficial, **los 8 controles deben seguir
   pasando** (`python tests/test_controls.py`). Si propones una taxonomía nueva y distinta,
   añade tu propio test de controles.
4. Documenta la capa en su docstring: qué hace, qué supone, dónde es débil.

---

## Hoja de ruta abierta (busca colaboradores)

- **Importador de catálogos** — script que traiga NASA Exoplanet Archive a la sandbox.
- **Capa temporal** — trayectorias E/C/R a ±1 Ga desde evolución estelar.
- **Visor web + mapa galáctico** — front que consuma el CSV de salida.
- **Fórmulas mejoradas** — el `indices_ecr` actual es deliberadamente tosco en R y C.

¿Tienes una idea de taxonomía distinta? Ábrela como propuesta. El objetivo no es que todos
usen la misma clasificación, sino que todos compartan el mismo núcleo y los mismos datos.
