# Design Document — Trade Recorder & PnL Service

## 1. Overview

The Trade Recorder & PnL Service is a backend application designed to ingest trades from multiple trading venues, maintain position records, calculate profit and loss (PnL), and reconcile internal trade records against external venue data.

The application follows a layered architecture using FastAPI for HTTP APIs, SQLAlchemy for database interactions, Pydantic for request validation, and PostgreSQL for persistent storage.

## 2. Architecture

The application is divided into four primary layers:

### API Layer — Routes

Located in `app/routes/`.

Responsible for:
- Exposing REST API endpoints.
- Accepting incoming requests.
- Injecting database sessions.
- Returning appropriate HTTP responses.
- Mapping service exceptions to HTTP status codes.

### Validation Layer — Schemas

Located in `app/schemas/`.

Uses Pydantic to validate incoming request data.

Validations include:
- Required fields and string length constraints.
- Positive trade quantities and prices.
- Valid BUY and SELL sides.
- Decimal precision constraints.
- Timezone-aware timestamps.
- Duplicate trade ID checks in reconciliation requests.

### Business Logic Layer — Services

Located in `app/services/`.

Responsible for:
- Trade ingestion and idempotency.
- Position updates.
- Average cost calculations.
- Oversell prevention.
- Market price storage.
- PnL calculations.
- Trade reconciliation.

### Persistence Layer — Models and Database

Located in `app/models.py` and `app/database.py`.

Uses SQLAlchemy ORM with PostgreSQL to persist trades, positions, and market prices.

Alembic manages database schema migrations.

## 3. Database Design

The application uses three primary tables.

### Trades

Stores individual trade records.

| Column | Description |
|---|---|
| id | UUID primary key |
| venue | Trading venue |
| trade_id | Unique trade identifier within a venue |
| symbol | Instrument symbol |
| side | BUY or SELL |
| quantity | Executed trade quantity |
| price | Execution price |
| timestamp | Time of trade execution |

A unique constraint on `(venue, trade_id)` prevents duplicate trade ingestion.

An index on `symbol` supports trade lookup operations.

### Positions

Stores the current position for each venue and symbol combination.

| Column | Description |
|---|---|
| id | UUID primary key |
| venue | Trading venue |
| symbol | Instrument symbol |
| net_quantity | Current net position |
| average_cost | Weighted average cost |
| realized_pnl | Accumulated realized profit or loss |

A unique constraint on `(venue, symbol)` ensures one position record per instrument per venue.

### Prices

Stores timestamped market price records.

| Column | Description |
|---|---|
| id | UUID primary key |
| symbol | Instrument symbol |
| price | Market price |
| timestamp | Price