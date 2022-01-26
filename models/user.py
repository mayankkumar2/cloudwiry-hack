from models.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String
from connection.con import engine
import uuid
import hashlib
from passlib.context import CryptContext


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(20), nullable=False, index=True, unique=True)
    password = Column(String(512), nullable=False)

    @staticmethod
    def __get_crypt_context():
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context

    @staticmethod
    def __calc_password(password) -> str:
        return User.__get_crypt_context().hash(password)

    def set_password(self, password):
        self.password = self.__calc_password(password)

    def cmp_password(self, pwd) -> bool:
        return User.__get_crypt_context().verify(pwd, self.password)

    pass


Base.metadata.create_all(bind=engine)
