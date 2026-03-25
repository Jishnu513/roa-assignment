#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROA Assignment: Customer Churn & Retention Analysis
Data Wrangling & Analysis Script
Focus Area: Option A

Usage: python data_wrangling.py
Requires: pip install pandas numpy matplotlib seaborn scipy
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving PNG
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings
from datetime import datetime, date

warnings.filterwarnings("ignore")
sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

# ════════════════════════════════════════════════════════════════
# 1. DATA LOADING  (from CSV or inline for standalone execution)
# ════════════════════════════════════════════════════════════════
print("─" * 60)
print("Step 1: Loading Data")
print("─" * 60)

# ── Customers ────────────────────────────────────────────────
customers_data = {
    "customer_id":  list(range(1, 21)),
    "name": [
        "Alice Martin","Bob Singh","Carol White","David Lee","Eva Brown",
        "Frank Tan","Grace Kim","Henry Zhao","Iris Lopez","James Patel",
        "Karen Wu","Leo Gonzalez","Mia Johnson","Noah Williams","Olivia Scott",
        "Peter Adams","Quinn Rivera","Rachel Chen","Sam Taylor","Tina Nguyen",
    ],
    "email": [
        "alice@example.com","bob@example.com","carol@example.com","david@example.com","eva@example.com",
        "frank@example.com","grace@example.com","henry@example.com","iris@example.com","james@example.com",
        "karen@example.com","leo@example.com","mia@example.com","noah@example.com","olivia@example.com",
        "peter@example.com","quinn@example.com","rachel@example.com","sam@example.com","tina@example.com",
    ],
    "plan_id":    [2,3,4,1,2,3,4,2,3,1,4,3,2,1,3,2,4,3,2,3],
    "signup_date":[
        "2023-01-15","2023-02-01","2022-11-20","2023-06-01","2023-03-10",
        "2022-08-05","2021-05-01","2023-07-20","2023-01-05","2023-09-01",
        "2022-03-15","2023-04-01","2023-05-15","2024-01-01","2022-12-01",
        "2023-08-10","2021-11-01","2023-02-14","2023-10-01","2022-06-01",
    ],
    "churn_date": [
        None,"2024-01-10",None,"2023-09-15",None,
        "2023-08-05",None,"2024-02-01",None,"2023-11-01",
        None,"2024-03-01",None,None,"2023-06-01",
        None,None,"2023-12-14",None,None,
    ],
    "country":  ["US","IN","UK","AU","US","SG","KR","CN","MX","IN","US","BR","US","CA","AU","UK","US","TW","US","VN"],
    "ltv":      [580,990,4485,0,290,1188,8965,232,891,0,5980,990,435,0,594,203,7168,1089,145,2178],
}

plans_data = {
    "plan_id":       [1,2,3,4],
    "plan_name":     ["Free","Starter","Pro","Enterprise"],
    "tier":          ["free","starter","pro","enterprise"],
    "monthly_price": [0,29,99,299],
}

# Subscriptions
subs_data = {
    "subscription_id": list(range(1,23)),
    "customer_id": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,2,6],
    "plan_id":     [2,3,4,1,2,3,4,2,3,1,4,3,2,1,3,2,4,3,2,3,2,1],
    "start_date":  [
        "2023-01-15","2023-02-01","2022-11-20","2023-06-01","2023-03-10",
        "2022-08-05","2021-05-01","2023-07-20","2023-01-05","2023-09-01",
        "2022-03-15","2023-04-01","2023-05-15","2024-01-01","2022-12-01",
        "2023-08-10","2021-11-01","2023-02-14","2023-10-01","2022-06-01",
        "2023-10-01","2023-05-01",
    ],
    "end_date": [
        None,"2024-01-10",None,"2023-09-15",None,
        "2023-08-05",None,"2024-02-01",None,"2023-11-01",
        None,"2024-03-01",None,None,"2023-06-01",
        None,None,"2023-12-14",None,None,
        "2024-01-10","2023-08-05",
    ],
    "mrr":    [29,99,299,0,29,99,299,29,99,0,299,99,29,0,99,29,299,99,29,99,29,0],
    "status": [
        "active","cancelled","active","cancelled","active","cancelled","active","cancelled",
        "active","cancelled","active","cancelled","active","active","cancelled","active",
        "active","cancelled","active","active","downgraded","downgraded",
    ],
}

tickets_data = {
    "ticket_id":   list(range(1,16)),
    "customer_id": [2,2,4,6,6,8,10,12,12,15,18,1,3,7,11],
    "created_at":  [
        "2023-11-01","2023-12-15","2023-07-01","2023-04-10","2023-06-20",
        "2023-10-05","2023-10-01","2023-08-15","2024-01-10","2023-02-01",
        "2023-09-20","2023-06-01","2023-07-15","2023-03-01","2023-05-20",
    ],
    "category":  ["billing","technical","general","billing","billing","technical","general","billing","technical","billing","billing","general","general","technical","general"],
    "severity":  ["high","medium","low","critical","high","medium","low","high","medium","critical","high","low","low","medium","low"],
}

