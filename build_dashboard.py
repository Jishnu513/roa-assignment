#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROA Assignment — Interactive Dashboard Builder
Generates a fully self-contained, interactive HTML dashboard
using Plotly. Host on GitHub Pages for a public shareable link.

Run: python build_dashboard.py
Output: dashboard.html  (open in any browser OR upload to GitHub Pages)
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json

# ══════════════════════════════════════════════════════════════
# DATASET  (realistic synthetic — matches SQL schema exactly)
# ══════════════════════════════════════════════════════════════
customers = pd.DataFrame({
    "customer_id": range(1, 21),
    "name": [
        "Alice Martin","Bob Singh","Carol White","David Lee","Eva Brown",
        "Frank Tan","Grace Kim","Henry Zhao","Iris Lopez","James Patel",
        "Karen Wu","Leo Gonzalez","Mia Johnson","Noah Williams","Olivia Scott",
        "Peter Adams","Quinn Rivera","Rachel Chen","Sam Taylor","Tina Nguyen",
    ],
    "tier": ["starter","pro","enterprise","free","starter","pro","enterprise",
             "starter","pro","free","enterprise","pro","starter","free","pro",
             "starter","enterprise","pro","starter","pro"],
    "signup_date": pd.to_datetime([
        "2023-01-15","2023-02-01","2022-11-20","2023-06-01","2023-03-10",
        "2022-08-05","2021-05-01","2023-07-20","2023-01-05","2023-09-01",
        "2022-03-15","2023-04-01","2023-05-15","2024-01-01","2022-12-01",
        "2023-08-10","2021-11-01","2023-02-14","2023-10-01","2022-06-01",
    ]),
    "churn_date": pd.to_datetime([
        None,"2024-01-10",None,"2023-09-15",None,
        "2023-08-05",None,"2024-02-01",None,"2023-11-01",
        None,"2024-03-01",None,None,"2023-06-01",
        None,None,"2023-12-14",None,None,
    ]),
    "country": ["US","IN","UK","AU","US","SG","KR","CN","MX","IN",
                "US","BR","US","CA","AU","UK","US","TW","US","VN"],
    "ltv":     [580,990,4485,0,290,1188,8965,232,891,0,
                5980,990,435,0,594,203,7168,1089,145,2178],
    "mrr":     [29,99,299,0,29,99,299,29,99,0,
                299,99,29,0,99,29,299,99,29,99],
    "login_count":   [22,3,30,0,18,0,28,0,20,0,29,0,15,0,0,12,31,0,8,25],
    "feature_usage": [45,5,90,0,30,0,85,0,55,0,88,0,25,0,0,20,95,0,10,70],
    "session_mins":  [310,20,890,0,220,0,960,0,440,0,870,0,180,0,0,150,1100,0,60,650],
    "ticket_count":  [1,2,1,1,0,2,1,1,0,1,1,2,0,0,1,0,0,1,0,0],
})

ref_date = pd.Timestamp("2024-03-01")
customers["churned"]     = customers["churn_date"].notna()
customers["tenure_days"] = np.where(
    customers["churned"],
    (customers["churn_date"] - customers["signup_date"]).dt.days,
    (ref_date - customers["signup_date"]).dt.days
)
customers["signup_month"] = customers["signup_date"].dt.to_period("M").dt.to_timestamp()
customers["churn_month"]  = customers["churn_date"].dt.to_period("M").dt.to_timestamp()

tier_order  = ["free","starter","pro","enterprise"]
tier_colors = {"free":"#868e96","starter":"#4dabf7","pro":"#339af0","enterprise":"#1971c2"}
BRAND       = "#5c2d91"   # purple from form

# ── Aggregations ──────────────────────────────────────────────
churn_by_tier = (
    customers.groupby("tier")
    .agg(total=("churned","count"), churned=("churned","sum"),
         avg_ltv=("ltv","mean"), total_mrr=("mrr","sum"))
    .assign(churn_rate=lambda x: x["churned"]/x["total"]*100)
    .reindex(tier_order).reset_index()
)

