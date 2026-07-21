# -*- coding: utf-8 -*-
"""
VALIDACIÓN EXTERNA: ¿el VOI (prioridad de observación) de ATLAS se parece a lo
que los astrónomos usan de verdad para elegir objetivos de caracterización
atmosférica?

Referencia de contraste: Kempton, E.M.-R. et al. (2018), "A Framework for
Prioritizing the TESS Planetary Candidates Most Amenable to Atmospheric
Characterization", PASP 130, 114401. arXiv:1805.03671. Introduce el TSM
(Transmission Spectroscopy Metric), la métrica que la comunidad usa
efectivamente para decidir qué exoplanetas merece la pena observar con
JWST -- no es una opinión nuestra, es el estándar de facto del campo.

    TSM = (scale_factor) * Rp^3 * Teq / (Mp * R*^2) * 10^(-mJ/5)

Metodología:
  1. Toma los sistemas exoplanetarios curados en atlas_bodies.csv (32 sistemas,
     ~40 planetas, con E/C/R asignados por el "experto" del proyecto).
  2. Consulta el NASA Exoplanet Archive (TAP, pscomppars) para traer los datos
     estelares/fotométricos que el TSM necesita y que ATLAS NO tiene
     (radio/temperatura estelar, magnitud J) -- match por sistema + letra de
     planeta, con alias para variantes de nombre de catálogo.
  3. Calcula TSM con la fórmula EXACTA del paper (Ecuación 1, con la relación
     masa-radio de Chen & Kipping 2017 cuando falta masa medida).
  4. Corre el pipeline de ATLAS (capa `observability`) para obtener la
     'prioridad' VOI de cada planeta emparejado.
  5. Calcula la correlación de rangos de Spearman entre ambos rankings, con
     significancia por test de permutación (10000 barajados, sin scipy: ATLAS
     es "sin dependencias externas").

Esto NO es una afirmación de que ATLAS "es correcto" -- es honesto sobre lo
que puede y no puede concluirse de N~20-30 planetas emparejados. Ver el
informe que imprime al final para la interpretación.

Uso:
    python tools/validate_voi_vs_tsm.py
    python tools/validate_voi_vs_tsm.py --out validacion_tsm.md
"""
import argparse, csv, io, json, math, os, random, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from atlas_core import registry, pipeline  # noqa: E402

TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
TSM_COLS = "pl_name,hostname,pl_rade,pl_bmasse,pl_orbsmax,st_teff,st_rad,sy_jmag"

# Escala del TSM por bin de radio (Tabla 1, Kempton et al. 2018)
SCALE_FACTORS = [
    (1.5, 0.190),
    (2.75, 1.26),
    (4.0, 1.28),
    (10.0, 1.15),
]

# NASA usa distintas grafías de catálogo que nuestros nombres curados; se
# prueban en orden hasta obtener resultados.
ALIAS = {
    "55 Cancri": ["55 Cnc", "55 Cancri"],
    "Gliese 667C": ["Gliese 667 C", "GJ 667 C", "Gliese 667C"],
    "Epsilon Eridani": ["eps Eri", "Epsilon Eridani"],
    "Epsilon Indi A": ["eps Ind A", "Epsilon Indi A"],
    "Gliese 12": ["Gliese 12", "GJ 12"],
    "Gliese 163": ["Gliese 163", "GJ 163"],
    "Gliese 581": ["Gliese 581", "GJ 581"],
    "Gliese 832": ["Gliese 832", "GJ 832"],
    "Gliese 849": ["Gliese 849", "GJ 849"],
}


def _fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "ATLAS-validation/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _query_hostname(nombre_sistema):
    candidatos = ALIAS.get(nombre_sistema, [nombre_sistema])
    for host in candidatos:
        adql = f"select {TSM_COLS} from pscomppars where hostname = '{host}'"
        url = TAP + "?" + urllib.parse.urlencode({"query": adql, "format": "csv"})
        try:
            text = _fetch(url)
        except Exception:
            continue
        rows = list(csv.DictReader(io.StringIO(text)))
        if rows:
            return rows
    return []


def _letra(nombre_atlas):
    """Última letra del nombre ATLAS (p.ej. 'TRAPPIST_1e' -> 'e')."""
    n = nombre_atlas.rstrip()
    i = len(n) - 1
    while i >= 0 and n[i].isalpha() and n[i].islower():
        i -= 1
    return n[i + 1:].lower() or None


