
from decimal import Decimal
from pydantic import BaseModel


# Response schema for position and PnL details
class PnLResponse(BaseModel):
    venue: str
    symbol: str

    # Current open position
    net_quantity: Decimal
    average_cost: Decimal

    # Latest available market price
    latest_price: Decimal

    # Profit/loss from completed SELL trades
    realized_pnl: Decimal

    # Profit/loss from the current open position
    unrealized_pnl: Decimal

    # Combined realized and unrealized profit/loss
    total_pnl: Decimal
