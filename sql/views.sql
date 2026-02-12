-- Minimal analytics views to power Streamlit dashboard.
-- These keep business logic out of the UI layer.

-- Donations by month (for trend charts)
CREATE OR REPLACE VIEW vw_monthly_giving AS
SELECT
  DATE_TRUNC('month', donation_date)::date AS month,
  COUNT(*)::int AS donation_count,
  COUNT(DISTINCT donor_id)::int AS unique_donors,
  SUM(amount)::numeric(14, 2) AS total_amount,
  AVG(amount)::numeric(14, 2) AS avg_amount
FROM donations
GROUP BY 1
ORDER BY 1;

-- Donor lifetime value (simple: total given + donation count)
CREATE OR REPLACE VIEW vw_donor_ltv AS
SELECT
  d.donor_id,
  d.first_name,
  d.last_name,
  d.email,
  COUNT(dn.donation_id)::int AS donation_count,
  SUM(dn.amount)::numeric(14, 2) AS total_given,
  MIN(dn.donation_date)::date AS first_gift_date,
  MAX(dn.donation_date)::date AS last_gift_date
FROM donors d
LEFT JOIN donations dn ON dn.donor_id = d.donor_id
GROUP BY d.donor_id, d.first_name, d.last_name, d.email;

-- Campaign performance (raised vs goal)
CREATE OR REPLACE VIEW vw_campaign_performance AS
SELECT
  c.campaign_id,
  c.campaign_name,
  c.start_date,
  c.end_date,
  c.goal_amount,
  c.campaign_type,
  COUNT(d.donation_id)::int AS donation_count,
  COUNT(DISTINCT d.donor_id)::int AS unique_donors,
  COALESCE(SUM(d.amount), 0)::numeric(14, 2) AS total_raised,
  (COALESCE(SUM(d.amount), 0) - COALESCE(c.goal_amount, 0))::numeric(14, 2) AS raised_minus_goal
FROM campaigns c
LEFT JOIN donations d ON d.campaign_id = c.campaign_id
GROUP BY
  c.campaign_id,
  c.campaign_name,
  c.start_date,
  c.end_date,
  c.goal_amount,
  c.campaign_type
ORDER BY total_raised DESC;

