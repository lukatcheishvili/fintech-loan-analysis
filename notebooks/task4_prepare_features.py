"""Task 4, step 2 (Hex Python cell): inspect and prepare the clustering features.

Input : Hex SQL result `task4_customers` (270,299 rows, one per customer/loan).
Output: X_scaled (6 standardised features), used by the clustering cell in the next step.
Rows are never dropped: extreme values are capped, not deleted.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

df = task4_customers.copy()  # noqa: F821  (provided by Hex from the SQL cell)
FEATURES = ["loan_amount", "int_rate_pct", "term_months", "annual_inc", "loan_to_income", "balance_to_income"]
SKEWED = ["annual_inc", "loan_to_income", "balance_to_income"]

print("rows:", len(df), "| columns:", df.shape[1])
print("NULLs in clustering features:", int(df[FEATURES].isna().sum().sum()))

raw = df[FEATURES].astype(float)

# 1. cap extreme values at the 1st / 99th percentile (rows are kept)
lo, hi = raw.quantile(0.01), raw.quantile(0.99)
capped = raw.clip(lower=lo, upper=hi, axis=1)
n_capped = ((raw < lo) | (raw > hi)).sum()

# 2. log-transform the heavily skewed features
X = capped.copy()
for c in SKEWED:
    X[c] = np.log1p(X[c])

# 3. standardise: mean 0, standard deviation 1
X_scaled = pd.DataFrame(StandardScaler().fit_transform(X), columns=FEATURES, index=df.index)

report = pd.DataFrame({
    "cap_low_1%": lo, "cap_high_99%": hi, "values_capped": n_capped,
    "skew_raw": raw.skew(), "skew_prepared": X.skew(),
    "scaled_mean": X_scaled.mean(), "scaled_std": X_scaled.std(),
}).round(3)
print()
print(report.to_string())
