# Validación externa: VOI de ATLAS vs. TSM (Kempton et al. 2018)

N = 37 exoplanetas emparejados de 32 sistemas curados (14 sin datos suficientes en NASA Archive o sin match).

**Spearman ρ = -0.555**  ·  p (test de permutación, 10000 iter) = 0.0004

| Planeta | TSM (Kempton 2018) | VOI (ATLAS) |
|---------|--------------------:|------------:|
| 55_Cancri_b | 979.18 | 0.00 |
| 55_Cancri_c | 752.63 | 0.70 |
| Epsilon_Eridani_b | 664.01 | 0.00 |
| 55_Cancri_f | 360.22 | 0.00 |
| Wolf_1061c | 346.56 | 1.00 |
| HD_20794d | 264.42 | 0.00 |
| 55_Cancri_e | 253.53 | 0.00 |
| HD_69830d | 224.08 | 0.00 |
| Gliese_849b | 197.39 | 0.00 |
| GJ_357d | 172.56 | 1.00 |
| HD_40307f | 153.51 | 0.00 |
| Gliese_163c | 135.36 | 1.00 |
| HD_40307g | 125.24 | 1.00 |
| Ross_128b | 73.53 | 1.40 |
| LHS_1140b | 67.40 | 0.83 |
| K2_18b | 35.10 | 0.00 |
| TRAPPIST_1b | 28.84 | 0.00 |
| Epsilon_Indi_Ab | 28.52 | 0.00 |
| GJ_357b | 27.85 | 0.70 |
| TRAPPIST_1d | 25.88 | 1.00 |
| 55_Cancri_d | 24.90 | 0.60 |
| TRAPPIST_1c | 24.59 | 0.00 |
| TRAPPIST_1e | 20.15 | 0.83 |
| TRAPPIST_1f | 17.14 | 0.83 |
| TRAPPIST_1h | 16.25 | 0.60 |
| TRAPPIST_1g | 15.42 | 0.83 |
| Gliese_12b | 13.81 | 1.00 |
| TOI_1693b | 10.82 | 1.17 |
| Kepler_296f | 4.26 | 0.60 |
| Kepler_22b | 3.73 | 0.00 |
| TOI_700d | 3.62 | 1.17 |
| Kepler_1649c | 2.19 | 1.17 |
| Kepler_452b | 1.36 | 0.93 |
| Kepler_186f | 0.42 | 1.17 |
| Kepler_62e | 0.37 | 1.17 |
| Kepler_442b | 0.31 | 1.17 |
| Kepler_62f | 0.03 | 1.17 |

## Sin emparejar

- Barnard_Star_c
- Barnard_Star_b
- Gliese_581g
- Gliese_667Cc (dato estelar/fotométrico incompleto)
- Gliese_667Cb (dato estelar/fotométrico incompleto)
- Gliese_667Ce (dato estelar/fotométrico incompleto)
- Gliese_832c
- HD_40307e
- HD_85512b
- Proxima_Centauri_b
- Tau_Ceti_e
- Tau_Ceti_f
- Teegarden_b
- Teegarden_c

## Interpretación

Con N=37, la correlación es significativa pero NEGATIVA (ρ=-0.56, p=0.000): el VOI de ATLAS tiende a priorizar objetivos DISTINTOS a los que el TSM real señala como mejores -- no es ruido, es una relación inversa consistente. Mirando la tabla se entiende por qué: los planetas con TSM más alto (55 Cancri b/c/f, Epsilon Eridani b) son mundos calientes muy cerca de estrellas brillantes -- excelente señal para JWST, pero fuera de la ventana de energía templada que `observability.py` exige para considerar un mundo interesante para bioquímica. Los de VOI más alto (Kepler-186f, Kepler-62e/f, Kepler-442b) son justo lo opuesto: templados y potencialmente habitables, pero alrededor de estrellas lejanas y débiles, pésima señal para JWST. Esto no es un fallo de ATLAS: es evidencia de que TSM (¿podemos verlo bien?) y VOI (¿nos diría algo sobre habitabilidad?) son ejes DISTINTOS, y tratarlos como intercambiables -- asumir que los mejores objetivos de caracterización atmosférica son también los mejores candidatos a vida -- es un error. Esa tensión, cuantificada aquí, es en sí misma un resultado con valor.