// ============================================================
// ROA Assignment: Customer Churn & Retention Analysis
// MongoDB Aggregation Queries — Shell Script (.js)
// Run with: mongosh roa_assignment mongo_queries.js
// ============================================================

// ── Helper: pretty print with label ──────────────────────────
function printSection(title, cursor) {
  print("\n" + "=".repeat(60));
  print(title);
  print("=".repeat(60));
  cursor.forEach(doc => printjson(doc));
}

// ── Seed data (run once) ─────────────────────────────────────
db.customers_mongo.drop();
db.sessions.drop();
db.events.drop();

db.customers_mongo.insertMany([
  { _id: 1,  name: "Alice Martin",  tier: "starter",    signup_date: new Date("2023-01-15"), churned: false, ltv: 580.00,  country: "US" },
  { _id: 2,  name: "Bob Singh",     tier: "pro",        signup_date: new Date("2023-02-01"), churned: true,  ltv: 990.00,  country: "IN" },
  { _id: 3,  name: "Carol White",   tier: "enterprise", signup_date: new Date("2022-11-20"), churned: false, ltv: 4485.00, country: "UK" },
  { _id: 4,  name: "David Lee",     tier: "free",       signup_date: new Date("2023-06-01"), churned: true,  ltv: 0.00,    country: "AU" },
  { _id: 5,  name: "Eva Brown",     tier: "starter",    signup_date: new Date("2023-03-10"), churned: false, ltv: 290.00,  country: "US" },
  { _id: 6,  name: "Frank Tan",     tier: "pro",        signup_date: new Date("2022-08-05"), churned: true,  ltv: 1188.00, country: "SG" },
  { _id: 7,  name: "Grace Kim",     tier: "enterprise", signup_date: new Date("2021-05-01"), churned: false, ltv: 8965.00, country: "KR" },
  { _id: 8,  name: "Henry Zhao",    tier: "starter",    signup_date: new Date("2023-07-20"), churned: true,  ltv: 232.00,  country: "CN" },
  { _id: 9,  name: "Iris Lopez",    tier: "pro",        signup_date: new Date("2023-01-05"), churned: false, ltv: 891.00,  country: "MX" },
  { _id: 10, name: "James Patel",   tier: "free",       signup_date: new Date("2023-09-01"), churned: true,  ltv: 0.00,    country: "IN" },
  { _id: 11, name: "Karen Wu",      tier: "enterprise", signup_date: new Date("2022-03-15"), churned: false, ltv: 5980.00, country: "US" },
  { _id: 12, name: "Leo Gonzalez",  tier: "pro",        signup_date: new Date("2023-04-01"), churned: true,  ltv: 990.00,  country: "BR" },
  { _id: 13, name: "Mia Johnson",   tier: "starter",    signup_date: new Date("2023-05-15"), churned: false, ltv: 435.00,  country: "US" },
  { _id: 14, name: "Noah Williams", tier: "free",       signup_date: new Date("2024-01-01"), churned: false, ltv: 0.00,    country: "CA" },
  { _id: 15, name: "Olivia Scott",  tier: "pro",        signup_date: new Date("2022-12-01"), churned: true,  ltv: 594.00,  country: "AU" },
  { _id: 16, name: "Peter Adams",   tier: "starter",    signup_date: new Date("2023-08-10"), churned: false, ltv: 203.00,  country: "UK" },
  { _id: 17, name: "Quinn Rivera",  tier: "enterprise", signup_date: new Date("2021-11-01"), churned: false, ltv: 7168.00, country: "US" },
  { _id: 18, name: "Rachel Chen",   tier: "pro",        signup_date: new Date("2023-02-14"), churned: true,  ltv: 1089.00, country: "TW" },
  { _id: 19, name: "Sam Taylor",    tier: "starter",    signup_date: new Date("2023-10-01"), churned: false, ltv: 145.00,  country: "US" },
  { _id: 20, name: "Tina Nguyen",   tier: "pro",        signup_date: new Date("2022-06-01"), churned: false, ltv: 2178.00, country: "VN" }
]);

