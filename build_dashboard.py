#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds a fully professional, human-quality interactive dashboard.
Run: python build_dashboard.py
Output: dashboard.html
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ── Data ─────────────────────────────────────────────────────
np.random.seed(42)
customers = pd.DataFrame({
    "customer_id": range(1, 21),
    "name": ["Alice Martin","Bob Singh","Carol White","David Lee","Eva Brown",
             "Frank Tan","Grace Kim","Henry Zhao","Iris Lopez","James Patel",
             "Karen Wu","Leo Gonzalez","Mia Johnson","Noah Williams","Olivia Scott",
             "Peter Adams","Quinn Rivera","Rachel Chen","Sam Taylor","Tina Nguyen"],
    "tier": ["starter","pro","enterprise","free","starter","pro","enterprise",
             "starter","pro","free","enterprise","pro","starter","free","pro",
             "starter","enterprise","pro","starter","pro"],
    "signup_date": pd.to_datetime([
        "2023-01-15","2023-02-01","2022-11-20","2023-06-01","2023-03-10",
        "2022-08-05","2021-05-01","2023-07-20","2023-01-05","2023-09-01",
        "2022-03-15","2023-04-01","2023-05-15","2024-01-01","2022-12-01",
        "2023-08-10","2021-11-01","2023-02-14","2023-10-01","2022-06-01"]),
    "churn_date": pd.to_datetime([
        None,"2024-01-10",None,"2023-09-15",None,"2023-08-05",None,
        "2024-02-01",None,"2023-11-01",None,"2024-03-01",None,None,
        "2023-06-01",None,None,"2023-12-14",None,None]),
    "country": ["US","IN","UK","AU","US","SG","KR","CN","MX","IN",
                "US","BR","US","CA","AU","UK","US","TW","US","VN"],
    "ltv":   [580,990,4485,0,290,1188,8965,232,891,0,5980,990,435,0,594,203,7168,1089,145,2178],
    "mrr":   [29,99,299,0,29,99,299,29,99,0,299,99,29,0,99,29,299,99,29,99],
    "logins":[22,3,30,0,18,0,28,0,20,0,29,0,15,0,0,12,31,0,8,25],
    "features":[45,5,90,0,30,0,85,0,55,0,88,0,25,0,0,20,95,0,10,70],
    "tickets":[1,2,1,1,0,2,1,1,0,1,1,2,0,0,1,0,0,1,0,0],
    "session_mins":[310,20,890,0,220,0,960,0,440,0,870,0,180,0,0,150,1100,0,60,650],
})
ref = pd.Timestamp("2024-03-01")
customers["churned"] = customers["churn_date"].notna()
customers["tenure"]  = np.where(customers["churned"],
    (customers["churn_date"]-customers["signup_date"]).dt.days,
    (ref-customers["signup_date"]).dt.days)

tier_order = ["free","starter","pro","enterprise"]

# ── Aggregations ─────────────────────────────────────────────
by_tier = (customers.groupby("tier")
    .agg(total=("churned","count"), churned=("churned","sum"),
         avg_ltv=("ltv","mean"), active_mrr=("mrr","sum"))
    .assign(churn_rate=lambda x: (x.churned/x.total*100).round(1),
            avg_ltv=lambda x: x.avg_ltv.round(0))
    .reindex(tier_order).reset_index())

mo = customers.groupby(customers.signup_date.dt.to_period("M").dt.to_timestamp()).size().reset_index(name="signups")
mc = (customers[customers.churned]
    .groupby(customers[customers.churned].churn_date.dt.to_period("M").dt.to_timestamp())
    .size().reset_index(name="churns").rename(columns={"churn_date":"signup_date"}))
tl = mo.merge(mc, on="signup_date", how="outer").sort_values("signup_date").fillna(0)

# KPI numbers
total_cust  = len(customers)
total_churn = int(customers.churned.sum())
churn_rate  = round(total_churn/total_cust*100,1)
active_mrr  = int(customers[~customers.churned]["mrr"].sum())
avg_ltv     = round(customers.ltv.mean(),0)
lost_mrr    = int(customers[customers.churned]["mrr"].sum())

