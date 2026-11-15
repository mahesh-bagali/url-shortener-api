
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Input schema for user registration."""

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLoginRequest(BaseModel):
    """Input schema for user login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Public user information returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    created_at: datetime


class UserLoginResponse(BaseModel):
    """Response returned after successful login."""

    message: str
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
