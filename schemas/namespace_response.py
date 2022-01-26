from pydantic import BaseModel


class NamespaceList(BaseModel):
    namespaces: list[str]
