import base64

from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Response

import filesystem
from factory.object_factory import ObjectFactory
from factory.file_factory import FileFactory
from factory.user_object_factory import UserObjectFactory
from connection.con import get_pg_db
from models import User, UserObject, Object, FileMetadata
from router.middleware import get_user
from schemas.file_request import FileModel

router = APIRouter()


@router.post("/create")
def create_file(f: FileModel, key: str, user: User = Depends(get_user), db: Session = Depends(get_pg_db)):
    try:
        key_count = db.query(UserObject).join(Object) \
            .filter(
            (UserObject.object_id == Object.id) & (UserObject.namespace == user.username) & (Object.keyname == key)) \
            .count()

        if key_count > 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        obj = ObjectFactory(key).create()
        db.add(obj)
        db.commit()
        file = FileFactory(obj).create()
        db.add(file)
        db.commit()
        filesystem.create_file_fs(file, base64.b64decode(f.content))
        user_obj = UserObjectFactory(user=user, obj=obj, namespace=user.username, owner=True).create()
        db.add(user_obj)
        db.commit()

        FileMetadata(file_id=file.id, filename=f.filename).save()

    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return {
        "status": "success"
    }

