import pandas as pd
import os
import pathlib
import sys
from itertools import product




module_path = pathlib.Path(__file__).parent.resolve()   # functions/
project_root = module_path.parent                        # TFG/

aux_func_path = os.path.join(project_root, "functions", "aux_func")
if str(aux_func_path) not in sys.path:
    sys.path.append(str(aux_func_path))
    
inputs_path = os.path.join(main_path,"inputs")

from df_creator_module import df_creator
from df_creator_module import df_creator_str
from df_creator_module import unicode_utf8


if "db_creator" not in globals():
    from db_creator_reader_module import db_creator
if "db_reader" not in globals():
    from db_creator_reader_module import db_reader



raw_data_path = r"rute\data.xlsx"
raw_data_sheet = "SHEET_NAME"

db_raw_data_path = os.path.join(main_path, "sqlite3","RAW_DATA.db")

CHECK_UPDATE = True

if CHECK_UPDATE == True:
    df_raw_data = df_creator_str(raw_data_path, "latin1", raw_data_sheet)
    db_creator(db_raw_data_path, "df_raw_data", df_raw_data)
else:
    df_raw_data = db_reader(db_raw_data_path, "df_raw_data")


df = df_raw_data
df["HISTORYAMOUNT"] = df["HISTORYAMOUNT"].astype(int)
df["HISTORYBEGDATE"] = pd.to_datetime(df["HISTORYBEGDATE"], format="%Y%m%d")

df["Month"] = df["HISTORYBEGDATE"].dt.to_period("M").astype(str)
df["Quarter"] = df["HISTORYBEGDATE"].dt.to_period("Q").astype(str)
df["Year"] = df["HISTORYBEGDATE"].dt.to_period("Y").astype(str)

# --- Aggregation (only periods with positive demand) ---

df_month = df.groupby(["HOSTPARTID", "Month"])["HISTORYAMOUNT"].sum().reset_index()
df_quarter = df.groupby(["HOSTPARTID", "Quarter"])["HISTORYAMOUNT"].sum().reset_index()
df_year = df.groupby(["HOSTPARTID", "Year"])["HISTORYAMOUNT"].sum().reset_index()

df_month = df_month.rename(columns={"HISTORYAMOUNT": "Qty"})
df_quarter = df_quarter.rename(columns={"HISTORYAMOUNT": "Qty"})
df_year = df_year.rename(columns={"HISTORYAMOUNT": "Qty"})

# --- Excel export ---

df_month.to_excel(os.path.join(inputs_path, "df_month.xlsx"), index=False)
df_quarter.to_excel(os.path.join(inputs_path, "df_quarter.xlsx"), index=False)
df_year.to_excel(os.path.join(inputs_path, "df_year.xlsx"), index=False)

# --- SQLite export ---

db_aggregated_path = os.path.join(main_path, "sqlite3", "AGGREGATED_DATA.db")

db_creator(db_aggregated_path, "df_month", df_month)
db_creator(db_aggregated_path, "df_quarter", df_quarter)
db_creator(db_aggregated_path, "df_year", df_year)
