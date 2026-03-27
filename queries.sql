-- ROA Assignment - Option A: Customer Churn & Retention Analysis
-- PostgreSQL queries file
-- Run schema first, then the 5 queries below

-- drop tables if re-running from scratch
DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS usage_metrics CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS plans CASCADE;

CREATE TABLE plans (
    plan_id       SERIAL PRIMARY KEY,
    plan_name     VARCHAR(50)  NOT NULL,
    tier          VARCHAR(20)  NOT NULL CHECK (tier IN ('free','starter','pro','enterprise')),
    monthly_price NUMERIC(10,2) NOT NULL
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    plan_id     INT REFERENCES plans(plan_id),
    signup_date DATE NOT NULL,
    churn_date  DATE,
    country     VARCHAR(50),
    ltv         NUMERIC(12,2) DEFAULT 0
);

CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    customer_id     INT REFERENCES customers(customer_id),
    plan_id         INT REFERENCES plans(plan_id),
    start_date      DATE NOT NULL,
    end_date        DATE,
    mrr             NUMERIC(10,2) NOT NULL,
    status          VARCHAR(20) CHECK (status IN ('active','cancelled','downgraded','upgraded'))
);

CREATE TABLE support_tickets (
    ticket_id   SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    created_at  TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    category    VARCHAR(50),
    severity    VARCHAR(20) CHECK (severity IN ('low','medium','high','critical'))
);

CREATE TABLE usage_metrics (
    metric_id     SERIAL PRIMARY KEY,
    customer_id   INT REFERENCES customers(customer_id),
    month         DATE NOT NULL,
    login_count   INT DEFAULT 0,
    feature_usage INT DEFAULT 0,
    session_mins  NUMERIC(10,2) DEFAULT 0
);

-- seed data
INSERT INTO plans (plan_name, tier, monthly_price) VALUES
  ('Free',       'free',        0.00),
  ('Starter',    'starter',    29.00),
  ('Pro',        'pro',        99.00),
  ('Enterprise', 'enterprise', 299.00);

INSERT INTO customers (name, email, plan_id, signup_date, churn_date, country, ltv) VALUES
  ('Alice Martin',  'alice@example.com',   2, '2023-01-15', NULL,         'US',  580.00),
  ('Bob Singh',     'bob@example.com',     3, '2023-02-01', '2024-01-10', 'IN',  990.00),
  ('Carol White',   'carol@example.com',   4, '2022-11-20', NULL,         'UK', 4485.00),
  ('David Lee',     'david@example.com',   1, '2023-06-01', '2023-09-15', 'AU',    0.00),
  ('Eva Brown',     'eva@example.com',     2, '2023-03-10', NULL,         'US',  290.00),
  ('Frank Tan',     'frank@example.com',   3, '2022-08-05', '2023-08-05', 'SG', 1188.00),
  ('Grace Kim',     'grace@example.com',   4, '2021-05-01', NULL,         'KR', 8965.00),
  ('Henry Zhao',    'henry@example.com',   2, '2023-07-20', '2024-02-01', 'CN',  232.00),
  ('Iris Lopez',    'iris@example.com',    3, '2023-01-05', NULL,         'MX',  891.00),
  ('James Patel',   'james@example.com',   1, '2023-09-01', '2023-11-01', 'IN',    0.00),
  ('Karen Wu',      'karen@example.com',   4, '2022-03-15', NULL,         'US', 5980.00),
  ('Leo Gonzalez',  'leo@example.com',     3, '2023-04-01', '2024-03-01', 'BR',  990.00),
  ('Mia Johnson',   'mia@example.com',     2, '2023-05-15', NULL,         'US',  435.00),
  ('Noah Williams', 'noah@example.com',    1, '2024-01-01', NULL,         'CA',    0.00),
  ('Olivia Scott',  'olivia@example.com',  3, '2022-12-01', '2023-06-01', 'AU',  594.00),
  ('Peter Adams',   'peter@example.com',   2, '2023-08-10', NULL,         'UK',  203.00),
  ('Quinn Rivera',  'quinn@example.com',   4, '2021-11-01', NULL,         'US', 7168.00),
  ('Rachel Chen',   'rachel@example.com',  3, '2023-02-14', '2023-12-14', 'TW', 1089.00),
  ('Sam Taylor',    'sam@example.com',     2, '2023-10-01', NULL,         'US',  145.00),
  ('Tina Nguyen',   'tina@example.com',    3, '2022-06-01', NULL,         'VN', 2178.00);

