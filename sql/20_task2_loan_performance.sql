-- Task 2: loan performance by origination year.
-- "principal" = loan_amount (funded_amount is identical for every loan).
-- int_rate is stored as a fraction, so *100 gives percent.
-- Two default-rate definitions (see docs/assumptions.md, "Default rate and censoring"):
--   default_rate_all_pct      = defaulted / ALL loans in the cohort  (biased low for recent cohorts: open loans cannot default yet)
--   default_rate_resolved_pct = defaulted / (paid_off + defaulted)   (ignores still-open loans; less biased, but not censoring-free)

-- Query A: summary table (one row per year)
SELECT
  issue_year,
  COUNT(*)                                                    AS loans,
  ROUND(AVG(int_rate) * 100, 2)                               AS avg_int_rate_pct,
  ROUND(AVG(loan_amount), 2)                                  AS avg_principal,
  COUNTIF(is_default)                                         AS defaulted,
  COUNTIF(is_resolved)                                        AS resolved,
  ROUND(100 * COUNTIF(is_default) / COUNT(*), 1)              AS default_rate_all_pct,
  ROUND(100 * COUNTIF(is_default) / COUNTIF(is_resolved), 1)  AS default_rate_resolved_pct
FROM `pave-bank-fintech.fintech_test.v_loans`
GROUP BY issue_year
ORDER BY issue_year;

-- Query B: same default rates in long format, one row per year and measure (feeds the line chart)
SELECT issue_year, 'All loans' AS measure,
       ROUND(100 * COUNTIF(is_default) / COUNT(*), 1) AS default_rate_pct
FROM `pave-bank-fintech.fintech_test.v_loans`
GROUP BY issue_year
UNION ALL
SELECT issue_year, 'Resolved loans only' AS measure,
       ROUND(100 * COUNTIF(is_default) / COUNTIF(is_resolved), 1) AS default_rate_pct
FROM `pave-bank-fintech.fintech_test.v_loans`
GROUP BY issue_year
ORDER BY issue_year, measure;
