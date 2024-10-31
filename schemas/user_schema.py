from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

# User schema
class UserSchema(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str = Field(..., pattern=r'^[A-Za-z\s]+$')
    last_name: str = Field(..., pattern=r'^[A-Za-z\s]+$')
    account_created: datetime
    account_updated: datetime

    # model_config = ConfigDict(
    #     from_attributes = True,
    #     read_only_fields = {"id", "account_created", "account_updated"},
    #     write_only_fields = {"password"}
    # )
    model_config = ConfigDict(
        from_attributes = True,
        json_schema_extra = {
            "read_only_fields": {"id", "account_created", "account_updated"},
            "write_only_fields": {"password"}
        }
    )
# User request body schema for POST method
class UserRequestBodyModel(BaseModel):
    email: EmailStr
    password: str
    first_name: str = Field(..., pattern=r'^[A-Za-z\s]+$')
    last_name: str = Field(..., pattern=r'^[A-Za-z\s]+$')

    model_config = ConfigDict(
        str_strip_whitespace = True
    )

# User request body schema for PUT method
class UserUpdateRequestBodyModel(BaseModel):
    first_name: str = Field(None, pattern=r'^[A-Za-z\s]+$')
    last_name: str = Field(None, pattern=r'^[A-Za-z\s]+$')
    password: str = None
    email: str = None

    model_config = ConfigDict(
        str_strip_whitespace = True
    )

class ImageCreatedUserSchema(BaseModel):
    file_name: str
    id: UUID
    url: str
    upload_date: datetime
    user_id: UUID
