-- Step 13: staging view. Single source of truth for cleaning rules and the
-- status_group / is_default / is_late definitions (see docs/assumptions.md).
-- Raw tables are never modified. Loans are LEFT JOINed so no loan can silently disappear.

CREATE OR REPLACE VIEW `pave-bank-fintech.fintech_test.v_loans` AS
SELECT
  l.loan_id,
  l.customer_id,

  -- Outcome definitions -------------------------------------------------------
  l.loan_status,
  CASE
    WHEN l.loan_status = 'Fully Paid'                  THEN 'paid_off'
    WHEN l.loan_status IN ('Charged Off', 'Default')   THEN 'defaulted'
    ELSE 'active'  -- Current, In Grace Period, Late (16-30 days), Late (31-120 days)
  END AS status_group,
  l.loan_status IN ('Charged Off', 'Default') AS is_default,
  -- Task 3 workaround: no payments table, so "late" is a snapshot of current status
  l.loan_status IN ('In Grace Period', 'Late (16-30 days)', 'Late (31-120 days)') AS is_late,
  -- Outcome known (paid or defaulted); use for default rates that ignore still-open loans
  l.loan_status IN ('Fully Paid', 'Charged Off', 'Default') AS is_resolved,

  -- Loan terms ----------------------------------------------------------------
  l.loan_amount,
  l.funded_amount,
  l.int_rate,                                              -- fraction: 0.1299 = 12.99%
  l.installment,
  CAST(REGEXP_EXTRACT(l.term, r'(\d+)') AS INT64) AS term_months,   -- ' 36 months' -> 36
  l.grade,
  PARSE_DATE('%b-%y', l.issue_d) AS issue_date,            -- 'Jun-13' -> 2013-06-01
  l.issue_year,
  CASE UPPER(TRIM(l.type))
    WHEN 'INDIVIDUAL' THEN 'Individual'
    WHEN 'JOINT'      THEN 'Joint'
    WHEN 'JOINT APP'  THEN 'Joint'
    WHEN 'DIRECT_PAY' THEN 'Direct Pay'
    ELSE l.type
  END AS application_type,
  l.purpose,
  l.pymnt_plan,

  -- Geography (state_region has one stray header row, filtered below) ---------
  l.state,
  sr.region,
  sr.subregion,

  -- Borrower --------------------------------------------------------------------
  c.emp_title,
  NULLIF(c.emp_length, 'n/a') AS emp_length,               -- 'n/a' is a missing value
  c.home_ownership,
  c.verification_status,
  c.zip_code,
  c.annual_inc,
  c.annual_inc_joint,                                       -- NULL unless a joint application
  SAFE_DIVIDE(l.loan_amount, c.annual_inc) AS loan_to_income,
  c.avg_cur_bal,
  c.Tot_cur_bal AS tot_cur_bal
FROM `pave-bank-fintech.fintech_test.loan` AS l
LEFT JOIN `pave-bank-fintech.fintech_test.customer` AS c
  ON l.customer_id = c.customer_id
LEFT JOIN (
  SELECT * FROM `pave-bank-fintech.fintech_test.state_region` WHERE state != 'state'
) AS sr
  ON l.state = sr.state;
