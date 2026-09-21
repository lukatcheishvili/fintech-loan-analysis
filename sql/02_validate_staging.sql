-- Step 13b: validate v_loans. Expected values come from the local CSV analysis
-- (docs/assumptions.md, docs/schema_profile.md). Every diff must be 0.

-- A. Counts and derived columns
SELECT check_name, actual, expected, actual - expected AS diff
FROM (
  SELECT 'rows' AS check_name, COUNT(*) AS actual, 270299 AS expected FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'status_group = paid_off',   COUNTIF(status_group = 'paid_off'),  76361  FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'status_group = defaulted',  COUNTIF(status_group = 'defaulted'), 17863  FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'status_group = active',     COUNTIF(status_group = 'active'),    176075 FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'is_default',                COUNTIF(is_default),                 17863  FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'is_late',                   COUNTIF(is_late),                    5614   FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'is_resolved',               COUNTIF(is_resolved),                94224  FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'NULL issue_date',           COUNTIF(issue_date IS NULL),         0      FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'issue_year <> YEAR(issue_date)', COUNTIF(issue_year != EXTRACT(YEAR FROM issue_date)), 0 FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'term_months = 36',          COUNTIF(term_months = 36),           189772 FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'term_months = 60',          COUNTIF(term_months = 60),           80527  FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'application_type = Individual', COUNTIF(application_type = 'Individual'), 251202 FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'application_type = Joint',      COUNTIF(application_type = 'Joint'),      18794  FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'application_type = Direct Pay', COUNTIF(application_type = 'Direct Pay'), 303    FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'NULL region',               COUNTIF(region IS NULL),             0      FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'NULL annual_inc (customer join)', COUNTIF(annual_inc IS NULL),   0      FROM `pave-bank-fintech.fintech_test.v_loans`
  UNION ALL SELECT 'NULL emp_length (was n/a)', COUNTIF(emp_length IS NULL),         18745  FROM `pave-bank-fintech.fintech_test.v_loans`
);

-- B. Region derived from state_region must agree with the provided loan_with_region file
--    (expect region_mismatches = 0 and joined_rows = 270299)
SELECT COUNTIF(v.region != r.region) AS region_mismatches, COUNT(*) AS joined_rows
FROM `pave-bank-fintech.fintech_test.v_loans` AS v
JOIN `pave-bank-fintech.fintech_test.loan_with_region` AS r
  ON v.loan_id = r.loan_id;

-- C. Eyeball a few rows
SELECT loan_id, loan_status, status_group, is_default, is_late, loan_amount, int_rate,
       term_months, grade, issue_date, issue_year, application_type, region, emp_length,
       annual_inc, loan_to_income
FROM `pave-bank-fintech.fintech_test.v_loans`
LIMIT 10;