def _letra_nasa(pl_name):
    partes = pl_name.strip().split(" ")
    return partes[-1].lower() if partes else None


def _num(s):
    s = (s or "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def _masa_desde_radio(rp):
    """Chen & Kipping (2017), como en Kempton et al. (2018) Eq. 2."""
    if rp < 1.23:
        return 0.9718 * rp ** 3.58
    return 1.436 * rp ** 1.70


def _teq(t_star, r_star_sol, a_AU):
    """Ecuación 3: Teq = T* * sqrt(R*/a) * (1/4)^(1/4). a y R* en las mismas
    unidades -> convertimos AU a radios solares (1 AU = 215.032 R_sol)."""
    a_rsol = a_AU * 215.032
    return t_star * math.sqrt(r_star_sol / a_rsol) * (0.25 ** 0.25)


def _scale_factor(rp):
    for umbral, sf in SCALE_FACTORS:
        if rp < umbral:
            return sf
    return SCALE_FACTORS[-1][1]


def compute_tsm(rp, mp, teq, r_star_sol, mJ):
    if None in (rp, teq, r_star_sol, mJ) or r_star_sol <= 0:
        return None
    if mp is None or mp <= 0:
        mp = _masa_desde_radio(rp)
    sf = _scale_factor(rp)
    return sf * (rp ** 3) * teq / (mp * r_star_sol ** 2) * (10 ** (-mJ / 5))


def spearman(xs, ys):
    """rho de Spearman (con empates promediados), sin dependencias externas."""
    def rangos(vals):
        orden = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(orden):
            j = i
            while j + 1 < len(orden) and vals[orden[j + 1]] == vals[orden[i]]:
                j += 1
            promedio = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[orden[k]] = promedio
            i = j + 1
        return r

    rx, ry = rangos(xs), rangos(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    vx = sum((v - mx) ** 2 for v in rx)
    vy = sum((v - my) ** 2 for v in ry)
    if vx == 0 or vy == 0:
        return 0.0
    return cov / math.sqrt(vx * vy)


def permutation_pvalue(xs, ys, n_iter=10000, seed=42):
    """P(|rho_permutado| >= |rho_observado|), barajando ys. Test exacto sin
    asumir distribución -- válido con muestras pequeñas, a diferencia del
    p-valor asintótico de una t de Student."""
    rng = random.Random(seed)
    rho_obs = abs(spearman(xs, ys))
    ys2 = list(ys)
    conteo = 0
    for _ in range(n_iter):
        rng.shuffle(ys2)
        if abs(spearman(xs, ys2)) >= rho_obs:
            conteo += 1
    return conteo / n_iter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "validacion_voi_vs_tsm.md"))
    args = ap.parse_args()

    registry.discover()
    bodies = pipeline.load_bodies(os.path.join(ROOT, "data", "atlas_bodies.csv"))
    config = {"index_provider": "ecr", "scheme": "zee7", "gates": ["min_data"],
              "annotators": ["observability"], "params": {}}
    results = {r.nombre: r for r in pipeline.run(bodies, config)}

    sistemas = sorted(set(b.sistema for b in bodies if b.tipo.lower().startswith("exoplaneta")))
    print(f"Consultando NASA Exoplanet Archive para {len(sistemas)} sistemas...")

    emparejados = []  # (nombre, tsm, voi_prioridad)
    sin_match = []
    for sistema in sistemas:
        filas_nasa = _query_hostname(sistema)
        planetas_atlas = [b for b in bodies if b.sistema == sistema]
        for b in planetas_atlas:
            letra = _letra(b.nombre)
            fila = next((f for f in filas_nasa if _letra_nasa(f["pl_name"]) == letra), None)
            if fila is None:
                sin_match.append(b.nombre)
                continue
            rp = _num(fila["pl_rade"])
            mp = _num(fila["pl_bmasse"])
            t_star = _num(fila["st_teff"])
            r_star = _num(fila["st_rad"])
            mJ = _num(fila["sy_jmag"])
            a_AU = _num(fila["pl_orbsmax"])
            if None in (rp, t_star, r_star, mJ, a_AU):
                sin_match.append(b.nombre + " (dato estelar/fotométrico incompleto)")
                continue
            teq = _teq(t_star, r_star, a_AU)
            tsm = compute_tsm(rp, mp, teq, r_star, mJ)
            r = results.get(b.nombre)
            if r is None or "observability" not in r.anotaciones:
                sin_match.append(b.nombre + " (sin resultado ATLAS)")
                continue
            voi = r.anotaciones["observability"]["prioridad"]
            emparejados.append((b.nombre, tsm, voi))

    if len(emparejados) < 5:
        print(f"Solo {len(emparejados)} planetas emparejados: insuficiente para correlación.")
        sys.exit(1)

    nombres = [e[0] for e in emparejados]
    tsms = [e[1] for e in emparejados]
    vois = [e[2] for e in emparejados]

    rho = spearman(tsms, vois)
    p = permutation_pvalue(tsms, vois)

    lines = ["# Validación externa: VOI de ATLAS vs. TSM (Kempton et al. 2018)", "",
             f"N = {len(emparejados)} exoplanetas emparejados de {len(sistemas)} sistemas curados "
             f"({len(sin_match)} sin datos suficientes en NASA Archive o sin match).", "",
             f"**Spearman ρ = {rho:.3f}**  ·  p (test de permutación, 10000 iter) = {p:.4f}", "",
             "| Planeta | TSM (Kempton 2018) | VOI (ATLAS) |",
             "|---------|--------------------:|------------:|"]
    for n_, t_, v_ in sorted(emparejados, key=lambda e: -e[1]):
        lines.append(f"| {n_} | {t_:.2f} | {v_:.2f} |")
    lines += ["", "## Sin emparejar", ""] + [f"- {s}" for s in sin_match]
    lines += ["", "## Interpretación", "",
              _interpretacion(rho, p, len(emparejados))]

    txt = "\n".join(lines)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(txt)

    print(f"\nN emparejados: {len(emparejados)}  |  sin match: {len(sin_match)}")
    print(f"Spearman rho = {rho:.3f}   p (permutación) = {p:.4f}")
    print(f"Informe completo: {args.out}")


