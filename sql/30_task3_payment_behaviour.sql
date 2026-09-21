-- Task 3: payment behaviour. No payments table exists, so "late" = current loan_status in
-- (In Grace Period, Late (16-30 days), Late (31-120 days)); see docs/assumptions.md.
-- Only OPEN loans can be late, so the denominator for late rates is active loans (not all loans).
-- One loan per customer, so "late payment frequency" = share of loans currently late within a group.

-- Step 1: what "late" looks like among active loans (expect 4 rows; late rows sum to 5,614)
SELECT
  loan_status,
  is_late,
  COUNT(*) AS loans,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_active
FROM `pave-bank-fintech.fintech_test.v_loans`
WHERE status_group = 'active'
GROUP BY loan_status, is_late
ORDER BY loans DESC;

-- Step 2: the customers with late payments (one row per late loan = per customer).
-- customer_id is an unreadable hashed value, so loan_id is the readable handle.
-- Most severe first, then largest loan first.
SELECT
  loan_id,
  loan_status,
  loan_amount,
  ROUND(int_rate * 100, 2) AS int_rate_pct,
  grade,
  term_months,
  issue_year,
  application_type,
  home_ownership,
  annual_inc,
  ROUND(loan_to_income, 3) AS loan_to_income,
  state
FROM `pave-bank-fintech.fintech_test.v_loans`
WHERE is_late
ORDER BY
  CASE loan_status
    WHEN 'Late (31-120 days)' THEN 1
    WHEN 'Late (16-30 days)'  THEN 2
    ELSE 3
  END,
  loan_amount DESC,
  loan_id;

-- Step 3: late rate by interest-rate band and term (feeds the scatter/bubble chart).
-- 2-point bands. int_rate is rounded to 2 decimals of a percent BEFORE banding so that
-- floating-point noise (e.g. 0.29 * 100 = 28.999999999999996) cannot push a loan into the wrong band.
-- Denominator = active loans; each row also shows its size so tiny groups can be read with care.
WITH active AS (
  SELECT
    CAST(FLOOR(ROUND(int_rate * 100, 2) / 2) * 2 AS INT64) AS band_start_pct,
    term_months,
    is_late
  FROM `pave-bank-fintech.fintech_test.v_loans`
  WHERE status_group = 'active'
)
SELECT
  band_start_pct,
  CONCAT(CAST(band_start_pct AS STRING), '-', CAST(band_start_pct + 2 AS STRING), '%') AS rate_band,
  term_months,
  COUNT(*)                                        AS active_loans,
  COUNTIF(is_late)                                AS late_loans,
  ROUND(100 * COUNTIF(is_late) / COUNT(*), 2)     AS late_rate_pct
FROM active
GROUP BY band_start_pct, term_months
ORDER BY band_start_pct, term_months;
