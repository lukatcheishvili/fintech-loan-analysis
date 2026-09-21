# AGENT.md: project context for AI assistants

Read this first in any new session. It records what the project is, what has been done, the decisions made, and how the
user likes to work. Facts here were verified against the source CSVs and the Hex notebook unless marked otherwise.

## 1. What this project is
A hiring take-home exercise (fintech loan analysis, "Pave Bank" data task). The candidate analyses the Kaggle
"BigQuery Fintech Dataset" with **SQL in BigQuery** and **SQL + Python in Hex**, in five tasks:
1. Loan outcomes (active / paid_off / defaulted) by origination year, bar chart.
2. Loan performance by year (avg rate, principal, default rate), default-rate line chart.
3. Payment behaviour: late payments vs interest rate (scatter or heatmap).
4. Customer segmentation in Python (cluster or bubble chart).
5. Markdown write-up: what predicts default or lateness, and what lending rules to flag or change.

A follow-up call with three data-literate business users will discuss method, findings and challenges.
The task PDF is confidential and is deliberately **not** in this repository.

## 2. Status (as of 2026-09-21)
All five tasks are built in Hex and the notebook ran cleanly top to bottom. Every number in the write-ups was checked
against local pandas calculations or against Hex outputs. Remaining work is listed in section 9.

## 3. Environment
- **GCP project** `pave-bank-fintech`; **BigQuery dataset** `fintech_test` (location US).
- Raw tables loaded through the BigQuery console with explicit schemas (`sql/schemas/*.json`, legacy type names
  INTEGER / FLOAT / BOOLEAN / STRING): `customer`, `loan`, `loan_with_region`, `loan_count_by_year`, `loan_purposes`,
  `state_region`. Raw tables are never modified.
- **`v_loans`** (`sql/00_staging.sql`) is the cleaned view and the single source of truth. Every task reads it.
- **Hex** project "Pave Bank - Fintech Loan Analysis" (the published app link is in `README.md`; whether outsiders can open it depends on the Hex sharing settings). Connection
  `pave-bank-bigquery` uses a read-only service account `hex-reader` (roles: BigQuery Data Viewer, Job User, Read Session
  User). The key file lives outside the repo. Never commit keys.
- **Local**: Windows 11, PowerShell, Python 3.12, project `.venv` (pandas, plotly, kaleido, ...). Raw CSVs are in
  `data/raw/` (gitignored). In `.venv`, scikit-learn's KMeans is blocked by a Windows Application Control policy: test
  clustering code with the system `python` instead (it has sklearn but not plotly).
- **Hex quirks**: scikit-learn needed `!pip --python /ipython/.venv/bin/python install scikit-learn`; Hex's native
  scatter cannot size bubbles by a field, so bubble charts are Plotly Python cells; only the last expression of a cell
  reliably displays, so cells end with the object to show.

## 4. The dataset (verified)
- 270,299 loans (issue years 2012-2019, latest issue month Dec 2019), one loan per customer (`loan` and `customer` match
  1:1 on `customer_id`).
- **No payments or transactions table**, no delay-in-days, no credit utilisation. The brief assumed they exist.
- Statuses: Current 170,461; Fully Paid 76,361; Charged Off 17,851; Late (31-120 days) 3,174; In Grace Period 1,638;
  Late (16-30 days) 802; Default 12.
- Data problems handled in `v_loans`: `customer_id` is a hashed byte string stored as text (join key only; `loan_id` is
  the readable handle); `n/a` is a missing-value code in `emp_length` (18,745); a stray header row inside
  `state_region`; five spellings of application type; a leading space in `term`; redundant `issue_date` and constant
  `notes` columns; income from $34 to $9.55M; `annual_inc_joint` 93% NULL by design.
- **Snapshot inconsistency**: 86% of 2016 loans are still "active" for both 36- and 60-month terms although the data
  runs to Dec 2019, and 29% of 2014's 36-month loans are still active (0% for 2013 and 2015). Working hypothesis
  (unproven): statuses come from different snapshot dates per cohort.

## 5. Definitions (all in `v_loans`)
- `status_group`: paid_off = Fully Paid; defaulted = Charged Off + Default; active = Current, In Grace Period,
  Late (16-30), Late (31-120).
- `is_default` = defaulted; `is_resolved` = paid_off or defaulted.
- `is_late` = In Grace Period, Late (16-30 days) or Late (31-120 days). **This is a Task 3 workaround** (approved by the
  user): a snapshot of current status, not payment history. Late rates use **active loans** as the denominator.
- Default rate is shown two ways: against all loans (biased low for recent years) and against resolved loans only.
- `balance_to_income` = total current balance / income is a **leverage proxy, not credit utilisation**.

