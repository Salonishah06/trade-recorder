
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Trade, Position
from app.schemas.trade import TradeCreate


class DuplicateTradeError(Exception):
    """Raised when the same venue trade is submitted more than once."""
    pass


class InsufficientPositionError(Exception):
    """Raised when a SELL quantity exceeds the available position."""
    pass


def ingest_trade(db: Session, trade_data: TradeCreate) -> Trade:
    """
    Ingest a trade and update the corresponding position.

    Uses weighted average cost for position valuation.

    The trade insertion and position update happen in one
    database transaction. If processing fails, both are rolled back.
    """

    try:
        # STEP 1: Check idempotency.
        # A venue must not submit the same trade ID twice.
        existing_trade = (
            db.query(Trade)
            .filter(
                Trade.venue == trade_data.venue,
                Trade.trade_id == trade_data.trade_id
            )
            .first()
        )

        if existing_trade:
            raise DuplicateTradeError(
                f"Trade {trade_data.trade_id} already exists "
                f"for venue {trade_data.venue}"
            )

        # STEP 2: Retrieve the existing position.
        # Lock an existing row to prevent concurrent updates.
        position = (
            db.query(Position)
            .filter(
                Position.venue == trade_data.venue,
                Position.symbol == trade_data.symbol
            )
            .with_for_update()
            .first()
        )

        # STEP 3: Create a position if one does not exist.
        if position is None:
            position = Position(
                venue=trade_data.venue,
                symbol=trade_data.symbol,
                net_quantity=Decimal("0"),
                average_cost=Decimal("0"),
                realized_pnl=Decimal("0")
            )
            db.add(position)

        # Convert database values to Decimal for safe calculations.
        current_quantity = Decimal(str(position.net_quantity))
        current_average_cost = Decimal(str(position.average_cost))
        current_realized_pnl = Decimal(str(position.realized_pnl))

        trade_quantity = trade_data.quantity
        trade_price = trade_data.price

        # STEP 4: Process BUY trades.
        if trade_data.side == "BUY":

            new_quantity = current_quantity + trade_quantity

            # Weighted average cost calculation:
            #
            # New average cost =
            # (Old quantity * Old average cost
            #  + New quantity * New purchase price)
            # / Total quantity

            new_average_cost = (
                (current_quantity * current_average_cost)
                + (trade_quantity * trade_price)
            ) / new_quantity

            position.net_quantity = new_quantity
            position.average_cost = new_average_cost

        # STEP 5: Process SELL trades.
        elif trade_data.side == "SELL":

            # Prevent selling more units than currently held.
            if trade_quantity > current_quantity:
                raise InsufficientPositionError(
                    f"Cannot sell {trade_quantity} units. "
                    f"Available quantity: {current_quantity}"
                )

            # Realized PnL =
            # (Selling price - Average purchase cost) * Quantity sold

            realized_profit = (
                (trade_price - current_average_cost)
                * trade_quantity
            )

            position.net_quantity = current_quantity - trade_quantity

            position.realized_pnl = (
                current_realized_pnl + realized_profit
            )

            # Reset average cost when the position is completely closed.
            if position.net_quantity == 0:
                position.average_cost = Decimal("0")

        # STEP 6: Create the trade record.
        new_trade = Trade(
            venue=trade_data.venue,
            trade_id=trade_data.trade_id,
            symbol=trade_data.symbol,
            side=trade_data.side,
            quantity=trade_quantity,
            price=trade_price,
            timestamp=trade_data.timestamp
        )

        db.add(new_trade)

        # STEP 7: Commit both changes atomically.
        db.commit()

        db.refresh(new_trade)

        return new_trade

    except DuplicateTradeError:
        db.rollback()
        raise

    except InsufficientPositionError:
        db.rollback()
        raise

    except IntegrityError:
        # The database unique constraint protects against
        # concurrent duplicate submissions.
        db.rollback()

        existing_trade = (
            db.query(Trade)
            .filter(
                Trade.venue == trade_data.venue,
                Trade.trade_id == trade_data.trade_id
            )
            .first()
        )

        if existing_trade:
            raise DuplicateTradeError(
                f"Trade {trade_data.trade_id} already exists "
                f"for venue {trade_data.venue}"
            )

        raise

    except Exception:
        # Any unexpected failure must roll back the transaction.
        db.rollback()
        raise
