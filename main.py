from fastapi import FastAPI
from router.router import v1router

app = FastAPI()

app.include_router(
    prefix='/api/v1',
    router=v1router
)



