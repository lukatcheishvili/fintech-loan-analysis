"""Task 5, step 2 (Hex Python cells): which characteristics predict default and late payment, taken together?

Needs `task4_customers` (SQL cell) and `X` (capped + log-transformed features from the Task 4 preparation cell).
Two logistic-regression models, each scored on a held-out 30% test set:
  * default model : resolved loans only (paid off vs defaulted)
  * late model    : active loans only (current vs late)
Grade is left out of the models because the interest rate is derived from it (they carry the same information);
its stand-alone predictive power is still shown in the tables.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

base = task4_customers.copy()  # noqa: F821
base["is_default"] = base["is_default"].astype(int)
base["is_late"] = base["is_late"].astype(int)

feat = X.copy()  # noqa: F821  capped, log-transformed, not yet standardised
feat["term_60"] = (base["term_months"] == 60).astype(float)
feat = feat.drop(columns=["term_months"])
feat["home_RENT"] = (base["home_ownership"] == "RENT").astype(float)
feat["home_OWN"] = (base["home_ownership"] == "OWN").astype(float)
feat["joint_application"] = (base["application_type"] == "Joint").astype(float)
grade_num = base["grade"].map({g: i for i, g in enumerate("ABCDEFG", start=1)})


def fit_and_report(mask, target):
    Xm, y = feat[mask], base.loc[mask, target]
    X_tr, X_te, y_tr, y_te = train_test_split(Xm, y, test_size=0.3, random_state=42, stratify=y)
    scaler = StandardScaler().fit(X_tr)
    model = LogisticRegression(max_iter=1000).fit(scaler.transform(X_tr), y_tr)
    test_auc = roc_auc_score(y_te, model.predict_proba(scaler.transform(X_te))[:, 1])

    alone = {c: roc_auc_score(y_te, X_te[c]) for c in X_te.columns}
    alone["grade (A=1 ... G=7)"] = roc_auc_score(y_te, grade_num.loc[X_te.index])
    table = pd.DataFrame({"auc_alone": pd.Series(alone)})
    table["odds_ratio_per_1sd"] = pd.Series(np.exp(model.coef_[0]), index=X_te.columns)
    table["auc_alone_strength"] = np.maximum(table["auc_alone"], 1 - table["auc_alone"])
    table["higher_value_means"] = np.where(table["auc_alone"] >= 0.5, "riskier", "safer")
    table = table.sort_values("auc_alone_strength", ascending=False).round(3)
    summary = {"target": target, "loans_modelled": len(Xm), "event_rate_pct": round(100 * y.mean(), 2),
               "test_rows": len(y_te), "model_test_auc": round(test_auc, 3)}
    return summary, table


s1, default_table = fit_and_report(base["status_group"] != "active", "is_default")
s2, late_table = fit_and_report(base["status_group"] == "active", "is_late")
model_summary = pd.DataFrame([s1, s2])
model_summary
