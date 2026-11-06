# Trade Recorder & PnL Service

A backend service built with **Python, FastAPI, PostgreSQL, and SQLAlchemy** to ingest trades from multiple venues, maintain positions, calculate Profit and Loss (PnL), and reconcile internal trades against venue-provided records.

## Features

- **Trade ingestion:** Separate BUY and SELL endpoints.
- **Input validation:** Validates trade fields, positive quantities and prices, and timezone-aware timestamps.
- **Idempotency:** Prevents duplicate trades using the combination of venue and trade ID.
- **Position management:** Maintains net quantity, average cost, and realized PnL.
- **Oversell protection:** Rejects SELL trades when the available position is insufficient.
- **Market price ingestion:** Stores timestamped market prices.
- **PnL calculation:** Calculates realized, unrealized, and total PnL using the latest available market price.
- **Reconciliation:** Identifies matched, missing, extra, and mismatched trades.
- **Database migrations:** Uses Alembic to manage database schema changes.
- **Automated testing:** Uses Pytest to test schemas and business logic.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| API Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Database Migrations | Alembic |
| Testing | Pytest |
| Database Driver | Psycopg2 |

## Project Structure

```text
trade-recorder/
├── app/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── alembic/
│   └── versions/
├── tests/
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── README.md
├── DESIGN.md
└── AI_USAGE.md
```

## Prerequisites

Install the following before running the project:

- Python 3.10 or later
- PostgreSQL
- Git

## Setup and Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd trade-recorder
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows Git Bash:

```bash
source venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure the database connection strings:

```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/trade_recorder
TEST_DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/trade_recorder_test
```

Replace the placeholders with your local PostgreSQL credentials.

**Do not commit the `.env` file or expose database credentials.**

### 5. Create PostgreSQL databases

Create the application and test databases:

```sql
CREATE DATABASE trade_recorder;
CREATE DATABASE trade_recorder_test;
```

### 6. Apply database migrations

```bash
alembic upgrade head
```

### 7. Start the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/trades/buy` | Ingest a BUY trade |
| POST | `/trades/sell` | Ingest a SELL trade |
| POST | `/prices/` | Add a market price |
| GET | `/positions/{venue}/{symbol}` | Retrieve a position |
| GET | `/pnl/{venue}/{symbol}` | Retrieve PnL details |
| POST | `/reconciliation/` | Reconcile venue trades |
| GET | `/` | Health check |

### 1. Ingest a BUY trade

`POST /trades/buy`

Example request:

```json
{
  "venue": "binance",
  "trade_id": "T-1001",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": "10",
  "price": "100",
  "timestamp": "2026-11-06T16:00:00+05:30"
}
```

### 2. Ingest a SELL trade

`POST /trades/sell`

Example request:

```json
{
  "venue": "binance",
  "trade_id": "T-1002",
  "symbol": "BTCUSDT",
  "side": "SELL",
  "quantity": "5",
  "price": "120",
  "timestamp": "2026-11-06T17:00:00+05:30"
}
```

A SELL trade is rejected if its quantity exceeds the available position.

### 3. Add a market price

`POST /prices/`

Example request:

```json
{
  "symbol": "BTCUSDT",
  "price": "125",
  "timestamp": "2026-11-06T18:00:00+05:30"
}
```

### 4. Retrieve a position

`GET /positions/binance/BTCUSDT`

Returns the venue, symbol, net quantity, average cost, and realized PnL.

### 5. Calculate PnL

`GET /pnl/binance/BTCUSDT`

Returns:

- Net quantity
- Average cost
- Latest market price
- Realized PnL
- Unrealized PnL
- Total PnL

### 6. Reconcile trades

`POST /reconciliation/`

Example request:

```json
{
  "venue": "binance",
  "trades": [
    {
      "trade_id": "T-1001",
      "symbol": "BTCUSDT",
      "side": "BUY",
      "quantity": "10",
      "price": "100",
      "timestamp": "2026-11-06T16:00:00+05:30"
    }
  ]
}
```

The response categorizes trades into:

- `matched`: Trades present in both systems with matching details.
- `missing`: Trades present at the venue but absent internally.
- `extra`: Trades present internally but absent at the venue.
- `mismatched`: Trades with matching IDs but differing trade details.

The current reconciliation implementation assumes the supplied venue trades represent a complete snapshot for that venue.

## Running Tests

Run the complete test suite:

```bash
python -m pytest -v
```

The tests cover trade validation, trade ingestion, duplicate prevention,