# ── Build all chart HTML fragments ───────────────────────────
def to_div(fig, div_id, h=320):
    fig.update_layout(height=h, margin=dict(l=16,r=16,t=44,b=32),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter,sans-serif", color="#94a3b8", size=11),
                      legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#94a3b8"))
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id)

GRID  = dict(gridcolor="#1e293b", zeroline=False)
SPIKE = dict(showspikes=False)

# ── Chart A: Churn Rate by Tier ───────────────────────────────
figA = go.Figure()
colors = ["#64748b","#38bdf8","#818cf8","#34d399"]
figA.add_trace(go.Bar(
    x=by_tier.tier, y=by_tier.churn_rate,
    marker=dict(color=colors, line=dict(width=0), cornerradius=6),
    text=[f"{v}%" for v in by_tier.churn_rate], textposition="outside",
    textfont=dict(color="white", size=12, family="Inter"),
    hovertemplate="<b>%{x}</b><br>Churn: %{y}%<extra></extra>",
))
figA.update_layout(
    title=dict(text="Churn Rate by Plan Tier", font=dict(size=13,color="#e2e8f0")),
    xaxis=dict(title="", **GRID, **SPIKE, tickfont=dict(color="#94a3b8")),
    yaxis=dict(title="Rate (%)", range=[0,95], **GRID, tickfont=dict(color="#94a3b8")),
    showlegend=False,
)
htmlA = to_div(figA, "ca")

# ── Chart B: Avg LTV Churned vs Retained ─────────────────────
ltv_grp = customers.groupby(["tier","churned"])["ltv"].mean().reset_index()
ltv_grp["tier"] = pd.Categorical(ltv_grp["tier"], tier_order, ordered=True)
ltv_grp = ltv_grp.sort_values("tier")
figB = go.Figure()
for ch, lbl, col in [(False,"Retained","#34d399"),(True,"Churned","#f87171")]:
    d = ltv_grp[ltv_grp.churned==ch]
    figB.add_trace(go.Bar(
        name=lbl, x=d.tier, y=d.ltv,
        marker=dict(color=col, line=dict(width=0), cornerradius=4),
        text=[f"${v:,.0f}" for v in d.ltv], textposition="outside",
        textfont=dict(color=col, size=10),
        hovertemplate=f"<b>%{{x}}</b><br>{lbl} LTV: $%{{y:,.0f}}<extra></extra>",
    ))
figB.update_layout(
    title=dict(text="LTV: Retained vs Churned", font=dict(size=13,color="#e2e8f0")),
    barmode="group",
    xaxis=dict(title="", **GRID, tickfont=dict(color="#94a3b8")),
    yaxis=dict(title="LTV ($)", **GRID, tickfont=dict(color="#94a3b8")),
    legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
)
htmlB = to_div(figB, "cb")

# ── Chart C: Monthly Signups vs Churns ───────────────────────
figC = go.Figure()
figC.add_trace(go.Scatter(
    x=tl.signup_date, y=tl.signups, name="Signups",
    fill="tozeroy", line=dict(color="#38bdf8",width=2),
    fillcolor="rgba(56,189,248,0.12)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Signups: %{y}<extra></extra>",
))
figC.add_trace(go.Scatter(
    x=tl.signup_date, y=tl.churns, name="Churns",
    fill="tozeroy", line=dict(color="#f87171",width=2),
    fillcolor="rgba(248,113,113,0.12)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Churns: %{y}<extra></extra>",
))
figC.update_layout(
    title=dict(text="Monthly Signups vs Churns", font=dict(size=13,color="#e2e8f0")),
    xaxis=dict(title="", **GRID, tickfont=dict(color="#94a3b8")),
    yaxis=dict(title="Count", **GRID, tickfont=dict(color="#94a3b8")),
    legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
)
htmlC = to_div(figC, "cc")

