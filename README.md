# Empirical Analysis of Turkey's Sovereign CDS Spreads

Replication code and data for the undergraduate thesis **"Pressure from Outside: An Empirical Investigation of the Effects of U.S. Interest Rates, the Dollar Index, and Domestic Vulnerabilities on Turkey's Country Risk Premium"** (Ali Altıntaş).

The study estimates the external and domestic determinants of Turkey's 5-year sovereign CDS spread using weekly data from January 2010 to December 2025 (N = 835), via OLS with Newey-West HAC standard errors.

## Repository structure

```
.
├── data/
│   ├── Turkiye_CDS_Veriseti.csv                  # analysis-ready dataset (see data_dictionary.md)
│   ├── TR_Model_Veriseti_Haftalik_corrected.xlsx # raw weekly data + correction note
│   └── data_dictionary.md
├── code/
│   └── cds_analysis.py                           # reproduces all tables below (A1–A5)
├── results/
│   └── results_output.txt                        # saved program output
└── requirements.txt
```

## How to run

```bash
pip install -r requirements.txt
python code/cds_analysis.py
```

## Model

```
CDS_t = β0 + β1·US10Y_t + β2·ln(DXY)_t + β3·ln(RES)_t + β4·BRUNSON_t + β5·AGBAL_t + ε_t
```

Model 1 includes US10Y; Model 2 (final) drops US10Y after diagnostic evaluation. Standard errors are Newey-West HAC (lag = 4).

## Results

### Model 1 — Full

| Variable | Coef. | Std. Err. | t | p |
|---|---|---|---|---|
| Constant | -1318.36 | 414.65 | -3.18 | 0.0015 *** |
| US10Y | -12.09 | 7.64 | -1.58 | 0.1139 |
| ln(DXY) | 1043.39 | 94.86 | 11.00 | 0.0000 *** |
| ln(RES) | -264.05 | 41.67 | -6.34 | 0.0000 *** |
| BRUNSON | 79.98 | 31.49 | 2.54 | 0.0113 ** |
| AGBAL | 68.04 | 14.53 | 4.68 | 0.0000 *** |

R² = 0.4841 · Adj. R² = 0.4810 · F = 187.67 · N = 835

### Model 2 — Final (US10Y excluded)

| Variable | Coef. | Std. Err. | t | p |
|---|---|---|---|---|
| Constant | -1014.91 | 400.28 | -2.54 | 0.0114 ** |
| ln(DXY) | 1027.52 | 94.70 | 10.85 | 0.0000 *** |
| ln(RES) | -286.69 | 39.06 | -7.34 | 0.0000 *** |
| BRUNSON | 73.80 | 30.92 | 2.39 | 0.0172 ** |
| AGBAL | 74.16 | 14.90 | 4.98 | 0.0000 *** |

R² = 0.4785 · Adj. R² = 0.4760 · F = 224.16 · N = 835

*Interpretation: a 1% rise in DXY is associated with ≈ 10.28 bps higher CDS; a 1% rise in reserves with ≈ 2.87 bps lower CDS.*

### VIF (Model 1)

| Variable | VIF |
|---|---|
| US10Y | 1.24 |
| ln(DXY) | 1.19 |
| ln(RES) | 1.35 |
| BRUNSON | 1.01 |
| AGBAL | 1.01 |

All VIF < 5 → no multicollinearity.

### Diagnostics

| Test | Statistic | Conclusion |
|---|---|---|
| Durbin-Watson (M1) | 0.0511 | Strong positive autocorrelation → HAC applied |
| Breusch-Pagan (M1 / M2) | 134.35 / 137.65 (p < 0.001) | Heteroskedasticity → HAC applied |
| Jarque-Bera (M1 / M2) | 111.39 / 100.49 (p < 0.001) | Non-normal residuals; mitigated by N = 835 |
| ADF — level (all vars) | non-stationary | Unit root; all variables I(1) |
| ADF — first difference | stationary | Stationary after differencing |
| Engle-Granger (M1 / M2) | -2.73 / -2.76 | No cointegration at conventional levels |

### Robustness — First Differences (Table A5)

Because all I(1) variables are differenced, this specification removes common trends; a relationship that survives differencing is not a spurious artifact of shared trending behaviour. The crisis dummies are kept in levels (they flag specific shock weeks).

| Variable | Coef. | Std. Err. | t | p |
|---|---|---|---|---|
| Constant | -0.29 | 0.70 | -0.41 | 0.6783 |
| Δ US10Y | -16.11 | 8.44 | -1.91 | 0.0568 * |
| Δ ln(DXY) | 672.30 | 139.37 | 4.82 | 0.0000 *** |
| Δ ln(RES) | -246.31 | 56.66 | -4.35 | 0.0000 *** |
| BRUNSON | 44.34 | 6.37 | 6.96 | 0.0000 *** |
| AGBAL | 40.91 | 21.23 | 1.93 | 0.0542 * |

R² = 0.1628 · Adj. R² = 0.1577 · F = 22.66 · N = 834

Δln(DXY) and Δln(RES) remain highly significant (p < 0.001) with the expected signs, confirming that the level-regression findings reflect a genuine economic relationship rather than a spurious one. The lower R² is expected, since the differenced model explains short-run weekly changes rather than the level of the spread.

**Note on the level regression.** Because the variables are I(1) and the Engle-Granger test does not provide significant evidence of cointegration, the level results are interpreted with caution and rely on the large sample and the HAC correction. The first-difference specification above (Table A5) serves as the robustness check; a full error-correction (ECM) framework is left for future work (see thesis Sections 4.3 and 5.3).

## Data

See [`data/data_dictionary.md`](data/data_dictionary.md). The only correction applied to the raw series is documented in the **Correction Note** sheet of the Excel file (one invalid negative CDS value at 2021-03-26 replaced with the nearest valid daily observation, 451.335).
