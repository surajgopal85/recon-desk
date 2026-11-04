"""Rule 3 (flatten every finding into one list) against the synthetic fixtures.

Red until collect_discrepancies has a body.
"""

from recon_engine.discrepancies import Discrepancy, collect_discrepancies
from recon_engine.match import MatchResult, match_by_spi
from recon_engine.models import LedgerEntry, StripeRecord
from recon_engine.verify import verify_parity
from tests.fixtures import (
    AMOUNT_DRIFT_SPI,
    BOTH_DRIFT_SPI,
    FEE_DRIFT_SPI,
    LEDGER_ONLY_SPI,
    STRIPE_ONLY_SPI,
    sample_ledger,
    sample_stripe,
)


def run_rules() -> list[Discrepancy]:
    """The real pipeline: rule 1, then rule 2 over its pairs, then rule 3."""
    match_result = match_by_spi(sample_ledger(), sample_stripe())
    mismatches = verify_parity(match_result.matched)
    return collect_discrepancies(match_result, mismatches)


def test_collects_every_planted_discrepancy() -> None:
    # 1 stripe-only + 1 ledger-only + 1 fee + 1 amount + 2 from the both-off pair
    assert len(run_rules()) == 6


def test_clean_rows_produce_nothing() -> None:
    flagged = {d.stripe_payment_id for d in run_rules()}

    assert flagged == {
        STRIPE_ONLY_SPI,
        LEDGER_ONLY_SPI,
        FEE_DRIFT_SPI,
        AMOUNT_DRIFT_SPI,
        BOTH_DRIFT_SPI,
    }


def test_stripe_only_record_is_missing_in_ledger() -> None:
    """The names invert: rule 1's unmatched_in_stripe becomes missing_in_ledger."""
    found = [d for d in run_rules() if d.stripe_payment_id == STRIPE_ONLY_SPI]

    assert len(found) == 1
    assert found[0].kind == "missing_in_ledger"
    assert found[0].entry is None
    assert found[0].record is not None
    assert found[0].delta_cents is None
    assert found[0].region == "cascadia"


def test_ledger_only_entry_is_missing_in_stripe() -> None:
    found = [d for d in run_rules() if d.stripe_payment_id == LEDGER_ONLY_SPI]

    assert len(found) == 1
    assert found[0].kind == "missing_in_stripe"
    assert found[0].entry is not None
    assert found[0].record is None
    assert found[0].delta_cents is None
    assert found[0].region == "piedmont"


def test_money_mismatches_carry_both_sides_and_the_delta() -> None:
    found = [d for d in run_rules() if d.stripe_payment_id == BOTH_DRIFT_SPI]

    assert [d.kind for d in found] == ["amount_mismatch", "fee_mismatch"]
    assert all(d.entry is not None and d.record is not None for d in found)
    assert [d.delta_cents for d in found] == [7500 - 7000, 248 - 231]


def test_field_name_maps_to_the_right_kind() -> None:
    kinds = {d.stripe_payment_id: d.kind for d in run_rules() if d.delta_cents is not None}

    assert kinds[AMOUNT_DRIFT_SPI] == "amount_mismatch"
    assert kinds[FEE_DRIFT_SPI] == "fee_mismatch"


def test_output_order_is_missing_in_ledger_then_stripe_then_mismatches() -> None:
    kinds = [d.kind for d in run_rules()]

    assert kinds == [
        "missing_in_ledger",
        "missing_in_stripe",
        "amount_mismatch",
        "fee_mismatch",
        "fee_mismatch",
        "amount_mismatch",
    ]


def test_matched_and_clean_pairs_are_ignored() -> None:
    entry = LedgerEntry("pi_tst_0003", "cascadia", 2500, 103, "2026-03-01T00:00:00Z")
    record = StripeRecord("pi_tst_0003", "cascadia", 2500, 103, "2026-03-01T00:00:04Z")
    match_result = MatchResult(matched=[(entry, record)])

    assert collect_discrepancies(match_result, []) == []


def test_empty_everything_is_empty() -> None:
    assert collect_discrepancies(MatchResult(), []) == []
