from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Date, DateTime, Numeric, Text, VARCHAR

from database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(VARCHAR(50), primary_key=True)
    first_name = Column(VARCHAR(100), nullable=False)
    last_name = Column(VARCHAR(100), nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    phone = Column(VARCHAR(20), nullable=True)
    address = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    account_balance = Column(Numeric(15, 2), nullable=True)
    created_at = Column(DateTime, nullable=True)


class CustomerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    address: str | None = None
    date_of_birth: date | None = None
    account_balance: Decimal | None = None
    created_at: datetime | None = None


class PaginatedResponse(BaseModel):
    data: list[CustomerSchema]
    total: int
    page: int
    limit: int