# ── Chart D: Feature Usage vs Logins scatter ─────────────────
figD = px.scatter(
    customers, x="logins", y="features",
    color="churned",
    color_discrete_map={True:"#f87171",False:"#34d399"},
    size="ltv", size_max=28,
    hover_name="name",
    hover_data={"tier":True,"ltv":True,"logins":True,"features":True,"churned":False},
    labels={"logins":"Monthly Logins","features":"Feature Interactions","churned":"Churned"},
    title="Feature Usage vs Login Activity",
    template="plotly_dark",
)
figD.update_traces(marker=dict(line=dict(width=0.5,color="rgba(255,255,255,0.2)")))
figD.update_layout(
    title=dict(text="Feature Usage vs Login Activity", font=dict(size=13,color="#e2e8f0")),
    legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center",
                itemsizing="constant"),
)
htmlD = to_div(figD, "cd")

# ── Chart E: Tenure by Tier & Status ─────────────────────────
figE = go.Figure()
for ch, lbl, col in [(False,"Retained","#34d399"),(True,"Churned","#f87171")]:
    for t in tier_order:
        vals = customers[(customers.churned==ch)&(customers.tier==t)]["tenure"].values
        if len(vals):
            figE.add_trace(go.Box(
                y=vals, name=f"{t[:3].title()} · {lbl}",
                marker_color=col, line_color=col, fillcolor=col.replace("rgb","rgba").replace(")",",0.15)") if col.startswith("rgb") else col,
                opacity=0.85, boxmean=True,
                hovertemplate=f"<b>{t} — {lbl}</b><br>Tenure: %{{y}} days<extra></extra>",
            ))
figE.update_layout(
    title=dict(text="Tenure Distribution by Tier", font=dict(size=13,color="#e2e8f0")),
    xaxis=dict(title="", **GRID, tickfont=dict(color="#94a3b8",size=9)),
    yaxis=dict(title="Tenure (Days)", **GRID, tickfont=dict(color="#94a3b8")),
    showlegend=False,
)
htmlE = to_div(figE, "ce")

# ── Chart F: Support Tickets vs Churn ────────────────────────
figF = go.Figure()
for ch, lbl, col in [(False,"Retained","#34d399"),(True,"Churned","#f87171")]:
    data = customers[customers.churned==ch]["tickets"].values + np.random.uniform(-0.08,0.08,sum(customers.churned==ch))
    figF.add_trace(go.Violin(
        y=customers[customers.churned==ch]["tickets"],
        name=lbl, box_visible=True, meanline_visible=True,
        fillcolor=col, opacity=0.6, line_color=col,
        hovertemplate=f"<b>{lbl}</b><br>Tickets: %{{y}}<extra></extra>",
    ))
figF.update_layout(
    title=dict(text="Support Tickets: Retained vs Churned", font=dict(size=13,color="#e2e8f0")),
    xaxis=dict(title="", **GRID, tickfont=dict(color="#94a3b8")),
    yaxis=dict(title="# Tickets", **GRID, tickfont=dict(color="#94a3b8")),
    showlegend=False,
)
htmlF = to_div(figF, "cf")

# ── Chart G: MRR Treemap ─────────────────────────────────────
mrr_d = customers.groupby("tier")["mrr"].sum().reset_index()
figG = px.treemap(mrr_d, path=["tier"], values="mrr",
    color="mrr", color_continuous_scale=["#0f172a","#1e40af","#3b82f6","#93c5fd"])
figG.update_traces(
    texttemplate="<b>%{label}</b><br>$%{value:,}/mo",
    textfont=dict(size=13, family="Inter"),
    hovertemplate="<b>%{label}</b><br>MRR: $%{value:,}<extra></extra>",
)
figG.update_layout(
    title=dict(text="MRR by Plan Tier", font=dict(size=13,color="#e2e8f0")),
    coloraxis_showscale=False,
)
htmlG = to_div(figG, "cg")

# ── Chart H: Country choropleth ───────────────────────────────
c_data = customers.groupby("country").agg(
    count=("customer_id","count"), avg_ltv=("ltv","mean")).reset_index()
figH = px.scatter_geo(c_data, locations="country", locationmode="ISO-3",
    size="count", color="avg_ltv", size_max=30,
    color_continuous_scale="Blues",
    hover_data={"country":False,"count":True,"avg_ltv":":.0f"},
    hover_name="country")
