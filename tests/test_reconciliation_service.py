from datetime import datetime, timezone
from decimal import Decimal

from app.models import Trade
from app.schemas.reconciliation import (
    ReconciliationRequest,
    VenueTrade,
)
from app.services.reconciliation_service import reconcile_trades


def test_reconcile_trades(db_session):
    # Use the same timestamp for internal and venue records.
    timestamp = datetime(2026, 11, 7, 10, 0, tzinfo=timezone.utc)

    # Create internal trades.
    internal_trades = [
        Trade(
            venue="binance",
            trade_id="T1",
            symbol="BTCUSDT",
            side="BUY",
            quantity=Decimal("10"),
            price=Decimal("100"),
            timestamp=timestamp
        ),
        Trade(
            venue="binance",
            trade_id="T2",
            symbol="BTCUSDT",
            side="BUY",
            quantity=Decimal("5"),
            price=Decimal("101"),
            timestamp=timestamp
        ),
        Trade(
            venue="binance",
            trade_id="T4",
            symbol="BTCUSDT",
            side="SELL",
            quantity=Decimal("2"),
            price=Decimal("105"),
            timestamp=timestamp
        )
    ]

    db_session.add_all(internal_trades)
    db_session.commit()

    # Simulate the trades received from Binance.
    venue_data = ReconciliationRequest(
        venue="binance",
        trades=[
            VenueTrade(
                trade_id="T1",
                symbol="BTCUSDT",
                side="BUY",
                quantity=Decimal("10"),
                price=Decimal("100"),
                timestamp=timestamp
            ),
            VenueTrade(
                trade_id="T2",
                symbol="BTCUSDT",
                side="BUY",
                quantity=Decimal("6"),  # Different quantity.
                price=Decimal("101"),
                timestamp=timestamp
            ),
            VenueTrade(
                trade_id="T3",
                symbol="BTCUSDT",
                side="BUY",
                quantity=Decimal("1"),
                price=Decimal("99"),
                timestamp=timestamp
            )
        ]
    )

    # Execute reconciliation.
    result = reconcile_trades(
        db=db_session,
        reconciliation_data=venue_data
    )

    # Verify all four reconciliation categories.
    assert result.matched == ["T1"]
    assert result.mismatched == ["T2"]
    assert result.missing == ["T3"]
    assert result.extra == ["T4"]