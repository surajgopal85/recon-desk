"""Rule 2: verify amount and fee parity inside pairs that rule 1 matched."""

from dataclasses import dataclass
from typing import Literal

from recon_engine.models import LedgerEntry, StripeRecord

# The only two fields rule 2 compares.
ParityField = Literal["amount_cents", "fee_cents"]


@dataclass(frozen=True)
class FieldMismatch:
    """One field disagreeing within one matched pair.

    Carries both records so downstream rules (and the LLM diagnosis layer) have
    the evidence in hand without re-reading the source reports.
    """

    entry: LedgerEntry
    record: StripeRecord
    field_name: ParityField
    ledger_cents: int
    stripe_cents: int

    @property
    def delta_cents(self) -> int:
        """Ledger minus Stripe. Positive means our ledger booked the larger number."""
        return self.ledger_cents - self.stripe_cents


def verify_parity(pairs: list[tuple[LedgerEntry, StripeRecord]]) -> list[FieldMismatch]:
    """Compare ``amount_cents`` and ``fee_cents`` within each matched pair.

    Contract
    --------
    - Input is ``MatchResult.matched`` from rule 1. Both halves of a pair are
      assumed to share an SPI; this rule does not re-check that.
    - ONLY ``amount_cents`` and ``fee_cents`` are compared. ``region`` and
      ``timestamp`` are not: the two systems legitimately stamp a payment
      seconds apart, so timestamp drift is not a discrepancy.
    - One FieldMismatch per disagreeing field, so a pair that disagrees on both
      amount and fee yields TWO mismatches. An amount drift and a fee drift have
      different root causes and are diagnosed separately — see ADR-0002.
    - A pair agreeing on both fields contributes nothing to the output.
    - Output order is deterministic: input pair order, and within a pair,
      amount before fee.
    - Inputs are not mutated.

    Returns:
        Every field-level disagreement found, in the order described above.
        Empty list means every matched pair ties out.
    """
    field_mismatches = []

    for entry, record in pairs:
        if entry.amount_cents != record.amount_cents:
            field_mismatches.append(FieldMismatch(
              entry=entry,
              record=record,
              field_name="amount_cents",
              ledger_cents=entry.amount_cents,
              stripe_cents=record.amount_cents
            ))
        if entry.fee_cents != record.fee_cents:
            field_mismatches.append(FieldMismatch(
              entry=entry,
              record=record,
              field_name="fee_cents",
              ledger_cents=entry.fee_cents,
              stripe_cents=record.fee_cents
            ))

    return field_mismatches
