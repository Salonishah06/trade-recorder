from sqlalchemy.orm import Session

from app.models import Position
from app.schemas.position import PositionResponse


class PositionNotFoundError(Exception):
    pass


def get_position(
    db: Session,
    venue: str,
    symbol: str
) -> PositionResponse:

    # Find the position using its venue and symbol.
    position = (
        db.query(Position)
        .filter(
            Position.venue == venue,
            Position.symbol == symbol
        )
        .first()
    )

    # Raise an error if the position does not exist.
    if position is None:
        raise PositionNotFoundError(
            f"No position found for {venue} and {symbol}"
        )

    # Convert the SQLAlchemy model into a Pydantic response.
    return PositionResponse(
        venue=position.venue,
        symbol=position.symbol,
        net_quantity=position.net_quantity,
        average_cost=position.average_cost,
        realized_pnl=position.realized_pnl
    )