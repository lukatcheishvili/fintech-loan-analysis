"""Task 5, step 1 (Hex Python cells): default and late rates by characteristic.

Needs `task4_customers` (the SQL cell from Task 4). Nothing is dropped or modelled here; each characteristic is
cut into buckets and we compare default rate (resolved loans) and late rate (active loans) across buckets.
Numeric characteristics are cut into five equal-sized groups (Q1 = lowest ... Q5 = highest).
issue_year is deliberately excluded: outcomes by year are distorted by the snapshot issue (see Tasks 1-2).
"""
import pandas as pd

# Sorted by loan_id so tied values (many loans share the same rate, income, ...) always fall into the same
# quintile, whatever order BigQuery returns the rows in. Without this, boundary buckets shift slightly per run.
d = task4_customers.sort_values("loan_id").reset_index(drop=True)  # noqa: F821
d["is_default"] = d["is_default"].astype(float)
d["is_late"] = d["is_late"].astype(float)

# ---- buckets (computed on ALL loans so a bucket means the same thing for default and late) ----
QLAB = ["Q1 (lowest)", "Q2", "Q3", "Q4", "Q5 (highest)"]


def quintile(s):
    return pd.qcut(s.rank(method="first"), 5, labels=QLAB)


d["term"] = d["term_months"].astype(int).astype(str) + " months"
d["home"] = d["home_ownership"].where(d["home_ownership"].isin(["MORTGAGE", "RENT", "OWN"]), "OTHER")
d["interest rate"] = quintile(d["int_rate_pct"])
d["loan-to-income"] = quintile(d["loan_to_income"])
d["annual income"] = quintile(d["annual_inc"])
d["balance-to-income"] = quintile(d["balance_to_income"])
d["loan amount"] = quintile(d["loan_amount"])

CHARACTERISTICS = {  # label -> column
    "grade": "grade", "term": "term", "interest rate": "interest rate", "loan-to-income": "loan-to-income",
    "annual income": "annual income", "balance-to-income": "balance-to-income", "loan amount": "loan amount",
    "home ownership": "home", "application type": "application_type",
}

resolved = d[d["status_group"] != "active"]   # paid off or defaulted
active = d[d["status_group"] == "active"]     # can still be late
overall_default = 100 * resolved["is_default"].mean()
overall_late = 100 * active["is_late"].mean()

parts = []
for label, col in CHARACTERISTICS.items():
    r = resolved.groupby(col, observed=True)["is_default"].agg(resolved_loans="size", default_rate_pct=lambda s: 100 * s.mean())
    a = active.groupby(col, observed=True)["is_late"].agg(active_loans="size", late_rate_pct=lambda s: 100 * s.mean())
    t = r.join(a, how="outer").reset_index().rename(columns={col: "bucket"})
    t.insert(0, "characteristic", label)
    parts.append(t)
drivers = pd.concat(parts, ignore_index=True)
drivers["bucket"] = drivers["bucket"].astype(str)
drivers["default_lift"] = drivers["default_rate_pct"] / overall_default
drivers = drivers.round(2)

# ---- ranking: how far apart are the best and worst bucket of each characteristic? ----
# Buckets with fewer than MIN_N loans are ignored here (a 62-loan bucket can show any rate by chance).
MIN_N = 500
drivers["small_bucket"] = (drivers["resolved_loans"] < MIN_N) | (drivers["active_loans"] < MIN_N)

big_r = drivers[drivers["resolved_loans"] >= MIN_N].groupby("characteristic")["default_rate_pct"]
big_a = drivers[drivers["active_loans"] >= MIN_N].groupby("characteristic")["late_rate_pct"]
ranking = pd.DataFrame({
    "default_lowest": big_r.min(), "default_highest": big_r.max(),
    "late_lowest": big_a.min(), "late_highest": big_a.max(),
})
ranking["default_spread_pts"] = ranking["default_highest"] - ranking["default_lowest"]
ranking["late_spread_pts"] = ranking["late_highest"] - ranking["late_lowest"]
ranking = ranking.sort_values("default_spread_pts", ascending=False).round(1)

print(f"overall default rate (resolved): {overall_default:.2f}% | overall late rate (active): {overall_late:.2f}%")
ranking
