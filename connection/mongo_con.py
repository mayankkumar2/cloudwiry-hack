from mongoengine import connect

connect(host='mongodb://root:root@127.0.0.1:27017/admin?directConnection=true&serverSelectionTimeoutMS=2000')
