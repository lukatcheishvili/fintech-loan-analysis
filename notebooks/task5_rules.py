"""Task 5, step 3 (Hex Python cell): how would candidate lending rules have performed?

Needs `task4_customers` (SQL cell from Task 4). Every rule uses information known at application time
(grade, interest rate, term, loan-to-income), so nothing here peeks at the outcome.
For each rule, on the historical data:
  * default_rate_flagged / default_rate_not_flagged : default rate (resolved loans) inside vs outside the rule
  * defaults_caught_pct     : share of ALL defaults that the rule flags
  * good_loans_flagged_pct  : share of loans that were paid off but would have been flagged (the cost of the rule)
  * late_rate_*             : late rate on active loans inside vs outside the rule
"""
import pandas as pd

d = task4_customers.copy()  # noqa: F821
d["is_default"] = d["is_default"].astype(bool)
d["is_late"] = d["is_late"].astype(bool)

rules = {
    "Grade D-G": d["grade"].isin(list("DEFG")),
    "Grade E-G": d["grade"].isin(list("EFG")),
    "Rate >= 20%": d["int_rate_pct"] >= 20,
    "Rate >= 25%": d["int_rate_pct"] >= 25,
    "60-month AND rate >= 16%": (d["term_months"] == 60) & (d["int_rate_pct"] >= 16),
    "Loan-to-income >= 0.35": d["loan_to_income"] >= 0.35,
    "60-month AND loan-to-income >= 0.30": (d["term_months"] == 60) & (d["loan_to_income"] >= 0.30),
    "Grade D-G OR (60-month AND LTI >= 0.30)": d["grade"].isin(list("DEFG")) | ((d["term_months"] == 60) & (d["loan_to_income"] >= 0.30)),
}

resolved = d["status_group"] != "active"   # paid off or defaulted
active = ~resolved                          # can still be late
total_defaults = d.loc[resolved, "is_default"].sum()
total_good = (~d.loc[resolved, "is_default"]).sum()

rows = []
for name, flag in rules.items():
    fr, nr = d[resolved & flag], d[resolved & ~flag]
    fa, na = d[active & flag], d[active & ~flag]
    rows.append({
        "rule": name,
        "flagged_pct_of_resolved": 100 * len(fr) / resolved.sum(),
        "default_rate_flagged": 100 * fr["is_default"].mean(),
        "default_rate_not_flagged": 100 * nr["is_default"].mean(),
        "defaults_caught_pct": 100 * fr["is_default"].sum() / total_defaults,
        "good_loans_flagged_pct": 100 * (~fr["is_default"]).sum() / total_good,
        "late_rate_flagged": 100 * fa["is_late"].mean(),
        "late_rate_not_flagged": 100 * na["is_late"].mean(),
    })
rules_table = pd.DataFrame(rows).round({
    "flagged_pct_of_resolved": 1, "default_rate_flagged": 1, "default_rate_not_flagged": 1,
    "defaults_caught_pct": 1, "good_loans_flagged_pct": 1, "late_rate_flagged": 2, "late_rate_not_flagged": 2,
})
print(f"overall default rate (resolved): {100 * d.loc[resolved, 'is_default'].mean():.1f}% | "
      f"overall late rate (active): {100 * d.loc[active, 'is_late'].mean():.2f}%")
rules_table
