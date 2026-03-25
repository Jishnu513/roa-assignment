"""
ROA Assignment: Customer Churn & Retention Analysis
MongoDB Aggregation Queries (Python - PyMongo)
Focus Area: Option A - Customer Churn & Retention Analysis

Run with: python mongo_queries.py
Requires:  pip install pymongo
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
from pprint import pprint
import json

# ── Connection ──────────────────────────────────────────────
client = MongoClient("mongodb://localhost:27017/")
db     = client["roa_assignment"]

# ── Seed Collections ─────────────────────────────────────────
# Drop and recreate for a clean run
for col in ["sessions", "events", "customers_mongo"]:
    db[col].drop()

# customers_mongo: mirrors the SQL customers table in document form
customers_mongo = [
    {"_id": 1,  "name": "Alice Martin",  "tier": "starter",    "signup_date": datetime(2023,1,15),  "churned": False, "ltv": 580.00,  "country": "US"},
    {"_id": 2,  "name": "Bob Singh",     "tier": "pro",        "signup_date": datetime(2023,2,1),   "churned": True,  "ltv": 990.00,  "country": "IN"},
    {"_id": 3,  "name": "Carol White",   "tier": "enterprise", "signup_date": datetime(2022,11,20), "churned": False, "ltv": 4485.00, "country": "UK"},
    {"_id": 4,  "name": "David Lee",     "tier": "free",       "signup_date": datetime(2023,6,1),   "churned": True,  "ltv": 0.00,    "country": "AU"},
    {"_id": 5,  "name": "Eva Brown",     "tier": "starter",    "signup_date": datetime(2023,3,10),  "churned": False, "ltv": 290.00,  "country": "US"},
    {"_id": 6,  "name": "Frank Tan",     "tier": "pro",        "signup_date": datetime(2022,8,5),   "churned": True,  "ltv": 1188.00, "country": "SG"},
    {"_id": 7,  "name": "Grace Kim",     "tier": "enterprise", "signup_date": datetime(2021,5,1),   "churned": False, "ltv": 8965.00, "country": "KR"},
    {"_id": 8,  "name": "Henry Zhao",    "tier": "starter",    "signup_date": datetime(2023,7,20),  "churned": True,  "ltv": 232.00,  "country": "CN"},
    {"_id": 9,  "name": "Iris Lopez",    "tier": "pro",        "signup_date": datetime(2023,1,5),   "churned": False, "ltv": 891.00,  "country": "MX"},
    {"_id": 10, "name": "James Patel",   "tier": "free",       "signup_date": datetime(2023,9,1),   "churned": True,  "ltv": 0.00,    "country": "IN"},
    {"_id": 11, "name": "Karen Wu",      "tier": "enterprise", "signup_date": datetime(2022,3,15),  "churned": False, "ltv": 5980.00, "country": "US"},
    {"_id": 12, "name": "Leo Gonzalez",  "tier": "pro",        "signup_date": datetime(2023,4,1),   "churned": True,  "ltv": 990.00,  "country": "BR"},
    {"_id": 13, "name": "Mia Johnson",   "tier": "starter",    "signup_date": datetime(2023,5,15),  "churned": False, "ltv": 435.00,  "country": "US"},
    {"_id": 14, "name": "Noah Williams", "tier": "free",       "signup_date": datetime(2024,1,1),   "churned": False, "ltv": 0.00,    "country": "CA"},
    {"_id": 15, "name": "Olivia Scott",  "tier": "pro",        "signup_date": datetime(2022,12,1),  "churned": True,  "ltv": 594.00,  "country": "AU"},
    {"_id": 16, "name": "Peter Adams",   "tier": "starter",    "signup_date": datetime(2023,8,10),  "churned": False, "ltv": 203.00,  "country": "UK"},
    {"_id": 17, "name": "Quinn Rivera",  "tier": "enterprise", "signup_date": datetime(2021,11,1),  "churned": False, "ltv": 7168.00, "country": "US"},
    {"_id": 18, "name": "Rachel Chen",   "tier": "pro",        "signup_date": datetime(2023,2,14),  "churned": True,  "ltv": 1089.00, "country": "TW"},
    {"_id": 19, "name": "Sam Taylor",    "tier": "starter",    "signup_date": datetime(2023,10,1),  "churned": False, "ltv": 145.00,  "country": "US"},
    {"_id": 20, "name": "Tina Nguyen",   "tier": "pro",        "signup_date": datetime(2022,6,1),   "churned": False, "ltv": 2178.00, "country": "VN"},
]
db["customers_mongo"].insert_many(customers_mongo)

# sessions: one document per user session
import random
random.seed(42)
sessions = []
tiers    = {1:"starter",2:"pro",3:"enterprise",4:"free",5:"starter",6:"pro",7:"enterprise",8:"starter",9:"pro",10:"free",11:"enterprise",12:"pro",13:"starter",14:"free",15:"pro",16:"starter",17:"enterprise",18:"pro",19:"starter",20:"pro"}
features = ["dashboard","reports","export","api","alerts","integrations","settings"]
for cid in range(1, 21):
    tier = tiers[cid]
    n    = random.randint(3, 20)
    for _ in range(n):
        start   = datetime(2024,1,1) - timedelta(days=random.randint(0,90))
        dur_min = random.randint(2, 120)
        sessions.append({
            "customer_id":  cid,
            "tier":         tier,
            "session_start": start,
            "session_end":   start + timedelta(minutes=dur_min),
            "duration_mins": dur_min,
            "feature_used":  random.choice(features),
            "page_views":    random.randint(1, 30),
        })
db["sessions"].insert_many(sessions)

# events: onboarding funnel + feature events
events = []
funnel_steps = ["signup","email_verified","profile_completed","first_feature_used","invited_team","billing_setup","active"]
for cid in range(1, 21):
    tier = tiers[cid]
    # Onboarding funnel (not all customers complete all steps)
    churned = next((c["churned"] for c in customers_mongo if c["_id"] == cid), False)
    max_step = random.randint(2, len(funnel_steps)) if not churned else random.randint(1, 4)
    base = datetime(2023,1,1) + timedelta(days=random.randint(0,300))
    for i, step in enumerate(funnel_steps[:max_step]):
        events.append({
            "customer_id":  cid,
            "tier":         tier,
            "event":        step,
            "event_type":   "onboarding",
            "timestamp":    base + timedelta(hours=i*random.randint(1,24)),
            "churned":      churned,
        })
    # Daily active usage events
    for _ in range(random.randint(0, 15)):
        events.append({
            "customer_id":  cid,
            "tier":         tier,
            "event":        random.choice(["login","feature_click","report_generated","export_done"]),
            "event_type":   "usage",
            "timestamp":    datetime(2024,1,1) - timedelta(days=random.randint(0,30)),
            "churned":      churned,
        })
db["events"].insert_many(events)

print("✅ MongoDB collections seeded: customers_mongo, sessions, events\n")

# ════════════════════════════════════════════════════════════════
# Q1 — AGGREGATION PIPELINE
#    Session statistics grouped by subscription tier:
#    avg session duration, total sessions, avg page views
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("Q1 — Aggregation Pipeline: Session Stats by Tier")
print("=" * 60)

q1_pipeline = [
    {
        "$group": {
            "_id": "$tier",
            "total_sessions":      {"$sum": 1},
            "avg_duration_mins":   {"$avg": "$duration_mins"},
            "total_duration_mins": {"$sum": "$duration_mins"},
            "avg_page_views":      {"$avg": "$page_views"},
            "unique_customers":    {"$addToSet": "$customer_id"},
        }
    },
    {
        "$project": {
            "tier":                "$_id",
            "total_sessions":      1,
            "avg_duration_mins":   {"$round": ["$avg_duration_mins", 2]},
            "total_duration_mins": {"$round": ["$total_duration_mins", 2]},
            "avg_page_views":      {"$round": ["$avg_page_views", 2]},
            "unique_customers":    {"$size": "$unique_customers"},
            "_id":                 0,
        }
    },
    {"$sort": {"total_sessions": -1}},
]

q1_results = list(db["sessions"].aggregate(q1_pipeline))
pprint(q1_results)
print()


# ════════════════════════════════════════════════════════════════
# Q2 — EVENT ANALYSIS
#    Daily Active Users (DAU) and feature retention:
#    Which features kept users engaged across tiers?
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("Q2 — Event Analysis: DAU & Feature Retention by Tier")
print("=" * 60)

thirty_days_ago = datetime(2024, 1, 1) - timedelta(days=30)

q2_pipeline = [
    {"$match": {
        "event_type": "usage",
        "timestamp":  {"$gte": thirty_days_ago},
    }},
    {
        "$group": {
            "_id": {
                "tier":    "$tier",
                "feature": "$event",
            },
            "unique_daily_users": {"$addToSet": "$customer_id"},
            "event_count":        {"$sum": 1},
        }
    },
    {
        "$project": {
            "tier":              "$_id.tier",
            "feature":           "$_id.feature",
            "unique_daily_users": {"$size": "$unique_daily_users"},
            "event_count":       1,
            "_id":               0,
        }
    },
    {
        "$group": {
            "_id": "$tier",
            "features": {
                "$push": {
                    "feature":           "$feature",
                    "unique_users":      "$unique_daily_users",
                    "total_events":      "$event_count",
                }
            },
            "total_active_users": {"$sum": "$unique_daily_users"},
        }
    },
    {"$sort": {"total_active_users": -1}},
]

q2_results = list(db["events"].aggregate(q2_pipeline))
pprint(q2_results)
print()


# ════════════════════════════════════════════════════════════════
# Q3 — FUNNEL ANALYSIS
#    Onboarding drop-off rates at each funnel step
#    per tier (churned vs retained)
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("Q3 — Funnel Analysis: Onboarding Drop-offs by Tier")
print("=" * 60)

q3_pipeline = [
    {"$match": {"event_type": "onboarding"}},
    {
        "$group": {
            "_id": {
                "tier":    "$tier",
                "step":    "$event",
                "churned": "$churned",
            },
            "user_count": {"$addToSet": "$customer_id"},
        }
    },
    {
        "$project": {
            "tier":       "$_id.tier",
            "funnel_step":"$_id.step",
            "churned":    "$_id.churned",
            "user_count": {"$size": "$user_count"},
            "_id":        0,
        }
    },
    {"$sort": {"tier": 1, "funnel_step": 1}},
    # Group again to get side-by-side churned vs retained
    {
        "$group": {
            "_id": {
                "tier":       "$tier",
                "funnel_step":"$funnel_step",
            },
            "retained_users": {
                "$sum": {
                    "$cond": [{"$eq": ["$churned", False]}, "$user_count", 0]
                }
            },
            "churned_users": {
                "$sum": {
                    "$cond": [{"$eq": ["$churned", True]}, "$user_count", 0]
                }
            },
        }
    },
    {
        "$project": {
            "tier":           "$_id.tier",
            "funnel_step":    "$_id.funnel_step",
            "retained_users": 1,
            "churned_users":  1,
            "total_users":    {"$add": ["$retained_users", "$churned_users"]},
            "_id":            0,
        }
    },
    {"$sort": {"tier": 1, "total_users": -1}},
]

q3_results = list(db["events"].aggregate(q3_pipeline))
pprint(q3_results)
print()


# ════════════════════════════════════════════════════════════════
# Q4 — CROSS-REFERENCE
#    Free-tier upsell targets: free-tier customers with
#    high engagement (session duration > avg) who haven't churned
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("Q4 — Cross-Reference: Free-Tier Upsell Targets")
print("=" * 60)

# Stage 1: Compute avg session duration across ALL customers
avg_pipeline = [
    {"$group": {"_id": None, "global_avg_duration": {"$avg": "$duration_mins"}}}
]
avg_result = list(db["sessions"].aggregate(avg_pipeline))
global_avg = avg_result[0]["global_avg_duration"] if avg_result else 30

q4_pipeline = [
    # Step 1: Get per-customer session stats
    {
        "$group": {
            "_id":              "$customer_id",
            "avg_session_mins": {"$avg": "$duration_mins"},
            "total_sessions":   {"$sum": 1},
            "total_page_views": {"$sum": "$page_views"},
        }
    },
    # Step 2: Join with customers_mongo to filter free-tier, non-churned
    {
        "$lookup": {
            "from":         "customers_mongo",
            "localField":   "_id",
            "foreignField": "_id",
            "as":           "customer_info",
        }
    },
    {"$unwind": "$customer_info"},
    # Step 3: Filter only free-tier, not churned, above-avg engagement
    {
        "$match": {
            "customer_info.tier":    "free",
            "customer_info.churned": False,
            "avg_session_mins":      {"$gte": global_avg},
        }
    },
    # Step 4: Shape the output
    {
        "$project": {
            "customer_id":      "$_id",
            "name":             "$customer_info.name",
            "country":          "$customer_info.country",
            "avg_session_mins": {"$round": ["$avg_session_mins", 2]},
            "total_sessions":   1,
            "total_page_views": 1,
            "ltv":              "$customer_info.ltv",
            "upsell_priority":  {
                "$switch": {
                    "branches": [
                        {"case": {"$gte": ["$avg_session_mins", global_avg * 1.5]}, "then": "High"},
                        {"case": {"$gte": ["$avg_session_mins", global_avg]},        "then": "Medium"},
                    ],
                    "default": "Low"
                }
            },
            "_id": 0,
        }
    },
    {"$sort": {"avg_session_mins": -1}},
]

q4_results = list(db["sessions"].aggregate(q4_pipeline))
if q4_results:
    pprint(q4_results)
else:
    print(f"(No free-tier customers above avg session duration of {global_avg:.1f} min — try adjusting seed data)")
print()

print("✅ All 4 MongoDB queries complete.")
client.close()
