from datetime import datetime

from mongoengine import Document, StringField, UUIDField
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from connection.con import engine
import uuid
from passlib.context import CryptContext
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FileMetadata(Document):
    filename = StringField(max_length=100)
    file_id = UUIDField(primary_key=True)
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(20), nullable=False, index=True, unique=True)
    password = Column(String(512), nullable=False)
    objects = relationship("UserObject", back_populates="user")

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


class File(Base):
    __tablename__ = 'files'
    id = Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id = Column('object_id', ForeignKey('objects.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    object = relationship("Object", back_populates="files")


class Object(Base):
    __tablename__ = 'objects'
    id = Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keyname = Column('keyname', String(1024), index=True, nullable=False)
    files = relationship("File", back_populates="object")
    permissions = relationship("UserObject", back_populates="object")


class UserObject(Base):
    __tablename__ = 'user_objects'
    user_id = Column('user_id', ForeignKey(User.id), primary_key=True)
    object_id = Column('object_id', ForeignKey(Object.id), primary_key=True)
    namespace = Column('namespace', String(20))
    owner = Column('owner', Boolean)
    read_perm = Column('read_perm', Boolean)
    update_perm = Column('update_perm', Boolean)
    object = relationship('Object', back_populates="permissions")
    user = relationship('User', back_populates="objects")


Base.metadata.create_all(bind=engine)
