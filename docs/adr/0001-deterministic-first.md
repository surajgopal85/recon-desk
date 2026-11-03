# ADR-0001: Deterministic matching first; the LLM only diagnoses what rules can't

Date: 2026-10-25
Status: Accepted

## Context
Recon Desk reconciles an internal ledger against Stripe. Most mismatches are
mechanical: a Stripe payment ID lines up, and amounts tie out once Stripe's fee
is removed. A minority are genuinely ambiguous — a missing webhook, a refund that
never propagated, a payment straddling a period boundary — and need a judgment
call with an explanation. Sending everything to an LLM is slower, costs per call,
and risks confident-but-wrong answers on cases arithmetic already settles. Pure
rules can flag those hard cases but can't explain them or propose a fix.

## Decision
Fixed pipeline order: (1) deterministic rules match and verify the clean cases;
(2) only the leftover ambiguous cases go to the LLM, which returns a root cause
from a fixed list, its evidence (record IDs), and a proposed fix; (3) every LLM
proposal goes to a human for approval before anything is acted on.

## Consequences
- Cost and latency scale with the number of *ambiguous* cases, not total volume.
- Every mechanical match is reproducible and auditable with no model in the path.
- Answers "when should an LLM not be in the loop?" cleanly — most of the time.
- The rules layer is now a real thing to build; quality lives in how well
  "ambiguous" is defined (what escalates vs. what rules decide).
- Needs an eval set to prove the LLM is right on the cases that do reach it.