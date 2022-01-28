import os

from mongoengine import connect

MONGO_URL = os.getenv("MONGO_URL")\
            or 'mongodb://root:root@192.168.29.132:27017/admin?directConnection=true&serverSelectionTimeoutMS=2000'
connect(host=MONGO_URL)
