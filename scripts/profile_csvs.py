"""Profile every CSV in data/raw and write docs/schema_profile.md.

Read-only on the data. For each file: row count, duplicate rows, and per-column
dtype, null %, distinct count, min/max (numeric), and top values (low-cardinality).
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "docs" / "schema_profile.md"

LOW_CARD = 15  # show top values when a column has at most this many distinct values


def profile_column(s: pd.Series) -> dict:
    n = len(s)
    nunique = s.nunique(dropna=True)
    row = {
        "column": s.name,
        "dtype": str(s.dtype),
        "null_%": round(100 * s.isna().mean(), 2),
        "distinct": nunique,
        "min": "",
        "max": "",
        "sample / top values": "",
    }
    if pd.api.types.is_numeric_dtype(s):
        row["min"], row["max"] = s.min(), s.max()
    elif s.dtype == object or str(s.dtype).startswith("str"):
        non_null = s.dropna().astype(str)
        if len(non_null):
            row["min"], row["max"] = non_null.min(), non_null.max()
    if nunique <= LOW_CARD and nunique > 0:
        vc = s.value_counts(dropna=False).head(LOW_CARD)
        row["sample / top values"] = "; ".join(f"{k}: {v}" for k, v in vc.items())
    else:
        row["sample / top values"] = "; ".join(map(str, s.dropna().unique()[:3]))
    return row


def main() -> None:
    files = sorted(RAW.rglob("*.csv"))
    lines = ["# Schema profile (auto-generated)\n"]
    if not files:
        raise SystemExit(f"No CSV files found under {RAW}")
    for f in files:
        df = pd.read_csv(f, low_memory=False)
        lines.append(f"\n## `{f.relative_to(RAW)}`\n")
        lines.append(f"- rows: **{len(df):,}**  |  columns: **{df.shape[1]}**")
        lines.append(f"- fully duplicated rows: **{df.duplicated().sum():,}**\n")
        prof = pd.DataFrame([profile_column(df[c]) for c in df.columns])
        lines.append(prof.to_markdown(index=False))
        print(f"profiled {f.name}: {len(df):,} rows, {df.shape[1]} cols")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
