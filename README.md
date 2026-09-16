# Forecasting Study for Intermittent Demand — Bachelor Thesis

Comparative study of demand forecasting methods for aeronautical spare parts, with a focus on **intermittent demand**. This repository contains the Python pipeline developed for a Bachelor's Thesis (TFG) on spare-parts forecasting and provisioning, combining classical statistical methods with methods specifically designed for intermittent demand (Croston and its variants), evaluated through walk-forward validation.

> **Note on data:** this repository contains **code only**. The raw data, aggregated datasets, SQLite databases, and generated outputs (tables, charts) used in the thesis are excluded for confidentiality reasons (see `.gitignore`). To use this pipeline you will need your own demand history data in the format described below.

## What this does

Given a historical record of spare-part demand (one row per demand event), the pipeline:

1. Aggregates demand per part at three time granularities: **monthly**, **quarterly**, and **yearly**.
2. Classifies each part's demand pattern using the **ADI / CV²** framework (Syntetos–Boylan), into Smooth, Erratic, Intermittent, or Lumpy demand.
3. Runs **walk-forward validation** (expanding window) for each part, comparing 8 forecasting methods:
   - Baselines: **Naive**, **Zero**
   - Classical: **Weighted Moving Average (WMA)**, **Simple Exponential Smoothing (SES)**, **Holt's linear trend**
   - Intermittent-demand specific: **Croston**, **Syntetos–Boylan Approximation (SBA)**, **Teunter–Syntetos–Babai (TSB)**
4. Evaluates each method with three complementary metrics: **MASE**, **RMSSE** (accuracy, scale-independent) and **CFE** (cumulative bias).
5. Selects a small set of representative example parts (one with high and one with low observation count per demand category) and generates per-part Excel tables and PNG charts (metric comparison bar charts, and real-vs-forecast time series), with an option to anonymize part identifiers.

## Repository structure

```
.
├── main.py                    # Orchestrator: runs the full pipeline for the example parts
├── functions/
│   ├── aux_func/
│   │   ├── df_creator_module.py         # Excel/CSV reading helpers
│   │   └── db_creator_reader_module.py  # SQLite save/read helpers
│   ├── dataupload.py          # ETL: raw Excel -> aggregated Month/Quarter/Year datasets
│   ├── classification.py      # ADI, CV2, SBC demand classification
│   ├── methods_baseline.py    # naive, zero
│   ├── methods_wma.py         # Weighted Moving Average
│   ├── methods_smoothing.py   # SES, Holt (via statsmodels)
│   ├── methods_croston.py     # Croston, SBA, TSB (hand-implemented)
│   ├── metrics.py             # MASE, RMSSE, CFE
│   ├── walkforward.py         # Generic walk-forward engine for a single series
│   ├── evaluation.py          # Runs walk-forward for one part across all methods/granularities
│   └── reporting.py           # Example-part selection, Excel/chart export
├── inputs/    (git-ignored)   # Aggregated Excel datasets
├── outputs/   (git-ignored)   # Generated tables and charts
└── sqlite3/   (git-ignored)   # RAW_DATA.db, AGGREGATED_DATA.db
```

## Requirements

```bash
pip install pandas numpy openpyxl statsmodels matplotlib
```

Tested with Python 3.14, pandas 3.0.5, numpy 2.5.3.

## Input data format

The pipeline expects an Excel file with (at least) these columns:

| Column           | Description                                      |
|-------------------|---------------------------------------------------|
| `HOSTPARTID`       | Part identifier                                   |
| `HISTORYBEGDATE`   | Demand date, as an integer in `YYYYMMDD` format    |
| `HISTORYAMOUNT`    | Quantity demanded (always positive)                |

Only positive demand events are expected — periods with no demand are **not** present in the raw data and are reconstructed by the pipeline where needed.

## Usage

1. Place your raw data Excel file and update the path/sheet name in `functions/dataupload.py`.
2. Run the ETL to build the aggregated datasets and SQLite databases:
   ```bash
   python functions/dataupload.py
   ```
3. Run the full study on the example parts:
   ```bash
   python main.py
   ```
   Results (per-part Excel tables and PNG charts) are written to `outputs/`.

   Set `ANONYMIZE = False` in `main.py` to use real part identifiers in the outputs instead of category-based labels (e.g. `"Lumpy - low N_d"`).

## Methodology notes / known limitations

- **WMA on yearly data**: WMA uses a fixed 4-period window. With only 3–4 years of history, the earliest walk-forward folds in the yearly granularity do not have enough history to compute a forecast; these folds are recorded as `NaN` rather than raising an error. This is treated as a study finding (WMA is not viable at yearly granularity with this dataset) rather than patched around.
- **MASE / RMSSE with all-zero training history**: when a fold's training window contains no demand at all, the naive-based scaling factor is zero, making the scaled error undefined. Such folds are excluded from the aggregated MASE/RMSSE calculation.
- **Croston / TSB initialization**: Croston's initial inter-demand interval is set to the position of the first observed non-zero demand (a real, observed waiting time). TSB's probability recursion starts at the first non-zero observation with `p = 1`, treating the preceding period as a non-informative burn-in — this choice can noticeably affect results on short series and is documented as an explicit methodological decision.
- **WMA weights** are fixed at `[0.6, 0.2, 0.1, 0.1]` (most recent period first), matching the configuration currently used manually by the company's planners, rather than being optimized per part.

## Author

Alfonso Vázquez Tagua — Bachelor's Thesis, Physics.
