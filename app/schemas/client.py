import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    cpf_cnpj: str | None = Field(default=None, max_length=18)
    email: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    type: Literal["pj", "pf"] | None = None


class ClientUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    cpf_cnpj: str | None = Field(default=None, max_length=18)
    email: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    type: Literal["pj", "pf"] | None = None


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    cpf_cnpj: str | None
    email: str | None
    phone: str | None
    type: Literal["pj", "pf"] | None
    created_at: datetime
