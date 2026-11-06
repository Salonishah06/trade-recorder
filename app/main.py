
from fastapi import FastAPI

app = FastAPI(
    title="Trade Recorder & PnL Service",
    description="Backend service for trade ingestion, position management and PnL calculations",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Trade Recorder & PnL Service is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
