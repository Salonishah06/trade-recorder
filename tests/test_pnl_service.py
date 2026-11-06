from datetime import datetime, timezone
from decimal import Decimal

from app.models import Position, Price
from app.services.pnl_service import calculate_pnl

import pytest

from app.services.pnl_service import (
    PositionNotFoundError,
    PriceNotFoundError,
)

def test_pnl_position_not_found(db_session):
    # No position exists for this venue and symbol.
    with pytest.raises(PositionNotFoundError):
        calculate_pnl(
            db=db_session,
            venue="binance",
            symbol="ETHUSDT"
        )


def test_pnl_price_not_found(db_session):
    # Create a position without adding a market price.
    position = Position(
        venue="binance",
        symbol="ETHUSDT",
        net_quantity=Decimal("5"),
        average_cost=Decimal("100"),
        realized_pnl=Decimal("0")
    )

    db_session.add(position)
    db_session.commit()

    # Position exists, but no market price is available.
    with pytest.raises(PriceNotFoundError):
        calculate_pnl(
            db=db_session,
            venue="binance",
            symbol="ETHUSDT"
        )
def test_calculate_pnl(db_session):
    # Arrange: Create a position.
    position = Position(
        venue="binance",
        symbol="BTCUSDT",
        net_quantity=Decimal("16"),
        average_cost=Decimal("100"),
        realized_pnl=Decimal("320")
    )

    # Arrange: Create the latest market price.
    price = Price(
        symbol="BTCUSDT",
        price=Decimal("125"),
        timestamp=datetime.now(timezone.utc)
    )

    db_session.add(position)
    db_session.add(price)
    db_session.commit()

    # Act: Calculate PnL.
    result = calculate_pnl(
        db=db_session,
        venue="binance",
        symbol="BTCUSDT"
    )

    # Assert: Verify the calculations.
    assert result.net_quantity == Decimal("16")
    assert result.average_cost == Decimal("100")
    assert result.latest_price == Decimal("125")
    assert result.realized_pnl == Decimal("320")
    assert result.unrealized_pnl == Decimal("400")
    assert result.total_pnl == Decimal("720")
    assert result.total_pnl == Decimal("720")