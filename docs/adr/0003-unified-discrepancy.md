# ADR-0003: Rule 3 emits one Discrepancy type with a kind tag

Date: 2026-11-03
Status: Accepted

## Context
Rules 1 and 2 produce three differently-shaped findings: Stripe records with no
ledger counterpart, ledger entries with no Stripe counterpart, and field-level
money disagreements inside pairs that did match. Rule 3 has to hand all of them
onward.

Two consumers sit downstream, and both want to iterate one thing. The LLM
diagnosis layer sends each ambiguous case for a root cause, evidence and a
proposed fix (ADR-0001) — three shapes would mean three prompt paths and three
result schemas. The human approval gate renders a queue of proposals, which
wants a stable row shape rather than a union the UI has to switch on.

The alternative considered was a tagged union of distinct dataclasses, which is
strictly more type-safe: no field is nullable because each class carries exactly
what it has. The cost is isinstance/match dispatch at every downstream site.

## Decision
Rule 3 flattens everything into `list[Discrepancy]`, one frozen dataclass with a
`kind` field drawn from a fixed Literal set:

- `missing_in_ledger`  — Stripe has it, our portal does not (missed webhook).
- `missing_in_stripe`  — our portal has it, Stripe does not (phantom row).
- `amount_mismatch`    — matched pair, amounts disagree.
- `fee_mismatch`       — matched pair, Stripe fees disagree.

`entry` and `record` are nullable because a one-sided discrepancy genuinely has
only one side. `delta_cents` is None for the missing_* kinds, where no
subtraction is defined.

Every Discrepancy carries `stripe_payment_id` and `region` flat, so rule 4 can
group by region without reaching into the nested records.

## Consequences
- One prompt shape, one approval row, one loop downstream.
- `kind` is the fixed root-cause vocabulary the LLM layer selects from, so that
  list is now pinned here rather than invented later at the prompt.
- Nullability is the price: a consumer reading `.entry` on a `missing_in_ledger`
  gets None, and mypy will not catch a wrong-kind access the way a union would.
  Downstream code must branch on `kind`, not on which fields are populated.
- Adding a rule means adding a `kind`, which is a one-line change here but a new
  case for every consumer that switches on it.
- Region drift between sides is still unmodeled: rule 2 does not compare region,
  so a pair whose two halves disagree on region is reported under the ledger's
  region with no finding raised. Deferred, not solved.
