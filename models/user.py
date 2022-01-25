from models.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String
from connection.con import engine
import uuid
import hashlib


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(20), nullable=False, index=True, unique=True)
    password = Column(String(512), nullable=False)

    @staticmethod
    def __calc_password(password):
        return hashlib.sha3_512(bytes(password, 'utf-8')).hexdigest()

    def set_password(self, password):
        self.password = self.__calc_password(password)

    def cmp_password(self, str1, str2) -> bool:
        return str1 == self.__calc_password(str2)

    pass


Base.metadata.create_all(bind=engine)