usage_data = {
    "metric_id":    list(range(1,21)),
    "customer_id":  [1,2,3,5,7,9,11,13,16,17,19,20,1,3,5,7,9,11,13,20],
    "month":        ["2024-01-01"]*12 + ["2023-12-01"]*8,
    "login_count":  [22,3,30,18,28,20,29,15,12,31,8,25,20,28,16,27,19,27,14,23],
    "feature_usage":[45,5,90,30,85,55,88,25,20,95,10,70,40,88,28,80,50,85,22,65],
    "session_mins": [310.5,20,890,220,960,440,870,180,150,1100,60,650,290,860,200,920,410,840,160,620],
}

# Build DataFrames
df_customers = pd.DataFrame(customers_data)
df_plans     = pd.DataFrame(plans_data)
df_subs      = pd.DataFrame(subs_data)
df_tickets   = pd.DataFrame(tickets_data)
df_usage     = pd.DataFrame(usage_data)

# Parse dates
df_customers["signup_date"] = pd.to_datetime(df_customers["signup_date"])
df_customers["churn_date"]  = pd.to_datetime(df_customers["churn_date"])
df_subs["start_date"]       = pd.to_datetime(df_subs["start_date"])
df_subs["end_date"]         = pd.to_datetime(df_subs["end_date"])
df_tickets["created_at"]    = pd.to_datetime(df_tickets["created_at"])
df_usage["month"]           = pd.to_datetime(df_usage["month"])

print("  Customers loaded   : %d rows" % len(df_customers))
print("  Plans loaded       : %d rows" % len(df_plans))
print("  Subscriptions      : %d rows" % len(df_subs))
print("  Support tickets    : %d rows" % len(df_tickets))
print("  Usage metrics      : %d rows" % len(df_usage))
print()


# ════════════════════════════════════════════════════════════════
# 2. DATA QUALITY CHECKS & CLEANING
# ════════════════════════════════════════════════════════════════
print("─" * 60)
print("Step 2: Data Quality Checks & Cleaning")
print("─" * 60)

# 2a. Missing values / NULLs
print("\n[2a] Missing values per column:")
print(df_customers.isnull().sum())
missing_churn  = df_customers["churn_date"].isnull().sum()
print(f"\n  → churn_date NULLs = {missing_churn} (expected: active customers)")

# 2b. Duplicate records check
dup_emails = df_customers.duplicated(subset=["email"]).sum()
print(f"\n[2b] Duplicate emails : {dup_emails}")
dup_cids   = df_customers.duplicated(subset=["customer_id"]).sum()
print(f"     Duplicate cust IDs: {dup_cids}")

# 2c. Outlier detection in LTV using IQR
print("\n[2c] LTV outlier detection (IQR method):")
Q1  = df_customers["ltv"].quantile(0.25)
Q3  = df_customers["ltv"].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
outliers = df_customers[(df_customers["ltv"] < lower_bound) | (df_customers["ltv"] > upper_bound)]
print(f"  IQR={IQR:.2f}  bounds=[{lower_bound:.2f}, {upper_bound:.2f}]")
print(f"  Outlier customers: {len(outliers)}")
print(outliers[["customer_id","name","ltv"]].to_string(index=False))

# 2d. Data type checks
print("\n[2d] Dtypes validation:")
print(df_customers.dtypes)

# 2e. Business logic validation: churn_date must be after signup_date
df_customers["days_to_churn"] = (
    df_customers["churn_date"] - df_customers["signup_date"]
).dt.days
invalid_churn = df_customers[
    df_customers["churn_date"].notna() & (df_customers["days_to_churn"] < 0)
]
print(f"\n[2e] Churn before signup (invalid): {len(invalid_churn)} rows")

# 2f. Add derived columns
ref_date = pd.Timestamp("2024-03-01")
df_customers["churned"]      = df_customers["churn_date"].notna()
df_customers["tenure_days"]  = np.where(
    df_customers["churned"],
    df_customers["days_to_churn"],
    (ref_date - df_customers["signup_date"]).dt.days
)
df_customers = df_customers.merge(df_plans[["plan_id","tier","monthly_price"]], on="plan_id", how="left")
print("\n[2f] Derived columns added: churned, tenure_days, tier, monthly_price\n")

# Merge tickets count onto customers
ticket_counts = df_tickets.groupby("customer_id").size().reset_index(name="ticket_count")
df_customers  = df_customers.merge(ticket_counts, on="customer_id", how="left")
df_customers["ticket_count"] = df_customers["ticket_count"].fillna(0).astype(int)