// Seed sessions
const tierMap = {1:"starter",2:"pro",3:"enterprise",4:"free",5:"starter",6:"pro",7:"enterprise",
8:"starter",9:"pro",10:"free",11:"enterprise",12:"pro",13:"starter",14:"free",15:"pro",
16:"starter",17:"enterprise",18:"pro",19:"starter",20:"pro"};
const features = ["dashboard","reports","export","api","alerts","integrations","settings"];

let sessionDocs = [];
for (let cid = 1; cid <= 20; cid++) {
  let n = Math.floor(Math.random() * 18) + 3;
  for (let i = 0; i < n; i++) {
    let start = new Date(new Date("2024-01-01") - Math.floor(Math.random() * 90) * 86400000);
    let dur   = Math.floor(Math.random() * 118) + 2;
    sessionDocs.push({
      customer_id:   cid,
      tier:          tierMap[cid],
      session_start: start,
      session_end:   new Date(start.getTime() + dur * 60000),
      duration_mins: dur,
      feature_used:  features[Math.floor(Math.random() * features.length)],
      page_views:    Math.floor(Math.random() * 29) + 1
    });
  }
}
db.sessions.insertMany(sessionDocs);

// Seed events (onboarding funnel + usage)
const funnelSteps = ["signup","email_verified","profile_completed",
                     "first_feature_used","invited_team","billing_setup","active"];
const usageEvents  = ["login","feature_click","report_generated","export_done"];
const churnedMap   = {1:false,2:true,3:false,4:true,5:false,6:true,7:false,8:true,
9:false,10:true,11:false,12:true,13:false,14:false,15:true,16:false,17:false,18:true,19:false,20:false};

let eventDocs = [];
for (let cid = 1; cid <= 20; cid++) {
  let churned  = churnedMap[cid];
  let maxStep  = churned ? Math.floor(Math.random() * 4) + 1 : Math.floor(Math.random() * 5) + 2;
  let base     = new Date(new Date("2023-01-01").getTime() + Math.random() * 300 * 86400000);
  for (let i = 0; i < Math.min(maxStep, funnelSteps.length); i++) {
    eventDocs.push({
      customer_id: cid, tier: tierMap[cid],
      event: funnelSteps[i], event_type: "onboarding",
      timestamp: new Date(base.getTime() + i * (1 + Math.floor(Math.random() * 23)) * 3600000),
      churned: churned
    });
  }
  let usageCount = Math.floor(Math.random() * 15);
  for (let j = 0; j < usageCount; j++) {
    eventDocs.push({
      customer_id: cid, tier: tierMap[cid],
      event: usageEvents[Math.floor(Math.random() * usageEvents.length)],
      event_type: "usage",
      timestamp: new Date(new Date("2024-01-01") - Math.floor(Math.random() * 30) * 86400000),
      churned: churned
    });
  }
}
db.events.insertMany(eventDocs);
print("\n[OK] Collections seeded: customers_mongo, sessions, events");

// ============================================================
// Q1 — AGGREGATION PIPELINE
//      Session statistics by subscription tier
// ============================================================
printSection("Q1 — Aggregation Pipeline: Session Stats by Tier",
  db.sessions.aggregate([
    {
      $group: {
        _id:                "$tier",
        total_sessions:     { $sum: 1 },
        avg_duration_mins:  { $avg: "$duration_mins" },
        total_mins:         { $sum: "$duration_mins" },
        avg_page_views:     { $avg: "$page_views" },
        unique_customers:   { $addToSet: "$customer_id" }
      }
    },
    {
      $project: {
        tier:               "$_id",
        total_sessions:     1,
        avg_duration_mins:  { $round: ["$avg_duration_mins", 2] },
        total_mins:         { $round: ["$total_mins", 2] },
        avg_page_views:     { $round: ["$avg_page_views", 2] },
        unique_customers:   { $size: "$unique_customers" },
        _id: 0
      }
    },
    { $sort: { total_sessions: -1 } }
  ])
);

