# Assumptions and decisions

Living record of every judgement call in this analysis. Numbers here were verified locally
against the CSVs in `data/raw/` (see `docs/schema_profile.md`).

## Data reality vs. the brief

| Brief says | Dataset has | Decision |
|---|---|---|
| Tables like loans, payments, customers, transactions | `customer`, `loan`, `loan_with_region`, `loan_count_by_year`, `loan_purposes`, `state_region` (**no payments or transactions table**) | Task 3 uses `loan_status` as the lateness signal (below). Disclosed on the call. |
| Statuses `active`, `paid_off`, `defaulted` | Current, Fully Paid, Charged Off, Late (31-120 days), In Grace Period, Late (16-30 days), Default | Mapped as below. |
| Segment by "average delay" or "credit utilisation" | Neither column exists | Segment on loan amount, interest rate, term, grade, income, loan-to-income, balances, employment length, home ownership. |

Grain: `loan` and `customer` are 1:1 (270,299 rows each, all `customer_id` match both ways),
so "total loan amount per customer" equals the single loan amount.

## Status mapping (Tasks 1, 2, 5)

| Brief term | `loan_status` values | Loans |
|---|---|---|
| paid_off | Fully Paid | 76,361 |
| defaulted | Charged Off, Default | 17,863 (17,851 + 12) |
| active | Current, In Grace Period, Late (16-30 days), Late (31-120 days) | 176,075 |

Sums to 270,299.

## "Late" definition (Task 3, approved by the candidate)

`is_late` = `loan_status` in (In Grace Period, Late (16-30 days), Late (31-120 days)).
This is a **point-in-time snapshot** of loan state, not payment history: it has no delay in days
and no count of missed payments. "Late payment frequency" is therefore the *share of loans
currently late* within an interest-rate band or grade. Loans that were late in the past and have
since cured, or defaulted, are not counted as late (defaulted ones count as defaulted).

## Default rate and censoring (Task 2)

Default rate = defaulted loans / all loans originated in that year. Recent cohorts are
**right-censored**: 2019 has 46,317 Current loans against 607 Charged Off, so a raw rate falls at
the recent end regardless of true risk. Defaulted loans also drop from 7,626 (2015, 18.2% of that year's loans) to 1,122 (2016, 2.6%), and 86% of 2016 loans are still active although a 36-month loan from 2016 should have finished by 2019-2020,
which needs investigating before we read the trend. Checked: 2016 loans are 86.1% active for BOTH 36- and 60-month terms, and the latest issue month is Dec-19, so term does not explain it. Working hypothesis (unproven): statuses were recorded at different snapshot dates for different cohorts, so year-to-year default counts are not fully comparable. Mitigations to evaluate: default rate among
resolved loans only (Fully Paid + defaulted), and annotating immature years.

## Cleaning rules (applied in the staging view, raw tables stay untouched)

- `customer_id`: STRING, exactly as written (Python byte-literal text such as `b'\x8d...'`; join key only).
- `term`: TRIM the leading space.
- `type`: normalise `INDIVIDUAL`/`Individual` to Individual, `JOINT`/`Joint App` to Joint; `DIRECT_PAY` stays its own value.
- `issue_d` (`Jun-13`) parsed to a DATE; `issue_date` is identical to `issue_d` and dropped; `issue_year` kept.
- `notes` dropped (constant text `desc` in every row).
- `state_region`: drop the stray header row (`state`, `subregion`, `region`), leaving 51 states.
- `customer.emp_length`: `n/a` (18,745 rows) treated as NULL.
- `annual_inc`: 16 values under $1,000 and a maximum of $9.55M are flagged, not deleted.
- `annual_inc_joint`: NULL for non-joint loans by design (joint loans: 18,794 = non-null count).

## Load design

Raw layer loaded via the BigQuery console with explicit schemas (`sql/schemas/*.json`),
`Number of errors allowed = 0`, Header rows to skip = 1. Dates that BigQuery cannot load as DATE
(`Jun-13`) stay STRING in the raw table and become DATE in the view. Column `Tot_cur_bal` keeps its
original capitalisation (BigQuery column names are case-insensitive).

## Task 4 segmentation design

- Grain: one row per customer (= one loan). "Total loan amount" therefore equals `loan_amount`.
- Not possible: "average delay" and "credit utilisation" do not exist in the data (no payment history, no credit limits).
- Leverage proxy: `balance_to_income` = `tot_cur_bal` / `annual_inc` (total current balance across accounts, includes mortgages). Not credit utilisation.
- Clustering features: loan_amount, int_rate_pct, term_months, annual_inc, loan_to_income, balance_to_income.
- Outcomes (`is_default`, `is_late`, `status_group`) and `grade` are excluded from clustering and used only to profile the clusters afterwards (grade is nearly determined by interest rate, so it would double count).
- Outliers (annual_inc down to $34, loan_to_income up to 175, balance_to_income up to 966): handled by log-transforming / capping before scaling, never by deleting rows. 16 loans have income under $1,000; 1,179 have loan_to_income above 1.
- Income used is `annual_inc` (the primary applicant); `annual_inc_joint` is ignored (joint applications are about 7% of loans), a known simplification.
