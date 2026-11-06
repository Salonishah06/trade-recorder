import pytest
from decimal import Decimal

from app.models import Position
from app.services.position_service import (
    get_position,
    PositionNotFoundError,
)


def test_get_position(db_session):
    # Create a position.
    position = Position(
        venue="binance",
        symbol="BTCUSDT",
        net_quantity=Decimal("16"),
        average_cost=Decimal("100"),
        realized_pnl=Decimal("320")
    )

    db_session.add(position)
    db_session.commit()

    # Retrieve the position.
    result = get_position(
        db=db_session,
        venue="binance",
        symbol="BTCUSDT"
    )

    # Verify the response.
    assert result.venue == "binance"
    assert result.symbol == "BTCUSDT"
    assert result.net_quantity == Decimal("16")
    assert result.average_cost == Decimal("100")
    assert result.realized_pnl == Decimal("320")


def test_get_position_not_found(db_session):
    # Verify that a missing position raises an exception.
    with pytest.raises(PositionNotFoundError):
        get_position(
            db=db_session,
            venue="binance",
            symbol="ETHUSDT"
        )