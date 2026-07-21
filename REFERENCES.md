# Referencias científicas de ATLAS

Este archivo documenta trabajos astronómicos y astrobiológicos que sustentan, informan o se complementan con ATLAS. Se organiza por relevancia y tema.

## 🔴 Críticas para observación y priorización

### Priorización observacional (el estándar del campo)

**Kempton, E.M.-R., Bean, J.L., Louie, D.R., Deming, D., Koll, D.D.B., et al.** (2018)  
**A Framework for Prioritizing the TESS Planetary Candidates Most Amenable to Atmospheric Characterization**  
*PASP 130, 114401 · arXiv:1805.03671*

- **Contribución:** Define el TSM (Transmission Spectroscopy Metric) y el ESM (Emission
  Spectroscopy Metric), las métricas que la comunidad usa DE HECHO para decidir qué
  exoplanetas observar con JWST. TSM = (scale_factor) × Rp³Teq / (Mp·R*²) × 10^(-mJ/5),
  con scale_factor por bin de radio (0.190 / 1.26 / 1.28 / 1.15) calibrado contra
  simulaciones JWST/NIRISS de 10h. Umbrales sugeridos: TSM>10 para mundos templados
  <2R⊕, TSM>90 para el resto hasta 10R⊕, ESM>7.5 para terrestres.
- **Para ATLAS:** Usado como contraste externo del VOI (`observability.py`) en
  `tools/validate_voi_vs_tsm.py`. Resultado (N=37, datos NASA Archive en vivo): Spearman
  ρ=-0.56, p=0.0004 -- correlación **significativa y negativa**. No es un fallo del VOI:
  TSM mide "¿podemos verlo bien?" (favorece mundos calientes cerca de estrellas
  brillantes) mientras VOI mide "¿nos diría algo sobre habitabilidad?" (favorece mundos
  templados, sin importar la calidad de la señal) -- son ejes distintos que el campo
  tiende a conflacionar. Ver `validacion_voi_vs_tsm.md` para la tabla completa y el
  razonamiento caso por caso.

**Cómo usarlo:**
```python
# tools/validate_voi_vs_tsm.py implementa el TSM completo (Eq. 1) con la
# relación masa-radio de Chen & Kipping 2017 cuando falta masa medida (Eq. 2)
```

---

### Spectroscopy & Radial Velocities

**Liang, Y., Winn, J.N., Melchior, P., Lu, S., Tran, Q.H.** (2026)  
**AESTRA II: Generative Spectral Modeling of the Sun as a Star for Precise Radial Velocities**  
*arXiv:2606.13574 · astro-ph.EP*

- **Contribución:** Método AESTRA descompone espectros en variabilidad estelar, absorción telúrica y ruido instrumental sin templates externos. Recupera 238 planetas en inyección-recovery, incluyendo 13 con K < 0.3 m/s (vs. 0 con CCF tradicional).
- **Para ATLAS:** 
  - Limpia datos para cálculo robusto de E (energía), C (persistencia química)
  - Periodicidades detectables (2.5–400 días) abarcan órbitas de mundos acuáticos
  - Cero detecciones espurias → confianza en admisión de candidatos
  - Prioriza observaciones de planetas pequeños donde falta dato de atmósfera

**Cómo usarlo:** 
```python
# En observability.py, considera AESTRA para calcular VOI (Value of Information)
# Un objetivo con K < 0.3 m/s sin datos de atmósfera es de máxima prioridad
```

---

### Thermal Energy & Habitability

**Hill, M.L., Kane, S.R., Foley, B.J., Schaefer, L.K.** (2026)  
**Smaller Than Earth Habitability Model (STEHM): The Lower Size Limit for Atmosphere Retention in the Habitable Zone**  
*The Planetary Science Journal, 7(6) · https://iopscience.iop.org/article/10.3847/PSJ/ae6804*

- **Contribución:** Modelo 1D (ExoPlex + evolución térmica de manto en tapa estancada +
  escape atmosférico por flujo XUV/Jeans) que determina el radio mínimo para retener
  atmósfera multi-gigaaño en zona habitable. Umbral por defecto: **0.8 R⊕**. El factor
  MÁS influyente no es el tamaño sino el **inventario inicial de carbono del manto**,
  seguido de fracción de núcleo, temperatura inicial del manto y elementos radiogénicos.
  Validado contra Venus y Marte como referencia observacional. Mundos pequeños con manto
  rico en carbono o núcleo pequeño pueden retener o RECUPERAR atmósfera aun por debajo
  del umbral por defecto.
- **Para ATLAS:**
  - Sustituye el corte de masa (0.1-10 M⊕) de `_R_formula()` por un umbral de **radio**
    con base física real (ver `layers/indices_ecr.py`)
  - Expone que ATLAS no modela composición de manto/núcleo -- la capa
    `layers/atmosphere_retention.py` lo marca explícitamente como laguna, en vez de
    fingir certeza que no existe
  - Un mundo bajo 0.8 R⊕ con composición desconocida es exactamente el tipo de objetivo
    que `observability.py` debería priorizar: el dato que falta (carbono del manto)
    puede cambiar la clasificación de "sin atmósfera" a "posible"

**Cómo usarlo:**
```python
# layers/indices_ecr.py: _R_formula() usa el umbral de 0.8 R⊕ cuando hay radio conocido
# layers/atmosphere_retention.py: annotator con la clasificación probable/incierta/improbable
# y la lista explícita de qué factores decisivos de STEHM no se observan en ATLAS
```

---

## 📚 Por agregar (planeado)

### Thermal Energy & Habitability (más allá de STEHM)
- Thermal modeling of icy moons (Juno, JWST data)
- Radioactive decay rates in rocky bodies -- modelar el inventario de carbono/HPE
  que STEHM identifica como factor dominante y que ATLAS aún no observa
- Tidal heating: Love numbers, orbital evolution

### Ecosystem Stability (teoría ZEE)
- Osborn et al. (2023) on biosignature false positives
- Krissansen-Totton et al. on coupled climate models
- Forget et al. on exoplanet GCMs

### Exoplanet Catalogs & Data
- NASA Exoplanet Archive (completeness, biases)
- JWST spectroscopy releases (atmospheric composition)
- Gaia astrometry improvements

---

## Cómo contribuir referencias

1. Si encuentras un paper relevante, abre un **Issue** o **PR** con:
   - Autores, año, título, arXiv/DOI
   - 1–2 párrafos de qué aporta a ATLAS
   - Sección sugerida (Observación, Modelos, Datos, etc.)

2. Si es crítico para alguna capa (p. ej., `indices_ecr.py`):
   - Comenta la referencia en el código
   - Agrégala aquí con link a la línea

3. Se prefieren:
   - Papers **revisados por pares** o preprints de arxiv
   - Trabajos **datados 2015+** (datos recientes)
   - Que **cuantifiquen** (fórmulas, datos, errores), no solo especulen

---

**Actualizado:** 20 Jul 2026  
**Mantenedor:** Comunidad ATLAS (pull requests bienvenidos)
