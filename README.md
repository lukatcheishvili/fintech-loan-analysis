# Fintech loan analysis (BigQuery + Hex)

Analysis of a public fintech loan dataset (270,299 loans, 2012-2019): loan outcomes, default rates, late payments,
customer segmentation, and lending-rule recommendations. SQL runs in BigQuery, and the analysis notebook runs in Hex
(SQL + Python).

## Headline findings
- The lender's own **grade / interest rate** is by far the strongest predictor of default (5.8% for grade A up to
  48.1% for grade G) and of late payment. A model using every other available characteristic reaches a test AUC of only
  0.70 (default) and 0.67 (late).
- Simple rules such as *grade E-G* or *60-month term with rate of 16% or more* flag about 10-12% of loans that default
  around 40% of the time, but they also flag many loans that turn out fine, so they suit review and pricing rather than
  automatic declines.
- Loan statuses appear to come from different snapshot dates (86% of 2016 loans are still "active"), so plain default
  rates by year are misleading; the analysis reports them two ways.

## Data limitations
The dataset has **no payments table, no days-late field and no credit-utilisation field**. "Late" is therefore derived
from current loan status, and customer segments use loan/customer attributes plus a balance-to-income leverage proxy.
See `docs/assumptions.md` for every judgement call and the reasons behind it.

## Repository layout
| Path | Contents |
|---|---|
| `sql/` | BigQuery queries: the cleaned view (`00_staging.sql`), load validation, and one file per task |
| `sql/schemas/` | Explicit BigQuery table schemas for the six source CSVs |
| `notebooks/` | The Python cells used in Hex (Tasks 3-5), as scripts |
| `scripts/` | Helper scripts: CSV profiling and schema generation |
| `docs/` | Assumptions, call talk track, generated schema profile |
| `Pave Bank - Fintech Loan Analysis.ipynb` | Export of the Hex notebook (SQL cells appear as commented code) |
| `AGENT.md` | Full project context for AI assistants |

## Reproducing
1. Download the Kaggle dataset "BigQuery Fintech Dataset" into `data/raw/` (not included in this repository).
2. Create a BigQuery dataset (`fintech_test`) and upload the six CSVs using the schemas in `sql/schemas/`.
3. Run `sql/00_staging.sql` to create `v_loans`, then the validation queries and task queries.
4. Use the scripts in `notebooks/` as Hex Python cells (needs pandas, scikit-learn, plotly).

Optional local profiling: `python scripts/profile_csvs.py` (needs pandas and tabulate).
