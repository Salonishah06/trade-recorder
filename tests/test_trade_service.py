
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.models import Trade, Position
from app.schemas.trade import TradeCreate
from app.services.trade_service import (
    ingest_trade,
    DuplicateTradeError,
    InsufficientPositionError,
)


def create_trade(
    trade_id,
    side,
    quantity,
    price
):
    """Helper function to create valid trade input."""

    return TradeCreate(
        venue="binance",
        trade_id=trade_id,
        symbol="BTCUSDT",
        side=side,
        quantity=Decimal(str(quantity)),
        price=Decimal(str(price)),
        timestamp=datetime.now(timezone.utc)
    )


def test_buy_trade_creates_position(db_session):
    """A BUY trade should create a new position."""

    trade = create_trade("T-1001", "BUY", 10, 100)

    result = ingest_trade(db_session, trade)

    position = (
        db_session.query(Position)
        .filter_by(venue="binance", symbol="BTCUSDT")
        .one()
    )

    assert result.trade_id == "T-1001"
    assert position.net_quantity == Decimal("10")
    assert position.average_cost == Decimal("100")
    assert position.realized_pnl == Decimal("0")


def test_sell_trade_updates_realized_pnl(db_session):
    """A SELL should reduce quantity and calculate realized PnL."""

    buy_trade = create_trade("T-1002", "BUY", 10, 100)
    sell_trade = create_trade("T-1003", "SELL", 5, 120)

    ingest_trade(db_session, buy_trade)
    ingest_trade(db_session, sell_trade)

    position = (
        db_session.query(Position)
        .filter_by(venue="binance", symbol="BTCUSDT")
        .one()
    )

    assert position.net_quantity == Decimal("5")
    assert position.average_cost == Decimal("100")
    assert position.realized_pnl == Decimal("100")


def test_duplicate_trade_is_rejected(db_session):
    """The same venue and trade ID must not be processed twice."""

    trade = create_trade("T-1004", "BUY", 10, 100)

    ingest_trade(db_session, trade)

    with pytest.raises(DuplicateTradeError):
        ingest_trade(db_session, trade)

    position = (
        db_session.query(Position)
        .filter_by(venue="binance", symbol="BTCUSDT")
        .one()
    )

    trade_count = (
        db_session.query(Trade)
        .filter_by(venue="binance", trade_id="T-1004")
        .count()
    )

    assert position.net_quantity == Decimal("10")
    assert trade_count == 1


def test_overselling_is_rejected_without_position_change(db_session):
    """An invalid SELL must not change the existing position."""

    buy_trade = create_trade("T-1005", "BUY", 10, 100)
    sell_trade = create_trade("T-1006", "SELL", 15, 120)

    ingest_trade(db_session, buy_trade)

    with pytest.raises(InsufficientPositionError):
        ingest_trade(db_session, sell_trade)

    position = (
        db_session.query(Position)
        .filter_by(venue="binance", symbol="BTCUSDT")
        .one()
    )

    rejected_trade_count = (
        db_session.query(Trade)
        .filter_by(venue="binance", trade_id="T-1006")
        .count()
    )

    assert position.net_quantity == Decimal("10")
    assert position.average_cost == Decimal("100")
    assert position.realized_pnl == Decimal("0")
    assert rejected_trade_count == 0


def test_weighted_average_cost_calculation(db_session):
    """
    Verify weighted average cost and realized PnL
    across multiple BUY and SELL trades.
    """

    # First purchase: 10 units at 100.
    trade_1 = create_trade("T-1007", "BUY", 10, 100)

    # Second purchase: 10 units at 110.
    trade_2 = create_trade("T-1008", "BUY", 10, 110)

    # Sell 5 units at 120.
    trade_3 = create_trade("T-1009", "SELL", 5, 120)

    ingest_trade(db_session, trade_1)
    ingest_trade(db_session, trade_2)
    ingest_trade(db_session, trade_3)

    position = (
        db_session.query(Position)
        .filter_by(venue="binance", symbol="BTCUSDT")
        .one()
    )

    # Weighted average cost = (10*100 + 10*110) / 20 = 105.
    assert position.net_quantity == Decimal("15")
    assert position.average_cost == Decimal("105")

    # Realized PnL = (120 - 105) * 5 = 75.
    assert position.realized_pnl == Decimal("75")
