from sqlalchemy.sql import text
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Response
from factory.object_factory import ObjectFactory
from factory.file_factory import FileFactory
from factory.user_object_factory import UserObjectFactory
import filesystem
from connection.con import get_pg_db
from models import User, UserObject, Object
from router.middleware import get_user
from schemas.namespace_response import NamespaceList

router = APIRouter()


@router.post("/create")
def create_file(key: str, user: User = Depends(get_user), db: Session = Depends(get_pg_db)):
    try:
        key_count = db.query(UserObject).join(Object) \
            .filter((UserObject.object_id == Object.id) & (UserObject.namespace == user.username) & (Object.keyname == key)) \
            .count()

        if key_count > 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

        obj = ObjectFactory(key).create()
        db.add(obj)
        db.commit()
        file = FileFactory(obj).create()
        db.add(file)
        db.commit()
        user_obj = UserObjectFactory(user=user, obj=obj, namespace=user.username, owner=True).create()
        db.add(user_obj)
        db.commit()
    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        pass
    return {
        "status": "success"
    }
    pass
