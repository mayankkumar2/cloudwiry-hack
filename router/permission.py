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
from factory.user_object_factory import UserObjectFactory

router = APIRouter()


@router.put("/add")
async def add_user(namespace_id: str,
                   object_id: uuid.UUID,
                   username: str,
                   read_perm: bool = False,
                   update_perm: bool = False, db: Session = Depends(get_pg_db),
                   user: User = Depends(get_user)):
    if not read_perm and not update_perm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        c_usr = db.query(User).filter_by(username=username).one()
        obj, usr_obj = db.query(Object, UserObject) \
            .filter((UserObject.user_id == user.id) &
                    (Object.id == UserObject.object_id) &
                    (Object.id == object_id)).one()
        if not usr_obj.owner:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not permitted to add user access")
        perm_user_obj = UserObjectFactory(
            obj, c_usr, user.username, False, read_perm, update_perm
        ).create()

        db.add(perm_user_obj)
        db.commit()
        return {
            "success": "ok"
        }
    except sqlalchemy.exc.NoResultFound as _:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/remove")
async def remove_user(namespace_id: str,
                      object_id: uuid.UUID,
                      username: str, db: Session = Depends(get_pg_db),
                      user: User = Depends(get_user)):
    try:
        c_usr = db.query(User).filter_by(username=username).one()
        obj, usr_obj = db.query(Object, UserObject) \
            .filter((UserObject.user_id == user.id) &
                    (Object.id == UserObject.object_id) &
                    (Object.id == object_id)).one()
        if not usr_obj.owner:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not permitted to add user access")
        perm_user_obj = db.query(UserObject).join(Object) \
            .filter((UserObject.user_id == c_usr.id) &
                    (Object.id == UserObject.object_id) &
                    (Object.id == object_id)).one()
        db.delete(perm_user_obj)
        db.commit()
        return {
            "success": "ok"
        }
    except sqlalchemy.exc.NoResultFound as _:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