// ============================================================
// Q2 — EVENT ANALYSIS
//      Daily Active Users (DAU) and feature engagement by tier
// ============================================================
printSection("Q2 — Event Analysis: DAU & Feature Retention by Tier",
  db.events.aggregate([
    {
      $match: {
        event_type: "usage",
        timestamp:  { $gte: new Date(new Date("2024-01-01") - 30 * 86400000) }
      }
    },
    {
      $group: {
        _id:               { tier: "$tier", feature: "$event" },
        unique_daily_users: { $addToSet: "$customer_id" },
        event_count:       { $sum: 1 }
      }
    },
    {
      $project: {
        tier:               "$_id.tier",
        feature:            "$_id.feature",
        unique_daily_users: { $size: "$unique_daily_users" },
        event_count:        1, _id: 0
      }
    },
    {
      $group: {
        _id: "$tier",
        features: {
          $push: {
            feature:      "$feature",
            unique_users: "$unique_daily_users",
            total_events: "$event_count"
          }
        },
        total_active_users: { $sum: "$unique_daily_users" }
      }
    },
    { $sort: { total_active_users: -1 } }
  ])
);

// ============================================================
// Q3 — FUNNEL ANALYSIS
//      Onboarding drop-offs by tier (churned vs retained)
// ============================================================
printSection("Q3 — Funnel Analysis: Onboarding Drop-offs by Tier",
  db.events.aggregate([
    { $match: { event_type: "onboarding" } },
    {
      $group: {
        _id:        { tier: "$tier", step: "$event", churned: "$churned" },
        user_count: { $addToSet: "$customer_id" }
      }
    },
    {
      $project: {
        tier:        "$_id.tier",
        funnel_step: "$_id.step",
        churned:     "$_id.churned",
        user_count:  { $size: "$user_count" },
        _id: 0
      }
    },
    {
      $group: {
        _id: { tier: "$tier", funnel_step: "$funnel_step" },
        retained_users: {
          $sum: { $cond: [{ $eq: ["$churned", false] }, "$user_count", 0] }
        },
        churned_users: {
          $sum: { $cond: [{ $eq: ["$churned", true] }, "$user_count", 0] }
        }
      }
    },
    {
      $project: {
        tier:           "$_id.tier",
        funnel_step:    "$_id.funnel_step",
        retained_users: 1,
        churned_users:  1,
        total_users:    { $add: ["$retained_users","$churned_users"] },
        _id: 0
      }
    },
    { $sort: { tier: 1, total_users: -1 } }
  ])
);

// ============================================================
// Q4 — CROSS-REFERENCE
//      Free-tier upsell targets: high engagement, not churned
// ============================================================
printSection("Q4 — Cross-Reference: Free-Tier Upsell Targets",
  db.sessions.aggregate([
    // Step 1: Per-customer session stats
    {
      $group: {
        _id:              "$customer_id",
        avg_session_mins: { $avg: "$duration_mins" },
        total_sessions:   { $sum: 1 },
        total_page_views: { $sum: "$page_views" }
      }
    },
    // Step 2: Join with customer collection
    {
      $lookup: {
        from: "customers_mongo",
        localField: "_id",
        foreignField: "_id",
        as: "customer_info"
      }
    },
    { $unwind: "$customer_info" },
    // Step 3: Filter free-tier, not churned, above-average engagement (>30 min avg)
    {
      $match: {
        "customer_info.tier":    "free",
        "customer_info.churned": false,
        avg_session_mins:        { $gte: 30 }
      }
    },
    // Step 4: Shape output with upsell priority
    {
      $project: {
        customer_id:      "$_id",
        name:             "$customer_info.name",
        country:          "$customer_info.country",
        avg_session_mins: { $round: ["$avg_session_mins", 2] },
        total_sessions:   1,
        total_page_views: 1,
        ltv:              "$customer_info.ltv",
        upsell_priority: {
          $switch: {
            branches: [
              { case: { $gte: ["$avg_session_mins", 45] }, then: "High" },
              { case: { $gte: ["$avg_session_mins", 30] }, then: "Medium" }
            ],
            default: "Low"
          }
        },
        _id: 0
      }
    },
    { $sort: { avg_session_mins: -1 } }
  ])
);

print("\n[DONE] All 4 MongoDB queries complete.");
