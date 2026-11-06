from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.reconciliation import (
    ReconciliationRequest,
    ReconciliationResponse,
)
from app.services.reconciliation_service import reconcile_trades

router = APIRouter(
    prefix="/reconciliation",
    tags=["Reconciliation"]
)


@router.post(
    "/",
    response_model=ReconciliationResponse
)
def run_reconciliation(
    reconciliation_data: ReconciliationRequest,
    db: Session = Depends(get_db)
):
    return reconcile_trades(
        db=db,
        reconciliation_data=reconciliation_data
    )