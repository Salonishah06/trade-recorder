from decimal import Decimal
from pydantic import BaseModel


class PositionResponse(BaseModel):
    venue: str
    symbol: str
    net_quantity: Decimal
    average_cost: Decimal
    realized_pnl: Decimal