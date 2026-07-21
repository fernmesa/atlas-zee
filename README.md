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

### Las cuatro clases de capa (contratos)

| Capa | Pregunta que responde | Contrato de función |
|------|----------------------|---------------------|
| `index_provider` | ¿Qué índices numéricos tiene el cuerpo? | `(body, ctx) -> (indices, origen)` |
| `scheme` | ¿A qué clase/código pertenece? | `(body, indices, ctx) -> {clase, codigo, centralidad, ...}` |
| `gate` | ¿Tiene datos suficientes para el catálogo oficial? | `(body, ctx) -> (admitido, motivos)` |
| `annotator` | Enriquece el resultado sin cambiar la clase | `(body, clase, indices, ctx) -> dict` |

Cada capa se auto-registra con un decorador (`@index_provider("ecr")`, etc.) y se activa
por nombre en la config. Añadir una capa = crear un archivo en `layers/`. **No se toca el núcleo.**

---

## Clonar y ejecutar

**Requisitos:** Python 3.8+, git. Sin dependencias externas.

```bash
# Opción 1: con GitHub CLI (recomendado si lo tienes)
gh repo clone fernmesa/atlas-zee
cd atlas-zee

# Opción 2: con git estándar
git clone https://github.com/fernmesa/atlas-zee.git
cd atlas-zee
```

### Verificar la instalación

```bash
python tests/test_controls.py         # verifica que el núcleo funciona (8 controles)
```

Debe decir: **los 8 controles pasan**. Si falla, reporta el error en Issues.

### Ejecutar la clasificación

```bash
python run.py                         # clasifica con config por defecto
```

Salida: `salida_clasificacion.csv` con todos los cuerpos y sus índices.

## Uso rápido

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
- **`hypothesis_biochem`** *(anotador)* — Por cada familia, aventura qué bioquímica sería
  compatible (disolvente, esqueleto, metabolismo, análogo terrestre), con etiqueta explícita
  de si es real, plausible o especulativo. No cambia la clasificación.
- **`observability`** *(anotador)* — Calcula el **valor de la información**: qué datos faltan,
  cuánto subiría la clasificación si fueran favorables, y con qué plausibilidad. Alimenta el
  generador de solicitudes de observación.
- **`indices_ecr_ml`** — Alternativa a `indices_ecr` con un tercer escalón: experto → fórmula →
  **fallback k-vecinos-más-cercanos** (Python puro, sin dependencias) para el caso límite de un
  cuerpo sin ningún observable físico/químico conocido. Úsala con `--provider ecr_ml`.
- **`gate_quality_schema`** — Valida forma y rango de los datos (masa negativa, familia mal
  escrita, radio implausible...) contra `data/atlas_body_schema.json`, antes de que lleguen a la
  ciencia. Complementa a `gate_min_data`: esta capa exige que lo que HAY sea válido, no que haya
  suficiente cantidad.
- **`energy_orbital`** *(anotador)* — Estima energía orbital específica, velocidad orbital y
  periodo (Kepler III) desde `dist_AU`, y detecta resonancias orbitales simples (2:1, 3:2...)
  entre cuerpos del mismo sistema. Asume estrella ~1 M☉ salvo en el sistema Solar.
- **`atmosphere_retention`** *(anotador)* — Clasifica probable/incierta/improbable la
  retención atmosférica según el umbral de radio de STEHM (0.8 R⊕, ver `REFERENCES.md`),
  y señala explícitamente qué factores decisivos del paper (carbono del manto, fracción
  de núcleo...) ATLAS no observa. También informa el umbral de `_R_formula()`.

## Herramientas (`tools/`)

```bash
python tools/import_nasa.py --limit 200        # importa exoplanetas reales del NASA Archive
python tools/observation_requests.py --top 10  # prioriza objetivos para pedir telescopio
python tools/classify_stars.py                 # clasifica estrellas por sus planetas
python tools/validate_voi_vs_tsm.py             # valida el VOI contra el TSM real (Kempton 2018)
```

`classify_stars.py` agrega la clasificación de los planetas de cada sistema en un
**índice anfitrión** por estrella (media ponderada de los 3 mejores mundos), pensado
para priorizar sistema completo en vez de planeta suelto. Sistemas binarios/múltiples:
`Body.sistema` ya nombra la componente estelar concreta (p.ej. "Gliese 667C"), siguiendo
la convención `host_star_flag` de NASA — ver `data/reference/nasa_exoplanet_archive_parameter_template.csv`.

`validate_voi_vs_tsm.py` contrasta la prioridad VOI de `observability.py` contra el TSM
(Transmission Spectroscopy Metric, la métrica real que la comunidad usa para elegir
objetivos JWST) para los ~40 exoplanetas curados, trayendo datos estelares/fotométricos
en vivo del NASA Exoplanet Archive. Resultado actual (ver `validacion_voi_vs_tsm.md`):
correlación de Spearman ρ=-0.56 (p=0.0004, N=37) — **negativa y significativa**, evidencia
de que VOI (¿nos diría algo sobre habitabilidad?) y TSM (¿podemos verlo bien con JWST?)
son ejes distintos, no intercambiables. Ver `REFERENCES.md` para la cita completa.

