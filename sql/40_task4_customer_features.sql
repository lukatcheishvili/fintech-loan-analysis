-- Task 4: customer-level feature table for segmentation (clustering happens in a Hex Python cell).
-- One row per loan = one row per customer (1:1). loan_id is the readable key (customer_id is a hashed blob).
-- Clustering features : loan_amount, int_rate_pct, term_months, annual_inc, loan_to_income, balance_to_income
-- Profiling-only      : grade, application_type, home_ownership, issue_year, status_group, is_default, is_late
--                       (outcomes are NOT clustering inputs; they validate the clusters afterwards)
-- No delay or credit-utilisation columns exist in the data; balance_to_income (total current balance / income)
-- is used as a leverage proxy and is NOT credit utilisation (no credit limits are available).

SELECT
  loan_id,
  loan_amount,
  ROUND(int_rate * 100, 2)                 AS int_rate_pct,
  term_months,
  annual_inc,
  loan_to_income,
  tot_cur_bal,
  SAFE_DIVIDE(tot_cur_bal, annual_inc)     AS balance_to_income,
  grade,
  application_type,
  home_ownership,
  issue_year,
  status_group,
  is_default,
  is_late
FROM `pave-bank-fintech.fintech_test.v_loans`;
