# Talk track: follow-up call (about 10 minutes + questions)

Every number below was checked against the Hex notebook or the source CSVs.

## 1. Opening (60 seconds)
- **Question:** which loan and customer characteristics predict default and late payment, and what lending rules follow?
- **Data:** public fintech dataset, 270,299 loans (2012-2019), one loan per customer. Loaded to BigQuery (`fintech_test`), analysed in Hex with SQL and Python.
- **Method in one line:** raw tables loaded as-is with explicit schemas and validated against the source files (row counts, sums, NULL counts); one cleaned view (`v_loans`) holds every definition, so all five tasks read the same logic.
- **Bottom line:** the lender's own grade / interest rate is by far the strongest predictor; simple rules can flag risky loans but flag many good ones, so use them for review and pricing, not automatic declines.

## 2. Walkthrough: one line per task
1. **Loan outcomes.** Volume grew from 2,594 loans (2012) to 51,737 (2019). 2016 looks odd: 86% of 2016 loans are still "active" and only 2.6% defaulted, for both 36- and 60-month terms.
2. **Performance.** Two default rates: all loans (18.2% in 2015, collapsing to 2.6% in 2016) vs resolved loans only (20.2% to 18.6%). The gap is unfinished loans, not credit quality. Average rate 12.6-14.5%, average principal about $13.7k-$16.5k every year.
3. **Payment behaviour.** No payments table exists, so "late" = current status in grace period / 16-30 / 31-120 days late. 5,614 of 176,075 active loans (3.19%) are late; late rate rises from 0.6% (4-6% rate band) to 14.9% (30-32%), and holds within each term.
4. **Segmentation.** k-means, k = 5 on six standardised features; default rates by segment range 10.6% to 32.3% although outcomes were not used to build the groups. Silhouette is about 0.2, so segments overlap.
5. **Insights.** Grade A to G: default 5.8% to 48.1%. Model AUC 0.697 (default) and 0.674 (late). Rules: grade E-G flags 10.2% of loans at 40.7% default vs 16.5%.

## 3. Challenges (say these openly)
- **The dataset did not match the brief.** No payments table, no delay-in-days, no credit utilisation. I agreed a workaround (late from loan status; a leverage proxy instead of utilisation) and documented it in `docs/assumptions.md`.
- **Loan statuses look like they come from different snapshot dates** (2016 loans mostly "active" although the data runs to Dec 2019). I show two default-rate definitions and label 2018-2019 as unreliable. Working hypothesis, unproven.
- **Data hygiene:** hashed customer IDs stored as text, `n/a` as a missing-value code, a stray header row inside a lookup table, inconsistent `type` spellings, a leading space in `term`. All handled in the view, raw tables untouched.
- **Tooling:** Hex's scatter cannot size bubbles by a field, so I used a Python chart; scikit-learn needed installing into the right environment; and I found and fixed an order-dependence bug in my quintile bucketing (numbers shifted by 0.1-0.2 points between runs).

## 4. Likely questions
- **How confident are you?** Moderate. Ranking of predictors is solid and consistent across three views (bucket rates, single-feature AUC, model). Predictive strength is modest (AUC about 0.70).
- **Why is the interest rate the top predictor, does it cause default?** No. The lender sets the rate from its own risk grade, so it mostly shows that pricing tracks risk. Other characteristics add only about 0.02 AUC.
- **Why k = 5?** Silhouette cannot choose (0.198-0.207 for k = 3 to 8). k = 5 was the most stable across random restarts among k = 4-7 (similarity 0.993 vs 0.975 for k = 4) and adds a distinct high-balance group. Judgement call.
- **Why resolved-only default rates?** Open loans cannot default yet. Resolved-only is less biased but still imperfect for recent years.
- **What would you do with more time or data?** Payment history and credit limits; rejected applications (we only see approved loans); out-of-time validation of the rules; a proper survival model for censoring.
- **What could break the rules in production?** Thresholds were chosen by eye and tested on the same data; snapshot inconsistency; population drift; selection bias.
- **Why not delete the outliers?** They were capped at the 1st/99th percentile so no customers disappear from the segments.

## 5. Before the call
- Confirm the Hex project is shared with the interviewers (view access) and the trial has not expired.
- Check BigQuery table expiry (sandbox tables expire after 60 days).
- Keep a PDF/screenshot copy of the notebook as a backup.
