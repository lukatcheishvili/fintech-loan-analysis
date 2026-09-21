"""Task 3 bubble chart (Hex Python cell).

Input: the Hex SQL result `task3_late_by_rate` (28 rows: 14 two-point interest-rate bands x 2 terms;
columns band_start_pct, rate_band, term_months, active_loans, late_loans, late_rate_pct).
Bubble area = number of active loans behind each point, so noisy small groups stay visible but small.
"""
import plotly.express as px

df = task3_late_by_rate.copy()  # noqa: F821  (provided by Hex from the SQL cell)
df["term"] = df["term_months"].astype(int).astype(str) + " months"
df["band_mid_pct"] = df["band_start_pct"] + 1  # centre of each 2-point band

fig = px.scatter(
    df,
    x="band_mid_pct",
    y="late_rate_pct",
    size="active_loans",
    color="term",
    color_discrete_map={"36 months": "#7b5cd6", "60 months": "#f28e2b"},
    category_orders={"term": ["36 months", "60 months"]},
    size_max=50,
    hover_name="rate_band",
    hover_data={"active_loans": ":,", "late_loans": ":,", "late_rate_pct": ":.2f",
                "band_mid_pct": False, "term": False},
    labels={"late_rate_pct": "Late rate (%)", "active_loans": "Active loans",
            "late_loans": "Late loans", "term": "Loan term"},
    title="Late-payment rate vs interest rate (active loans; bubble size = number of loans)",
)
fig.update_traces(marker=dict(sizemin=4, opacity=0.75, line=dict(width=1, color="white")))
fig.update_xaxes(title="Interest rate band midpoint (%)", tick0=5, dtick=2)
fig.update_yaxes(title="Late rate (% of active loans)", rangemode="tozero")
fig  # Hex displays the last expression in the cell
