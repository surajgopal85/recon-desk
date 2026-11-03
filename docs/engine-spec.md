# Reconciliation engine — what it computes

Not a decision record. Decisions live in `docs/adr/`; this is the standing
description of the engine's domain, inputs and rules.

## Domain
Synthetic, modeled on SAWA (Scholastic Art and Writing Awards) run on Stripe
Connect. Each year SAWA manages regional payments through Connect: we own the
parent account, regional affiliates own the child accounts. Every region accepts
Stripe payments, and a set split (TBD) of fees returns to our backend after
Stripe takes its cut.

Regions come in two flavors:
- **Self-serve** — the region has its own child account and keeps its split.
- **Reconciled** — the region declines a child account, so the parent holds all
  funds in that region and pays the affiliate a lump sum at period end.

The engine's job is to confirm that what we received and what we owe affiliates
are both accurate, and to evidence every claim it makes.

## Inputs
- Stripe reports
- Portal reports (our own system)

## Rules
Run in order. Rule 1 feeds rule 2; rule 3 reports on 1 and 2; rule 4 is the
money question that depends on all three.

1. **Match SPIs** — pair Stripe payment IDs across the Stripe and portal
   reports. Identity only; no amounts. *(implemented: `match_by_spi`)*
2. **Verify parity row by row** — for each matched pair, confirm the amount and
   the Stripe fee agree between the two sides. Row-level, not per-region
   aggregate — see ADR-0002.
3. **List discrepancies** — every case where rule 1 or rule 2 disagreed.
4. **Propose dollars owed per region** — with the evidentiary reports and a
   summary of works paid via Stripe behind each number.

## Boundaries
- Rules 1–3 are deterministic and model-free. Only the ambiguous leftovers reach
  the LLM, which diagnoses and proposes — see ADR-0001.
- Nothing the engine proposes is ever executed. The human approval gate is the
  product.

## Open questions
- The fee split percentage is still TBD.
- Duplicate SPIs within one side are currently assumed away, not handled.