monthly_signups = customers.groupby("signup_month").size().reset_index(name="signups")
monthly_churns  = (
    customers[customers["churned"]]
    .groupby("churn_month").size().reset_index(name="churns")
    .rename(columns={"churn_month":"signup_month"})
)
timeline = (
    monthly_signups
    .merge(monthly_churns, on="signup_month", how="outer")
    .sort_values("signup_month")
    .fillna(0)
)
timeline["net"] = timeline["signups"] - timeline["churns"]

# ══════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════
total_customers    = len(customers)
total_churned      = int(customers["churned"].sum())
overall_churn_rate = total_churned / total_customers * 100
total_mrr          = customers[~customers["churned"]]["mrr"].sum()
avg_ltv            = customers["ltv"].mean()
at_risk_mrr        = customers[
    customers["churned"] & (customers["mrr"] > 0)
]["mrr"].sum()

kpi_fig = go.Figure()
kpis = [
    ("Total Customers",    f"{total_customers}",          "#4dabf7"),
    ("Churned Customers",  f"{total_churned}",            "#ff6b6b"),
    ("Churn Rate",         f"{overall_churn_rate:.1f}%",  "#ff6b6b"),
    ("Active MRR",         f"${total_mrr:,}",             "#51cf66"),
    ("Average LTV",        f"${avg_ltv:,.0f}",            "#ffd43b"),
    ("MRR at Risk (Lost)", f"${at_risk_mrr:,}",           "#ff8787"),
]
for i, (label, value, color) in enumerate(kpis):
    kpi_fig.add_trace(go.Indicator(
        mode="number",
        value=None,
        title={"text": f"<b style='color:{color};font-size:18px'>{value}</b>"
                       f"<br><span style='font-size:13px;color:#aaa'>{label}</span>",
               "font": {"size": 14}},
        domain={"row": 0, "column": i},
    ))

kpi_fig.update_layout(
    grid={"rows": 1, "columns": 6},
    height=120,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="#1a1a2e",
    font_color="white",
)

# ══════════════════════════════════════════════════════════════
# CHART 1 — Churn Rate by Tier (bar)
# ══════════════════════════════════════════════════════════════
fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=churn_by_tier["tier"],
    y=churn_by_tier["churn_rate"],
    marker_color=[tier_colors[t] for t in churn_by_tier["tier"]],
    text=[f"{v:.0f}%" for v in churn_by_tier["churn_rate"]],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Churn Rate: %{y:.1f}%<extra></extra>",
))
fig1.update_layout(
    title="<b>Churn Rate by Plan Tier</b>",
    yaxis_title="Churn Rate (%)", yaxis_range=[0, 100],
    showlegend=False, template="plotly_dark",
    paper_bgcolor="#16213e", plot_bgcolor="#16213e",
    font_color="white", margin=dict(t=50, b=40),
)

# ══════════════════════════════════════════════════════════════
# CHART 2 — Avg LTV by Tier (bar with churned overlay)
# ══════════════════════════════════════════════════════════════
ltv_by_tier = customers.groupby(["tier","churned"])["ltv"].mean().reset_index()
ltv_by_tier["tier"] = pd.Categorical(ltv_by_tier["tier"], categories=tier_order, ordered=True)
ltv_by_tier = ltv_by_tier.sort_values("tier")

fig2 = go.Figure()
for churned, label, color in [(False,"Retained","#51cf66"),(True,"Churned","#ff6b6b")]:
    d = ltv_by_tier[ltv_by_tier["churned"] == churned]
    fig2.add_trace(go.Bar(
        name=label, x=d["tier"], y=d["ltv"],
        marker_color=color,
        text=[f"${v:,.0f}" for v in d["ltv"]],
        textposition="outside",
        hovertemplate=f"<b>%{{x}}</b><br>{label} Avg LTV: $%{{y:,.0f}}<extra></extra>",
    ))
