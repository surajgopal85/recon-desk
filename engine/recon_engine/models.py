"""Core record types for reconciliation.

Both sides of a reconciliation share the same shape: a Stripe payment ID, the
region that took the payment, the gross amount, Stripe's fee, and when it
happened. The ledger is our portal's view; the Stripe record is Stripe's.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LedgerEntry:
    """One payment as our internal portal recorded it."""

    stripe_payment_id: str
    region: str
    amount_cents: int
    fee_cents: int
    timestamp: str  # ISO-8601


@dataclass(frozen=True)
class StripeRecord:
    """One payment as Stripe reported it."""

    stripe_payment_id: str
    region: str
    amount_cents: int
    fee_cents: int
    timestamp: str  # ISO-8601
