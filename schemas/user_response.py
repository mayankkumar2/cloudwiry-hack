import uuid

from pydantic import BaseModel


class LoginResponse(BaseModel):
    token: str


class UserResponse(BaseModel):
    username: str
    id: uuid.UUID