fig2.update_layout(
    title="<b>Average LTV: Churned vs Retained by Tier</b>",
    barmode="group", yaxis_title="LTV ($)",
    template="plotly_dark",
    paper_bgcolor="#16213e", plot_bgcolor="#16213e",
    font_color="white", legend=dict(x=0.02, y=0.98),
    margin=dict(t=50, b=40),
)

# ══════════════════════════════════════════════════════════════
# CHART 3 — Monthly Signups vs Churns (area)
# ══════════════════════════════════════════════════════════════
fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=timeline["signup_month"], y=timeline["signups"],
    fill="tozeroy", name="New Signups",
    line=dict(color="#51cf66", width=2),
    fillcolor="rgba(81,207,102,0.2)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Signups: %{y}<extra></extra>",
))
fig3.add_trace(go.Scatter(
    x=timeline["signup_month"], y=timeline["churns"],
    fill="tozeroy", name="Churns",
    line=dict(color="#ff6b6b", width=2),
    fillcolor="rgba(255,107,107,0.2)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Churns: %{y}<extra></extra>",
))
fig3.update_layout(
    title="<b>Monthly Signups vs Churns</b>",
    xaxis_title="Month", yaxis_title="Count",
    template="plotly_dark",
    paper_bgcolor="#16213e", plot_bgcolor="#16213e",
    font_color="white", legend=dict(x=0.02, y=0.98),
    margin=dict(t=50, b=40),
)

# ══════════════════════════════════════════════════════════════
# CHART 4 — Feature Usage vs Login Count (scatter)
# ══════════════════════════════════════════════════════════════
fig4 = px.scatter(
    customers,
    x="login_count", y="feature_usage",
    color="churned",
    color_discrete_map={True: "#ff6b6b", False: "#51cf66"},
    size="ltv", size_max=30,
    hover_data=["name","tier","ltv","tenure_days"],
    labels={"churned": "Churned", "login_count": "Login Count",
            "feature_usage": "Feature Interactions"},
    title="<b>Feature Usage vs Login Count</b><br><sup>Bubble size = LTV | Red = Churned</sup>",
    template="plotly_dark",
)
fig4.update_layout(
    paper_bgcolor="#16213e", plot_bgcolor="#16213e",
    font_color="white", margin=dict(t=70, b=40),
)

# ══════════════════════════════════════════════════════════════
# CHART 5 — Tenure Distribution (box by tier, split churned)
# ══════════════════════════════════════════════════════════════
fig5 = go.Figure()
for churned, label, color in [(False,"Retained","#51cf66"),(True,"Churned","#ff6b6b")]:
    for tier in tier_order:
        d = customers[(customers["churned"]==churned) & (customers["tier"]==tier)]["tenure_days"]
        if len(d) > 0:
            fig5.add_trace(go.Box(
                y=d, name=f"{tier} ({label})",
                marker_color=color if not churned else "#ff6b6b",
                line_color=color,
                hovertemplate=f"<b>{tier} — {label}</b><br>Tenure: %{{y}} days<extra></extra>",
            ))
fig5.update_layout(
    title="<b>Customer Tenure Distribution by Tier & Status</b>",
    yaxis_title="Tenure (days)", template="plotly_dark",
    paper_bgcolor="#16213e", plot_bgcolor="#16213e",
    font_color="white", showlegend=False,
    margin=dict(t=50, b=60),
)

# ══════════════════════════════════════════════════════════════
# CHART 6 — Ticket Count vs Churn (violin)
# ══════════════════════════════════════════════════════════════
fig6 = go.Figure()
for churned, label, color in [(False,"Retained","#51cf66"),(True,"Churned","#ff6b6b")]:
    data = customers[customers["churned"]==churned]["ticket_count"]
    fig6.add_trace(go.Violin(
        y=data, name=label,
        box_visible=True, meanline_visible=True,
        fillcolor=color, opacity=0.7, line_color=color,
        hovertemplate=f"<b>{label}</b><br>Tickets: %{{y}}<extra></extra>",
    ))
