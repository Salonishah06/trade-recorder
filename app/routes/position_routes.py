from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.position import PositionResponse
from app.services.position_service import (
    get_position,
    PositionNotFoundError,
)

router = APIRouter(prefix="/positions", tags=["Positions"])


@router.get(
    "/{venue}/{symbol}",
    response_model=PositionResponse,
    status_code=status.HTTP_200_OK
)
def fetch_position(
    venue: str,
    symbol: str,
    db: Session = Depends(get_db)
):
    try:
        return get_position(
            db=db,
            venue=venue,
            symbol=symbol.upper()
        )

    except PositionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )