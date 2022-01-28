from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import logging

DB_STRING = "postgresql://postgres:root@192.168.29.132:5432/postgres"
engine = create_engine(DB_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_pg_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
