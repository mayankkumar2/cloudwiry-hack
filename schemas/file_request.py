from pydantic import BaseModel


class FileModel(BaseModel):
    filename: str
    content: str
