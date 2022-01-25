import uuid
from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    password: str


class UserLoginRequest(BaseModel):
    username: str
    password: str
