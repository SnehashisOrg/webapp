from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class UserSchema(BaseModel):
    id: UUID
    email: EmailStr
    firstname: str
    lastname: str
    account_created: datetime
    account_updated: datetime

    class Config:
        orm_mode = True
        fields = {"id": {"readOnly": True}, "password": {"writeOnly": True}, "account_created": {"readOnly": True}, "account_updated": {"readOnly": True}}

class UserRequestBodyModel(BaseModel):
    email: EmailStr
    password: str
    firstname: str
    lastname: str

class UserUpdateRequestBodyModel(BaseModel):
    first_name: str = None
    last_name: str = None
    password: str = None
    email: str = None