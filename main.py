from fastapi import FastAPI
from router.router import v1router
import connection.mongo_con as _
app = FastAPI()

app.include_router(
    prefix='/api/v1',
    router=v1router
)



