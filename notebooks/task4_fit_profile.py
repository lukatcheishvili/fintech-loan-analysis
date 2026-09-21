"""Task 4, step 4 (Hex Python cell): fit the final k=5 model and profile the segments.

Needs `task4_customers` (SQL cell) and `X_scaled` (feature-preparation cell).
Segments are numbered 1-5 by average loan amount (small -> large) so the numbering is stable and readable.
Outcomes (default / late) are NOT clustering inputs; they are used here only to describe each segment.
"""
import pandas as pd
from sklearn.cluster import KMeans

km = KMeans(n_clusters=5, n_init=10, random_state=42)
raw_labels = km.fit_predict(X_scaled)  # noqa: F821

seg = task4_customers.copy()  # noqa: F821
seg["is_default"] = seg["is_default"].astype(float)
seg["is_late"] = seg["is_late"].astype(float)
seg["raw_cluster"] = raw_labels

order = seg.groupby("raw_cluster")["loan_amount"].mean().sort_values().index
relabel = {old: new for new, old in enumerate(order, start=1)}
seg["segment"] = seg["raw_cluster"].map(relabel)

resolved = seg["status_group"] != "active"   # paid off or defaulted
active = seg["status_group"] == "active"     # can still be late

profile = seg.groupby("segment").agg(
    customers=("loan_id", "size"),
    avg_loan_amount=("loan_amount", "mean"),
    avg_int_rate_pct=("int_rate_pct", "mean"),
    pct_60_month=("term_months", lambda s: 100 * (s == 60).mean()),
    median_annual_inc=("annual_inc", "median"),
    median_loan_to_income=("loan_to_income", "median"),
    median_balance_to_income=("balance_to_income", "median"),
)
profile.insert(1, "share_pct", 100 * profile["customers"] / len(seg))
profile["default_rate_resolved_pct"] = 100 * seg[resolved].groupby("segment")["is_default"].mean()
profile["late_rate_active_pct"] = 100 * seg[active].groupby("segment")["is_late"].mean()
profile = profile.round(2)
profile
