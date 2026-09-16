import pandas as pd
import numpy as np
import pathlib
import sys
import os

from walkforward import densify, run_walkforward
from metrics import mase, rmsse, cfe

from naivezero_method import naive, zero
from wma_method import wma
from smoothing_method import ses, holt
from croston_methods import croston, sba, tsb

METHODS = {
    "Naive": naive,
    "Zero": zero,
    "WMA": wma,
    "SES": ses,
    "Holt": holt,
    "Croston": croston,
    "SBA": sba,
    "TSB": tsb,
}


def _build_series(df: pd.DataFrame, part_id: str, period_col: str) -> np.ndarray:
    all_periods = sorted(df[period_col].unique())
    group = df[df["HOSTPARTID"] == part_id]
    return densify(group[period_col].tolist(), group["Qty"].tolist(), all_periods)


def evaluate_piece(part_id: str, df_month: pd.DataFrame, df_quarter: pd.DataFrame,
                    df_year: pd.DataFrame, methods: dict = METHODS) -> pd.DataFrame:
    """
    Perform a walk-forward search for a single part across all three granularities and all methods.
    Returns a table with one row for each method x granularity combination:
    Method | Granularity | Prediction | MASE | RMSSE | CFE
    """
    granularities = {
        "Month": (df_month, "Month"),
        "Quarter": (df_quarter, "Quarter"),
        "Year": (df_year, "Year"),
    }

    rows = []

    for gran_name, (df, period_col) in granularities.items():
        y = _build_series(df, part_id, period_col)
        results = run_walkforward(y, methods)

        for method_name, res in results.items():
            y_real = np.array(res["y_real"])
            y_pred = np.array(res["y_pred"])
            scales = np.array(res["scales"])
            scales2 = np.array(res["scales2"])

            valid_pred = ~np.isnan(y_pred)
            valid_scale = valid_pred & ~np.isnan(scales) & (scales != 0)
            valid_scale2 = valid_pred & ~np.isnan(scales2) & (scales2 != 0)

            mase_val = mase(y_real[valid_scale], y_pred[valid_scale], scales[valid_scale]) if valid_scale.any() else np.nan
            rmsse_val = rmsse(y_real[valid_scale2], y_pred[valid_scale2], scales2[valid_scale2]) if valid_scale2.any() else np.nan
            cfe_val = cfe(y_real[valid_pred], y_pred[valid_pred]) if valid_pred.any() else np.nan

            last_pred = y_pred[-1] if len(y_pred) > 0 else np.nan

            rows.append({
                "Method": method_name,
                "Granularity": gran_name,
                "Prediction": last_pred,
                "MASE": mase_val,
                "RMSSE": rmsse_val,
                "CFE": cfe_val,
            })

    return pd.DataFrame(rows)



## prueba funcional
""" module_path = pathlib.Path(__file__).parent.resolve()   # functions/
project_root = module_path.parent                        # TFG/

aux_func_path = os.path.join(project_root, "functions", "aux_func")
if str(aux_func_path) not in sys.path:
    sys.path.append(str(aux_func_path))

from db_creator_reader_module import db_reader

db_aggregated_path = os.path.join(project_root, "sqlite3", "AGGREGATED_DATA.db")
df_year = db_reader(db_aggregated_path, "df_year")
df_month = db_reader(db_aggregated_path, "df_month")
df_quarter = db_reader(db_aggregated_path, "df_quarter")

tabla = evaluate_piece("A-01", df_month, df_quarter, df_year)
print(tabla) """