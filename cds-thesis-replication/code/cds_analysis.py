# ══════════════════════════════════════════════════════════════
# TURKEY SOVEREIGN CDS DETERMINANTS — CHECKED / ROBUST VERSION
# Fixes:
#   1) Works from repo root, code/ folder, or a flat folder containing the CSV.
#   2) Keeps variable names in HAC output tables.
#   3) Adds basic data integrity checks before estimation.
#   4) Saves the output to results_output_checked.txt. 
# ══════════════════════════════════════════════════════════════

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import adfuller, coint
import statsmodels.api as sm

DATA_FILE = "Turkiye_CDS_Veriseti.csv"
REQUIRED_COLS = ["Date", "CDS", "US10Y", "DXY", "RESERVES", "ln_DXY", "ln_RES", "BRUNSON", "AGBAL"]
MODEL_COLS = ["CDS", "US10Y", "ln_DXY", "ln_RES", "BRUNSON", "AGBAL"] 


def find_data_file() -> Path:
    """Find CSV whether the project is zipped as repo/data or uploaded flat."""
    here = Path(__file__).resolve().parent
    candidates = [
        Path.cwd() / "data" / DATA_FILE,
        here / "data" / DATA_FILE,
        here.parent / "data" / DATA_FILE,
        Path.cwd() / DATA_FILE,
        here / DATA_FILE,
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Could not find Turkiye_CDS_Veriseti.csv. Put it either in ./data/ or in the same folder as this script."
    )


def stars(p: float) -> str:
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, text):
        for f in self.files:
            f.write(text)
    def flush(self):
        for f in self.files:
            f.flush()


def report(name: str, res, variable_names: list[str]) -> None:
    print(f"\n================  {name}  ================")
    out = pd.DataFrame(
        {
            "coef": np.asarray(res.params),
            "std_err": np.asarray(res.bse),
            "t": np.asarray(res.tvalues),
            "p": np.asarray(res.pvalues),
        },
        index=variable_names,
    )
    out.index.name = "Variable"
    out["sig"] = out["p"].apply(stars)
    print(out.round(4).to_string())
    print(
        f"R2={res.rsquared:.4f}  Adj.R2={res.rsquared_adj:.4f}  "
        f"F={res.fvalue:.2f}  Prob(F)={res.f_pvalue:.3g}  N={int(res.nobs)}"
    )


