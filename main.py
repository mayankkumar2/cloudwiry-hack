from fastapi import FastAPI, Header, Response, status, Depends
from sqlalchemy.orm import Session

from router.router import v1router
from connection.con import get_pg_db

app = FastAPI()

app.include_router(
    prefix='/api/v1',
    router=v1router
)

