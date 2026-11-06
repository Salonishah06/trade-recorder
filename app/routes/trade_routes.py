
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.trade import TradeCreate, TradeResponse
from app.services.trade_service import (
    ingest_trade,
    DuplicateTradeError,
    InsufficientPositionError,
)

router = APIRouter(prefix="/trades", tags=["Trades"])


# Common function to process both BUY and SELL transactions
def process_trade(
    trade_data: TradeCreate,
    db: Session
):
    try:
        return ingest_trade(db, trade_data)

    except DuplicateTradeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )

    except InsufficientPositionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        )


# Endpoint for BUY transactions
@router.post(
    "/buy",
    response_model=TradeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_buy_trade(
    trade_data: TradeCreate,
    db: Session = Depends(get_db)
):
    if trade_data.side != "BUY":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint only accepts BUY trades"
        )

    return process_trade(trade_data, db)


# Endpoint for SELL transactions
@router.post(
    "/sell",
    response_model=TradeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_sell_trade(
    trade_data: TradeCreate,
    db: Session = Depends(get_db)
):
    if trade_data.side != "SELL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint only accepts SELL trades"
        )

    return process_trade(trade_data, db)
