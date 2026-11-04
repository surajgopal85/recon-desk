"""Rule 3: flatten every rule 1 and rule 2 finding into one discrepancy list."""

from dataclasses import dataclass
from typing import Literal

from recon_engine.match import MatchResult
from recon_engine.models import LedgerEntry, StripeRecord
from recon_engine.verify import FieldMismatch

# The fixed root-cause vocabulary. See ADR-0003.
DiscrepancyKind = Literal[
    "missing_in_ledger",
    "missing_in_stripe",
    "amount_mismatch",
    "fee_mismatch",
]

# Maps rule 2's compared field to the kind it surfaces as.
_MISMATCH_KINDS: dict[str, DiscrepancyKind] = {
    "amount_cents": "amount_mismatch",
    "fee_cents": "fee_mismatch",
}


@dataclass(frozen=True)
class Discrepancy:
    """One thing that did not tie out, in the shape downstream consumes.

    ``stripe_payment_id`` and ``region`` are flat so rule 4 can group by region
    without reaching into the nested records.

    Which fields are populated depends on ``kind`` — branch on the tag, never on
    whether a field happens to be None:

    ===================  =======  ========  ============
    kind                 entry    record    delta_cents
    ===================  =======  ========  ============
    missing_in_ledger    None     set       None
    missing_in_stripe    set      None      None
    amount_mismatch      set      set       set
    fee_mismatch         set      set       set
    ===================  =======  ========  ============
    """

    kind: DiscrepancyKind
    stripe_payment_id: str
    region: str
    entry: LedgerEntry | None = None
    record: StripeRecord | None = None
    delta_cents: int | None = None


def collect_discrepancies(
    match_result: MatchResult,
    mismatches: list[FieldMismatch],
) -> list[Discrepancy]:
    """Flatten rule 1's unmatched records and rule 2's field mismatches into one list.

    Contract
    --------
    - Takes the OUTPUTS of rules 1 and 2, not the raw reports, so each rule stays
      independently testable.
    - Diagnoses nothing. ``kind`` states what disagreed, never why — the root
      cause and proposed fix come from the LLM layer later (ADR-0001).
    - ``MatchResult.matched`` is ignored here: a pair that matched and tied out is
      not a discrepancy, and a pair that matched but disagreed on money already
      arrived via ``mismatches``.

    Mind the inversion when mapping rule 1's lists — the names flip:
    - ``unmatched_in_stripe`` (Stripe records with no ledger partner)
      becomes kind ``missing_in_ledger``.
    - ``unmatched_in_ledger`` (ledger entries with no Stripe partner)
      becomes kind ``missing_in_stripe``.

    Field notes:
    - ``region`` comes from whichever record exists; for a mismatch, from the
      ledger entry (our portal's view is authoritative for reporting).
    - ``delta_cents`` is None for both missing_* kinds — with one side absent,
      there is nothing to subtract.

    Output order is deterministic:
      1. every ``missing_in_ledger``, in rule 1's ``unmatched_in_stripe`` order
      2. every ``missing_in_stripe``, in rule 1's ``unmatched_in_ledger`` order
      3. every mismatch, in the order rule 2 emitted them

    Inputs are not mutated.

    Returns:
        Every discrepancy found, in the order above. Empty list means the two
        reports reconcile exactly.
    """
    discrepancy_list = []
    for record in match_result.unmatched_in_stripe:
        discrepancy_list.append(Discrepancy(
            kind="missing_in_ledger",
            stripe_payment_id=record.stripe_payment_id,
            region=record.region,
            entry=None,
            record=record,
            delta_cents=None,
        ))

    for entry in match_result.unmatched_in_ledger:
        discrepancy_list.append(Discrepancy(
            kind="missing_in_stripe",
            stripe_payment_id=entry.stripe_payment_id,
            region=entry.region,
            entry=entry,
            record=None,
            delta_cents=None,
        ))

    for mismatch in mismatches:
        discrepancy_list.append(Discrepancy(
            kind=_MISMATCH_KINDS[mismatch.field_name],
            stripe_payment_id=mismatch.entry.stripe_payment_id,
            region=mismatch.entry.region,
            entry=mismatch.entry,
            record=mismatch.record,
            delta_cents=mismatch.delta_cents,
        ))

    return discrepancy_list
