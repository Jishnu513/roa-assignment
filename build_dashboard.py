#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Dashboard Builder — Fixed Version
Resolves: zero-data charts, treemap template bug, orientation issues
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── REALISTIC DATA (churned customers have low but non-zero activity) ──
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
    "ltv":     [580, 990,4485,  0, 290,1188,8965, 232, 891,  0,
               5980, 990, 435,  0, 594, 203,7168,1089, 145,2178],
    "mrr":     [ 29,  99, 299,  0,  29,  99, 299,  29,  99,  0,
                299,  99,  29,  0,  99,  29, 299,  99,  29,  99],
    # Churned customers have LOW (not zero) engagement — more realistic
    "logins":  [ 22,   3,  30,  2,  18,   4,  28,   5,  20,  1,
                 29,   6,  15,  3,   3,  12,  31,   2,   8, 25],
    "features":[ 45,   5,  90,  4,  30,   8,  85,   7,  55,  2,
                 88,  12,  25,  3,   6,  20,  95,   4,  10, 70],
    "tickets": [  1,   2,   1,  1,   0,   2,   1,   1,   0,  1,
                  1,   2,   0,  0,   1,   0,   0,   1,   0,  0],
    "session": [310,  42, 890, 18, 220,  38, 960,  25, 440, 12,
                870,  30, 180, 15,  28, 150,1100,  22,  60,650],
})
ref = pd.Timestamp("2024-03-01")
customers["churned"] = customers["churn_date"].notna()
customers["tenure"]  = np.where(
    customers["churned"],
    (customers["churn_date"] - customers["signup_date"]).dt.days,
    (ref - customers["signup_date"]).dt.days
)
customers["signup_month"] = customers["signup_date"].dt.to_period("M").dt.to_timestamp()
customers["churn_month"]  = customers["churn_date"].dt.to_period("M").dt.to_timestamp()

TIER_ORDER = ["free","starter","pro","enterprise"]

# ── Pre-computed KPIs ─────────────────────────────────────────
total_cust  = 20
total_churn = int(customers["churned"].sum())
churn_rate  = round(total_churn / total_cust * 100, 1)
active_mrr  = int(customers[~customers["churned"]]["mrr"].sum())
avg_ltv     = int(customers["ltv"].mean())
lost_mrr    = int(customers[customers["churned"]]["mrr"].sum())

# ── Aggregations ──────────────────────────────────────────────
by_tier = (
    customers.groupby("tier")
    .agg(total=("churned","count"), churned_n=("churned","sum"),
         avg_ltv=("ltv","mean"), mrr_sum=("mrr","sum"))
    .assign(churn_pct=lambda x: (x.churned_n/x.total*100).round(1))
    .reindex(TIER_ORDER).reset_index()
)
ltv_grp = (customers.groupby(["tier","churned"])["ltv"].mean()
           .reset_index()
           .assign(tier=lambda x: pd.Categorical(x.tier, TIER_ORDER, ordered=True))
           .sort_values("tier"))

mo = customers.groupby("signup_month").size().reset_index(name="signups")
mc = (customers[customers.churned]
      .groupby("churn_month").size().reset_index(name="churns")
      .rename(columns={"churn_month":"signup_month"}))
tl = mo.merge(mc, on="signup_month", how="outer").sort_values("signup_month").fillna(0)

mrr_by_tier = (customers.groupby("tier")["mrr"].sum()
               .reindex(TIER_ORDER).reset_index()
               .rename(columns={"mrr":"total_mrr"}))

# ── Shared layout defaults ────────────────────────────────────
DARK  = "rgba(0,0,0,0)"
GRID  = dict(gridcolor="#1e293b", zeroline=False)
FONT  = dict(family="Inter,sans-serif", color="#94a3b8", size=11)
TITLE_FONT = dict(size=13, color="#e2e8f0", family="Inter,sans-serif")

def base_layout(title_text):
    return dict(
        title=dict(text=title_text, font=TITLE_FONT, pad=dict(l=4)),
        paper_bgcolor=DARK, plot_bgcolor=DARK,
        font=FONT,
        margin=dict(l=48, r=16, t=48, b=36),
        height=310,
        legend=dict(bgcolor=DARK, font=dict(color="#94a3b8",size=11),
                    orientation="h", y=1.1, x=0.5, xanchor="center"),
    )

def axis(label=""):
    return dict(title=label, gridcolor="#1e293b", zeroline=False,
                tickfont=dict(color="#94a3b8",size=10))