INSERT INTO subscriptions (customer_id, plan_id, start_date, end_date, mrr, status) VALUES
  (1,  2, '2023-01-15', NULL,         29.00,  'active'),
  (2,  3, '2023-02-01', '2024-01-10', 99.00,  'cancelled'),
  (3,  4, '2022-11-20', NULL,        299.00,  'active'),
  (4,  1, '2023-06-01', '2023-09-15',  0.00,  'cancelled'),
  (5,  2, '2023-03-10', NULL,         29.00,  'active'),
  (6,  3, '2022-08-05', '2023-08-05', 99.00,  'cancelled'),
  (7,  4, '2021-05-01', NULL,        299.00,  'active'),
  (8,  2, '2023-07-20', '2024-02-01', 29.00,  'cancelled'),
  (9,  3, '2023-01-05', NULL,         99.00,  'active'),
  (10, 1, '2023-09-01', '2023-11-01',  0.00,  'cancelled'),
  (11, 4, '2022-03-15', NULL,        299.00,  'active'),
  (12, 3, '2023-04-01', '2024-03-01', 99.00,  'cancelled'),
  (13, 2, '2023-05-15', NULL,         29.00,  'active'),
  (14, 1, '2024-01-01', NULL,          0.00,  'active'),
  (15, 3, '2022-12-01', '2023-06-01', 99.00,  'cancelled'),
  (16, 2, '2023-08-10', NULL,         29.00,  'active'),
  (17, 4, '2021-11-01', NULL,        299.00,  'active'),
  (18, 3, '2023-02-14', '2023-12-14', 99.00,  'cancelled'),
  (19, 2, '2023-10-01', NULL,         29.00,  'active'),
  (20, 3, '2022-06-01', NULL,         99.00,  'active'),
  -- downgrade history for churn correlation
  (2,  2, '2023-10-01', '2024-01-10', 29.00, 'downgraded'),
  (6,  1, '2023-05-01', '2023-08-05',  0.00, 'downgraded');

INSERT INTO support_tickets (customer_id, created_at, resolved_at, category, severity) VALUES
  (2,  '2023-11-01 10:00', '2023-11-02 12:00', 'billing',   'high'),
  (2,  '2023-12-15 09:00', '2023-12-15 18:00', 'technical', 'medium'),
  (4,  '2023-07-01 14:00', '2023-07-01 16:00', 'general',   'low'),
  (6,  '2023-04-10 11:00', '2023-04-12 11:00', 'billing',   'critical'),
  (6,  '2023-06-20 15:00', '2023-06-21 10:00', 'billing',   'high'),
  (8,  '2023-10-05 09:30', '2023-10-06 09:30', 'technical', 'medium'),
  (10, '2023-10-01 08:00', '2023-10-01 10:00', 'general',   'low'),
  (12, '2023-08-15 13:00', '2023-08-16 13:00', 'billing',   'high'),
  (12, '2024-01-10 10:00', '2024-01-11 10:00', 'technical', 'medium'),
  (15, '2023-02-01 12:00', '2023-02-03 12:00', 'billing',   'critical'),
  (18, '2023-09-20 16:00', '2023-09-21 09:00', 'billing',   'high'),
  (1,  '2023-06-01 11:00', '2023-06-01 14:00', 'general',   'low'),
  (3,  '2023-07-15 10:00', '2023-07-15 11:00', 'general',   'low'),
  (7,  '2023-03-01 09:00', '2023-03-01 11:00', 'technical', 'medium'),
  (11, '2023-05-20 14:00', '2023-05-20 16:00', 'general',   'low');