## 6. Key results (verified in Hex)
- Task 1: volume 2,594 (2012) to 51,737 (2019). Default share 14.5-18.2% for 2012-2015, 2.6% for 2016.
- Task 2: all-loans default rate 18.2% (2015) falls to 2.6% (2016); resolved-only is 20.2% to 18.6%. Average rate stays
  12.6-14.5%; average principal about $13.7k-$16.5k.
- Task 3: 5,614 of 176,075 active loans (3.19%) are late. Late rate rises from 0.6% (4-6% rate band) to 14.9% (30-32%),
  and holds within each term. 36-month loans are late more often than 60-month in 11 of 14 bands.
- Task 4: k-means, k = 5, six standardised features (loan amount, rate, term, income, loan-to-income, balance-to-income),
  after capping at the 1st/99th percentile and log-transforming the skewed three. Silhouette is about 0.20 for every
  k = 3..8 (cannot choose); k = 5 chosen on stability and interpretability (judgement call). Segment default rates
  (resolved) range 10.6% to 32.3%; late rates 2.5% to 4.0%. Outcomes were not used to build the segments.
- Task 5: grade / interest rate are by far the strongest predictors (default 5.8% grade A to 48.1% grade G). Logistic
  model test AUC 0.697 (default) and 0.674 (late); grade or rate alone about 0.68 / 0.67. Rules tested historically:
  grade E-G flags 10.2% of resolved loans at 40.7% default vs 16.5%; 60-month AND rate >= 16% flags 12.4% at 39.0% vs
  16.1%. Even the best rules flag many good loans (60-67% of flagged loans did not default), so they suit review and
  pricing, not automatic declines.

## 7. Repository map
| Path | What it holds |
|---|---|
| `sql/00_staging.sql` | The `v_loans` view (all definitions) |
| `sql/01_validate_load.sql`, `sql/02_validate_staging.sql` | Load and view validation queries with expected values |
| `sql/10_*`, `11_*`, `20_*`, `30_*`, `40_*` | Task 1-4 queries |
| `sql/schemas/*.json` | BigQuery table schemas (generated by `scripts/make_schemas.py`) |
| `scripts/profile_csvs.py` | Profiles every CSV in `data/raw/` into `docs/schema_profile.md` |
| `notebooks/task*.py` | The Python cells used in Hex (Tasks 3-5), kept as scripts |
| `Pave Bank - Fintech Loan Analysis.ipynb` | Snapshot export of the Hex project (SQL cells appear as commented code, no outputs; native Hex charts are not exported) |
| `docs/assumptions.md` | Every judgement call and cleaning rule |
| `docs/talk_track.md` | Call preparation: opening, per-task lines, challenges, likely questions |
| `docs/schema_profile.md` | Auto-generated column profile of the source CSVs |

## 8. Conventions and how the user likes to work
- **Guide one step at a time**, with detailed and precise explanations. Give one step, wait for the user's result, check
  it against expected values, then continue. The user objected once to receiving several steps at once.
- Give **paste-ready code in code blocks** and say which terminal or editor it belongs in (a PowerShell command was once
  pasted into the BigQuery editor). Copy only what is inside code blocks.
- **Compute expected values locally** (pandas on `data/raw/`) before asking the user to run something, and compare their
  screenshots cell by cell. Say plainly what was not verified.
- **Comment style** the user asked for: trailing comments aligned in one column (col 64); lines too long get their
  comment on the line above; header comment at the top; never change the code itself. Verify with an AST comparison.
- The user asked for Opus to plan and Sonnet to write code.
- **Never commit**: `.env` (holds a GitHub token), `data/` (source CSVs), `.venv/`, service-account key files, or the task
  PDF. `.gitignore` covers these; check `git status` before every commit.

## 9. Open items
1. Review of the Hex export found text to fix in Hex (then re-export the `.ipynb`): Task 5 Markdown still says
   "6.1% to 33.7%" and "22.7%" (correct: **6.0% to 33.8%** and **22.6%**) and ends with a "Where the claims come from"
   section that should be deleted; Task 4 Markdown footnote is broken (put "(resolved loans)" / "(active loans)" in the
   table headers); Task 3 Markdown has an internal "Where each claim comes from" section to delete; Task 2 "Interesting
   findings" contains coaching wording; typo "lowns" in the first SQL comment.
2. **The Task 5 lending-rules cell (`notebooks/task5_rules.py`) was missing from the exported notebook**; add it to Hex and
   check its table against the numbers above.
3. Task 4's "k = 5 is stable across seeds" claim comes from a separate local test (adjusted Rand index 0.993 for k = 5,
   0.975 for k = 4); add a Hex cell that reproduces it or label it as checked separately.
4. Share the Hex project with the interviewers (view access), check the Hex trial end date and BigQuery table expiry
   (sandbox tables expire after 60 days), and keep a PDF backup.
