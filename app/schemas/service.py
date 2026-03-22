import uuid

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category_id: uuid.UUID


class ServiceUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category_id: uuid.UUID


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category_id: uuid.UUID