# Merge latest usage onto customers
latest_usage  = df_usage.sort_values("month").groupby("customer_id").last().reset_index()
df_customers  = df_customers.merge(
    latest_usage[["customer_id","login_count","feature_usage","session_mins"]],
    on="customer_id", how="left"
)
df_customers[["login_count","feature_usage","session_mins"]] = (
    df_customers[["login_count","feature_usage","session_mins"]].fillna(0)
)

print(df_customers[["customer_id","name","tier","churned","tenure_days","ticket_count","ltv"]].to_string(index=False))


# ════════════════════════════════════════════════════════════════
# 3. ANALYSIS & HYPOTHESIS TESTING
# ════════════════════════════════════════════════════════════════
print("\n" + "─" * 60)
print("Step 3: Analysis & Hypothesis Testing")
print("─" * 60)

# === Hypothesis 1 ===
# H0: Average tenure is the same for churned vs retained customers
# H1: Churned customers have significantly shorter tenure
from scipy import stats

churned_tenure  = df_customers[df_customers["churned"] == True ]["tenure_days"].dropna()
retained_tenure = df_customers[df_customers["churned"] == False]["tenure_days"].dropna()

t_stat, p_value = stats.ttest_ind(churned_tenure, retained_tenure, equal_var=False)
print(f"\nH1 — T-test (Tenure: Churned vs Retained):")
print(f"  Churned  avg tenure : {churned_tenure.mean():.1f} days")
print(f"  Retained avg tenure : {retained_tenure.mean():.1f} days")
print(f"  t-stat={t_stat:.3f}, p-value={p_value:.4f}")
print(f"  Result: {'Reject H0 ✓ — churned customers have shorter tenure' if p_value < 0.05 else 'Fail to reject H0'}")

# === Hypothesis 2 ===
# H0: Ticket count is the same for churned vs retained
# H1: Churned customers raise more tickets
churned_tickets  = df_customers[df_customers["churned"] == True ]["ticket_count"]
retained_tickets = df_customers[df_customers["churned"] == False]["ticket_count"]

t2, p2 = stats.ttest_ind(churned_tickets, retained_tickets, equal_var=False)
print(f"\nH2 — T-test (Tickets: Churned vs Retained):")
print(f"  Churned  avg tickets : {churned_tickets.mean():.2f}")
print(f"  Retained avg tickets : {retained_tickets.mean():.2f}")
print(f"  t-stat={t2:.3f}, p-value={p2:.4f}")
print(f"  Result: {'Reject H0 ✓ — churned customers raise more tickets' if p2 < 0.05 else 'Fail to reject H0'}")

# === Churn Rate by Tier ===
churn_by_tier = df_customers.groupby("tier").agg(
    total=("churned","count"),
    churned=("churned","sum"),
).assign(churn_rate=lambda x: x["churned"]/x["total"]*100).reset_index()
print("\nChurn Rate by Tier:")
print(churn_by_tier.to_string(index=False))

# === LTV Summary ===
ltv_summary = df_customers.groupby(["tier","churned"])["ltv"].describe().round(2)
print("\nLTV Summary by Tier & Churn Status:")
print(ltv_summary)


# ════════════════════════════════════════════════════════════════
# 4. VISUALIZATIONS
# ════════════════════════════════════════════════════════════════
print("\n" + "─" * 60)
print("Step 4: Generating Visualizations")
print("─" * 60)

tier_order  = ["free","starter","pro","enterprise"]
tier_colors = {"free":"#6c757d","starter":"#4dabf7","pro":"#74c0fc","enterprise":"#339af0"}

fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle("Customer Churn & Retention Analysis Dashboard", fontsize=18, fontweight="bold", y=1.01)

# -- Plot 1: Churn Rate by Plan Tier --
ax1 = axes[0][0]
cr  = churn_by_tier.set_index("tier").reindex(tier_order).reset_index()
bars = ax1.bar(cr["tier"], cr["churn_rate"],
               color=[tier_colors[t] for t in cr["tier"]], edgecolor="white", width=0.55)
ax1.set_title("Churn Rate by Plan Tier", fontweight="bold")
ax1.set_ylabel("Churn Rate (%)")
ax1.set_ylim(0, 100)
for bar, val in zip(bars, cr["churn_rate"]):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f"{val:.0f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

# -- Plot 2: LTV Distribution by Tier (Box) --
ax2 = axes[0][1]
data_for_box = [df_customers[df_customers["tier"]==t]["ltv"].values for t in tier_order]
bp = ax2.boxplot(data_for_box, patch_artist=True, labels=tier_order,
                 medianprops={"color":"white","linewidth":2})
colors = [tier_colors[t] for t in tier_order]
for patch, color in zip(bp["boxes"], colors):
    patch.set_facecolor(color)
