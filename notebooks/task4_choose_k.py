"""Task 4, step 3 (Hex Python cells): compare k = 2..8 for k-means on X_scaled.

Cell A computes `k_report` (ends with the table). Cell B draws the elbow/silhouette chart.
Needs X_scaled from the feature-preparation cell.
"""
# ---- Cell A ---------------------------------------------------------------------------------
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

rows = []
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=5, random_state=42)
    labels = km.fit_predict(X_scaled)  # noqa: F821  (from the preparation cell)
    sil = silhouette_score(X_scaled, labels, sample_size=10000, random_state=42)  # noqa: F821
    rows.append({"k": k, "inertia": round(km.inertia_), "silhouette": round(sil, 3)})
k_report = pd.DataFrame(rows)
k_report

# ---- Cell B ---------------------------------------------------------------------------------
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(rows=1, cols=2, subplot_titles=("Inertia (lower = tighter clusters)",
                                                    "Silhouette (higher = better separated)"))
fig.add_trace(go.Scatter(x=k_report["k"], y=k_report["inertia"], mode="lines+markers"), row=1, col=1)
fig.add_trace(go.Scatter(x=k_report["k"], y=k_report["silhouette"], mode="lines+markers"), row=1, col=2)
fig.update_xaxes(title="Number of clusters (k)", dtick=1)
fig.update_layout(showlegend=False, height=380, title="Choosing the number of clusters")
fig
