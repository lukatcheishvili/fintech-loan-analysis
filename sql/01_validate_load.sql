-- Step 12: validate the raw load. Run in BigQuery Studio after all 6 tables are uploaded.
-- "expected" values come from the local CSVs (scripts/profile_csvs.py + pandas checks).
-- Every `diff` column should be 0 (or ~0 for float sums: BigQuery may add in a different order).

-- A. Row counts ---------------------------------------------------------------
SELECT 'customer'           AS tbl, COUNT(*) AS actual, 270299 AS expected, COUNT(*) - 270299 AS diff FROM `pave-bank-fintech.fintech_test.customer`
UNION ALL SELECT 'loan',               COUNT(*), 270299, COUNT(*) - 270299 FROM `pave-bank-fintech.fintech_test.loan`
UNION ALL SELECT 'loan_with_region',   COUNT(*), 270299, COUNT(*) - 270299 FROM `pave-bank-fintech.fintech_test.loan_with_region`
UNION ALL SELECT 'loan_count_by_year', COUNT(*), 8,      COUNT(*) - 8      FROM `pave-bank-fintech.fintech_test.loan_count_by_year`
UNION ALL SELECT 'loan_purposes',      COUNT(*), 13,     COUNT(*) - 13     FROM `pave-bank-fintech.fintech_test.loan_purposes`
UNION ALL SELECT 'state_region',       COUNT(*), 52,     COUNT(*) - 52     FROM `pave-bank-fintech.fintech_test.state_region`;  -- 52 = 51 states + 1 stray header row (filtered later)

-- B. Content checks on loan ----------------------------------------------------
SELECT check_name, actual, expected, actual - expected AS diff
FROM (
  SELECT 'SUM(loan_amount)'      AS check_name, CAST(SUM(loan_amount) AS FLOAT64)          AS actual, 4166072400        AS expected FROM `pave-bank-fintech.fintech_test.loan`
  UNION ALL SELECT 'SUM(funded_amount)',    CAST(SUM(funded_amount) AS FLOAT64),        4166072400        FROM `pave-bank-fintech.fintech_test.loan`
  UNION ALL SELECT 'AVG(int_rate) (6dp)',   ROUND(AVG(int_rate), 6),                    0.130765          FROM `pave-bank-fintech.fintech_test.loan`
  UNION ALL SELECT 'SUM(installment) (2dp)',ROUND(SUM(installment), 2),                 122693899.23      FROM `pave-bank-fintech.fintech_test.loan`
  UNION ALL SELECT 'NULL description',      COUNTIF(description IS NULL),               2343              FROM `pave-bank-fintech.fintech_test.loan`
  UNION ALL SELECT 'pymnt_plan = TRUE',     COUNTIF(pymnt_plan),                        40                FROM `pave-bank-fintech.fintech_test.loan`
  UNION ALL SELECT 'DISTINCT customer_id',  COUNT(DISTINCT customer_id),                270299            FROM `pave-bank-fintech.fintech_test.loan`
);

-- C. Content checks on customer -------------------------------------------------
SELECT check_name, actual, expected, actual - expected AS diff
FROM (
  SELECT 'SUM(annual_inc) (2dp)'  AS check_name, ROUND(SUM(annual_inc), 2)      AS actual, 21520664782.41 AS expected FROM `pave-bank-fintech.fintech_test.customer`
  UNION ALL SELECT 'SUM(Tot_cur_bal) (2dp)', ROUND(SUM(Tot_cur_bal), 2),        39110405893.0     FROM `pave-bank-fintech.fintech_test.customer`
  UNION ALL SELECT 'NULL emp_title',         COUNTIF(emp_title IS NULL),        23658             FROM `pave-bank-fintech.fintech_test.customer`
  UNION ALL SELECT 'NULL annual_inc_joint',  COUNTIF(annual_inc_joint IS NULL), 251505            FROM `pave-bank-fintech.fintech_test.customer`
  UNION ALL SELECT "emp_length = 'n/a'",     COUNTIF(emp_length = 'n/a'),       18745             FROM `pave-bank-fintech.fintech_test.customer`
  UNION ALL SELECT 'DISTINCT customer_id',   COUNT(DISTINCT customer_id),       270299            FROM `pave-bank-fintech.fintech_test.customer`
);

-- D. Join integrity: every loan has exactly one customer, and vice versa (expect 0 and 0)
SELECT
  (SELECT COUNT(*) FROM `pave-bank-fintech.fintech_test.loan` l
     LEFT JOIN `pave-bank-fintech.fintech_test.customer` c ON l.customer_id = c.customer_id WHERE c.customer_id IS NULL) AS loans_without_customer,
  (SELECT COUNT(*) FROM `pave-bank-fintech.fintech_test.customer` c
     LEFT JOIN `pave-bank-fintech.fintech_test.loan` l ON c.customer_id = l.customer_id WHERE l.customer_id IS NULL)     AS customers_without_loan;

-- E. True status vocabulary (expect the 7 values profiled locally)
SELECT loan_status, COUNT(*) AS loans
FROM `pave-bank-fintech.fintech_test.loan`
GROUP BY loan_status
ORDER BY loans DESC;