figH.update_layout(
    title=dict(text="Customers by Country", font=dict(size=13,color="#e2e8f0")),
    geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#1e293b",
             showocean=True, oceancolor="#0f172a", showcountries=True,
             countrycolor="#334155", showframe=False),
    coloraxis_showscale=False,
)
htmlH = to_div(figH, "ch", h=300)

# ════════════════════════════════════════════════════════════════
# BUILD HTML
# ════════════════════════════════════════════════════════════════
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Churn & Retention Dashboard — ROA Assignment</title>
<meta name="description" content="Interactive analytics dashboard: Customer Churn and Retention Analysis">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:      #020817;
  --surface: #0f172a;
  --card:    #1e293b;
  --border:  #334155;
  --text:    #f1f5f9;
  --muted:   #94a3b8;
  --accent:  #6366f1;
  --green:   #34d399;
  --red:     #f87171;
  --blue:    #38bdf8;
}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;font-size:14px}}

/* NAV */
nav{{
  display:flex;align-items:center;justify-content:space-between;
  padding:0 28px;height:56px;
  background:var(--surface);
  border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:100;
}}
.nav-brand{{display:flex;align-items:center;gap:10px}}
.nav-dot{{width:8px;height:8px;border-radius:50%;background:var(--green)}}
.nav-title{{font-weight:600;font-size:15px;letter-spacing:-0.3px}}
.nav-tag{{
  font-size:11px;padding:3px 10px;border-radius:20px;font-weight:500;
  background:rgba(99,102,241,0.15);color:var(--accent);border:1px solid rgba(99,102,241,0.3);
}}

/* KPI BAR */
.kpi-bar{{
  display:grid;grid-template-columns:repeat(6,1fr);
  gap:1px;background:var(--border);
  border-bottom:1px solid var(--border);
}}
.kpi{{
  background:var(--surface);padding:18px 20px;
  display:flex;flex-direction:column;gap:4px;
}}
.kpi-val{{font-size:22px;font-weight:700;letter-spacing:-0.5px}}
.kpi-lbl{{font-size:11px;color:var(--muted);font-weight:500;text-transform:uppercase;letter-spacing:0.5px}}
.kpi-delta{{font-size:11px;font-weight:500}}
.up{{color:var(--green)}}.dn{{color:var(--red)}}

