
import uuid

from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    UniqueConstraint,
    Index
)

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Trade(Base):
    """
    Represents an individual trade received from an external trading venue.

    Each trade is uniquely identified by the combination of
    venue and trade_id. This prevents duplicate trade ingestion.
    """

    # Name of the database table
    __tablename__ = "trades"

    # Internal unique identifier for every trade record.
    # UUID avoids depending on an external venue's trade ID.
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Trading exchange or platform, e.g. Binance, Coinbase
    venue = Column(String(50), nullable=False)

    # Trade identifier provided by the external venue
    trade_id = Column(String(100), nullable=False)

    # Financial instrument being traded, e.g. BTCUSDT, AAPL
    symbol = Column(String(50), nullable=False)

    # Direction of the trade: BUY or SELL
    side = Column(String(10), nullable=False)

    # Number of units traded.
    # Numeric is used instead of Float for financial precision.
    quantity = Column(Numeric(28, 10), nullable=False)

    # Execution price of the trade.
    # Numeric avoids floating-point precision errors.
    price = Column(Numeric(28, 10), nullable=False)

    # Time at which the trade was executed.
    # Timezone-aware timestamps help maintain consistency across venues.
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Database-level constraints and indexes
    __table_args__ = (

        # A venue cannot submit the same trade ID more than once.
        # The same trade ID can still exist on a different venue.
        UniqueConstraint(
            "venue",
            "trade_id",
            name="uq_trade_venue_trade_id"
        ),

        # Improves query performance when filtering trades by symbol.
        Index("ix_trades_symbol", "symbol"),
    )


class Position(Base):
    """
    Represents the current position held for a particular symbol
    on a particular trading venue.

    The position is updated whenever a new BUY or SELL trade
    is successfully processed.
    """

    __tablename__ = "positions"

    # Internal unique identifier for the position
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Trading venue, e.g. Binance or Coinbase
    venue = Column(String(50), nullable=False)

    # Financial instrument, e.g. BTCUSDT or AAPL
    symbol = Column(String(50), nullable=False)

    # Current net quantity:
    # BUY increases quantity, SELL decreases quantity.
    net_quantity = Column(
        Numeric(28, 10),
        nullable=False,
        default=0
    )

    # Weighted average purchase price of the open position.
    # This is used to calculate realized and unrealized PnL.
    average_cost = Column(
        Numeric(28, 10),
        nullable=False,
        default=0
    )

    # Cumulative profit or loss from completed SELL transactions.
    realized_pnl = Column(
        Numeric(28, 10),
        nullable=False,
        default=0
    )

    # One position per venue and symbol.
    # Prevents multiple position records for the same combination.
    __table_args__ = (
        UniqueConstraint(
            "venue",
            "symbol",
            name="uq_position_venue_symbol"
        ),
    )


class Price(Base):
    """
    Stores market price information for financial instruments.

    The latest available price for a symbol is used to calculate
    unrealized PnL on open positions.
    """

    __tablename__ = "prices"

    # Internal unique identifier for each price record
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Financial instrument, e.g. BTCUSDT or AAPL
    symbol = Column(
        String(50),
        nullable=False
    )

    # Latest market price received for the symbol.
    # Numeric ensures precision in financial calculations.
    price = Column(
        Numeric(28, 10),
        nullable=False
    )

    # Timestamp indicating when this market price was recorded.
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False
    )

    # Index helps retrieve price records efficiently by symbol.
    __table_args__ = (
        Index("ix_prices_symbol_timestamp", "symbol", "timestamp"),
    )

    