import uuid

from pydantic import BaseModel


class ObjectsListResponse(BaseModel):
    object_id: uuid.UUID
    key_name: str
    namespace: str
    owner_perm: bool
    read_perm: bool
    update_perm: bool
