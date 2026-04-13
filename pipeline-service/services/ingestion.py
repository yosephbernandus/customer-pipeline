import os
from datetime import date, datetime

import dlt
import httpx

MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://mock-server:5000")


def _parse_customer(raw: dict) -> dict:
    record = dict(raw)
    if record.get("date_of_birth"):
        record["date_of_birth"] = date.fromisoformat(record["date_of_birth"])
    if record.get("created_at"):
        record["created_at"] = datetime.fromisoformat(
            record["created_at"].replace("Z", "+00:00")
        )
    return record


@dlt.resource(
    table_name="customers",
    write_disposition="merge",
    primary_key="customer_id",
)
def customers_resource():
    page = 1
    limit = 50

    while True:
        resp = httpx.get(
            f"{MOCK_SERVER_URL}/api/customers",
            params={"page": page, "limit": limit},
        )
        resp.raise_for_status()
        payload = resp.json()

        yield [_parse_customer(c) for c in payload["data"]]

        if page * limit >= payload["total"]:
            break
        page += 1


def run_ingestion() -> int:
    database_url = os.environ["DATABASE_URL"]

    pipeline = dlt.pipeline(
        pipeline_name="customer_pipeline",
        destination=dlt.destinations.postgres(database_url),
        dataset_name="public",
    )

    info = pipeline.run(customers_resource())
    info.raise_on_failed_jobs()

    with pipeline.sql_client() as client:
        with client.execute_query("SELECT count(*) FROM customers") as cursor:
            return cursor.fetchone()[0]
