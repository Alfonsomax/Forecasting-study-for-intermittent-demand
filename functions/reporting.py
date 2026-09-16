import pathlib
import os
import sys
import pandas as pd
import numpy as np

from walkforward import densify
from classification import adi, cv2, classify_sbc
import matplotlib.pyplot as plt

from walkforward import densify, run_walkforward



def find_examples(df: pd.DataFrame, min_periods: int = 3) -> pd.DataFrame:
    """
    df: Aggregated DataFrame (columns HOSTPARTID, Year, Qty).
    Returns a DataFrame with 8 records (2 per SBC category: high N_d and low N_d),
    along with their classification and ADI/CV2/N_d metrics.
    """
    all_years = sorted(df["Year"].unique())

    records = []
    for part, group in df.groupby("HOSTPARTID"):
        y = densify(group["Year"].tolist(), group["Qty"].tolist(), all_years)
        n_d = int((y != 0).sum())

        if n_d < min_periods:
            continue

        records.append({
            "HOSTPARTID": part,
            "N_d": n_d,
            "ADI": adi(y),
            "CV2": cv2(y),
            "Classification": classify_sbc(y),
        })

    df_classif = pd.DataFrame(records)

    examples = []
    for classif, group in df_classif.groupby("Classification"):
        if classif == "Not enough data":
            continue
        group_sorted = group.sort_values("N_d")

        low = group_sorted.iloc[0].copy()
        high = group_sorted.iloc[-1].copy()
        low["Label"] = f"{classif} - Low N_d"
        high["Label"] = f"{classif} - High N_d"

        examples.append(low)
        examples.append(high)

    return pd.DataFrame(examples).reset_index(drop=True)


def export_piece_table(table, part_id, outputs_path, display_name=None):
    """Save the results table for a piece as an Excel file in the outputs/ folder."""
    name = display_name or part_id
    filename = os.path.join(outputs_path, f"{name.replace('/', '__')}_report.xlsx")
    table.to_excel(filename, index=False)


def plot_metrics_bars(table, part_id, outputs_path, display_name=None):
    """Generate a bar chart (MASE and RMSSE by method) for each granularity."""
    name = display_name or part_id
    for gran, group in table.groupby("Granularity"):
        fig, ax = plt.subplots(figsize=(10, 5))
        x = group["Method"]
        ax.bar(x, group["MASE"], width=0.4, label="MASE", align="edge")
        ax.bar(x, group["RMSSE"], width=-0.4, label="RMSSE", align="edge")
        ax.set_title(f"{name} - {gran} - MASE / RMSSE per method")
        ax.set_ylabel("Escalated error")
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        filename = os.path.join(outputs_path, f"{name.replace('/', '__')}_{gran}_metrics.png")
        plt.savefig(filename)
        plt.close(fig)


GAP_LABEL = "..."
MIN_LEADING_ZEROS = 3

def _collapse_leading_zeros(all_periods, y, preds_by_method):
    """If the series begins with several periods with no demand, it collapses them into a
    single gap ‘...’ between the first period and the one preceding the first hit."""
    nz = np.nonzero(y)[0]
    first_hit = int(nz[0]) if len(nz) else 0

    if first_hit < MIN_LEADING_ZEROS:
        labels = list(all_periods)
        y_plot = list(y)
        preds_plot = {m: [np.nan] + list(p) for m, p in preds_by_method.items()}
        return labels, y_plot, preds_plot

    keep = list(range(first_hit - 1, len(y)))
    labels = [all_periods[0], GAP_LABEL] + [all_periods[i] for i in keep]
    y_plot = [y[0], np.nan] + [y[i] for i in keep]

    preds_plot = {}
    for m, p in preds_by_method.items():
        full = [np.nan] + list(p)   # The first period is never predictable.
        preds_plot[m] = [full[0], np.nan] + [full[i] for i in keep]

    return labels, y_plot, preds_plot


def plot_piece_series(part_id: str, df: pd.DataFrame, period_col: str, methods: dict,
                       outputs_path: str, display_name: str = None) -> None:
    name = display_name or part_id

    all_periods = sorted(df[period_col].unique())
    group = df[df["HOSTPARTID"] == part_id]
    y = densify(group[period_col].tolist(), group["Qty"].tolist(), all_periods)

    results = run_walkforward(y, methods)
    preds_by_method = {m: res["y_pred"] for m, res in results.items()}

    labels, y_plot, preds_plot = _collapse_leading_zeros(all_periods, y, preds_by_method)
    x = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x, y_plot, label="Real Hits", color="lightgray")

    for method_name, p in preds_plot.items():
        ax.plot(x, p, marker="o", label=method_name)

    ax.set_title(f"{name} - {period_col} - Forecast vs Real")
    ax.set_ylabel("Qty")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45)
    plt.legend()
    plt.tight_layout()

    filename = os.path.join(outputs_path, f"{name.replace('/', '__')}_{period_col}_series.png")
    plt.savefig(filename)
    plt.close(fig)


def export_mapping(examples: pd.DataFrame, outputs_path: str) -> None:
    """It maintains the correspondence between the actual part and the anonymized label."""
    cols = ["Label", "HOSTPARTID", "Classification", "N_d", "ADI", "CV2"]
    filename = os.path.join(outputs_path, "piece_mapping.xlsx")
    examples[cols].to_excel(filename, index=False)



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

outputs_path = os.path.join(project_root, "outputs")

from evaluation import evaluate_piece, METHODS

tabla = evaluate_piece("A-01", df_month, df_quarter, df_year)

export_piece_table(tabla, "A-01", outputs_path)
plot_metrics_bars(tabla, "A-01", outputs_path)
plot_piece_series("A-01", df_year, "Year", METHODS, outputs_path) """