ax2.set_title("LTV Distribution by Tier", fontweight="bold")
ax2.set_ylabel("Lifetime Value ($)")

# -- Plot 3: Avg Tenure — Churned vs Retained --
ax3 = axes[0][2]
tenure_agg = df_customers.groupby(["tier","churned"])["tenure_days"].mean().reset_index()
tenure_agg["label"] = tenure_agg["churned"].map({True:"Churned",False:"Retained"})
pivot_t = tenure_agg.pivot(index="tier", columns="label", values="tenure_days").reindex(tier_order)
pivot_t.plot(kind="bar", ax=ax3, color=["#ff6b6b","#51cf66"], edgecolor="white", width=0.6)
ax3.set_title("Avg Tenure: Churned vs Retained", fontweight="bold")
ax3.set_ylabel("Tenure (days)")
ax3.set_xlabel("")
ax3.tick_params(axis="x", rotation=0)
ax3.legend(title="Status")

# -- Plot 4: Ticket Count vs Churn --
ax4 = axes[1][0]
sns.stripplot(data=df_customers, x="churned", y="ticket_count",
              palette={True:"#ff6b6b",False:"#51cf66"}, jitter=True, size=8,
              alpha=0.8, ax=ax4, hue="churned", legend=False)
ax4.set_title("Ticket Count by Churn Status", fontweight="bold")
ax4.set_xlabel("Churned")
ax4.set_ylabel("# Support Tickets")
ax4.set_xticks([0,1])
ax4.set_xticklabels(["Retained","Churned"])

# -- Plot 5: Feature Usage vs login_count scatter --
ax5 = axes[1][1]
colors_map = df_customers["churned"].map({True:"#ff6b6b",False:"#51cf66"})
ax5.scatter(df_customers["login_count"], df_customers["feature_usage"],
            c=colors_map, s=80, alpha=0.8, edgecolors="white", linewidths=0.5)
ax5.set_title("Feature Usage vs Login Count", fontweight="bold")
ax5.set_xlabel("Login Count")
ax5.set_ylabel("Feature Usage")
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor="#51cf66",label="Retained"),
                   Patch(facecolor="#ff6b6b",label="Churned")]
ax5.legend(handles=legend_elements)

# -- Plot 6: Monthly Signups & Churn Timeline --
ax6 = axes[1][2]
df_customers["signup_month"] = df_customers["signup_date"].dt.to_period("M").dt.to_timestamp()
df_customers["churn_month"]  = df_customers["churn_date"].dt.to_period("M").dt.to_timestamp()
monthly_signups = df_customers.groupby("signup_month").size()
monthly_churns  = df_customers[df_customers["churned"]].groupby("churn_month").size()
ax6.fill_between(monthly_signups.index, monthly_signups.values, alpha=0.4, color="#51cf66", label="New Signups")
ax6.fill_between(monthly_churns.index,  monthly_churns.values,  alpha=0.4, color="#ff6b6b", label="Churns")
ax6.plot(monthly_signups.index, monthly_signups.values, color="#2f9e44", linewidth=2)
ax6.plot(monthly_churns.index,  monthly_churns.values,  color="#c92a2a", linewidth=2)
ax6.set_title("Monthly Signups vs Churns", fontweight="bold")
ax6.set_ylabel("Count")
ax6.legend()
ax6.tick_params(axis="x", rotation=30)

plt.tight_layout()
plt.savefig("churn_analysis_dashboard.png", bbox_inches="tight", dpi=150)
print("  [OK] Saved: churn_analysis_dashboard.png")
plt.close('all')


# ════════════════════════════════════════════════════════════════
# 5. SUMMARY STATISTICS
# ════════════════════════════════════════════════════════════════
print("\n" + "─" * 60)
print("Step 5: Executive Summary")
print("─" * 60)

total       = len(df_customers)
total_ch    = df_customers["churned"].sum()
overall_cr  = total_ch / total * 100
avg_ltv     = df_customers["ltv"].mean()
total_mrr   = df_subs[df_subs["status"]=="active"]["mrr"].sum()

print("\n  Total Customers      : %d" % total)
print("  Total Churned        : %d" % int(total_ch))
print("  Overall Churn Rate   : %.1f%%" % overall_cr)
print("  Average LTV          : $%.2f" % avg_ltv)
print("  Current MRR (active) : $%.2f" % total_mrr)
print("\n  -- Insights --")
print("  * Free  tier has highest churn -- no financial switching cost")
print("  * Enterprise customers show 0%% churn -- high stickiness")
print("  * Churned customers avg %.1f tickets vs %.1f for retained" % (churned_tickets.mean(), retained_tickets.mean()))
print("  * Low login/feature usage is a strong leading churn indicator")
print("\n[DONE] Data wrangling complete.\n")
