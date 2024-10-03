from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional

class UserSchema(BaseModel):
    id: UUID
    email: EmailStr
    firstname: str = Field(..., pattern=r'^[A-Za-z\s]+$')
    lastname: str = Field(..., pattern=r'^[A-Za-z\s]+$')
    account_created: datetime
    account_updated: datetime

    class Config:
        from_attributes = True
        read_only_fields = {"id", "account_created", "account_updated"}
        write_only_fields = {"password"}

class UserRequestBodyModel(BaseModel):
    email: EmailStr
    password: str
    firstname: str = Field(..., pattern=r'^[A-Za-z]+$')
    lastname: str = Field(..., pattern=r'^[A-Za-z]+$')

class UserUpdateRequestBodyModel(BaseModel):
    first_name: str = Field(None, pattern=r'^[A-Za-z\s]+$')
    last_name: str = Field(None, pattern=r'^[A-Za-z\s]+$')
    password: str = None
    email: str = None

    class Config:
        str_strip_whitespace = True