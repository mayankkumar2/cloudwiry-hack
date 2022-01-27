import datetime
import uuid

from pydantic import BaseModel


class FileResponse(BaseModel):
    created_at: datetime.datetime
    file_id: uuid.UUID
    metadata: dict
