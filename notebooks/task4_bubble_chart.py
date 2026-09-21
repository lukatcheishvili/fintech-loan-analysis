"""Task 4, step 5 (Hex Python cell): bubble chart of the five customer segments.

Needs `profile` from the fit-and-profile cell. Segments are numbered 1-5 by average loan amount, so the
names below stay attached to the same kind of segment. Bubble area = number of customers; the number
inside each bubble is the segment id.
"""
import plotly.express as px

names = {
    1: "Small loans, low leverage",
    2: "Small loans, high existing balances",
    3: "Low income, stretched",
    4: "60-month, higher-rate loans",
    5: "Large loans, high income",
}
plot_df = profile.reset_index()  # noqa: F821  (from the fit-and-profile cell)
plot_df["label"] = plot_df["segment"].astype(str) + " · " + plot_df["segment"].map(names)

fig = px.scatter(
    plot_df,
    x="avg_loan_amount",
    y="default_rate_resolved_pct",
    size="customers",
    color="label",
    text="segment",
    size_max=60,
    hover_name="label",
    hover_data={
        "customers": ":,", "share_pct": ":.1f", "avg_int_rate_pct": ":.2f", "pct_60_month": ":.1f",
        "median_annual_inc": ":,.0f", "late_rate_active_pct": ":.2f", "default_rate_resolved_pct": ":.1f",
        "avg_loan_amount": False, "label": False, "segment": False,
    },
    labels={"customers": "Customers", "share_pct": "Share of customers (%)", "avg_int_rate_pct": "Avg interest rate (%)",
            "pct_60_month": "60-month loans (%)", "median_annual_inc": "Median income ($)",
            "late_rate_active_pct": "Late rate, active loans (%)", "default_rate_resolved_pct": "Default rate, resolved (%)",
            "label": "Segment"},
    title="Customer segments: loan size vs default rate (bubble size = number of customers)",
)
fig.update_traces(textposition="middle center", textfont=dict(color="white", size=15),
                  marker=dict(opacity=0.85, line=dict(width=1, color="white")))
fig.update_xaxes(title="Average loan amount ($)", tickprefix="$", tickformat=",", range=[0, 34000])
fig.update_yaxes(title="Default rate, resolved loans only (%)", range=[0, 40])
fig.update_layout(legend_title_text="Segment", height=520)
fig
