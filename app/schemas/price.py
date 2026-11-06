
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Schema for receiving a market price from the API
class PriceCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=50)

    price: Decimal = Field(
        gt=0,
        max_digits=28,
        decimal_places=10
    )

    timestamp: datetime

    # Remove unnecessary whitespace from the symbol
    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        value = value.strip().upper()

        if not value:
            raise ValueError("Symbol cannot be empty")

        return value

    # Ensure the timestamp includes timezone information
    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include a timezone")

        return value


# Schema for returning the stored market price
class PriceResponse(BaseModel):
    id: UUID
    symbol: str
    price: Decimal
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
