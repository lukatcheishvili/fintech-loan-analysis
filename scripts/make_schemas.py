"""Generate BigQuery schema JSON files (sql/schemas/<table>.json) for the 6 raw CSVs.

Paste each file's contents into the BigQuery console: Create table -> Schema -> "Edit as text".
Columns are loaded by POSITION, so the order below must match each CSV header exactly;
this script asserts that before writing anything.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "sql" / "schemas"

# Raw layer: load faithfully, clean later in views. Dates like 'Jun-13' cannot be
# loaded as DATE by BigQuery, so they stay STRING here and are parsed in the staging view.
SCHEMAS = {
    "customer": {
        "customer_id": "STRING", "emp_title": "STRING", "emp_length": "STRING",
        "home_ownership": "STRING", "annual_inc": "FLOAT", "annual_inc_joint": "FLOAT",
        "verification_status": "STRING", "zip_code": "STRING", "addr_state": "STRING",
        "avg_cur_bal": "FLOAT", "Tot_cur_bal": "FLOAT",
    },
    "loan": {
        "loan_id": "INTEGER", "customer_id": "STRING", "loan_status": "STRING",
        "loan_amount": "INTEGER", "state": "STRING", "funded_amount": "INTEGER",
        "term": "STRING", "int_rate": "FLOAT", "installment": "FLOAT",
        "grade": "STRING", "issue_d": "STRING", "issue_date": "STRING",
        "issue_year": "INTEGER", "pymnt_plan": "BOOLEAN", "type": "STRING",
        "purpose": "STRING", "description": "STRING", "notes": "STRING",
    },
    "loan_with_region": {"loan_id": "INTEGER", "loan_amount": "INTEGER", "region": "STRING"},
    "loan_count_by_year": {"issue_year": "INTEGER", "loan_count": "INTEGER"},
    "loan_purposes": {"purpose": "STRING"},
    "state_region": {"state": "STRING", "subregion": "STRING", "region": "STRING"},
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for table, cols in SCHEMAS.items():
        header = list(pd.read_csv(RAW / f"{table}.csv", nrows=0).columns)
        assert header == list(cols), f"{table}: CSV header {header} != schema {list(cols)}"
        fields = [{"name": n, "type": t, "mode": "NULLABLE"} for n, t in cols.items()]
        (OUT / f"{table}.json").write_text(json.dumps(fields, indent=2) + "\n", encoding="utf-8")
        print(f"ok  {table}: {len(fields)} columns")


if __name__ == "__main__":
    main()
