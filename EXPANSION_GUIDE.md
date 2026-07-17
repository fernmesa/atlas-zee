# ATLAS Expansion Guide

## Expanding the Dataset with NASA Exoplanet Archive

The ATLAS dataset currently includes 90+ curated bodies. To expand significantly, integrate data from NASA's Exoplanet Archive.

### Method 1: Direct CSV Download (Recommended)

1. **Visit NASA Exoplanet Archive:**
   https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView

2. **Select "Exoplanet table" and filter:**
   - Click: Planet Radius, Planet Mass, Discovery Year, Discovery Method
   - Optionally: Equilibrium Temperature, Orbital Period, Host Star Distance

3. **Download as CSV:**
   - Click "Download Table" → CSV format
   - Save as: `data/exoplanet_archive.csv`

4. **Process with merge tool:**
   ```bash
   python tools/merge_nasa_to_atlas.py
   ```

### Method 2: Automated API (if TAP endpoint recovers)

```bash
python tools/import_nasa_robust.py
```

This uses NASA TAP (Table Access Protocol) with retries.

### Merging Data

Once you have NASA data, the system:

1. **Preserves** all existing curated data (exp_E, exp_C, exp_R, exp_familia)
2. **Enriches** with NASA metadata (discovery_year, discovery_method, reference_links)
3. **Calculates** E, C, R indices using formulas when expert values unavailable
4. **Marks** confidence levels appropriately (MEDIA if masa+radio, BAJA otherwise)

Output: `data/atlas_bodies_merged.csv`

### Analyzing Expanded Patterns

After merging:

```bash
python tools/pattern_analysis_expanded.py
```

This detects:
- Family distribution across the galaxy
- Clustering patterns (e.g., Acuatics group at ~12 ly from center)
- Distance trends by family type
- High-value observation targets (VOI ranking)

### Contribution Guidelines

To add new data via GitHub:

1. **Fork** the repository
2. **Download NASA data** (Method 1 above)
3. **Merge** locally: `python tools/merge_nasa_to_atlas.py`
4. **Run analysis** to validate patterns: `python tools/pattern_analysis_expanded.py`
5. **Commit** the merged CSV + analysis results
6. **Pull Request** with description of new pattern findings

**Important:** Always preserve expert annotations (exp_E, exp_C, exp_R) for curated bodies. NASA data supplements, never replaces, expert judgments.

### Dataset Statistics (Current)

- Curated bodies: 90
- With complete coordinates: 31
- NASA exoplanets available: 5,600+
- Target after expansion: 500-1000 (verified, well-characterized)

### Quick Start

```bash
# Download NASA data to data/exoplanet_archive.csv (via browser)
python tools/merge_nasa_to_atlas.py
python tools/pattern_analysis_expanded.py
```

Then check updated visualizations at `docs/index.html`
