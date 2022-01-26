from sqlalchemy.orm import Session
from models import Object


class ObjectFactory:
    __key: str
    __obj: Object | None = None

    def __init__(self, key: str):
        self.__key = key

    def create(self) -> Object:
        if self.__obj is None:
            self.__obj = Object(keyname=self.__key)
        return self.__obj
