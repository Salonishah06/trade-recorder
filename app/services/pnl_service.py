
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Position, Price
from app.schemas.pnl import PnLResponse


# Custom exceptions for missing database records
class PositionNotFoundError(Exception):
    pass


class PriceNotFoundError(Exception):
    pass


def calculate_pnl(db: Session, venue: str, symbol: str) -> PnLResponse:

    # Step 1: Retrieve the current position for this venue and symbol
    position = (
        db.query(Position)
        .filter(
            Position.venue == venue,
            Position.symbol == symbol
        )
        .first()
    )

    if position is None:
        raise PositionNotFoundError(
            f"No position found for {venue} and {symbol}"
        )

    # Step 2: Retrieve the latest recorded market price for this symbol
    latest_price_record = (
        db.query(Price)
        .filter(Price.symbol == symbol)
        .order_by(
            Price.timestamp.desc(),
            Price.id.desc()
        )
        .first()
    )

    if latest_price_record is None:
        raise PriceNotFoundError(
            f"No market price found for {symbol}"
        )

    # Step 3: Convert database values to Decimal
    net_quantity = Decimal(str(position.net_quantity))
    average_cost = Decimal(str(position.average_cost))
    realized_pnl = Decimal(str(position.realized_pnl))
    latest_price = Decimal(str(latest_price_record.price))

    # Step 4: Calculate unrealized PnL
    # Formula: (Current Market Price - Average Cost) * Net Quantity
    unrealized_pnl = (
        latest_price - average_cost
    ) * net_quantity

    # Step 5: Calculate total PnL
    total_pnl = realized_pnl + unrealized_pnl

    # Step 6: Return the calculated PnL response
    return PnLResponse(
        venue=venue,
        symbol=symbol,
        net_quantity=net_quantity,
        average_cost=average_cost,
        latest_price=latest_price,
        realized_pnl=realized_pnl,
        unrealized_pnl=unrealized_pnl,
        total_pnl=total_pnl
    )
