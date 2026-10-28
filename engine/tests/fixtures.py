"""Synthetic reconciliation fixtures.

Shaped like SAWA's Stripe Connect data (regions as child accounts, one row per
payment) but entirely invented: no real payment IDs, regions or amounts.

Two discrepancies are planted, and only two:
  1. ``pi_cas_0007_ghostwebhook`` — present in Stripe, missing from the ledger.
     (Stands in for a webhook our portal never received.)
  2. ``pi_pie_0042_phantomrow``   — present in the ledger, missing from Stripe.
     (Stands in for a row our portal wrote that Stripe never saw.)

The other nine SPIs appear on both sides, so rule 1 should report 9 matches.
Amounts and fees deliberately disagree on one shared SPI
(``pi_pie_0019_shortfee``) — rule 1 must ignore that; it is rule 2's problem.
"""

from recon_engine.models import LedgerEntry, StripeRecord

# SPIs present on both sides.
SHARED_SPIS = [
    "pi_cas_0001_entryfee",
    "pi_cas_0002_entryfee",
    "pi_cas_0003_portfolio",
    "pi_pie_0011_entryfee",
    "pi_pie_0012_portfolio",
    "pi_pie_0019_shortfee",
    "pi_hpl_0021_entryfee",
    "pi_hpl_0022_entryfee",
    "pi_hpl_0030_portfolio",
]


def sample_ledger() -> list[LedgerEntry]:
    """Ten portal-side rows: the nine shared SPIs plus one Stripe never saw."""
    return [
        LedgerEntry("pi_cas_0001_entryfee", "cascadia", 2500, 103, "2026-01-12T14:02:11Z"),
        LedgerEntry("pi_cas_0002_entryfee", "cascadia", 2500, 103, "2026-01-12T16:44:03Z"),
        LedgerEntry("pi_cas_0003_portfolio", "cascadia", 7500, 248, "2026-01-13T09:15:40Z"),
        LedgerEntry("pi_pie_0011_entryfee", "piedmont", 2500, 103, "2026-01-14T11:27:55Z"),
        LedgerEntry("pi_pie_0012_portfolio", "piedmont", 7500, 248, "2026-01-14T12:01:09Z"),
        # Shared SPI, but the ledger booked a different fee than Stripe did.
        # Rule 1 still matches it; rule 2 is what catches the 103 vs. 118 gap.
        LedgerEntry("pi_pie_0019_shortfee", "piedmont", 2500, 103, "2026-01-15T08:33:21Z"),
        LedgerEntry("pi_hpl_0021_entryfee", "high_plains", 2500, 103, "2026-01-16T10:05:02Z"),
        LedgerEntry("pi_hpl_0022_entryfee", "high_plains", 2500, 103, "2026-01-16T10:58:47Z"),
        LedgerEntry("pi_hpl_0030_portfolio", "high_plains", 7500, 248, "2026-01-17T13:22:30Z"),
        # PLANTED (2): in the ledger, absent from Stripe.
        LedgerEntry("pi_pie_0042_phantomrow", "piedmont", 2500, 103, "2026-01-18T15:40:00Z"),
    ]


def sample_stripe() -> list[StripeRecord]:
    """Ten Stripe-side rows: the nine shared SPIs plus one the ledger missed."""
    return [
        StripeRecord("pi_cas_0001_entryfee", "cascadia", 2500, 103, "2026-01-12T14:02:09Z"),
        StripeRecord("pi_cas_0002_entryfee", "cascadia", 2500, 103, "2026-01-12T16:44:01Z"),
        StripeRecord("pi_cas_0003_portfolio", "cascadia", 7500, 248, "2026-01-13T09:15:38Z"),
        StripeRecord("pi_pie_0011_entryfee", "piedmont", 2500, 103, "2026-01-14T11:27:52Z"),
        StripeRecord("pi_pie_0012_portfolio", "piedmont", 7500, 248, "2026-01-14T12:01:06Z"),
        # Same SPI as the ledger row above, different fee. Rule 1 ignores this.
        StripeRecord("pi_pie_0019_shortfee", "piedmont", 2500, 118, "2026-01-15T08:33:18Z"),
        StripeRecord("pi_hpl_0021_entryfee", "high_plains", 2500, 103, "2026-01-16T10:04:59Z"),
        StripeRecord("pi_hpl_0022_entryfee", "high_plains", 2500, 103, "2026-01-16T10:58:44Z"),
        StripeRecord("pi_hpl_0030_portfolio", "high_plains", 7500, 248, "2026-01-17T13:22:27Z"),
        # PLANTED (1): in Stripe, absent from the ledger.
        StripeRecord("pi_cas_0007_ghostwebhook", "cascadia", 7500, 248, "2026-01-18T17:11:12Z"),
    ]
