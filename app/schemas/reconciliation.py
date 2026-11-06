from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, model_validator


class VenueTrade(BaseModel):
    trade_id: str
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    timestamp: datetime


class ReconciliationRequest(BaseModel):
    venue: str
    trades: list[VenueTrade]

    @model_validator(mode="after")
    def validate_unique_trade_ids(self):
        # Extract all trade IDs from the incoming venue data.
        trade_ids = [trade.trade_id for trade in self.trades]

        # Compare the list with its set to detect duplicates.
        if len(trade_ids) != len(set(trade_ids)):
            raise ValueError("Duplicate trade IDs found in reconciliation data")

        return self

class ReconciliationResponse(BaseModel):
    missing: list[str]
    extra: list[str]
    mismatched: list[str]
    matched: list[str]