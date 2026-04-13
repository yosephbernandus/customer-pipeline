# Customer Data Pipeline

A data pipeline with 3 Docker services: Flask mock server → FastAPI ingestion (dlt) → PostgreSQL.

## Prerequisites

- Docker Desktop (running)
- Python 3.10+
- Git

## Quick Start

```bash
docker-compose up -d
```

Wait for all services to be healthy, then ingest data:

```bash
# Ingest customer data from Flask into PostgreSQL
curl -X POST http://localhost:8000/api/ingest
```

## Endpoints

### Flask Mock Server (port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/customers` | GET | Paginated list (`page`, `limit` params) |
| `/api/customers/{id}` | GET | Single customer |

### FastAPI Pipeline (port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ingest` | POST | Fetch from Flask, upsert into PostgreSQL |
| `/api/customers` | GET | Paginated list from database |
| `/api/customers/{id}` | GET | Single customer from database |

## Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Flask - paginated customers
curl "http://localhost:5000/api/customers?page=1&limit=5"

# Flask - single customer
curl http://localhost:5000/api/customers/CUST-001

# Ingest data
curl -X POST http://localhost:8000/api/ingest

# Pipeline - paginated customers from DB
curl "http://localhost:8000/api/customers?page=1&limit=5"

# Pipeline - single customer from DB
curl http://localhost:8000/api/customers/CUST-001
```

## Updating Customer Data

The mock server reads from `mock-server/data/customers.json`, which is copied into the Docker image at build time. To update the data:

```bash
# 1. Edit the JSON file
#    e.g., change a customer's name in mock-server/data/customers.json

# 2. Rebuild the mock server to pick up changes
docker-compose up -d --build mock-server

# 3. Re-ingest to sync changes into PostgreSQL
curl -X POST http://localhost:8000/api/ingest

# 4. Verify the update
curl http://localhost:8000/api/customers/CUST-001
```

The ingest endpoint uses upsert logic (dlt `merge`) — existing records are updated by `customer_id`, no duplicates are created.

## Configuration

All settings have sensible defaults no extra setup needed. Override via environment variables if required:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `password` | PostgreSQL password |
| `POSTGRES_DB` | `customer_db` | PostgreSQL database name |
| `DEBUG` | `false` | Enable debug mode for Flask and FastAPI |

```bash
# Default (production mode)
# With custom config
POSTGRES_PASSWORD=secret DEBUG=true docker-compose up -d
```

## Architecture

```
customers.json (file)
       │
       ▼
  Flask Mock Server (:5000)
       │
       ▼ HTTP GET (paginated)
       │
  FastAPI Pipeline (:8000)
       │
       ▼ dlt pipeline (upsert)
       │
  PostgreSQL (:5432)
```

## Project Structure

```
customer-pipeline/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── models/customer.py
    ├── services/ingestion.py
    ├── database.py
    ├── Dockerfile
    └── requirements.txt
```
