import pathlib
import os
import sys


main_path = pathlib.Path(__file__).parent.resolve()   # TFG/

functions_path = os.path.join(main_path, "functions")
aux_func_path = os.path.join(functions_path, "aux_func")

for p in (functions_path, aux_func_path):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from db_creator_reader_module import db_reader
from reporting import find_examples, export_piece_table, plot_metrics_bars, plot_piece_series, export_mapping
from evaluation import evaluate_piece, METHODS

# --- Loading Aggregated Data ---

db_aggregated_path = os.path.join(main_path, "sqlite3", "AGGREGATED_DATA.db")

df_month = db_reader(db_aggregated_path, "df_month")
df_quarter = db_reader(db_aggregated_path, "df_quarter")
df_year = db_reader(db_aggregated_path, "df_year")

outputs_path = os.path.join(main_path, "outputs")

# --- Selection of Sample Parts ---

examples = find_examples(df_year)
export_mapping(examples, outputs_path)
print(examples)

# --- Evaluation and reporting for each piece ---

granularities = [
    (df_month, "Month"),
    (df_quarter, "Quarter"),
    (df_year, "Year"),
]

ANONYMIZE = True   # <-- Set to False to use the actual name of the part in the outputs

for _, row in examples.iterrows():
    part_id = row["HOSTPARTID"]
    display_name = row["Label"] if ANONYMIZE else part_id
    category_path = os.path.join(outputs_path, row["Classification"])
    os.makedirs(category_path, exist_ok=True)

    print(f"Processing {part_id}...")

    table = evaluate_piece(part_id, df_month, df_quarter, df_year)

    export_piece_table(table, part_id, category_path, display_name)
    plot_metrics_bars(table, part_id, category_path, display_name)

    for df, period_col in granularities:
        plot_piece_series(part_id, df, period_col, METHODS, category_path, display_name)

print("Process completed.")