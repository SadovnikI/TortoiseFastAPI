from pydantic import BaseModel, Field, EmailStr, SecretStr
from tortoise.contrib.pydantic import pydantic_model_creator

from models.user_models import User


# ==========================================================
#                      User Schemas


class UserSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: SecretStr = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Some full name",
                "email": "some_full_name@x.com",
                "password": "weakpassword"
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "some_full_name@x.com",
                "password": "weakpassword"
            }
        }


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


# ==========================================================
#           User Pydentic Tortoise ORM Schemas


UserPydantic = pydantic_model_creator(
    User,
    name='User',
)