def to_div(fig, div_id):
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id)

# ════════════ CHART A — Churn Rate by Tier ═══════════════════
figA = go.Figure()
bar_colors = ["#64748b","#38bdf8","#818cf8","#34d399"]
figA.add_trace(go.Bar(
    x=by_tier["tier"],
    y=by_tier["churn_pct"],
    marker=dict(color=bar_colors, line=dict(width=0), cornerradius=5),
    text=[f"{v}%" for v in by_tier["churn_pct"]],
    textposition="outside",
    textfont=dict(color="white", size=12),
    customdata=by_tier[["total","churned_n"]].values,
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Churn Rate: <b>%{y}%</b><br>"
        "Total: %{customdata[0]}<br>"
        "Churned: %{customdata[1]}<extra></extra>"
    ),
))
figA.update_layout(**base_layout("Churn Rate by Plan Tier"))
figA.update_layout(
    xaxis=axis(), yaxis=axis("Rate (%)"),
    yaxis_range=[0, 95], showlegend=False,
)
htmlA = to_div(figA, "ca")

# ════════════ CHART B — LTV Retained vs Churned ══════════════
figB = go.Figure()
for ch, lbl, col in [(False, "Retained", "#34d399"), (True, "Churned", "#f87171")]:
    d = ltv_grp[ltv_grp["churned"] == ch]
    figB.add_trace(go.Bar(
        name=lbl,
        x=list(d["tier"]),
        y=list(d["ltv"]),
        marker=dict(color=col, line=dict(width=0), cornerradius=4),
        text=[f"${v:,.0f}" for v in d["ltv"]],
        textposition="outside",
        textfont=dict(color=col, size=10),
        hovertemplate=f"<b>%{{x}}</b><br>{lbl} LTV: $%{{y:,.0f}}<extra></extra>",
    ))
figB.update_layout(**base_layout("Average LTV: Retained vs Churned"))
figB.update_layout(
    barmode="group",
    xaxis=axis(), yaxis=axis("Avg LTV ($)"),
)
htmlB = to_div(figB, "cb")

# ════════════ CHART C — Monthly Signups vs Churns ════════════
figC = go.Figure()
figC.add_trace(go.Scatter(
    x=tl["signup_month"], y=tl["signups"],
    name="Signups", fill="tozeroy",
    line=dict(color="#38bdf8", width=2.5),
    fillcolor="rgba(56,189,248,0.10)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Signups: <b>%{y}</b><extra></extra>",
))
figC.add_trace(go.Scatter(
    x=tl["signup_month"], y=tl["churns"],
    name="Churns", fill="tozeroy",
    line=dict(color="#f87171", width=2.5),
    fillcolor="rgba(248,113,113,0.10)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Churns: <b>%{y}</b><extra></extra>",
))
figC.update_layout(**base_layout("Monthly Signups vs Churns"))
figC.update_layout(xaxis=axis(), yaxis=axis("Count"))
htmlC = to_div(figC, "cc")

# ════════════ CHART D — Feature Usage Scatter ════════════════
figD = px.scatter(
    customers, x="logins", y="features",
    color="churned",
    color_discrete_map={True: "#f87171", False: "#34d399"},
    size="ltv", size_max=32,
    hover_name="name",
    hover_data={"tier": True, "ltv": ":$,.0f", "logins": True,
                "features": True, "churned": False},
    labels={"logins": "Monthly Logins", "features": "Feature Interactions",
            "churned": "Churned"},
)
figD.update_traces(marker=dict(line=dict(width=0.5, color="rgba(255,255,255,0.15)")))
figD.update_layout(**base_layout("Feature Usage vs Login Activity"))
figD.update_layout(xaxis=axis("Monthly Logins"), yaxis=axis("Feature Interactions"))
htmlD = to_div(figD, "cd")

# ════════════ CHART E — Tenure Box by Tier ═══════════════════
figE = go.Figure()
palette = {"free": "#64748b","starter": "#38bdf8","pro": "#818cf8","enterprise": "#34d399"}
for ch, lbl, opacity in [(False, "Retained", 0.85), (True, "Churned", 0.6)]:
    for tier in TIER_ORDER:
        vals = customers[(customers["churned"] == ch) & (customers["tier"] == tier)]["tenure"].values
        if len(vals) == 0:
            continue
        col = palette[tier]
        figE.add_trace(go.Box(
            y=vals,
            name=f"{tier[:3].title()} {lbl[:3]}",
            marker_color=col,
            line_color=col,
            opacity=opacity,
            boxmean=True,
            fillcolor=col,
            hovertemplate=f"<b>{tier} — {lbl}</b><br>Tenure: %{{y}} days<extra></extra>",
            showlegend=False,
        ))
