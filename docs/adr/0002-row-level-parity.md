# ADR-0002: Rule 2 verifies parity row by row, not per-region aggregate

Date: 2026-11-02
Status: Accepted

## Context
The engine spec states rule 2 as "ensure the $ collected in Stripe matches the
# of txns per region less Stripe fees." That admits two readings: compare each
matched pair's amount and fee field by field, or compare per-region sums.

Aggregates hide offsetting errors. Two rows in the same region off by +15 and
-15 cents sum to zero: the region ties out and both rows are still wrong. An
aggregate check can also only report *that* a region disagrees, never which row
caused it — so it produces no evidence to diagnose or to show a human.

Rule 3 ("list every discrepancy") and rule 4 (propose dollars owed, justified
with evidence) both need row-level granularity. Rule 4 already computes the
per-region totals it pays out on, so aggregating in rule 2 as well would compute
the same sums twice in two places that could drift apart.

## Decision
Rule 2 takes the matched pairs from rule 1 and compares `amount_cents` and
`fee_cents` field by field, emitting one mismatch record per disagreeing field
with the signed delta. A row that disagrees on both fields produces two
mismatches: an amount drift and a fee drift have different root causes (stale
price vs. stale fee assumption) and the LLM layer diagnoses per cause.

Per-region aggregation happens once, in rule 4, over the verified rows.

## Consequences
- Offsetting errors within a region can no longer cancel out unnoticed.
- Every rule 2 finding carries its own evidence: the pair, the field, the delta.
- Rule 2's output is a flat list whose length is bounded by matched pairs x 2,
  not by region count — more findings to triage, each individually actionable.
- Rule 4 owns region math alone, so there is one place where totals are defined.
- Rows that rule 1 never matched are out of scope here; they are already
  discrepancies from rule 1 and flow straight to rule 3.
