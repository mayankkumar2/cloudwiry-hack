from sqlalchemy.sql import text
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status
from connection.con import get_pg_db
from models import User, UserObject
from router.middleware import get_user
from schemas.namespace_response import NamespaceList
from .file import router as file_router

router = APIRouter()


@router.post("/list")
def list_namespaces(db: Session = Depends(get_pg_db), user: User = Depends(get_user)):
    with db.connection() as con:
        try:
            rs = con.execute(text("SELECT DISTINCT namespace FROM user_objects WHERE user_id = :id"), id=user.id)
            namespaces = []
            for r in rs:
                namespaces.append(r[0])
            return NamespaceList(
                namespaces=namespaces
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


router.include_router(
    prefix="/file",
    router=file_router
)
