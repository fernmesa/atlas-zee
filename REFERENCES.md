# Referencias científicas de ATLAS

Este archivo documenta trabajos astronómicos y astrobiológicos que sustentan, informan o se complementan con ATLAS. Se organiza por relevancia y tema.

## 🔴 Críticas para observación y priorización

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

## 📚 Por agregar (planeado)

### Thermal Energy & Habitability
- Thermal modeling of icy moons (Juno, JWST data)
- Radioactive decay rates in rocky bodies
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

**Actualizado:** 18 Jul 2026  
**Mantenedor:** Comunidad ATLAS (pull requests bienvenidos)
