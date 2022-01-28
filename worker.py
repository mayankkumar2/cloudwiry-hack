import os
import uuid
from models import FileMetadata


async def cleanup(_id: str):
    _path = f"data/{_id}"
    os.remove(_path)


async def delete_file(_id: str):
    id = uuid.UUID(_id)
    FileMetadata(file_id=id).delete()
    await cleanup(_id)
