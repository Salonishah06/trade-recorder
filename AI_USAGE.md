# AI Usage Disclosure

## 1. AI Tool Used

- **Tool:** ChatGPT (OpenAI)

## 2. Areas Where AI Assistance Was Used

AI assistance was used as a supporting development tool during the implementation of the Trade Recorder & PnL Service.

The assistance included:

- **Project structure:** Discussing the organization of the application into routes, schemas, services, models, and database configuration.
- **Implementation guidance:** Understanding FastAPI, SQLAlchemy, Pydantic validation, PostgreSQL integration, and Alembic migrations.
- **Business logic:** Reviewing approaches for trade ingestion, idempotency, weighted average cost calculations, oversell prevention, and PnL calculations.
- **Reconciliation:** Discussing methods to compare internal and venue trade records and classify missing, extra, matched, and mismatched trades.
- **Debugging:** Investigating implementation errors, API response validation issues, database connectivity, and test failures.
- **Testing:** Developing test scenarios for business rules, validation, and edge cases.
- **Documentation:** Structuring the README, design document, and technical explanations.

## 3. Developer Responsibility

AI assistance was used for guidance, explanations, debugging support, and implementation suggestions.

The developer was responsible for:

- Reviewing and understanding the suggested implementations.
- Integrating the code into the project.
- Configuring the PostgreSQL database and application environment.
- Running database migrations.
- Testing API endpoints through Swagger UI.
- Executing the automated test suite.
- Reviewing and validating the resulting application behavior.

## 4. Verification

The application was tested locally using Pytest.

The test suite covers trade validation, trade ingestion, duplicate prevention, oversell protection, position management, PnL calculations, database connectivity, and reconciliation.

All implementation decisions and generated suggestions were reviewed as part of the development process.