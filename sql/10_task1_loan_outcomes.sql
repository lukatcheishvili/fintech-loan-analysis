-- Task 1: total loans by outcome group and origination year (feeds a stacked bar chart in Hex).
-- status_group is defined once in v_loans: paid_off = Fully Paid; defaulted = Charged Off + Default;
-- active = Current + In Grace Period + Late (16-30) + Late (31-120).

SELECT
  issue_year,
  status_group,
  COUNT(*) AS loans
FROM `pave-bank-fintech.fintech_test.v_loans`
GROUP BY issue_year, status_group
ORDER BY issue_year, status_group;
