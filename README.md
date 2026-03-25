# Customer Churn & Retention Analysis
### ROA Assignment — Option A

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-View%20Now-6366f1?style=for-the-badge&logo=plotly&logoColor=white)](https://jishnu513.github.io/roa-assignment/dashboard.html)
[![SQL](https://img.shields.io/badge/PostgreSQL-5%20Queries-336791?style=for-the-badge&logo=postgresql&logoColor=white)](queries.sql)
[![MongoDB](https://img.shields.io/badge/MongoDB-4%20Pipelines-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](mongo_queries.js)
[![Python](https://img.shields.io/badge/Python-Analysis%20Notebook-3776AB?style=for-the-badge&logo=python&logoColor=white)](data_wrangling.ipynb)

---

## 🔗 Interactive Dashboard (Click to Open)

> **[https://jishnu513.github.io/roa-assignment/dashboard.html](https://jishnu513.github.io/roa-assignment/dashboard.html)**

The dashboard features:
- 6 live KPI cards (Churn Rate, Active MRR, Avg LTV, MRR at Risk)
- 8 interactive Plotly charts with hover tooltips
- Tier filter buttons (Free / Starter / Pro / Enterprise)
- Geographic customer map
- Top 3 business insights with supporting evidence

---

## 📁 File Structure

| File | Description |
|------|-------------|
| [`queries.sql`](queries.sql) | PostgreSQL schema + Q1–Q5 queries (Joins, Window Functions, CTEs, Time Series, Duplicate Detection) |
| [`mongo_queries.js`](mongo_queries.js) | MongoDB shell — Q1–Q4 aggregation pipelines |
| [`mongo_queries.py`](mongo_queries.py) | Python/PyMongo version of MongoDB queries |
| [`data_wrangling.ipynb`](data_wrangling.ipynb) | Jupyter Notebook — cleaning, hypothesis testing, visualizations |
| [`data_wrangling.py`](data_wrangling.py) | Python script version of the analysis |
| [`dashboard.html`](https://jishnu513.github.io/roa-assignment/dashboard.html) | Interactive Plotly dashboard (GitHub Pages) |
| [`customers_dataset.csv`](customers_dataset.csv) | Dataset used for analysis |
| [`churn_analysis_dashboard.png`](churn_analysis_dashboard.png) | Static dashboard preview |

---

## 🗄️ Database Schema (PostgreSQL)

```sql
plans            → plan_id, plan_name, tier, monthly_price
customers        → customer_id, name, email, plan_id, signup_date, churn_date, country, ltv
subscriptions    → subscription_id, customer_id, plan_id, start_date, end_date, mrr, status
support_tickets  → ticket_id, customer_id, created_at, category, severity
usage_metrics    → metric_id, customer_id, month, login_count, feature_usage, session_mins
```

---

## 🔍 SQL Queries

| Query | Type | What It Answers |
|-------|------|-----------------|
| Q1 | JOINs + Aggregation | Avg LTV, MRR, and ticket rate per plan tier |
| Q2 | Window Functions | LTV ranking & tier comparison using RANK / AVG OVER |
| Q3 | CTEs + Subqueries | Downgrade events correlated with pre-churn tickets |
| Q4 | Time Series | MoM signup growth & rolling 3-month churn rate |
| Q5 | Advanced | Duplicate account detection by email/name proximity |

**Setup:**
```bash
psql -U postgres -c "CREATE DATABASE roa_assignment;"
psql -U postgres -d roa_assignment -f queries.sql
```

---

## 🍃 MongoDB Queries

| Query | Type | What It Answers |
|-------|------|-----------------|
| Q1 | Aggregation Pipeline | Session duration & page views by tier |
| Q2 | Event Analysis | DAU & feature engagement by tier |
| Q3 | Funnel Analysis | Onboarding drop-off rates (churned vs retained) |
| Q4 | Cross-Reference | Free-tier upsell targets by engagement score |

**Setup:**
```bash
mongosh roa_assignment mongo_queries.js
```

---

## 🧹 Data Wrangling (Python)

- **Missing values** — NULL churn_date treated as active (retained boolean flag added)
- **Outlier detection** — IQR method on LTV column
- **Hypothesis testing** — Welch's t-test on tenure (churned vs retained)
  - H0: Mean tenure equal; H1: Churned customers have shorter tenure
  - Result: t = −2.14, p = 0.048 → **Reject H0** ✓
- **6 visualizations** — churn rate, LTV distribution, tenure, feature usage, tickets, timeline

**Setup:**
```bash
pip install pandas numpy matplotlib seaborn scipy
python data_wrangling.py
```

---

## 📊 Key Insights

| # | Insight | Impact |
|---|---------|--------|
| 1 | Pro tier churns at 71% — higher than Free — value gap at $99/month | **High** |
| 2 | Customers completing all onboarding steps have near-zero 90-day churn | **High** |
| 3 | Enterprise generates 6.7× more LTV than Pro at 0% churn rate | **High** |

---

*Built with PostgreSQL · MongoDB · Python · Plotly*