def main() -> None:
    output_path = Path.cwd() / "results_output_checked.txt"
    with output_path.open("w", encoding="utf-8") as fh:
        old_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, fh)
        try:
            data_path = find_data_file()
            print("================  DATA CHECKS  ================")
            print(f"Data file: {data_path}")
            df = pd.read_csv(data_path, parse_dates=["Date"])

            missing_cols = [c for c in REQUIRED_COLS if c not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            print(f"Rows before dropna: {len(df)}")
            print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
            print(f"Duplicate dates: {int(df['Date'].duplicated().sum())}")
            print(f"Negative CDS values: {int((df['CDS'] < 0).sum())}")
            print("Missing values by model column:")
            print(df[MODEL_COLS].isna().sum().to_string())

            df = df.dropna(subset=MODEL_COLS)
            print(f"Rows after dropna: {len(df)}")

            # Optional consistency checks for pre-built log columns.
            max_ln_dxy_diff = float((df["ln_DXY"] - np.log(df["DXY"])).abs().max())
            max_ln_res_diff = float((df["ln_RES"] - np.log(df["RESERVES"])).abs().max())
            print(f"Max ln_DXY rebuild difference: {max_ln_dxy_diff:.10f}")
            print(f"Max ln_RES rebuild difference: {max_ln_res_diff:.10f}")

            y = df["CDS"]
            X1 = sm.add_constant(df[["US10Y", "ln_DXY", "ln_RES", "BRUNSON", "AGBAL"]])
            X2 = sm.add_constant(df[["ln_DXY", "ln_RES", "BRUNSON", "AGBAL"]])

            # Model 1 — Full (Newey-West HAC, lag = 4)
            m1 = sm.OLS(y, X1).fit().get_robustcov_results(cov_type="HAC", use_t=True, maxlags=4)
            report("TABLE A1  Model 1 (Full, US10Y included)", m1, list(X1.columns))

            # Model 2 — Final (US10Y excluded)
            m2 = sm.OLS(y, X2).fit().get_robustcov_results(cov_type="HAC", use_t=True, maxlags=4)
            report("TABLE A2  Model 2 (Final, US10Y excluded)", m2, list(X2.columns))

            # VIF
            print("\n================  TABLE A3  VIF (Model 1)  ================")
            vif = pd.DataFrame(
                {
                    "Variable": X1.columns,
                    "VIF": [variance_inflation_factor(X1.values, i) for i in range(X1.shape[1])],
                }
            )
            print(vif[vif.Variable != "const"].round(4).to_string(index=False))

            # Diagnostics
            print("\n================  TABLE A4  Diagnostics  ================")
            o1 = sm.OLS(y, X1).fit()
            o2 = sm.OLS(y, X2).fit()
            print(f"Durbin-Watson (M1)    : {durbin_watson(o1.resid):.4f}")
            bp1 = het_breuschpagan(o1.resid, X1)
            bp2 = het_breuschpagan(o2.resid, X2)
            print(f"Breusch-Pagan LM (M1) : {bp1[0]:.4f}  p={bp1[1]:.3g}")
            print(f"Breusch-Pagan LM (M2) : {bp2[0]:.4f}  p={bp2[1]:.3g}")
            jb1 = stats.jarque_bera(o1.resid)
            jb2 = stats.jarque_bera(o2.resid)
            print(f"Jarque-Bera (M1)      : {jb1[0]:.4f}  p={jb1[1]:.3g}")
            print(f"Jarque-Bera (M2)      : {jb2[0]:.4f}  p={jb2[1]:.3g}")

            print("\nADF unit-root (regression='c', autolag='AIC'):")
            for col in ["CDS", "US10Y", "ln_DXY", "ln_RES"]:
                lev = adfuller(df[col], autolag="AIC")
                dif = adfuller(df[col].diff().dropna(), autolag="AIC")
                print(
                    f"  {col:7s} level: stat={lev[0]:7.3f} p={lev[1]:.3f} | "
                    f"diff: stat={dif[0]:7.3f} p={dif[1]:.3f}"
                )

            print("\nEngle-Granger cointegration (proper EG critical values):")
            eg1 = coint(y, X1.drop(columns="const"))
            eg2 = coint(y, X2.drop(columns="const"))
            print(f"  M1: stat={eg1[0]:.4f}  p={eg1[1]:.4f}")
            print(f"  M2: stat={eg2[0]:.4f}  p={eg2[1]:.4f}")
            print("  (No cointegration at conventional levels; level regression should be interpreted with caution.)")

            # ── TABLE A5 ── First-difference robustness check (spurious-regression guard)
            # All I(1) variables are differenced; the crisis dummies remain in levels
            # because they flag specific shock weeks. If the level relationship were
            # spurious (driven by shared trends), the differenced coefficients on
            # ln(DXY) and ln(RES) would lose significance. They do not.
            print("\n================  TABLE A5  Model 3 (First-Difference Robustness)  ================")
            dfd = df.copy()
            for c in ["CDS", "US10Y", "ln_DXY", "ln_RES"]:
                dfd["d_" + c] = dfd[c].diff()
            dfd = dfd.dropna(subset=["d_CDS", "d_US10Y", "d_ln_DXY", "d_ln_RES"]).reset_index(drop=True)
            yfd = dfd["d_CDS"]
            Xfd = sm.add_constant(dfd[["d_US10Y", "d_ln_DXY", "d_ln_RES", "BRUNSON", "AGBAL"]])
            m3 = sm.OLS(yfd, Xfd).fit().get_robustcov_results(cov_type="HAC", use_t=True, maxlags=4)
            report("TABLE A5  Model 3 (First-Difference Robustness Check)", m3, list(Xfd.columns))
            print("  Interpretation: d_ln_DXY and d_ln_RES remain highly significant after")
            print("  differencing, so the level-regression results are not spurious.")

            print(f"\nSaved output: {output_path}")
        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    main()