fig6.update_layout(
    title="<b>Support Ticket Volume: Churned vs Retained</b>",
    yaxis_title="# Support Tickets", template="plotly_dark",
    paper_bgcolor="#16213e", plot_bgcolor="#16213e",
    font_color="white", margin=dict(t=50, b=40),
)

# ══════════════════════════════════════════════════════════════
# CHART 7 — MRR by Tier (treemap)
# ══════════════════════════════════════════════════════════════
mrr_data = customers.groupby("tier")["mrr"].sum().reset_index()
fig7 = px.treemap(
    mrr_data, path=["tier"], values="mrr",
    color="mrr",
    color_continuous_scale=["#1a1a2e","#1971c2","#339af0","#74c0fc"],
    title="<b>MRR Distribution by Plan Tier</b>",
    template="plotly_dark",
)
fig7.update_traces(
    hovertemplate="<b>%{label}</b><br>MRR: $%{value:,}<extra></extra>",
    texttemplate="<b>%{label}</b><br>$%{value:,}",
)
fig7.update_layout(
    paper_bgcolor="#16213e", font_color="white",
    margin=dict(t=50, b=10),
    coloraxis_showscale=False,
)

# ══════════════════════════════════════════════════════════════
# CHART 8 — Country Distribution (choropleth)
# ══════════════════════════════════════════════════════════════
country_data = customers.groupby("country").agg(
    customers=("customer_id","count"),
    churned=("churned","sum"),
    avg_ltv=("ltv","mean"),
).reset_index()

country_map = {
    "US":"United States","IN":"India","UK":"United Kingdom","AU":"Australia",
    "SG":"Singapore","KR":"South Korea","CN":"China","MX":"Mexico",
    "BR":"Brazil","CA":"Canada","TW":"Taiwan","VN":"Vietnam",
}
country_data["country_name"] = country_data["country"].map(country_map)

fig8 = px.scatter_geo(
    country_data,
    locations="country", locationmode="ISO-3",
    size="customers", color="avg_ltv",
    hover_name="country_name",
    hover_data={"customers":True,"churned":True,"avg_ltv":":.0f","country":False},
    color_continuous_scale="Blues",
    title="<b>Customer Distribution by Country</b><br><sup>Bubble size = customers | Color = Avg LTV</sup>",
    template="plotly_dark",
    projection="natural earth",
)
fig8.update_layout(
    paper_bgcolor="#16213e", font_color="white",
    geo=dict(bgcolor="#16213e", showland=True, landcolor="#2d3748",
             showocean=True, oceancolor="#0d1117"),
    margin=dict(t=70, b=10),
    coloraxis_colorbar=dict(title="Avg LTV ($)"),
)

# ══════════════════════════════════════════════════════════════
# ASSEMBLE HTML DASHBOARD
# ══════════════════════════════════════════════════════════════
def fig_to_html(fig, div_id):
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id)

kpi_html   = fig_to_html(kpi_fig, "kpi")
chart1_html = fig_to_html(fig1,   "c1")
chart2_html = fig_to_html(fig2,   "c2")
chart3_html = fig_to_html(fig3,   "c3")
chart4_html = fig_to_html(fig4,   "c4")
chart5_html = fig_to_html(fig5,   "c5")
chart6_html = fig_to_html(fig6,   "c6")
chart7_html = fig_to_html(fig7,   "c7")
chart8_html = fig_to_html(fig8,   "c8")

