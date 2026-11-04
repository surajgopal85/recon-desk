"""Synthetic reconciliation fixtures.

Shaped like SAWA's Stripe Connect data (regions as child accounts, one row per
payment) but entirely invented: no real payment IDs, regions or amounts.

Two discrepancies are planted, and only two:
  1. ``pi_cas_0007_ghostwebhook`` — present in Stripe, missing from the ledger.
     (Stands in for a webhook our portal never received.)
  2. ``pi_pie_0042_phantomrow``   — present in the ledger, missing from Stripe.
     (Stands in for a row our portal wrote that Stripe never saw.)

The other nine SPIs appear on both sides, so rule 1 should report 9 matches.

Three of those nine shared SPIs deliberately disagree on money, for rule 2 to
catch. Rule 1 must match all three anyway — identity only:
  - ``pi_pie_0019_shortfee``    — fee differs, amount agrees (103 vs. 118).
  - ``pi_hpl_0022_amountdrift`` — amount differs, fee agrees (2500 vs. 3000).
  - ``pi_cas_0003_bothoff``     — both differ, so rule 2 reports two mismatches.
Fields are isolated on purpose: a real amount change would move the fee too, but
isolating them keeps a rule that only checks one field from passing by accident.
The remaining six shared SPIs tie out exactly.
"""

from recon_engine.models import LedgerEntry, StripeRecord

# SPIs present on both sides.
SHARED_SPIS = [
    "pi_cas_0001_entryfee",
    "pi_cas_0002_entryfee",
    "pi_cas_0003_bothoff",
    "pi_pie_0011_entryfee",
    "pi_pie_0012_portfolio",
    "pi_pie_0019_shortfee",
    "pi_hpl_0021_entryfee",
    "pi_hpl_0022_amountdrift",
    "pi_hpl_0030_portfolio",
]

# SPIs present on only one side. Rule 1 reports these; rule 2 never sees them.
STRIPE_ONLY_SPI = "pi_cas_0007_ghostwebhook"
LEDGER_ONLY_SPI = "pi_pie_0042_phantomrow"

# Shared SPIs that rule 2 should flag, and what it should find on each.
FEE_DRIFT_SPI = "pi_pie_0019_shortfee"
AMOUNT_DRIFT_SPI = "pi_hpl_0022_amountdrift"
BOTH_DRIFT_SPI = "pi_cas_0003_bothoff"


def sample_ledger() -> list[LedgerEntry]:
    """Ten portal-side rows: the nine shared SPIs plus one Stripe never saw."""
    return [
        LedgerEntry("pi_cas_0001_entryfee", "cascadia", 2500, 103, "2026-01-12T14:02:11Z"),
        LedgerEntry("pi_cas_0002_entryfee", "cascadia", 2500, 103, "2026-01-12T16:44:03Z"),
        # Shared SPI off on BOTH amount and fee: +500 and +17 against Stripe.
        LedgerEntry("pi_cas_0003_bothoff", "cascadia", 7500, 248, "2026-01-13T09:15:40Z"),
        LedgerEntry("pi_pie_0011_entryfee", "piedmont", 2500, 103, "2026-01-14T11:27:55Z"),
        LedgerEntry("pi_pie_0012_portfolio", "piedmont", 7500, 248, "2026-01-14T12:01:09Z"),
        # Shared SPI, but the ledger booked a different fee than Stripe did.
        # Rule 1 still matches it; rule 2 is what catches the 103 vs. 118 gap.
        LedgerEntry("pi_pie_0019_shortfee", "piedmont", 2500, 103, "2026-01-15T08:33:21Z"),
        LedgerEntry("pi_hpl_0021_entryfee", "high_plains", 2500, 103, "2026-01-16T10:05:02Z"),
        # Shared SPI off on amount only: -500 against Stripe, fee agrees.
        LedgerEntry("pi_hpl_0022_amountdrift", "high_plains", 2500, 103, "2026-01-16T10:58:47Z"),
        LedgerEntry("pi_hpl_0030_portfolio", "high_plains", 7500, 248, "2026-01-17T13:22:30Z"),
        # PLANTED (2): in the ledger, absent from Stripe.
        LedgerEntry("pi_pie_0042_phantomrow", "piedmont", 2500, 103, "2026-01-18T15:40:00Z"),
    ]


def sample_stripe() -> list[StripeRecord]:
    """Ten Stripe-side rows: the nine shared SPIs plus one the ledger missed."""
    return [
        StripeRecord("pi_cas_0001_entryfee", "cascadia", 2500, 103, "2026-01-12T14:02:09Z"),
        StripeRecord("pi_cas_0002_entryfee", "cascadia", 2500, 103, "2026-01-12T16:44:01Z"),
        # Both fields lower than the ledger booked.
        StripeRecord("pi_cas_0003_bothoff", "cascadia", 7000, 231, "2026-01-13T09:15:38Z"),
        StripeRecord("pi_pie_0011_entryfee", "piedmont", 2500, 103, "2026-01-14T11:27:52Z"),
        StripeRecord("pi_pie_0012_portfolio", "piedmont", 7500, 248, "2026-01-14T12:01:06Z"),
        # Same SPI as the ledger row above, different fee. Rule 1 ignores this.
        StripeRecord("pi_pie_0019_shortfee", "piedmont", 2500, 118, "2026-01-15T08:33:18Z"),
        StripeRecord("pi_hpl_0021_entryfee", "high_plains", 2500, 103, "2026-01-16T10:04:59Z"),
        # Amount higher than the ledger booked; fee matches.
        StripeRecord("pi_hpl_0022_amountdrift", "high_plains", 3000, 103, "2026-01-16T10:58:44Z"),
        StripeRecord("pi_hpl_0030_portfolio", "high_plains", 7500, 248, "2026-01-17T13:22:27Z"),
        # PLANTED (1): in Stripe, absent from the ledger.
        StripeRecord("pi_cas_0007_ghostwebhook", "cascadia", 7500, 248, "2026-01-18T17:11:12Z"),
    ]
