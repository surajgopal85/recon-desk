"""Rule 1 (SPI set-matching) against the synthetic fixtures.

Red until match_by_spi has a body.
"""

from recon_engine.match import match_by_spi
from tests.fixtures import SHARED_SPIS, sample_ledger, sample_stripe

LEDGER_ONLY_SPI = "pi_pie_0042_phantomrow"
STRIPE_ONLY_SPI = "pi_cas_0007_ghostwebhook"


def test_matches_every_shared_spi() -> None:
    result = match_by_spi(sample_ledger(), sample_stripe())

    assert len(result.matched) == len(SHARED_SPIS)
    assert {entry.stripe_payment_id for entry, _ in result.matched} == set(SHARED_SPIS)
    # Each pair is two views of the same payment.
    assert all(
        entry.stripe_payment_id == record.stripe_payment_id for entry, record in result.matched
    )


def test_ledger_only_spi_is_unmatched_in_ledger() -> None:
    result = match_by_spi(sample_ledger(), sample_stripe())

    assert [e.stripe_payment_id for e in result.unmatched_in_ledger] == [LEDGER_ONLY_SPI]


def test_stripe_only_spi_is_unmatched_in_stripe() -> None:
    result = match_by_spi(sample_ledger(), sample_stripe())

    assert [r.stripe_payment_id for r in result.unmatched_in_stripe] == [STRIPE_ONLY_SPI]


def test_every_input_record_is_accounted_for() -> None:
    ledger, stripe = sample_ledger(), sample_stripe()
    result = match_by_spi(ledger, stripe)

    assert len(result.matched) + len(result.unmatched_in_ledger) == len(ledger)
    assert len(result.matched) + len(result.unmatched_in_stripe) == len(stripe)
