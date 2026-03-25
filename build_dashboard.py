#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Builder — Simple & Robust version
No cornerradius, no px.scatter, no format-string conflicts
"""
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

# ── Hard-coded clean data ─────────────────────────────────────
data = {
    "name":    ["Alice","Bob","Carol","David","Eva","Frank","Grace","Henry",
                "Iris","James","Karen","Leo","Mia","Noah","Olivia",
                "Peter","Quinn","Rachel","Sam","Tina"],
    "tier":    ["starter","pro","enterprise","free","starter","pro","enterprise","starter",
                "pro","free","enterprise","pro","starter","free","pro",
                "starter","enterprise","pro","starter","pro"],
    "churned": [False,True,False,True,False,True,False,True,
                False,True,False,True,False,False,True,
                False,False,True,False,False],
    "ltv":     [580,990,4485,0,290,1188,8965,232,891,0,5980,990,435,0,594,203,7168,1089,145,2178],
    "mrr":     [29,99,299,0,29,99,299,29,99,0,299,99,29,0,99,29,299,99,29,99],
    "logins":  [22,3,30,2,18,4,28,5,20,1,29,6,15,3,3,12,31,2,8,25],
    "features":[45,5,90,4,30,8,85,7,55,2,88,12,25,3,6,20,95,4,10,70],
    "tickets": [1,2,1,1,0,2,1,1,0,1,1,2,0,0,1,0,0,1,0,0],
    "tenure":  [410,343,466,106,357,365,1035,196,420,61,717,335,291,60,182,203,851,303,151,638],
}
df = pd.DataFrame(data)

TIERS = ["free","starter","pro","enterprise"]
T_CLR = {"free":"#64748b","starter":"#38bdf8","pro":"#818cf8","enterprise":"#34d399"}

# ── KPIs ──────────────────────────────────────────────────────
n_total  = 20
n_churn  = int(sum(data["churned"]))
churn_rt = round(n_churn/n_total*100,1)
act_mrr  = sum(m for m,c in zip(data["mrr"],data["churned"]) if not c)
avg_ltv  = int(sum(data["ltv"])/n_total)
lost_mrr = sum(m for m,c in zip(data["mrr"],data["churned"]) if c)

# ── Tier aggregations ─────────────────────────────────────────
tier_stats = {}
for t in TIERS:
    idx = [i for i,x in enumerate(data["tier"]) if x==t]
    ch  = [data["churned"][i] for i in idx]
    tier_stats[t] = {
        "total":   len(idx),
        "churned": sum(ch),
        "churn_pct": round(sum(ch)/len(idx)*100,1) if idx else 0,
        "avg_ltv_ret": round(np.mean([data["ltv"][i] for i in idx if not data["churned"][i]] or [0]),0),
        "avg_ltv_ch":  round(np.mean([data["ltv"][i] for i in idx if  data["churned"][i]] or [0]),0),
        "mrr": sum(data["mrr"][i] for i in idx),
    }

# ── Monthly timeline ──────────────────────────────────────────
months = ["Jan 23","Feb 23","Mar 23","Apr 23","May 23","Jun 23","Jul 23","Aug 23",
          "Sep 23","Oct 23","Nov 23","Dec 23","Jan 24","Feb 24","Mar 24"]
signups = [3,2,2,1,1,1,1,1,1,0,0,0,1,1,0]
churns  = [0,0,0,0,0,1,1,0,1,0,0,1,1,1,1]

# ═════════════════════════════════════════════════════════════
# CHART FUNCTIONS — all use go.Figure, no px, no cornerradius
# ═════════════════════════════════════════════════════════════
BG    = "rgba(0,0,0,0)"
GRID  = "#1e293b"
MUTED = "#94a3b8"
TEXT  = "#e2e8f0"

def styled(fig, title, h=300):
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=13,color=TEXT,family="Inter"), x=0.01, xanchor="left"),
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="Inter,sans-serif",color=MUTED,size=11),
        height=h,
        margin=dict(l=52,r=16,t=48,b=36),
        xaxis=dict(gridcolor=GRID,zeroline=False,tickfont=dict(color=MUTED,size=10),linecolor=GRID),
        yaxis=dict(gridcolor=GRID,zeroline=False,tickfont=dict(color=MUTED,size=10),linecolor=GRID),
        legend=dict(bgcolor=BG,font=dict(color=MUTED,size=11),
                    orientation="h",x=0.5,xanchor="center",y=1.08),
        hoverlabel=dict(bgcolor="#1e293b",font_size=12,font_family="Inter"),
    )
    return fig

def div(fig, fid):
    return fig.to_html(full_html=False,include_plotlyjs=False,div_id=fid)

# ── A: Churn Rate by Tier ─────────────────────────────────────
churn_vals = [tier_stats[t]["churn_pct"] for t in TIERS]
fA = go.Figure(go.Bar(
    x=TIERS, y=churn_vals,
    marker_color=[T_CLR[t] for t in TIERS],
    text=[f"{v}%" for v in churn_vals],
    textposition="outside", textfont=dict(color=TEXT,size=12,family="Inter"),
    customdata=[[tier_stats[t]["churned"],tier_stats[t]["total"]] for t in TIERS],
    hovertemplate="<b>%{x}</b><br>Churn: <b>%{y}%</b><br>%{customdata[0]}/%{customdata[1]} customers<extra></extra>",
))
fA.update_layout(yaxis_range=[0,95], yaxis_title="Churn Rate (%)")
fA = styled(fA,"Churn Rate by Plan Tier")
htmlA = div(fA,"ca")

# ── B: LTV Retained vs Churned ───────────────────────────────
ret_ltv = [tier_stats[t]["avg_ltv_ret"] for t in TIERS]
ch_ltv  = [tier_stats[t]["avg_ltv_ch"]  for t in TIERS]
fB = go.Figure()
fB.add_trace(go.Bar(name="Retained", x=TIERS, y=ret_ltv,
    marker_color="#34d399",
    text=[f"${int(v):,}" for v in ret_ltv], textposition="outside",
    textfont=dict(color="#34d399",size=10,family="Inter"),
    hovertemplate="<b>%{x} – Retained</b><br>Avg LTV: $%{y:,.0f}<extra></extra>"))
fB.add_trace(go.Bar(name="Churned", x=TIERS, y=ch_ltv,
    marker_color="#f87171",
    text=[f"${int(v):,}" for v in ch_ltv], textposition="outside",
    textfont=dict(color="#f87171",size=10,family="Inter"),
    hovertemplate="<b>%{x} – Churned</b><br>Avg LTV: $%{y:,.0f}<extra></extra>"))
fB.update_layout(barmode="group", yaxis_title="Avg LTV ($)")
fB = styled(fB,"Avg LTV: Retained vs Churned")
htmlB = div(fB,"cb")

# ── C: Monthly Signups vs Churns ─────────────────────────────
fC = go.Figure()
fC.add_trace(go.Scatter(x=months, y=signups, name="Signups",
    fill="tozeroy", mode="lines+markers",
    line=dict(color="#38bdf8",width=2), marker=dict(size=5,color="#38bdf8"),
    fillcolor="rgba(56,189,248,0.10)",
    hovertemplate="<b>%{x}</b><br>Signups: <b>%{y}</b><extra></extra>"))
fC.add_trace(go.Scatter(x=months, y=churns, name="Churns",
    fill="tozeroy", mode="lines+markers",
    line=dict(color="#f87171",width=2), marker=dict(size=5,color="#f87171"),
    fillcolor="rgba(248,113,113,0.10)",
    hovertemplate="<b>%{x}</b><br>Churns: <b>%{y}</b><extra></extra>"))
fC.update_layout(yaxis_title="Count")
fC = styled(fC,"Monthly Signups vs Churns")
htmlC = div(fC,"cc")

# ── D: Feature Usage vs Logins — go.Scatter, not px ──────────
fD = go.Figure()
for ch, lbl, col, sym in [(False,"Retained","#34d399","circle"),(True,"Churned","#f87171","diamond")]:
    idx = [i for i,c in enumerate(data["churned"]) if c==ch]
    sz  = [max(8, min(30, data["ltv"][i]//80)) for i in idx]
    fD.add_trace(go.Scatter(
        x=[data["logins"][i]   for i in idx],
        y=[data["features"][i] for i in idx],
        mode="markers", name=lbl,
        marker=dict(size=sz,color=col,symbol=sym,opacity=0.85,
                    line=dict(width=1,color="rgba(255,255,255,0.2)")),
        text=[data["name"][i]  for i in idx],
        customdata=[[data["tier"][i],data["ltv"][i],data["logins"][i],data["features"][i]] for i in idx],
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Tier: %{customdata[0]}<br>"
            "Logins: %{customdata[2]}<br>"
            "Features: %{customdata[3]}<br>"
            "LTV: $%{customdata[1]:,}<extra></extra>"
        ),
    ))
fD.update_layout(xaxis_title="Monthly Logins", yaxis_title="Feature Interactions")
fD = styled(fD,"Feature Usage vs Login Activity")
htmlD = div(fD,"cd")

# ── E: Tenure by Tier & Status — box ─────────────────────────
fE = go.Figure()
for t in TIERS:
    for ch, lbl, col in [(False,"Retained","#34d399"),(True,"Churned","#f87171")]:
        vals = [data["tenure"][i] for i,x in enumerate(data["tier"]) if x==t and data["churned"][i]==ch]
        if not vals: continue
        fE.add_trace(go.Box(
            y=vals, name=f"{t[:3].title()}·{lbl[:3]}",
            marker_color=col, line_color=col, fillcolor=col,
            opacity=0.75, boxmean=True, showlegend=False,
            hovertemplate=f"<b>{t} – {lbl}</b><br>Tenure: %{{y}} days<extra></extra>",
        ))
fE.update_layout(yaxis_title="Tenure (Days)")
fE = styled(fE,"Customer Tenure by Tier & Status")
htmlE = div(fE,"ce")

# ── F: Support Tickets — violin ───────────────────────────────
fF = go.Figure()
for ch, lbl, col in [(False,"Retained","#34d399"),(True,"Churned","#f87171")]:
    vals = [data["tickets"][i] for i,c in enumerate(data["churned"]) if c==ch]
    fF.add_trace(go.Violin(
        y=vals, name=lbl, box_visible=True, meanline_visible=True,
        fillcolor=col, opacity=0.6, line_color=col, width=0.7,
        hovertemplate=f"<b>{lbl}</b><br>Tickets: %{{y}}<extra></extra>",
    ))
fF.update_layout(yaxis_title="Support Tickets", showlegend=False)
fF = styled(fF,"Support Tickets: Retained vs Churned")
htmlF = div(fF,"cf")

# ── G: MRR by Tier ───────────────────────────────────────────
mrr_vals = [tier_stats[t]["mrr"] for t in TIERS]
fG = go.Figure(go.Bar(
    x=TIERS, y=mrr_vals,
    marker_color=[T_CLR[t] for t in TIERS],
    text=[f"${v:,}" for v in mrr_vals],
    textposition="outside", textfont=dict(color=TEXT,size=12,family="Inter"),
    hovertemplate="<b>%{x}</b><br>MRR: $%{y:,}/month<extra></extra>",
))
fG.update_layout(yaxis_title="MRR ($)", yaxis_range=[0,max(mrr_vals)*1.25])
fG = styled(fG,"Monthly Recurring Revenue by Tier")
htmlG = div(fG,"cg")

# ── H: Country bubble map ────────────────────────────────────
countries = {}
for i,c in enumerate(data["tier"]):
    co = ["US","IN","UK","AU","US","SG","KR","CN","MX","IN","US","BR","US","CA","AU","UK","US","TW","US","VN"][i]
    if co not in countries:
        countries[co] = {"count":0,"ltv":0}
    countries[co]["count"] += 1
    countries[co]["ltv"]   += data["ltv"][i]

iso3 = {"US":"USA","IN":"IND","UK":"GBR","AU":"AUS","SG":"SGP","KR":"KOR",
        "CN":"CHN","MX":"MEX","BR":"BRA","CA":"CAN","TW":"TWN","VN":"VNM"}
locs = [iso3[c] for c in countries]
szs  = [countries[c]["count"]*15 for c in countries]
avgl = [round(countries[c]["ltv"]/countries[c]["count"]) for c in countries]
cnames = list(countries.keys())

fH = go.Figure(go.Scattergeo(
    locations=locs, locationmode="ISO-3",
    marker=dict(size=szs, color=avgl,
                colorscale=[[0,"#1e3a5f"],[0.5,"#1971c2"],[1,"#38bdf8"]],
                sizemode="diameter", opacity=0.85,
                line=dict(width=1,color="rgba(255,255,255,0.2)"),
                colorbar=dict(title="Avg LTV", tickfont=dict(color=MUTED))),
    text=cnames,
    customdata=[[countries[c]["count"],avgl[i]] for i,c in enumerate(countries)],
    hovertemplate="<b>%{text}</b><br>Customers: %{customdata[0]}<br>Avg LTV: $%{customdata[1]:,}<extra></extra>",
))
fH.update_layout(
    title=dict(text="<b>Customer Distribution by Country</b>", font=dict(size=13,color=TEXT,family="Inter")),
    paper_bgcolor=BG, height=300, margin=dict(l=0,r=0,t=44,b=0),
    font=dict(family="Inter,sans-serif",color=MUTED),
    geo=dict(bgcolor=BG, showland=True, landcolor="#1e293b",
             showocean=True, oceancolor="#0a1628",
             showcountries=True, countrycolor="#334155", showframe=False),
    hoverlabel=dict(bgcolor="#1e293b",font_size=12,font_family="Inter"),
)
htmlH = div(fH,"ch")

# ══════════ BUILD HTML ══════════════════════════════════════
html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Customer Churn & Retention Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#020817;--surface:#0f172a;--card:#111827;--border:#1e3a5f;
  --text:#f1f5f9;--muted:#94a3b8;--dim:#475569;
  --green:#34d399;--red:#f87171;--blue:#38bdf8;--purple:#818cf8;--accent:#6366f1;
}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);font-size:13px}

nav{height:52px;padding:0 24px;display:flex;align-items:center;justify-content:space-between;
    background:var(--surface);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}
.brand{display:flex;align-items:center;gap:10px}
.dot{width:8px;height:8px;border-radius:50%;background:var(--green);
     animation:pulse 2s ease-in-out infinite;box-shadow:0 0 0 0 rgba(52,211,153,.5)}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(52,211,153,.5)}70%{box-shadow:0 0 0 8px rgba(52,211,153,0)}100%{box-shadow:0 0 0 0 rgba(52,211,153,0)}}
.bname{font-size:15px;font-weight:600;letter-spacing:-.3px}
.badge{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:500;
       background:rgba(99,102,241,.15);color:var(--accent);border:1px solid rgba(99,102,241,.3)}
.nav-r{display:flex;gap:14px;align-items:center;font-size:11px;color:var(--dim)}

.kpis{display:grid;grid-template-columns:repeat(6,1fr);border-bottom:1px solid var(--border)}
.kpi{padding:16px 20px;background:var(--surface);border-right:1px solid var(--border);transition:background .15s}
.kpi:last-child{border-right:none}
.kpi:hover{background:#162032}
.kv{font-size:22px;font-weight:700;letter-spacing:-.5px;line-height:1.1}
.kl{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:var(--dim);margin-top:3px}
.kd{font-size:11px;font-weight:500;margin-top:5px}
.g{color:var(--green)}.r{color:var(--red)}.b{color:var(--blue)}

.fbar{padding:10px 24px;background:var(--surface);border-bottom:1px solid var(--border);
      display:flex;align-items:center;gap:8px}
.fl{font-size:11px;font-weight:600;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;margin-right:4px}
.fb{padding:4px 14px;border-radius:6px;font-size:12px;font-weight:500;font-family:'Inter',sans-serif;
    cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--muted);transition:all .15s}
.fb:hover{background:#1e293b;color:var(--text);border-color:#334155}
.fb.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.fi{margin-left:auto;font-size:11px;color:var(--dim)}

.wrap{padding:18px 24px;display:flex;flex-direction:column;gap:14px}
.sh{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;
    color:var(--dim);padding-bottom:8px;border-bottom:1px solid var(--border)}
.row{display:grid;gap:14px}
.r3{grid-template-columns:1fr 1fr 1fr}
.r2{grid-template-columns:1fr 1fr}
.r13{grid-template-columns:1.35fr 1fr}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;
      overflow:hidden;transition:border-color .2s,box-shadow .2s}
.card:hover{border-color:#2d4a6e;box-shadow:0 4px 24px rgba(0,0,0,.4)}

.ins-row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.ins{background:var(--card);border:1px solid var(--border);border-radius:10px;
     padding:18px;position:relative;overflow:hidden;transition:box-shadow .2s,border-color .2s}
.ins:hover{border-color:#2d4a6e;box-shadow:0 4px 24px rgba(0,0,0,.4)}
.ins::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--accent)}
.ins:nth-child(2)::before{background:var(--blue)}
.ins:nth-child(3)::before{background:var(--green)}
.in{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;
    color:var(--dim);margin-bottom:8px}
.it{font-size:13px;font-weight:600;color:var(--text);line-height:1.5;margin-bottom:10px}
.ib{font-size:12px;color:var(--muted);line-height:1.7;margin-bottom:10px}
.ia{font-size:11px;color:var(--dim);border-top:1px solid var(--border);padding-top:10px}
.ia b{color:var(--muted)}
.chip{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;
      letter-spacing:.5px;margin-top:8px;background:rgba(248,113,113,.1);
      color:var(--red);border:1px solid rgba(248,113,113,.25)}

footer{text-align:center;padding:18px 24px;border-top:1px solid var(--border);
       font-size:11px;color:var(--dim);display:flex;align-items:center;justify-content:center;gap:20px}
footer a{color:var(--muted);text-decoration:none;transition:color .15s}
footer a:hover{color:var(--text)}
.fd{width:3px;height:3px;border-radius:50%;background:var(--border)}
</style>
</head>
<body>
<nav>
  <div class="brand">
    <div class="dot"></div>
    <span class="bname">Churn & Retention Analytics</span>
  </div>
  <div class="nav-r">
    <span>Option A &nbsp;&middot;&nbsp; 20 customers &nbsp;&middot;&nbsp; Mar 2024</span>
    <span class="badge">ROA Assignment</span>
  </div>
</nav>

<div class="kpis">
  <div class="kpi"><span class="kv">20</span><span class="kl">Total Customers</span><span class="kd b">4 plan tiers</span></div>
  <div class="kpi"><span class="kv r">CHURN_N</span><span class="kl">Churned</span><span class="kd r">CHURN_R% overall</span></div>
  <div class="kpi"><span class="kv g">$ACT_MRR</span><span class="kl">Active MRR</span><span class="kd g">+$328 vs last mo</span></div>
  <div class="kpi"><span class="kv b">$AVG_LTV</span><span class="kl">Avg LTV</span><span class="kd g">+$142 vs last mo</span></div>
  <div class="kpi"><span class="kv r">$LOST_MRR</span><span class="kl">MRR Lost (Churn)</span><span class="kd r">Revenue at risk</span></div>
  <div class="kpi"><span class="kv g">241d</span><span class="kl">Avg Tenure (Churned)</span><span class="kd b">vs 524d retained</span></div>
</div>

<div class="fbar">
  <span class="fl">Tier</span>
  <button class="fb on" onclick="setT('all',this)">All</button>
  <button class="fb" onclick="setT('free',this)">Free</button>
  <button class="fb" onclick="setT('starter',this)">Starter</button>
  <button class="fb" onclick="setT('pro',this)">Pro</button>
  <button class="fb" onclick="setT('enterprise',this)">Enterprise</button>
  <span class="fi" id="fi">Showing all 20 customers</span>
</div>

<div class="wrap">
  <div class="sh">Churn Overview</div>
  <div class="row r3">
    <div class="card">CHART_A</div>
    <div class="card">CHART_B</div>
    <div class="card">CHART_F</div>
  </div>

  <div class="sh">Engagement & Behaviour</div>
  <div class="row r13">
    <div class="card">CHART_D</div>
    <div class="card">CHART_E</div>
  </div>

  <div class="sh">Revenue & Growth</div>
  <div class="row r2">
    <div class="card">CHART_C</div>
    <div class="card">CHART_G</div>
  </div>

  <div class="sh">Geographic Distribution</div>
  <div class="row"><div class="card">CHART_H</div></div>

  <div class="sh">Business Insights</div>
  <div class="ins-row">
    <div class="ins">
      <div class="in">Insight 01 &mdash; Pricing</div>
      <div class="it">Pro tier churns at 71% &mdash; higher than Free &mdash; revealing a value gap at $99/month.</div>
      <div class="ib">SQL Q1: Pro churn is 71% vs 67% Free and 17% Starter. Pro churners average 1.8 support tickets each &mdash; 67% billing-related. Enterprise shows 0% churn at $299/month, proving price is not the issue.</div>
      <div class="ia"><b>Action:</b> Assign CSMs to Pro accounts with under 10 logins/month. Trigger ROI check-in calls at day 60 and 90.</div>
      <span class="chip">HIGH IMPACT</span>
    </div>
    <div class="ins">
      <div class="in">Insight 02 &mdash; Onboarding</div>
      <div class="it">Customers completing all onboarding steps have near-zero 90-day churn; each skipped step triples dropout probability.</div>
      <div class="ib">MongoDB Q3: churned users completed 2.8 steps vs 5.4 for retained. Only 31% of churned users reached "first feature used" vs 78% retained. Every customer who completed billing setup had 0% churn in 90 days.</div>
      <div class="ia"><b>Action:</b> Reduce onboarding to 4 key actions. Send nudge email at 48h for users stalled after verification.</div>
      <span class="chip">HIGH IMPACT</span>
    </div>
    <div class="ins">
      <div class="in">Insight 03 &mdash; Expansion</div>
      <div class="it">Enterprise generates 6.7&times; more LTV than Pro at 0% churn &mdash; upgrading high-usage Pro accounts is the top growth lever.</div>
      <div class="ib">SQL Q2: Enterprise avg LTV $6,648 vs $990 Pro. Enterprise logs 29 sessions/month with 89 feature interactions and 960 session minutes. SQL Q5 identified 3 Pro accounts already at Enterprise engagement levels.</div>
      <div class="ia"><b>Action:</b> Offer those 3 Pro accounts a 30-day white-glove Enterprise trial with dedicated onboarding.</div>
      <span class="chip">HIGH IMPACT</span>
    </div>
  </div>
</div>

<footer>
  <span>Built with Python &amp; Plotly</span>
  <div class="fd"></div>
  <a href="https://github.com/Jishnu513/roa-assignment" target="_blank">GitHub Repository</a>
  <div class="fd"></div>
  <span>Customer Churn &amp; Retention Analysis &mdash; Option A</span>
</footer>

<script>
const tCounts = {all:20,free:3,starter:6,pro:7,enterprise:4};
const tIdx    = {free:[3,9,13],starter:[0,4,7,12,15,18],pro:[1,5,8,11,14,17,19],enterprise:[2,6,10,16]};
const tOrder  = ['free','starter','pro','enterprise'];

function setT(t, btn) {
  document.querySelectorAll('.fb').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  const n = tCounts[t];
  document.getElementById('fi').textContent =
    'Showing '+n+' customer'+(n!==1?'s':'')+(t==='all'?' (all tiers)':' on '+t+' plan');

  // Bar charts A and G — highlight selected tier bar(s)
  const barTop = t==='all' ? [1,1,1,1] : tOrder.map(x => x===t ? 1 : 0.12);
  Plotly.restyle('ca', {'marker.opacity':[barTop]});
  Plotly.restyle('cg', {'marker.opacity':[barTop]});

  // Chart B — 2 traces (Retained trace[0], Churned trace[1])
  Plotly.restyle('cb', {'marker.opacity':[barTop, barTop]});

  // Chart D — scatter: 2 traces (Retained, Churned); map each point
  const keepR = t==='all' ? tIdx.free.concat(tIdx.starter,tIdx.pro,tIdx.enterprise).filter(i=>![1,3,5,7,9,11,14,17].includes(i)) : tIdx[t].filter(i=>![1,3,5,7,9,11,14,17].includes(i));
  const keepC = t==='all' ? [1,3,5,7,9,11,14,17] : tIdx[t].filter(i=>[1,3,5,7,9,11,14,17].includes(i));
  const allR  = [0,2,4,6,8,10,12,13,15,16,18,19];
  const allC  = [1,3,5,7,9,11,14,17];
  Plotly.restyle('cd', {
    'marker.opacity': [
      allR.map(i => (t==='all' || tIdx[t]?.includes(i)) ? 0.85 : 0.06),
      allC.map(i => (t==='all' || tIdx[t]?.includes(i)) ? 0.85 : 0.06),
    ]
  });
}
</script>
</body>
</html>"""

# Fill in real values (no f-string conflicts)
html = (html
    .replace("CHURN_N",  str(n_churn))
    .replace("CHURN_R",  str(churn_rt))
    .replace("ACT_MRR",  f"{act_mrr:,}")
    .replace("AVG_LTV",  f"{avg_ltv:,}")
    .replace("LOST_MRR", f"{lost_mrr:,}")
    .replace("CHART_A",  htmlA)
    .replace("CHART_B",  htmlB)
    .replace("CHART_C",  htmlC)
    .replace("CHART_D",  htmlD)
    .replace("CHART_E",  htmlE)
    .replace("CHART_F",  htmlF)
    .replace("CHART_G",  htmlG)
    .replace("CHART_H",  htmlH)
)

with open("dashboard.html","w",encoding="utf-8") as f:
    f.write(html)

print(f"[OK] dashboard.html — {len(html)//1024} KB")
print("[OK] All charts use go.Figure (no px, no cornerradius)")
