# Data Dictionary

**File:** `Turkiye_CDS_Veriseti.csv` — analysis-ready weekly dataset (N = 835), Jan 2010 – Dec 2025 (Friday-dated weeks).

| Column | Description | Unit | Source | Transformation |
|---|---|---|---|---|
| `Date` | Week-ending Friday | date | — | — |
| `CDS` | Turkey 5-year sovereign CDS spread (dependent variable) | basis points | Investing.com | level |
| `US10Y` | U.S. 10-year Treasury yield | percent | FRED (St. Louis Fed) | level |
| `DXY` | U.S. Dollar Index | index | Investing.com | used as ln(DXY) |
| `RESERVES` | CBRT gross foreign exchange reserves | million USD | CBRT | used as ln(RES) |
| `ln_DXY` | Natural log of DXY | — | derived | ln(DXY) |
| `ln_RES` | Natural log of RESERVES | — | derived | ln(RESERVES) |
| `BRUNSON` | Brunson crisis dummy (03–31 Aug 2018) | 0/1 | constructed | binary |
| `AGBAL` | Ağbal dismissal dummy (26 Mar–09 Apr 2021) | 0/1 | constructed | binary |

## Source file
`TR_Model_Veriseti_Haftalik_corrected.xlsx` contains the raw weekly series (sheet **Weekly Data**) plus a **Correction Note** sheet documenting one fix:

- **2021-03-26**: the source row contained an invalid negative CDS value (−2.17); it was replaced with **451.335**, the nearest valid prior daily observation (25.03.2021 High–Low average from the daily CDS file).

No other corrections were made. The dataset has no missing values, no duplicate dates, and no gaps (all weekly spacings = 7 days). 
