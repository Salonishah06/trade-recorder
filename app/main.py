
from fastapi import FastAPI

from app.routes.trade_routes import router as trade_router

from app.routes.price_routes import router as price_router

from app.routes.pnl_routes import router as pnl_router

app = FastAPI(
    title="Trade Recorder & PnL Service",
    description="Backend service for trade ingestion, position tracking and PnL calculation.",
    version="1.0.0"
)


# Register the trade ingestion endpoint.
app.include_router(trade_router)
app.include_router(price_router)
app.include_router(pnl_router)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "Trade Recorder & PnL Service"
    }
