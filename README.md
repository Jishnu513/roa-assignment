# ROA Assignment — Customer Churn & Retention Analysis

## Focus Area: Option A — Customer Churn & Retention Analysis

---

## 📁 File Structure

```
ROA Assignment/
├── queries.sql            ← PostgreSQL schema + Q1–Q5 queries
├── mongo_queries.py       ← MongoDB Q1–Q4 aggregation pipelines
├── data_wrangling.py      ← Data cleaning, analysis & visualizations
├── churn_analysis_dashboard.png  ← Generated after running data_wrangling.py
└── README.md              ← This file
```

---

## 🗄️ Database Schema (PostgreSQL)

| Table              | Description                              |
|--------------------|------------------------------------------|
| `plans`            | Subscription tiers (Free→Enterprise)     |
| `customers`        | Customer profiles, signup/churn dates    |
| `subscriptions`    | Plan history, MRR, status changes        |
| `support_tickets`  | Helpdesk tickets with severity/category  |
| `usage_metrics`    | Monthly login/feature usage per customer |

---

## 🔍 SQL Queries (PostgreSQL)

| Query | Type               | What It Answers                                     |
|-------|--------------------|-----------------------------------------------------|
| Q1    | Joins + Aggregation | Avg LTV, MRR, and support ticket rate per plan tier |
| Q2    | Window Functions    | LTV ranking & tier comparison using RANK/AVG OVER   |
| Q3    | CTEs + Subqueries   | Downgrade events correlated with pre-churn tickets  |
| Q4    | Time Series         | MoM signup growth & rolling 3-month churn rate      |
| Q5    | Advanced            | Duplicate account detection by email/name proximity |

### Setup & Run

```bash
# 1. Start PostgreSQL and connect
psql -U postgres

# 2. Create and use a new database
CREATE DATABASE roa_assignment;
\c roa_assignment

# 3. Run the full file (schema + data + queries)
\i queries.sql
```

---

## 🍃 MongoDB Queries (Python/PyMongo)

| Query | Type                | What It Answers                                     |
|-------|---------------------|-----------------------------------------------------|
| Q1    | Aggregation Pipeline | Session duration & page views grouped by tier       |
| Q2    | Event Analysis       | Daily Active Users & feature engagement by tier     |
| Q3    | Funnel Analysis      | Onboarding drop-off rates (churned vs retained)     |
| Q4    | Cross-Reference      | Free-tier upsell targets by engagement score        |

### Setup & Run

```bash
# 1. Make sure MongoDB is running
mongod --dbpath /data/db

# 2. Install PyMongo
pip install pymongo

# 3. Run the queries
python mongo_queries.py
```

---

## 🧹 Data Wrangling Script (Python)

Covers:
- **Missing value detection** (churn_date NULLs = active customers)
- **Duplicate detection** (email + customer_id uniqueness)
- **Outlier detection** using IQR method on LTV
- **Data type validation** and business-logic checks (churn > signup)
- **Derived columns**: `churned`, `tenure_days`, `ticket_count`
- **Hypothesis Testing**:
  - H1: Churned customers have shorter tenure (Welch's t-test)
  - H2: Churned customers raise more support tickets (Welch's t-test)
- **6-panel visualization dashboard** saved as PNG

### Setup & Run

```bash
# Install dependencies
pip install pandas numpy matplotlib seaborn scipy

# Run
python data_wrangling.py
```

---

## 📊 Dashboard

Built with Matplotlib/Seaborn — outputs `churn_analysis_dashboard.png`:
1. Churn Rate by Plan Tier (bar chart)
2. LTV Distribution by Tier (boxplot)
3. Avg Tenure: Churned vs Retained (grouped bar)
4. Ticket Count by Churn Status (strip plot)
5. Feature Usage vs Login Count (scatter)
6. Monthly Signups vs Churns (area chart)

For **Tableau / Power BI**, connect these Python DataFrames as CSV exports or connect directly to PostgreSQL.

---

## 🔑 Key Insights

| Insight | Finding |
|---------|---------|
| Churn leader | Free-tier customers churn most (no switching cost) |
| Most sticky | Enterprise — 0% churn rate |
| Churn signal | Churned customers avg 2× more support tickets |
| Engagement | Low login count = strong leading indicator of churn |
| Revenue risk | Mid-tier (Pro) carries the most churn-related MRR loss |

---

## ⏱️ Time Spent
~3–4 hours
