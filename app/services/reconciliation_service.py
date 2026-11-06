from sqlalchemy.orm import Session

from app.models import Trade
from app.schemas.reconciliation import (
    ReconciliationRequest,
    ReconciliationResponse,
)



def reconcile_trades(
    db: Session,
    reconciliation_data: ReconciliationRequest
) -> ReconciliationResponse:

    venue = reconciliation_data.venue.strip()

    # Retrieve all internally recorded trades for this venue.
    internal_trades = (
        db.query(Trade)
        .filter(Trade.venue == venue)
        .all()
    )

    # Convert internal trades into a dictionary for quick lookup.
    internal_trade_map = {
        trade.trade_id: trade
        for trade in internal_trades
    }

    # Convert incoming venue trades into a dictionary.
    venue_trade_map = {
        trade.trade_id: trade
        for trade in reconciliation_data.trades
    }

    missing = []
    extra = []
    mismatched = []
    matched = []

    # Identify trades reported by the venue.
    for trade_id, venue_trade in venue_trade_map.items():

        internal_trade = internal_trade_map.get(trade_id)

        # Venue has the trade, but internal database does not.
        if internal_trade is None:
            missing.append(trade_id)
            continue

        # Compare important trade attributes.
        is_mismatched = (
            internal_trade.symbol != venue_trade.symbol
            or internal_trade.side != venue_trade.side
            or internal_trade.quantity != venue_trade.quantity
            or internal_trade.price != venue_trade.price
            or internal_trade.timestamp != venue_trade.timestamp
        )

        if is_mismatched:
            mismatched.append(trade_id)
        else:
            matched.append(trade_id)

    # Identify trades recorded internally but absent from venue data.
    for trade_id in internal_trade_map:
        if trade_id not in venue_trade_map:
            extra.append(trade_id)

    return ReconciliationResponse(
        missing=missing,
        extra=extra,
        mismatched=mismatched,
        matched=matched
    )