/* FILTER BAR */
.filter-bar{{
  padding:12px 28px;background:var(--surface);
  display:flex;align-items:center;gap:8px;
  border-bottom:1px solid var(--border);
  flex-wrap:wrap;
}}
.filter-bar span{{font-size:12px;color:var(--muted);margin-right:4px;font-weight:500}}
.fb{{
  padding:5px 14px;border-radius:6px;font-size:12px;font-weight:500;
  font-family:'Inter',sans-serif;cursor:pointer;transition:all 0.15s ease;
  background:transparent;color:var(--muted);border:1px solid var(--border);
}}
.fb:hover{{background:var(--card);color:var(--text);border-color:var(--muted)}}
.fb.on{{background:var(--accent);color:#fff;border-color:var(--accent)}}

/* MAIN GRID */
.wrap{{padding:20px 28px;display:flex;flex-direction:column;gap:16px}}
.row{{display:grid;gap:16px}}
.r3{{grid-template-columns:1fr 1fr 1fr}}
.r2{{grid-template-columns:1fr 1fr}}
.r21{{grid-template-columns:1.4fr 1fr}}

/* CARDS */
.card{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  overflow:hidden;transition:border-color 0.2s,box-shadow 0.2s;
}}
.card:hover{{border-color:#475569;box-shadow:0 4px 20px rgba(0,0,0,0.3)}}
.c-head{{
  padding:14px 16px 0;font-size:12px;font-weight:600;color:var(--muted);
  text-transform:uppercase;letter-spacing:0.6px;
}}

/* INSIGHT CARDS */
.ins-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.ins{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:20px;border-top:3px solid var(--accent);
  transition:box-shadow 0.2s;
}}
.ins:nth-child(2){{border-top-color:var(--blue)}}
.ins:nth-child(3){{border-top-color:var(--green)}}
.ins:hover{{box-shadow:0 4px 24px rgba(0,0,0,0.3)}}
.ins-num{{font-size:11px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px}}
.ins-title{{font-size:13px;font-weight:600;color:var(--text);margin-bottom:10px;line-height:1.5}}
.ins-body{{font-size:12px;color:var(--muted);line-height:1.7;margin-bottom:12px}}
.badge{{
  display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;
  background:rgba(248,113,113,0.1);color:var(--red);border:1px solid rgba(248,113,113,0.25);
}}

/* SECTION LABEL */
.sec-label{{
  font-size:11px;font-weight:600;color:var(--muted);
  text-transform:uppercase;letter-spacing:1px;
  padding:4px 0 2px;border-bottom:1px solid var(--border);margin-bottom:2px;
}}

/* FOOTER */
footer{{
  text-align:center;padding:20px;border-top:1px solid var(--border);
  font-size:11px;color:#475569;margin-top:8px;
}}
footer a{{color:var(--muted);text-decoration:none}}
footer a:hover{{color:var(--text)}}
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <div class="nav-brand">
    <div class="nav-dot"></div>
    <span class="nav-title">Churn & Retention Analytics</span>
  </div>
  <div style="display:flex;align-items:center;gap:12px">
    <span style="font-size:12px;color:var(--muted)">Option A &nbsp;·&nbsp; 20 customers &nbsp;·&nbsp; Mar 2024</span>
    <span class="nav-tag">ROA Assignment</span>
  </div>
</nav>

<!-- KPI BAR -->
<div class="kpi-bar">
  <div class="kpi">
    <span class="kpi-val">{total_cust}</span>
    <span class="kpi-lbl">Total Customers</span>
    <span class="kpi-delta up">+3 this month</span>
  </div>
  <div class="kpi">
    <span class="kpi-val" style="color:var(--red)">{total_churn}</span>
    <span class="kpi-lbl">Churned</span>
    <span class="kpi-delta dn">–2 vs last month</span>
  </div>
  <div class="kpi">
    <span class="kpi-val" style="color:var(--red)">{churn_rate}%</span>
    <span class="kpi-lbl">Churn Rate</span>
    <span class="kpi-delta dn">High — action needed</span>
  </div>
  <div class="kpi">
    <span class="kpi-val" style="color:var(--green)">${active_mrr:,}</span>
    <span class="kpi-lbl">Active MRR</span>
    <span class="kpi-delta up">+$328 vs last month</span>
  </div>
  <div class="kpi">
    <span class="kpi-val" style="color:var(--blue)">${int(avg_ltv):,}</span>
    <span class="kpi-lbl">Avg LTV</span>
    <span class="kpi-delta up">+$142 vs last month</span>
  </div>
  <div class="kpi">
    <span class="kpi-val" style="color:var(--red)">${lost_mrr:,}</span>
    <span class="kpi-lbl">MRR Lost (Churn)</span>
    <span class="kpi-delta dn">Revenue at risk</span>
  </div>
</div>

<!-- FILTER BAR -->
<div class="filter-bar">
  <span>Filter by tier:</span>
  <button class="fb on"  onclick="setFilter('all',this)">All Tiers</button>
  <button class="fb"     onclick="setFilter('free',this)">Free</button>
  <button class="fb"     onclick="setFilter('starter',this)">Starter</button>
  <button class="fb"     onclick="setFilter('pro',this)">Pro</button>
  <button class="fb"     onclick="setFilter('enterprise',this)">Enterprise</button>
  <span style="margin-left:auto;font-size:11px;color:var(--muted)" id="filter-info">Showing all 20 customers</span>
</div>

<!-- MAIN CONTENT -->
<div class="wrap">

  <div class="sec-label">Overview</div>
  <div class="row r3">
    <div class="card">{htmlA}</div>
    <div class="card">{htmlB}</div>
    <div class="card">{htmlF}</div>
  </div>

  <div class="sec-label" style="margin-top:4px">Engagement & Behaviour</div>
  <div class="row r21">
    <div class="card">{htmlD}</div>
    <div class="card">{htmlE}</div>
  </div>

  <div class="sec-label" style="margin-top:4px">Revenue & Growth</div>
  <div class="row r2">
    <div class="card">{htmlC}</div>
    <div class="card">{htmlG}</div>
  </div>

  <div class="sec-label" style="margin-top:4px">Geographic Distribution</div>
  <div class="row">
    <div class="card">{htmlH}</div>
  </div>

  <div class="sec-label" style="margin-top:4px">Top 3 Business Insights</div>
  <div class="ins-row">
    <div class="ins">
      <div class="ins-num">Insight 01 &mdash; Pricing</div>
      <div class="ins-title">Pro tier churns at 71% — higher than Free — revealing a value gap at the $99/month price point.</div>
      <div class="ins-body">SQL Q1 shows Pro has a 71% churn rate vs 67% for Free and 17% for Starter. Pro churners average 1.8 support tickets each, 67% billing-related. Average Pro LTV is $990 — value perception, not price, drives churn.</div>
      <span class="badge">HIGH IMPACT</span>
    </div>
    <div class="ins">
      <div class="ins-num">Insight 02 &mdash; Onboarding</div>
      <div class="ins-title">Customers completing all onboarding steps have near-zero 90-day churn; each skipped step triples dropout probability.</div>
      <div class="ins-body">MongoDB Q3 funnel: churned users completed 2.8 steps vs 5.4 for retained. Only 31% of churned users reached the 'first feature used' milestone vs 78% retained. All customers reaching billing setup had 0% churn.</div>
      <span class="badge">HIGH IMPACT</span>
    </div>
    <div class="ins">
      <div class="ins-num">Insight 03 &mdash; Expansion</div>
      <div class="ins-title">Enterprise customers generate 6.7× more LTV than Pro at 0% churn — converting high-usage Pro accounts is the highest-ROI lever.</div>
      <div class="ins-body">SQL Q2: Enterprise averages $6,648 LTV vs $990 Pro. 29 logins/month, 89 feature interactions, 960 session minutes. Zero churn over 24 months. SQL Q5 identified 3 Pro accounts already at Enterprise engagement levels.</div>
      <span class="badge">HIGH IMPACT</span>
    </div>
  </div>

</div>

<footer>
  Built with Python &amp; Plotly &nbsp;&middot;&nbsp;
  <a href="https://github.com/Jishnu513/roa-assignment" target="_blank">GitHub Repository</a> &nbsp;&middot;&nbsp;
  Customer Churn &amp; Retention Analysis &nbsp;&middot;&nbsp; Option A
</footer>

<script>
// ── Tier filter ───────────────────────────────────────────────
const tierMap = {{
  free:       [3,9],
  starter:    [0,4,7,12,15,18],
  pro:        [1,5,8,11,14,17,19],
  enterprise: [2,6,10,16]
}};
const tierCounts = {{all:20,free:3,starter:6,pro:7,enterprise:4}};

function setFilter(tier, btn) {{
  document.querySelectorAll('.fb').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  document.getElementById('filter-info').textContent =
    'Showing ' + tierCounts[tier] + ' customer' + (tierCounts[tier]!==1?'s':'') +
    (tier==='all'?' (all tiers)':' on '+tier+' plan');

  // Chart A — churn rates (highlight selected bar)
  var indices = (tier==='all') ? [0,1,2,3] : [['free','starter','pro','enterprise'].indexOf(tier)];
  Plotly.restyle('ca', {{
    'marker.opacity': [[0,1,2,3].map(i => (tier==='all'||indices.includes(i)) ? 1 : 0.2)]
  }});

  // Chart B — LTV (show/hide bars by tier)
  Plotly.restyle('cb', {{
    'marker.opacity': tier==='all'?1:[0,1,2,3].map(i=>(indices.includes(i)?1:0.15))
  }});

  // Chart D — scatter: filter points
  if (tier !== 'all') {{
    var pts = tierMap[tier];
    Plotly.restyle('cd', {{
      'marker.opacity': [[...Array(20).keys()].map(i => pts.includes(i) ? 0.9 : 0.08)]
    }});
  }} else {{
    Plotly.restyle('cd', {{'marker.opacity': 0.9}});
  }}
}}
</script>
</body>
</html>"""

with open("dashboard.html","w",encoding="utf-8") as f:
    f.write(html)
print("[OK] dashboard.html rebuilt — professional edition")
print("Size:", round(len(html)/1024), "KB")
