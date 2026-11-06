
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.price import PriceCreate, PriceResponse
from app.services.price_service import create_price


router = APIRouter(prefix="/prices", tags=["Prices"])


# Endpoint to receive and store market price updates
@router.post(
    "/",
    response_model=PriceResponse,
    status_code=status.HTTP_201_CREATED
)
def add_market_price(
    price_data: PriceCreate,
    db: Session = Depends(get_db)
):
    return create_price(db, price_data)
