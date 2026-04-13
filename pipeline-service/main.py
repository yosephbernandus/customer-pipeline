import os

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models.customer import Customer, CustomerSchema, PaginatedResponse
from services.ingestion import run_ingestion

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(title="Customer Pipeline Service", debug=DEBUG)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/ingest")
def ingest_customers():
    try:
        count = run_ingestion()
        return {"status": "success", "records_processed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers")
def list_customers(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    total = db.query(Customer).count()
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()

    return PaginatedResponse(
        data=[CustomerSchema.model_validate(c) for c in customers],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return CustomerSchema.model_validate(customer)
