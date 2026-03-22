import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    client_id: uuid.UUID | None = None
    service_id: uuid.UUID
    is_expense: bool
    is_personal: bool = False
    pjpf: Literal["pj", "pf"] | None = None
    amount: Decimal = Field(gt=0)
    description: str | None = None
    status: Literal["pending", "paid", "cancelled"] = "pending"
    payment_method: Literal["pix", "cash", "card", "transfer"] | None = None
    transaction_date: date


class TransactionUpdate(BaseModel):
    client_id: uuid.UUID | None = None
    service_id: uuid.UUID
    is_expense: bool
    is_personal: bool = False
    pjpf: Literal["pj", "pf"] | None = None
    amount: Decimal = Field(gt=0)
    description: str | None = None
    status: Literal["pending", "paid", "cancelled"] = "pending"
    payment_method: Literal["pix", "cash", "card", "transfer"] | None = None
    transaction_date: date


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID | None
    service_id: uuid.UUID
    is_expense: bool
    is_personal: bool
    pjpf: Literal["pj", "pf"] | None
    amount: Decimal
    description: str | None
    status: Literal["pending", "paid", "cancelled"]
    payment_method: Literal["pix", "cash", "card", "transfer"] | None
    transaction_date: date
    created_at: datetime