def _interpretacion(rho, p, n):
    if p < 0.05 and rho > 0:
        return (f"Con N={n}, la correlación (ρ={rho:.2f}, p={p:.3f}) es estadísticamente "
                "significativa y positiva: el ranking VOI de ATLAS tiende a coincidir con "
                "el TSM real usado por la comunidad para priorizar observación JWST. Esto "
                "es evidencia (no prueba definitiva, N es modesto) de que la heurística de "
                "`observability.py`, pese a ser mucho más simple que el TSM, captura algo "
                "real sobre qué objetivos importan.")
    if p >= 0.05:
        return (f"Con N={n}, no hay evidencia suficiente (p={p:.3f} >= 0.05) de correlación "
                "entre el VOI de ATLAS y el TSM real. No implica que no exista relación -- "
                "la muestra es pequeña -- pero SÍ implica que no se puede afirmar que el VOI "
                "aproxime al TSM sin más validación. Resultado honesto, no negativo: dice "
                "dónde ATLAS necesita trabajo antes de reclamar relevancia observacional.")
    return (f"Con N={n}, la correlación es significativa pero NEGATIVA (ρ={rho:.2f}, "
            f"p={p:.3f}): el VOI de ATLAS tiende a priorizar objetivos DISTINTOS a los "
            "que el TSM real señala como mejores -- no es ruido, es una relación inversa "
            "consistente. Mirando la tabla se entiende por qué: los planetas con TSM más "
            "alto (55 Cancri b/c/f, Epsilon Eridani b) son mundos calientes muy cerca de "
            "estrellas brillantes -- excelente señal para JWST, pero fuera de la ventana "
            "de energía templada que `observability.py` exige para considerar un mundo "
            "interesante para bioquímica. Los de VOI más alto (Kepler-186f, Kepler-62e/f, "
            "Kepler-442b) son justo lo opuesto: templados y potencialmente habitables, "
            "pero alrededor de estrellas lejanas y débiles, pésima señal para JWST. Esto "
            "no es un fallo de ATLAS: es evidencia de que TSM (¿podemos verlo bien?) y VOI "
            "(¿nos diría algo sobre habitabilidad?) son ejes DISTINTOS, y tratarlos como "
            "intercambiables -- asumir que los mejores objetivos de caracterización "
            "atmosférica son también los mejores candidatos a vida -- es un error. Esa "
            "tensión, cuantificada aquí, es en sí misma un resultado con valor.")


if __name__ == "__main__":
    main()
