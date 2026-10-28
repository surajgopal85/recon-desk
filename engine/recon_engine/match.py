"""Rule 1: match ledger entries to Stripe records by Stripe payment ID."""

from dataclasses import dataclass, field

from recon_engine.models import LedgerEntry, StripeRecord


@dataclass
class MatchResult:
    """Outcome of an SPI match: the pairs, plus what each side was missing."""

    matched: list[tuple[LedgerEntry, StripeRecord]] = field(default_factory=list)
    unmatched_in_ledger: list[LedgerEntry] = field(default_factory=list)
    unmatched_in_stripe: list[StripeRecord] = field(default_factory=list)


def match_by_spi(ledger: list[LedgerEntry], stripe: list[StripeRecord]) -> MatchResult:
    """Pair ledger entries with Stripe records that share a Stripe payment ID.

    Contract
    --------
    - Matching is on ``stripe_payment_id`` alone. Amounts, fees, regions and
      timestamps are NOT compared here — that is rule 2's job. A pair whose
      amounts disagree is still ``matched`` as far as this rule is concerned.
    - Every input record appears exactly once in the result: an SPI present on
      both sides yields one entry in ``matched``; an SPI present only in
      ``ledger`` yields one entry in ``unmatched_in_ledger``; an SPI present
      only in ``stripe`` yields one entry in ``unmatched_in_stripe``.
    - Inputs are not mutated.

    Returns:
        A MatchResult partitioning both inputs into matched pairs and the
        leftovers on each side.
    """
    raise NotImplementedError