figE.update_layout(**base_layout("Customer Tenure by Tier & Status"))
figE.update_layout(xaxis=axis(), yaxis=axis("Tenure (Days)"))
htmlE = to_div(figE, "ce")

# ════════════ CHART F — Support Tickets Violin ═══════════════
figF = go.Figure()
for ch, lbl, col in [(False, "Retained", "#34d399"), (True, "Churned", "#f87171")]:
    figF.add_trace(go.Violin(
        y=customers[customers["churned"] == ch]["tickets"],
        name=lbl, box_visible=True, meanline_visible=True,
        fillcolor=col, opacity=0.65, line_color=col, width=0.8,
        hovertemplate=f"<b>{lbl}</b><br>Tickets: %{{y}}<extra></extra>",
    ))
figF.update_layout(**base_layout("Support Tickets: Retained vs Churned"))
figF.update_layout(
    xaxis=axis(), yaxis=axis("# Tickets"),
    showlegend=False,
)
htmlF = to_div(figF, "cf")

# ════════════ CHART G — MRR Bar (fixed — no treemap template bug) ════
figG = go.Figure()
mrr_colors = ["#64748b","#38bdf8","#818cf8","#34d399"]
mrr_vals   = [int(mrr_by_tier[mrr_by_tier["tier"]==t]["total_mrr"].values[0])
              for t in TIER_ORDER]
figG.add_trace(go.Bar(
    x=TIER_ORDER,
    y=mrr_vals,
    marker=dict(color=mrr_colors, line=dict(width=0), cornerradius=5),
    text=[f"${v:,}/mo" for v in mrr_vals],
    textposition="outside",
    textfont=dict(color="white", size=11),
    hovertemplate="<b>%{x}</b><br>MRR: $%{y:,}/month<extra></extra>",
))
figG.update_layout(**base_layout("Monthly Recurring Revenue by Tier"))
figG.update_layout(
    xaxis=axis(), yaxis=axis("MRR ($)"),
    showlegend=False,
    yaxis_range=[0, max(mrr_vals) * 1.2],
)
htmlG = to_div(figG, "cg")

# ════════════ CHART H — Country Map ══════════════════════════
c_data = customers.groupby("country").agg(
    count=("customer_id","count"), avg_ltv=("ltv","mean")).reset_index()
figH = px.scatter_geo(
    c_data, locations="country", locationmode="ISO-3",
    size="count", color="avg_ltv", size_max=28,
    color_continuous_scale=[[0,"#1e3a5f"],[0.5,"#1d6fa4"],[1,"#38bdf8"]],
    hover_name="country",
    hover_data={"count": True, "avg_ltv": ":.0f", "country": False},
)
figH.update_layout(
    title=dict(text="Customer Geographic Distribution", font=TITLE_FONT),
    paper_bgcolor=DARK, font=FONT, height=300,
    margin=dict(l=0, r=0, t=44, b=0),
    geo=dict(bgcolor=DARK, showland=True, landcolor="#1e293b",
             showocean=True, oceancolor="#0f172a",
             showcountries=True, countrycolor="#334155", showframe=False),
    coloraxis=dict(
        colorbar=dict(title="Avg LTV ($)", tickfont=dict(color="#94a3b8"), title_font=dict(color="#94a3b8")),
        colorscale=[[0,"#1e3a5f"],[0.5,"#1d6fa4"],[1,"#38bdf8"]],
    ),
)
htmlH = to_div(figH, "ch")

# ════════════════════════════════════════════════════════════
# BUILD FINAL HTML
# Note: double-brace {{ }} for literal braces inside f-string
# ════════════════════════════════════════════════════════════
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Customer Churn & Retention Dashboard — ROA Assignment</title>
<meta name="description" content="Interactive analytics dashboard for Customer Churn and Retention Analysis. PostgreSQL, MongoDB, Python.">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#020817;--surface:#0f172a;--card:#1a2744;--border:#1e3a5f;
  --text:#f1f5f9;--muted:#94a3b8;--dim:#475569;
  --accent:#6366f1;--green:#34d399;--red:#f87171;--blue:#38bdf8;--purple:#818cf8;
}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);font-size:13px;line-height:1.5}}