El importador trae lo medible (masa, radio, insolación) y deja atmósfera/agua en blanco:
los mundos sin datos caen honestamente en **X** con confianza BAJA, y el generador de
solicitudes los señala como candidatos donde una espectroscopía cambiaría más la clasificación.

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
│   ├── scheme_zee7.py · scheme_simple3.py
│   ├── gate_min_data.py
│   ├── hypothesis_biochem.py     # anotador: hipótesis de vida por familia
│   └── observability.py          # anotador: prioridad de observación (VOI)
├── tools/             # importador NASA + generador de solicitudes
├── data/
│   ├── atlas_bodies.csv    # fuente única de verdad (90 cuerpos curados)
│   └── host_stars.csv      # 15 estrellas con coordenadas verificadas
├── docs/index.html    # visor web (mapas E-C, orbital, vecindario, galáctico)
├── config/default.json
├── run.py
└── tests/test_controls.py  # contrato de calibración (8 controles)
```

## Desplegar el visor web

El visor interactivo (`docs/atlas_visual.html`) es una página estática pura — sin servidor,
sin dependencias. Corre en el navegador con los datos incrustados.

### Opciones de despliegue

| Plataforma | Costo | Público/Privado | Configuración |
|------------|-------|-----------------|---------------|
| **Cloudflare Pages** | Gratis | Ambos | Conectar repo, output dir `/docs` |
| **GitHub Pages** | Gratis | Solo público | Settings → Pages → `/docs` branch main |
| **Netlify / Vercel** | Gratis | Ambos | Deploy desde `/docs`, sin build |

El repo es **privado** — GitHub Pages requeriría plan de pago para ello, pero **Cloudflare Pages**
funciona gratis incluso para repos privados. Recomendado.

### Servir en local (desarrollo)

```bash
python -m http.server -d docs 8000
# abre http://localhost:8000/atlas_visual.html
```

## Contribuir

El repo usa **rama `main` protegida**: todo cambio pasa por Pull Request (PR). No hay push directo.

```bash
# Tu flujo
git checkout -b tu-rama
# ...haz cambios, tests, commits...
git push origin tu-rama
# Abre un PR en GitHub (gh pr create)
```

Ver `CONTRIBUTING.md` para estándares de código.

## Estado y hoja de ruta

- **v0.2 (esto)** — núcleo modular, capas intercambiables, 90 cuerpos curados, 4 esquemas.
  Visor web con 4 vistas (E-C, orbital, vecindario, galactocéntrico). Importador NASA,
  generador de solicitudes de observación. 8 controles calibrados.
- **v0.3** — trayectorias temporales ±1 Ga (simulación de evolución estelar).
  Integración con catálogos de exoplanetas (~5900 confirmados). Deduplicación automática.
- **v1.0** — publicación peer-reviewed, API abierta, dashboard colaborativo vía PR.

Ver `CONTRIBUTING.md` para cómo proponer nuevas capas o mejoras al modelo.

---

## Referencias científicas

ATLAS se apoya en observaciones, datos y métodos de la comunidad astronómica. Esta lista marca trabajos de especial relevancia para la priorización de observaciones y mejora de datos espectrales.

### Detección de exoplanetas terrestres

- **Liang, Y., Winn, J.N., Melchior, P., Lu, S., Tran, Q.H.** (2026)  
  *AESTRA II: Generative Spectral Modeling of the Sun as a Star for Precise Radial Velocities*  
  arXiv:2606.13574  
  **Relevancia para ATLAS:** Descomposición espectral mejora dramáticamente la detección de planetas pequeños (K < 0.3 m/s). AESTRA filtra variabilidad estelar, absorción telúrica e instrumental, dejando datos limpios para calcular parámetros E, C, R. El método identifica 238 planetas en pruebas de inyección-recuperación, incluyendo 13 bajo 0.3 m/s. Usamos sus rangos de periodicidad (2.5-400 días) y métricas de confiabilidad para priorizar candidatos a observar.

### Retención atmosférica y habitabilidad

- **Hill, M.L., Kane, S.R., Foley, B.J., Schaefer, L.K.** (2026)  
  *Smaller Than Earth Habitability Model (STEHM): The Lower Size Limit for Atmosphere Retention in the Habitable Zone*  
  The Planetary Science Journal, 7(6) · https://iopscience.iop.org/article/10.3847/PSJ/ae6804  
  **Relevancia para ATLAS:** Determina el radio mínimo (0.8 R⊕ bajo condiciones tipo Tierra) para retener atmósfera en escalas multi-gigaaño, y muestra que el factor más decisivo es el inventario de carbono del manto, no el tamaño. Sustituye el corte de masa previo de `_R_formula()` por este umbral de radio, con base física real. La capa `atmosphere_retention` documenta explícitamente qué factores del paper (composición de manto/núcleo) ATLAS no observa, en vez de fingir certeza inexistente.

---

Cita: *ATLAS v0.2 (2026), CC-BY-4.0. Motor abierto de clasificación de Zonas de Estabilidad Ecosistémica.*