INSERT INTO usage_metrics (customer_id, month, login_count, feature_usage, session_mins) VALUES
  (1,  '2024-01-01', 22, 45,  310.5),
  (2,  '2023-12-01',  3,  5,   20.0),
  (3,  '2024-01-01', 30, 90,  890.0),
  (5,  '2024-01-01', 18, 30,  220.0),
  (7,  '2024-01-01', 28, 85,  960.0),
  (9,  '2024-01-01', 20, 55,  440.0),
  (11, '2024-01-01', 29, 88,  870.0),
  (13, '2024-01-01', 15, 25,  180.0),
  (16, '2024-01-01', 12, 20,  150.0),
  (17, '2024-01-01', 31, 95, 1100.0),
  (19, '2024-01-01',  8, 10,   60.0),
  (20, '2024-01-01', 25, 70,  650.0),
  (1,  '2023-12-01', 20, 40,  290.0),
  (3,  '2023-12-01', 28, 88,  860.0),
  (5,  '2023-12-01', 16, 28,  200.0),
  (7,  '2023-12-01', 27, 80,  920.0),
  (9,  '2023-12-01', 19, 50,  410.0),
  (11, '2023-12-01', 27, 85,  840.0),
  (13, '2023-12-01', 14, 22,  160.0),
  (20, '2023-12-01', 23, 65,  620.0);


-- Q1: churn rate, avg LTV, MRR and ticket rate per plan tier
-- joining 4 tables to get a full picture of each tier's health

SELECT
    p.tier,
    p.plan_name,
    COUNT(DISTINCT c.customer_id)                                          AS total_customers,
    COUNT(DISTINCT CASE WHEN c.churn_date IS NOT NULL
                        THEN c.customer_id END)                            AS churned_customers,
    ROUND(
        COUNT(DISTINCT CASE WHEN c.churn_date IS NOT NULL
                            THEN c.customer_id END)::NUMERIC
        / NULLIF(COUNT(DISTINCT c.customer_id), 0) * 100, 1
    )                                                                      AS churn_rate_pct,
    ROUND(AVG(c.ltv), 2)                                                   AS avg_ltv,
    SUM(s.mrr)                                                             AS total_mrr,
    COUNT(t.ticket_id)                                                     AS total_tickets,
    ROUND(
        COUNT(t.ticket_id)::NUMERIC
        / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2
    )                                                                      AS tickets_per_customer
FROM customers c
JOIN plans p ON c.plan_id = p.plan_id
LEFT JOIN subscriptions s ON c.customer_id = s.customer_id AND s.status = 'active'
LEFT JOIN support_tickets t ON c.customer_id = t.customer_id
GROUP BY p.tier, p.plan_name
ORDER BY p.monthly_price;


-- Q2: rank customers by LTV within their tier, compare to tier average
-- window functions: RANK, DENSE_RANK, AVG OVER, running total

