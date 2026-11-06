
from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


class TradeCreate(BaseModel):
    """
    Schema for validating incoming trade requests.

    This schema validates data before it reaches the database.
    """

    # Trading venue, e.g. Binance or Coinbase
    venue: str = Field(
        min_length=1,
        max_length=50
    )

    # Unique trade identifier provided by the venue
    trade_id: str = Field(
        min_length=1,
        max_length=100
    )

    # Financial instrument, e.g. BTCUSDT
    symbol: str = Field(
        min_length=1,
        max_length=50
    )

    # Only BUY and SELL are accepted
    side: Literal["BUY", "SELL"]

    # Decimal avoids floating-point precision errors
    quantity: Decimal = Field(
        gt=0,
        max_digits=28,
        decimal_places=10
    )

    # Execution price must be positive
    price: Decimal = Field(
        gt=0,
        max_digits=28,
        decimal_places=10
    )

    # Time at which the trade was executed
    timestamp: datetime

    @field_validator("venue", "trade_id", "symbol")
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        """Reject strings containing only whitespace."""
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value

    @field_validator("side", mode="before")
    @classmethod
    def normalize_side(cls, value):
        """Normalize lowercase trade sides to uppercase."""
        if isinstance(value, str):
            return value.strip().upper()

        return value

    @field_validator("timestamp")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        """Require timezone-aware timestamps."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include a timezone")

        return value


class TradeResponse(BaseModel):
    """
    Schema for returning a stored trade to the API consumer.
    """

    id: UUID
    venue: str
    trade_id: str
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    timestamp: datetime

    # Allows Pydantic to read values directly from SQLAlchemy objects.
    model_config = ConfigDict(from_attributes=True)
