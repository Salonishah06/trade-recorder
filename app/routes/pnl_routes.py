
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pnl import PnLResponse
from app.services.pnl_service import (
    calculate_pnl,
    PositionNotFoundError,
    PriceNotFoundError,
)


router = APIRouter(prefix="/pnl", tags=["PnL"])


# Retrieve realized and unrealized PnL for a venue and symbol
@router.get(
    "/{venue}/{symbol}",
    response_model=PnLResponse,
    status_code=status.HTTP_200_OK
)
def get_pnl(
    venue: str,
    symbol: str,
    db: Session = Depends(get_db)
):
    try:
        return calculate_pnl(
            db=db,
            venue=venue,
            symbol=symbol.upper()
        )

    except PositionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )

    except PriceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
