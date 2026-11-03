"""Rule 2 (row-level amount/fee parity) against the synthetic fixtures.

Red until verify_parity has a body.
"""

from recon_engine.match import match_by_spi
from recon_engine.models import LedgerEntry, StripeRecord
from recon_engine.verify import FieldMismatch, verify_parity
from tests.fixtures import (
    AMOUNT_DRIFT_SPI,
    BOTH_DRIFT_SPI,
    FEE_DRIFT_SPI,
    sample_ledger,
    sample_stripe,
)


def matched_pairs() -> list[tuple[LedgerEntry, StripeRecord]]:
    """Rule 2's real input: whatever rule 1 paired up."""
    return match_by_spi(sample_ledger(), sample_stripe()).matched


def test_flags_every_planted_money_discrepancy() -> None:
    mismatches = verify_parity(matched_pairs())

    # fee-only (1) + amount-only (1) + both-fields (2) == 4
    assert len(mismatches) == 4


def test_clean_pairs_are_not_flagged() -> None:
    mismatches = verify_parity(matched_pairs())
    flagged = {m.entry.stripe_payment_id for m in mismatches}

    assert flagged == {FEE_DRIFT_SPI, AMOUNT_DRIFT_SPI, BOTH_DRIFT_SPI}


def test_fee_drift_reports_only_the_fee_field() -> None:
    mismatches = [
        m for m in verify_parity(matched_pairs()) if m.entry.stripe_payment_id == FEE_DRIFT_SPI
    ]

    assert [m.field_name for m in mismatches] == ["fee_cents"]
    assert mismatches[0].delta_cents == 103 - 118


def test_amount_drift_reports_only_the_amount_field() -> None:
    mismatches = [
        m for m in verify_parity(matched_pairs()) if m.entry.stripe_payment_id == AMOUNT_DRIFT_SPI
    ]

    assert [m.field_name for m in mismatches] == ["amount_cents"]
    assert mismatches[0].delta_cents == 2500 - 3000


def test_pair_off_on_both_fields_yields_two_mismatches_amount_first() -> None:
    mismatches = [
        m for m in verify_parity(matched_pairs()) if m.entry.stripe_payment_id == BOTH_DRIFT_SPI
    ]

    assert [m.field_name for m in mismatches] == ["amount_cents", "fee_cents"]
    assert [m.delta_cents for m in mismatches] == [7500 - 7000, 248 - 231]


def test_delta_is_signed_ledger_minus_stripe() -> None:
    entry = LedgerEntry("pi_tst_0001", "cascadia", 2500, 103, "2026-02-01T00:00:00Z")
    record = StripeRecord("pi_tst_0001", "cascadia", 2000, 103, "2026-02-01T00:00:02Z")

    mismatches = verify_parity([(entry, record)])

    assert mismatches == [
        FieldMismatch(
            entry=entry,
            record=record,
            field_name="amount_cents",
            ledger_cents=2500,
            stripe_cents=2000,
        )
    ]
    assert mismatches[0].delta_cents == 500


def test_identical_pair_produces_no_mismatches() -> None:
    entry = LedgerEntry("pi_tst_0002", "piedmont", 7500, 248, "2026-02-02T00:00:00Z")
    record = StripeRecord("pi_tst_0002", "piedmont", 7500, 248, "2026-02-02T00:00:05Z")

    assert verify_parity([(entry, record)]) == []