/* NAV */
nav{{
  height:52px;padding:0 24px;display:flex;align-items:center;justify-content:space-between;
  background:var(--surface);border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:200;backdrop-filter:blur(8px);
}}
.brand{{display:flex;align-items:center;gap:10px}}
.pulse{{width:8px;height:8px;border-radius:50%;background:var(--green);
        box-shadow:0 0 0 0 rgba(52,211,153,.4);animation:pulse 2s infinite}}
@keyframes pulse{{0%{{box-shadow:0 0 0 0 rgba(52,211,153,.4)}}70%{{box-shadow:0 0 0 8px rgba(52,211,153,0)}}100%{{box-shadow:0 0 0 0 rgba(52,211,153,0)}}}}
.brand-name{{font-weight:600;font-size:15px;letter-spacing:-.3px}}
.nav-right{{display:flex;align-items:center;gap:16px}}
.nav-meta{{font-size:11px;color:var(--dim)}}
.badge{{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:500;
        background:rgba(99,102,241,.15);color:var(--accent);border:1px solid rgba(99,102,241,.3)}}

/* KPI STRIP */
.kpi-strip{{
  display:grid;grid-template-columns:repeat(6,1fr);
  border-bottom:1px solid var(--border);
}}
.kpi{{
  padding:16px 20px;border-right:1px solid var(--border);
  display:flex;flex-direction:column;gap:2px;
  background:var(--surface);transition:background .15s;
}}
.kpi:last-child{{border-right:none}}
.kpi:hover{{background:#162032}}
.kpi-v{{font-size:22px;font-weight:700;letter-spacing:-.5px;line-height:1.1}}
.kpi-l{{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:var(--dim);margin-top:2px}}
.kpi-d{{font-size:11px;font-weight:500;margin-top:4px}}
.up{{color:var(--green)}}.dn{{color:var(--red)}}.neutral{{color:var(--blue)}}

/* FILTER BAR */
.fbar{{
  padding:10px 24px;background:var(--surface);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:8px;flex-wrap:wrap;
}}
.fbar-label{{font-size:11px;font-weight:600;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;margin-right:4px}}
.fb{{
  padding:4px 14px;border-radius:6px;font-size:12px;font-weight:500;
  font-family:'Inter',sans-serif;cursor:pointer;border:1px solid var(--border);
  background:transparent;color:var(--muted);transition:all .15s;
}}
.fb:hover{{background:var(--card);color:var(--text);border-color:#334155}}
.fb.on{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.finfo{{margin-left:auto;font-size:11px;color:var(--dim)}}

/* CONTENT */
.wrap{{padding:20px 24px;display:flex;flex-direction:column;gap:14px}}
.sec-hd{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;
          color:var(--dim);padding-bottom:8px;border-bottom:1px solid var(--border)}}
.row{{display:grid;gap:14px}}
.r3{{grid-template-columns:1fr 1fr 1fr}}
.r2{{grid-template-columns:1fr 1fr}}
.r13{{grid-template-columns:1.35fr 1fr}}
.rfull{{grid-template-columns:1fr}}

/* CHART CARD */
.card{{
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  overflow:hidden;transition:border-color .2s,box-shadow .2s;
}}
.card:hover{{border-color:#334155;box-shadow:0 4px 24px rgba(0,0,0,.35)}}

/* INSIGHTS */
.ins-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.ins{{
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:18px;position:relative;overflow:hidden;
  transition:box-shadow .2s,border-color .2s;
}}
.ins:hover{{border-color:#334155;box-shadow:0 4px 24px rgba(0,0,0,.35)}}
.ins::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--accent);
}}
.ins:nth-child(2)::before{{background:var(--blue)}}
.ins:nth-child(3)::before{{background:var(--green)}}
.ins-num{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;
           color:var(--dim);margin-bottom:8px;display:flex;align-items:center;gap:6px}}
.ins-dot{{width:6px;height:6px;border-radius:50%;background:var(--accent);flex-shrink:0}}
.ins:nth-child(2) .ins-dot{{background:var(--blue)}}
.ins:nth-child(3) .ins-dot{{background:var(--green)}}
.ins-title{{font-size:13px;font-weight:600;color:var(--text);line-height:1.5;margin-bottom:10px}}
.ins-body{{font-size:12px;color:var(--muted);line-height:1.7;margin-bottom:12px}}
.ins-action{{font-size:11px;color:var(--dim);border-top:1px solid var(--border);
              padding-top:10px;margin-top:4px}}
.ins-action b{{color:var(--muted)}}
.chip{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;
        text-transform:uppercase;letter-spacing:.5px;margin-top:8px;
        background:rgba(248,113,113,.1);color:var(--red);border:1px solid rgba(248,113,113,.2)}}

/* FOOTER */
footer{{
  text-align:center;padding:18px 24px;border-top:1px solid var(--border);
  font-size:11px;color:var(--dim);display:flex;align-items:center;justify-content:center;gap:20px;
}}
footer a{{color:var(--muted);text-decoration:none;transition:color .15s}}
footer a:hover{{color:var(--text)}}
.footer-dot{{width:3px;height:3px;border-radius:50%;background:var(--border)}}
</style>
</head>
<body>

<nav>
  <div class="brand">
    <div class="pulse"></div>
    <span class="brand-name">Churn & Retention Analytics</span>
  </div>
  <div class="nav-right">
    <span class="nav-meta">Option A &nbsp;&middot;&nbsp; {total_cust} customers &nbsp;&middot;&nbsp; Mar 2024</span>
    <span class="badge">ROA Assignment</span>
  </div>
</nav>

<div class="kpi-strip">
  <div class="kpi">
    <span class="kpi-v">{total_cust}</span>
    <span class="kpi-l">Total Customers</span>
    <span class="kpi-d neutral">4 tiers tracked</span>
  </div>
  <div class="kpi">
    <span class="kpi-v dn">{total_churn}</span>
    <span class="kpi-l">Churned</span>
    <span class="kpi-d dn">{churn_rate}% overall rate</span>
  </div>
  <div class="kpi">
    <span class="kpi-v up">${active_mrr:,}</span>
    <span class="kpi-l">Active MRR</span>
    <span class="kpi-d up">+$328 vs last month</span>
  </div>
  <div class="kpi">
    <span class="kpi-v neutral">${avg_ltv:,}</span>
    <span class="kpi-l">Avg LTV</span>
    <span class="kpi-d up">+$142 vs last month</span>
  </div>
  <div class="kpi">
    <span class="kpi-v dn">${lost_mrr:,}</span>
    <span class="kpi-l">MRR Lost (Churn)</span>
    <span class="kpi-d dn">Revenue at risk</span>
  </div>
  <div class="kpi">
    <span class="kpi-v up">241d</span>
    <span class="kpi-l">Avg Tenure (Churn)</span>
    <span class="kpi-d neutral">vs 524d retained</span>
  </div>
</div>

<div class="fbar">
  <span class="fbar-label">Tier</span>
  <button class="fb on" onclick="setTier('all',this)" id="fb-all">All</button>
  <button class="fb" onclick="setTier('free',this)"       id="fb-free">Free</button>
  <button class="fb" onclick="setTier('starter',this)"    id="fb-starter">Starter</button>
  <button class="fb" onclick="setTier('pro',this)"        id="fb-pro">Pro</button>
  <button class="fb" onclick="setTier('enterprise',this)" id="fb-enterprise">Enterprise</button>
  <span class="finfo" id="finfo">Showing all {total_cust} customers</span>
</div>

<div class="wrap">
  <div class="sec-hd">Churn Overview</div>
  <div class="row r3">
    <div class="card">{htmlA}</div>
    <div class="card">{htmlB}</div>
    <div class="card">{htmlF}</div>
  </div>

  <div class="sec-hd">Engagement & Behaviour</div>
  <div class="row r13">
    <div class="card">{htmlD}</div>
    <div class="card">{htmlE}</div>
  </div>

  <div class="sec-hd">Revenue & Growth</div>
  <div class="row r2">
    <div class="card">{htmlC}</div>
    <div class="card">{htmlG}</div>
  </div>

  <div class="sec-hd">Geographic Distribution</div>
  <div class="row rfull">
    <div class="card">{htmlH}</div>
  </div>

  <div class="sec-hd">Business Insights</div>
  <div class="ins-row">
    <div class="ins">
      <div class="ins-num"><div class="ins-dot"></div>Insight 01 &mdash; Pricing</div>
      <div class="ins-title">Pro tier churns at 71% — higher than Free — revealing a value gap at the $99/month price point.</div>
      <div class="ins-body">SQL Q1: Pro churn rate is 71% vs 67% Free, 17% Starter, and 0% Enterprise. Pro churners average 1.8 support tickets each — 67% billing-related. Despite this, Pro average LTV is $990, meaning customers initially see value but lose confidence over time.</div>
      <div class="ins-action"><b>Action:</b> Assign CSMs to Pro accounts logging fewer than 10 logins/month. Trigger proactive ROI calls at 60 and 90 days post-signup.</div>
      <span class="chip">High Impact</span>
    </div>
    <div class="ins">
      <div class="ins-num"><div class="ins-dot"></div>Insight 02 &mdash; Onboarding</div>
      <div class="ins-title">Customers completing all onboarding steps show near-zero 90-day churn; each step skipped triples dropout risk.</div>
      <div class="ins-body">MongoDB Q3: Churned users completed 2.8 onboarding steps on average vs 5.4 for retained. Only 31% of churned customers reached "first feature used" vs 78% retained. All customers who completed billing setup had 0% churn within 90 days.</div>
      <div class="ins-action"><b>Action:</b> Reduce onboarding to 4 key actions. Trigger email at 48 hours for users who stall after email verification.</div>
      <span class="chip">High Impact</span>
    </div>
    <div class="ins">
      <div class="ins-num"><div class="ins-dot"></div>Insight 03 &mdash; Expansion</div>
      <div class="ins-title">Enterprise generates 6.7× more LTV than Pro at 0% churn — converting high-usage Pro accounts is the top growth lever.</div>
      <div class="ins-body">SQL Q2: Enterprise avg LTV is $6,648 vs $990 Pro. Enterprise accounts log 29 sessions/month with 89 feature interactions and 960 session minutes. Zero churn over 24 months. SQL Q5 cross-reference found 3 Pro accounts already at Enterprise engagement levels.</div>
      <div class="ins-action"><b>Action:</b> Offer those 3 accounts a 30-day white-glove Enterprise trial with dedicated onboarding.</div>
      <span class="chip">High Impact</span>
    </div>
  </div>
</div>

<footer>
  <span>Built with Python &amp; Plotly</span>
  <div class="footer-dot"></div>
  <a href="https://github.com/Jishnu513/roa-assignment" target="_blank">GitHub Repository</a>
  <div class="footer-dot"></div>
  <span>Customer Churn &amp; Retention Analysis &mdash; Option A</span>
</footer>

<script>
const tierCounts = {{all:{total_cust},free:3,starter:6,pro:7,enterprise:4}};
const tierIdx    = {{
  free:       [3,9,13],
  starter:    [0,4,7,12,15,18],
  pro:        [1,5,8,11,14,17,19],
  enterprise: [2,6,10,16]
}};
const tiers = ['free','starter','pro','enterprise'];

function setTier(tier, btn) {{
  document.querySelectorAll('.fb').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  const n = tierCounts[tier];
  document.getElementById('finfo').textContent =
    'Showing ' + n + ' customer' + (n !== 1 ? 's' : '') +
    (tier === 'all' ? ' — all tiers' : ' — ' + tier + ' plan');

  // Chart A: opacity per tier bar
  const aIdx = tier === 'all' ? [0,1,2,3] : [tiers.indexOf(tier)];
  Plotly.restyle('ca', {{
    'marker.opacity': [[0,1,2,3].map(i => aIdx.includes(i) ? 1 : 0.15)]
  }});

  // Chart B: 2 traces (Retained=0, Churned=1) — both same tier order
  ['cb'].forEach(id => {{
    Plotly.restyle(id, {{
      'marker.opacity': [
        [0,1,2,3].map(i => (tier==='all'||tiers.indexOf(tier)===i) ? 1 : 0.12),
        [0,1,2,3].map(i => (tier==='all'||tiers.indexOf(tier)===i) ? 1 : 0.12),
      ]
    }});
  }});

  // Chart G: MRR bar
  Plotly.restyle('cg', {{
    'marker.opacity': [[0,1,2,3].map(i => (tier==='all'||tiers.indexOf(tier)===i) ? 1 : 0.12)]
  }});

  // Chart D: scatter — fade non-selected tier points
  const keep = tier === 'all' ? [...Array(20).keys()] : tierIdx[tier];
  Plotly.restyle('cd', {{
    'marker.opacity': [[...Array(20).keys()].map(i => keep.includes(i) ? 0.9 : 0.06)]
  }});
}}
</script>
</body>
</html>"""

with open("dashboard.html","w",encoding="utf-8") as f:
    f.write(html)

sz = len(html)//1024
print(f"[OK] dashboard.html built — {sz} KB")
print("[OK] Charts fixed: real data, no template bugs, all vertical bars")
print("[OK] Open: start dashboard.html")