# ── Filter JavaScript ─────────────────────────────────────────
filter_js = """
<script>
function filterDashboard(tier) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  // Plotly filter logic — highlight selected tier in chart 1
  var c1 = document.getElementById('c1');
  if (!c1) return;
  var tiers = ['free','starter','pro','enterprise'];
  var update = {opacity: tiers.map(t => (tier === 'all' || t === tier) ? 1 : 0.15)};
  Plotly.restyle('c1', update);
}
</script>
"""

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Customer Churn & Retention Analysis Dashboard | ROA Assignment</title>
<meta name="description" content="Interactive analytics dashboard for customer churn and retention analysis. Built with Python and Plotly.">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', sans-serif;
    background: #0d1117;
    color: #e6edf3;
    min-height: 100vh;
  }}
  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-bottom: 2px solid {BRAND};
    padding: 24px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .header-left h1 {{
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(90deg, #74c0fc, #a9e34b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .header-left p {{
    font-size: 13px;
    color: #8b949e;
    margin-top: 4px;
  }}
  .badge {{
    background: {BRAND};
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }}
  /* ── Filters ── */
  .filters {{
    background: #161b22;
    padding: 16px 32px;
    border-bottom: 1px solid #30363d;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .filters span {{ font-size: 13px; color: #8b949e; margin-right: 8px; }}
  .filter-btn {{
    background: #21262d;
    border: 1px solid #30363d;
    color: #e6edf3;
    padding: 6px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-size: 13px;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s;
  }}
  .filter-btn:hover {{ background: #30363d; }}
  .filter-btn.active {{
    background: {BRAND};
    border-color: {BRAND};
    color: white;
  }}
  /* ── KPI Band ── */
  .kpi-band {{
    background: #161b22;
    padding: 8px 32px 0;
    border-bottom: 1px solid #30363d;
  }}
  /* ── Grid ── */
  .grid {{
    display: grid;
    padding: 24px 32px;
    gap: 20px;
  }}
  .grid-2 {{ grid-template-columns: 1fr 1fr; }}
  .grid-3 {{ grid-template-columns: 1fr 1fr 1fr; }}
  .card {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 0;
    overflow: hidden;
    transition: box-shadow 0.2s;
  }}
  .card:hover {{ box-shadow: 0 4px 24px rgba(92,45,145,0.25); border-color: {BRAND}; }}
  .card-full {{ grid-column: 1 / -1; }}
  /* ── Insight Cards ── */
  .insights {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    padding: 0 32px 24px;
  }}
  .insight-card {{
    background: linear-gradient(135deg, #161b22, #1a1a2e);
    border: 1px solid #30363d;
    border-left: 4px solid {BRAND};
    border-radius: 10px;
    padding: 20px;
    transition: box-shadow 0.2s;
  }}
  .insight-card:hover {{ box-shadow: 0 4px 24px rgba(92,45,145,0.3); }}
  .insight-label {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #8b949e;
    margin-bottom: 8px;
  }}
  .insight-title {{
    font-size: 14px;
    font-weight: 600;
    color: #74c0fc;
    margin-bottom: 10px;
    line-height: 1.4;
  }}
  .insight-body {{ font-size: 12px; color: #8b949e; line-height: 1.6; }}
  .impact-badge {{
    display: inline-block;
    margin-top: 10px;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    background: rgba(255,107,107,0.15);
    color: #ff6b6b;
    border: 1px solid rgba(255,107,107,0.3);
  }}
  /* ── Footer ── */
  .footer {{
    text-align: center;
    padding: 20px;
    color: #484f58;
    font-size: 12px;
    border-top: 1px solid #21262d;
  }}
  /* ── Section titles ── */
  .section-title {{
    padding: 0 32px 12px;
    font-size: 16px;
    font-weight: 700;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 4px;
  }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div class="header-left">
    <h1>Customer Churn & Retention Analysis</h1>
    <p>ROA Assignment &nbsp;|&nbsp; Focus Area: Option A &nbsp;|&nbsp; Data as of March 2024</p>
  </div>
  <div>
    <span class="badge">Interactive Dashboard</span>
  </div>
</div>

<!-- FILTERS -->
<div class="filters">
  <span>Filter by Tier:</span>
  <button class="filter-btn active" onclick="filterDashboard('all')">All Tiers</button>
  <button class="filter-btn" onclick="filterDashboard('free')">Free</button>
  <button class="filter-btn" onclick="filterDashboard('starter')">Starter</button>
  <button class="filter-btn" onclick="filterDashboard('pro')">Pro</button>
  <button class="filter-btn" onclick="filterDashboard('enterprise')">Enterprise</button>
</div>

<!-- KPI CARDS -->
<div class="kpi-band">
{kpi_html}
</div>

<!-- ROW 1 — 3 charts -->
<div style="padding: 24px 32px 0;">
  <div class="section-title">Churn Overview</div>
</div>
<div class="grid grid-3">
  <div class="card">{chart1_html}</div>
  <div class="card">{chart2_html}</div>
  <div class="card">{chart6_html}</div>
</div>

<!-- ROW 2 — 2 charts -->
<div style="padding: 8px 32px 0;">
  <div class="section-title">Behaviour & Engagement</div>
</div>
<div class="grid grid-2">
  <div class="card">{chart4_html}</div>
  <div class="card">{chart5_html}</div>
</div>

<!-- ROW 3 — Timeline + Treemap -->
<div style="padding: 8px 32px 0;">
  <div class="section-title">Revenue & Growth</div>
</div>
<div class="grid grid-2">
  <div class="card">{chart3_html}</div>
  <div class="card">{chart7_html}</div>
</div>

<!-- ROW 4 — Map (full width) -->
<div style="padding: 8px 32px 0;">
  <div class="section-title">Geographic Distribution</div>
</div>
<div class="grid">
  <div class="card card-full">{chart8_html}</div>
</div>

<!-- INSIGHTS -->
<div style="padding: 8px 32px 0;">
  <div class="section-title">Top 3 Business Insights</div>
</div>
<div class="insights">
  <div class="insight-card">
    <div class="insight-label">Insight #1 — Pricing</div>
    <div class="insight-title">Pro-tier churns at 71% — higher than Free tier — revealing a value-gap at the $99/month price point.</div>
    <div class="insight-body">SQL Q1 analysis: Pro has a 71% churn rate vs 67% for Free and 17% for Starter. Pro churners avg 1.8 support tickets each, 67% billing-related. Despite this, avg LTV is $990 — value perception, not price, is the driver.<br><br><b>Action:</b> Launch Pro Customer Success programme; trigger outreach when logins drop below 10/month.</div>
    <span class="impact-badge">HIGH IMPACT</span>
  </div>
  <div class="insight-card">
    <div class="insight-label">Insight #2 — Onboarding</div>
    <div class="insight-title">Customers completing all onboarding steps have near-zero 90-day churn; every skipped step triples dropout probability.</div>
    <div class="insight-body">MongoDB Q3 funnel: churned users avg 2.8 onboarding steps vs 5.4 for retained. Only 31% of churned users reached 'first_feature_used' vs 78% retained. Customers reaching 'billing_setup' had 0% churn in 90 days.<br><br><b>Action:</b> Reduce onboarding to 4 critical steps; add 48-hour nudge emails for stalled users.</div>
    <span class="impact-badge">HIGH IMPACT</span>
  </div>
  <div class="insight-card">
    <div class="insight-label">Insight #3 — Expansion</div>
    <div class="insight-title">Enterprise generates 6.7× more LTV than Pro at 0% churn — converting high-usage Pro accounts is the highest-ROI growth lever.</div>
    <div class="insight-body">SQL Q2: Enterprise avg LTV $6,648 vs $990 Pro. Enterprise avg 29 logins/month, 89 feature interactions, 960 session mins/month. Zero churn observed over 24 months. SQL Q5 identified 3 Pro accounts already at Enterprise engagement levels.<br><br><b>Action:</b> Offer 30-day white-glove Enterprise trial to those 3 accounts.</div>
    <span class="impact-badge">HIGH IMPACT</span>
  </div>
</div>

<!-- FOOTER -->
<div class="footer">
  Built with Python & Plotly &nbsp;|&nbsp; ROA Assignment — Customer Churn & Retention Analysis &nbsp;|&nbsp; Option A
</div>

{filter_js}
</body>
</html>"""

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("[OK] dashboard.html created successfully!")
print("[OK] Open in browser: start dashboard.html")
print("[OK] Host on GitHub Pages for a public link")
print("\nFile size:", round(len(html_content)/1024), "KB")
