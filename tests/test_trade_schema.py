
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.trade import TradeCreate


def test_valid_trade():
    """A valid trade should pass schema validation."""

    trade = TradeCreate(
        venue="binance",
        trade_id="T-1001",
        symbol="BTCUSDT",
        side="BUY",
        quantity="10",
        price="100",
        timestamp=datetime.now(timezone.utc),
    )

    assert trade.venue == "binance"
    assert trade.side == "BUY"
    assert trade.quantity == Decimal("10")
    assert trade.price == Decimal("100")


def test_invalid_quantity():
    """Negative quantities must be rejected."""

    with pytest.raises(ValidationError):
        TradeCreate(
            venue="binance",
            trade_id="T-1002",
            symbol="BTCUSDT",
            side="BUY",
            quantity="-10",
            price="100",
            timestamp=datetime.now(timezone.utc),
        )


def test_invalid_side():
    """Unsupported trade directions must be rejected."""

    with pytest.raises(ValidationError):
        TradeCreate(
            venue="binance",
            trade_id="T-1003",
            symbol="BTCUSDT",
            side="HOLD",
            quantity="10",
            price="100",
            timestamp=datetime.now(timezone.utc),
        )


def test_timezone_is_required():
    """Naive timestamps must be rejected."""

    with pytest.raises(ValidationError):
        TradeCreate(
            venue="binance",
            trade_id="T-1004",
            symbol="BTCUSDT",
            side="BUY",
            quantity="10",
            price="100",
            timestamp=datetime(2026, 11, 6, 10, 30),
        )
