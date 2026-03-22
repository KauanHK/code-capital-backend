from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    number: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    id: uuid.UUID
    username: str
    number: str
    created_at: datetime
    
    model_config = {'from_attributes': True}


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
