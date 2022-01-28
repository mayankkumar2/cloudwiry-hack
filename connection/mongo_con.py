from mongoengine import connect

connect(host='mongodb://root:root@192.168.29.132:27017/admin?directConnection=true&serverSelectionTimeoutMS=2000')
