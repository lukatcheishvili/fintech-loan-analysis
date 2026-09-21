-- Task 1 (companion chart): each origination year's outcome mix as a percentage.
-- Shows proportions the counts chart hides (e.g. the 2016 anomaly). Each year sums to ~100.

SELECT
  issue_year,
  status_group,
  COUNT(*) AS loans,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY issue_year), 1) AS pct_of_year
FROM `pave-bank-fintech.fintech_test.v_loans`
GROUP BY issue_year, status_group
ORDER BY issue_year, status_group;
