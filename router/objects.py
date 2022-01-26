import uuid
import sqlalchemy.exc
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status
from connection.con import get_pg_db
from models import User, UserObject, Object
from router.middleware import get_user
from schemas.object_response import ObjectsListResponse
from factory.file_factory import FileFactory
from router.permission import router as permission_router

router = APIRouter()


@router.get("/list", response_model=list[ObjectsListResponse])
async def list_objects(namespace_id: str, db: Session = Depends(get_pg_db), user: User = Depends(get_user)):
    usr_obj = db.query(UserObject, Object) \
        .filter((UserObject.object_id == Object.id) & (UserObject.user_id == user.id) & (
            UserObject.namespace == namespace_id)).all()
    objs = []
    for u, o in usr_obj:
        objs.append(ObjectsListResponse(
            object_id=o.id,
            key_name=o.keyname,
            namespace=u.namespace,
            owner_perm=u.owner,
            read_perm=u.read_perm,
            update_perm=u.update_perm
        ))
    return objs


@router.patch("/{object_id}/rename", response_model=dict)
async def object_key_rename(namespace_id: str, object_id: uuid.UUID, key: str, db: Session = Depends(get_pg_db),
                            user: User = Depends(get_user)):
    try:
        obj, usr_obj = db.query(Object, UserObject) \
            .filter((UserObject.object_id == Object.id) &
                    (UserObject.user_id == user.id) &
                    (Object.id == object_id)).one()

        key_count = db.query(UserObject).join(Object) \
            .filter((UserObject.object_id == Object.id) &
                    (UserObject.namespace == namespace_id) &
                    (Object.keyname == key)) \
            .count()

        if key_count > 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

        if not usr_obj.owner:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not permitted to rename")

        obj.keyname = key
        db.commit()
        return {
            "status": "ok"
        }
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put("/{object_id}/save")
async def update_object(namespace_id: str, object_id: uuid.UUID, db: Session = Depends(get_pg_db),
                        user: User = Depends(get_user)):
    try:
        obj, usr_obj = db.query(Object, UserObject) \
            .filter((UserObject.user_id == user.id) &
                    (Object.id == UserObject.object_id) &
                    (Object.id == object_id)).one()

        if not usr_obj.owner:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not permitted to rename")

        file = FileFactory(obj).create()
        db.add(file)
        db.commit()

        return {
            "status": "ok"
        }
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{object_id}/delete", response_model=dict)
async def object_key_delete(namespace_id: str, object_id: uuid.UUID, db: Session = Depends(get_pg_db),
                            user: User = Depends(get_user)):
    try:
        obj, usr_obj = db.query(Object, UserObject) \
            .filter((UserObject.user_id == user.id) &
                    (Object.id == UserObject.object_id) &
                    (Object.id == object_id)).one()

        if not usr_obj.owner:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not permitted to rename")

        with db.connection() as con:
            con.execute(text("DELETE FROM user_objects WHERE object_id = :obj_id"), obj_id=obj.id)
            con.execute(text("DELETE FROM files WHERE object_id = :obj_id"), obj_id=obj.id)
            con.execute(text("DELETE FROM objects WHERE id = :obj_id"), obj_id=obj.id)

        return {
            "status": "ok"
        }
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


router.include_router(
    prefix="/{object_id}/permission",
    router=permission_router
)
