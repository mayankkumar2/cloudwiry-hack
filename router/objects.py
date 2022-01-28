import base64
import mimetypes
import uuid
import sqlalchemy.exc
from fastapi import Depends
from sqlalchemy import text, desc
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Response
import filesystem
from connection import mq_con
from connection.con import get_pg_db
from models import User, UserObject, Object, FileMetadata, File
from router.middleware import get_user
from schemas.file_request import FileModel
from schemas.files_reponse import FileResponse
from schemas.object_response import ObjectsListResponse
from factory.file_factory import FileFactory
from router.permission import router as permission_router
from service import file_svc

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
async def update_object(f: FileModel, namespace_id: str, object_id: uuid.UUID, db: Session = Depends(get_pg_db),
                        user: User = Depends(get_user)):
    try:
        obj, usr_obj = db.query(Object, UserObject) \
            .filter((UserObject.user_id == user.id) &
                    (Object.id == UserObject.object_id) &
                    (Object.id == object_id)).one()

        if not usr_obj.update_perm:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not permitted to update the file")

        file = FileFactory(obj).create()
        db.add(file)
        db.commit()

        filesystem.create_file_fs(file, base64.b64decode(f.content))

        FileMetadata(file_id=file.id, filename=f.filename).save()

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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not permitted to delete")

        files = db.query(File).filter(File.object_id == obj.id).all()

        with db.connection() as con:
            con.execute(text("DELETE FROM user_objects WHERE object_id = :obj_id"), obj_id=obj.id)
            con.execute(text("DELETE FROM files WHERE object_id = :obj_id"), obj_id=obj.id)
            con.execute(text("DELETE FROM objects WHERE id = :obj_id"), obj_id=obj.id)
            con.execute(text("COMMIT"))
        for f in files:
            await mq_con.publish_message(f.id.hex)
        return {
            "status": "success"
        }
    except sqlalchemy.exc.NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e)


@router.get("/{object_id}/versions", response_model=list[FileResponse])
async def object_key_versions(namespace_id: str, object_id: uuid.UUID, db: Session = Depends(get_pg_db),
                              user: User = Depends(get_user)):
    try:
        obj, usr_obj = db.query(Object, UserObject) \
            .filter((UserObject.user_id == user.id) &
                    (Object.id == UserObject.object_id) &
                    (Object.id == object_id)).one()

        if not usr_obj.read_perm:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not permitted to read")

        files = db.query(File).filter(File.object_id == obj.id).all()

        files = [FileResponse(
            created_at=f.created_at,
            file_id=f.id,
            metadata=await file_svc.get_file_metadata(f.id))
            for f in files]

        return files
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/{object_id}/get")
async def object_key_get(namespace_id: str, object_id: uuid.UUID, version_id: uuid.UUID | None = None,
                         db: Session = Depends(get_pg_db),
                         user: User = Depends(get_user)):
    try:
        obj, usr_obj = db.query(Object, UserObject) \
            .filter((UserObject.user_id == user.id) &
                    (Object.id == UserObject.object_id) &
                    (Object.id == object_id)).one()

        if not usr_obj.read_perm:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not permitted to read")
        if version_id is None:
            file = db.query(File) \
                .filter(File.object_id == obj.id).order_by(
                desc(File.created_at)
            ).first()

            if file is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            file_metadata = await file_svc.get_file_metadata(file.id)

        else:
            file = db.query(File) \
                .filter((File.object_id == obj.id) & (File.id == version_id)).order_by(
                desc(File.created_at)
            ).first()

            if file is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            file_metadata = await file_svc.get_file_metadata(file.id)

        if not (file_metadata is None or file is None):
            mime_type = mimetypes.guess_type(file_metadata["filename"])[0] or 'text/plain'
            b = filesystem.read_file_fs(file)
            return Response(content=b, media_type=mime_type)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


router.include_router(
    prefix="/{object_id}/permission",
    router=permission_router
)