SELECT
    c.customer_id,
    c.name,
    p.tier,
    c.ltv,
    RANK()       OVER (PARTITION BY p.tier ORDER BY c.ltv DESC)           AS tier_rank,
    DENSE_RANK() OVER (ORDER BY c.ltv DESC)                               AS overall_rank,
    ROUND(AVG(c.ltv) OVER (PARTITION BY p.tier), 2)                      AS avg_tier_ltv,
    ROUND(c.ltv - AVG(c.ltv) OVER (PARTITION BY p.tier), 2)              AS vs_tier_avg,
    SUM(c.ltv) OVER (
        PARTITION BY p.tier ORDER BY c.ltv DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                                                      AS running_tier_ltv
FROM customers c
JOIN plans p ON c.plan_id = p.plan_id
ORDER BY p.tier, tier_rank;


-- Q3: do customers raise more tickets before they downgrade?
-- two CTEs: first finds downgrades, second counts tickets in 90 days before each one

WITH downgraded AS (
    SELECT
        customer_id,
        MIN(start_date) AS downgrade_date
    FROM subscriptions
    WHERE status = 'downgraded'
    GROUP BY customer_id
),
pre_downgrade_tickets AS (
    SELECT
        d.customer_id,
        d.downgrade_date,
        COUNT(t.ticket_id) AS ticket_count
    FROM downgraded d
    LEFT JOIN support_tickets t
        ON  t.customer_id = d.customer_id
        AND t.created_at >= (d.downgrade_date - INTERVAL '90 days')
        AND t.created_at <  d.downgrade_date
    GROUP BY d.customer_id, d.downgrade_date
)
SELECT
    c.name,
    p.tier,
    pdt.downgrade_date,
    pdt.ticket_count                                    AS tickets_before_downgrade,
    c.ltv,
    CASE WHEN c.churn_date IS NOT NULL THEN 'Churned' ELSE 'Retained' END AS final_status,
    -- compare to average across all downgraders
    (SELECT ROUND(AVG(ticket_count), 2) FROM pre_downgrade_tickets)       AS avg_for_all_downgraders
FROM pre_downgrade_tickets pdt
JOIN customers c ON c.customer_id = pdt.customer_id
JOIN plans p ON p.plan_id = c.plan_id
ORDER BY pdt.ticket_count DESC;


-- Q4: monthly signups, churns, MRR and rolling 3-month churn rate
-- uses LAG for MoM growth and a window frame for the rolling rate

WITH monthly_signups AS (
    SELECT DATE_TRUNC('month', signup_date) AS month,
           COUNT(*)   AS new_customers,
           SUM(ltv)   AS new_ltv
    FROM customers
    GROUP BY 1
),
monthly_churns AS (
    SELECT DATE_TRUNC('month', churn_date) AS month,
           COUNT(*) AS churned
    FROM customers
    WHERE churn_date IS NOT NULL
    GROUP BY 1
),
monthly_mrr AS (
    SELECT DATE_TRUNC('month', start_date) AS month,
           SUM(mrr) AS new_mrr
    FROM subscriptions
    WHERE status = 'active'
    GROUP BY 1
),
combined AS (
    SELECT
        COALESCE(s.month, c.month, m.month) AS month,
        COALESCE(s.new_customers, 0)        AS new_customers,
        COALESCE(c.churned, 0)              AS churned,
        COALESCE(m.new_mrr, 0)              AS new_mrr
    FROM monthly_signups s
    FULL OUTER JOIN monthly_churns c USING (month)
    FULL OUTER JOIN monthly_mrr    m USING (month)
)
SELECT
    month,
    new_customers,
    churned,
    new_mrr,
    SUM(new_customers) OVER (ORDER BY month)           AS cumulative_customers,
    LAG(new_customers) OVER (ORDER BY month)           AS prev_month_signups,
    ROUND(
        (new_customers - LAG(new_customers) OVER (ORDER BY month))::NUMERIC
        / NULLIF(LAG(new_customers) OVER (ORDER BY month), 0) * 100, 2
    )                                                  AS mom_growth_pct,
    ROUND(
        SUM(churned) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)::NUMERIC
        / NULLIF(
            SUM(new_customers) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0
        ) * 100, 2
    )                                                  AS rolling_3m_churn_pct
FROM combined
ORDER BY month;


-- Q5: find potential duplicate accounts (same email domain + signed up within 30 days)
-- also flags exact name matches regardless of case

WITH email_parts AS (
    SELECT
        customer_id,
        name,
        email,
        LOWER(SPLIT_PART(email, '@', 2)) AS domain,
        signup_date,
        ltv
    FROM customers
),
possible_dupes AS (
    SELECT
        a.customer_id   AS id_a,
        a.name          AS name_a,
        a.email         AS email_a,
        b.customer_id   AS id_b,
        b.name          AS name_b,
        b.email         AS email_b,
        a.domain,
        a.signup_date   AS signed_up_a,
        b.signup_date   AS signed_up_b,
        ABS(b.signup_date - a.signup_date) AS days_apart,
        a.ltv           AS ltv_a,
        b.ltv           AS ltv_b,
        CASE
            WHEN LOWER(a.name) = LOWER(b.name)
                 THEN 'exact name match'
            WHEN a.domain = b.domain AND ABS(b.signup_date - a.signup_date) <= 30
                 THEN 'same domain, close signup date'
            ELSE 'other'
        END AS reason
    FROM email_parts a
    JOIN email_parts b ON a.customer_id < b.customer_id
    AND (
        LOWER(a.name) = LOWER(b.name)
        OR (a.domain = b.domain AND ABS(b.signup_date - a.signup_date) <= 30)
    )
)
SELECT
    id_a, name_a, email_a,
    id_b, name_b, email_b,
    domain,
    signed_up_a, signed_up_b,
    days_apart,
    ltv_a, ltv_b,
    reason,
    -- keep whichever account has higher LTV
    CASE WHEN ltv_a >= ltv_b THEN id_a ELSE id_b END AS keep_id
FROM possible_dupes
ORDER BY reason, days_apart;
