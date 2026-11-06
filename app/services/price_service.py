
from sqlalchemy.orm import Session

from app.models import Price
from app.schemas.price import PriceCreate


def create_price(db: Session, price_data: PriceCreate) -> Price:
    """
    Store a market price in the database.

    Each submitted price is stored as a separate record.
    This allows us to maintain price history and retrieve
    the latest price later.
    """

    # Create a new Price database object
    new_price = Price(
        symbol=price_data.symbol,
        price=price_data.price,
        timestamp=price_data.timestamp
    )

    # Add the price record to the database session
    db.add(new_price)

    try:
        # Commit the transaction to PostgreSQL
        db.commit()

        # Refresh to retrieve the generated database ID
        db.refresh(new_price)

        return new_price

    except Exception:
        # Roll back if database insertion fails
        db.rollback()
        raise
