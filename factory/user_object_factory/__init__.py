from models import User, Object, UserObject


class UserObjectFactory:
    __user: User
    __obj: Object
    __owner: bool = False
    __read: bool = False
    __update: bool = False
    __user_obj: UserObject | None = None
    __namespace: str

    def __init__(self, obj: Object, user: User, namespace: str, owner: bool = False, read: bool = False,
                 update: bool = False):
        self.__obj = obj
        self.__user = user
        self.__namespace = namespace
        if owner:
            self.__owner = self.__read = self.__update = owner
        else:
            self.__read = read
            self.__update = update

    def create(self):
        print(self.__obj.id)
        if self.__user_obj is None:
            self.__user_obj = UserObject(
                user_id=self.__user.id,
                object_id=self.__obj.id,
                namespace=self.__namespace,
                owner=self.__owner,
                read_perm=self.__read,
                update_perm=self.__update
            )
        return self.__user_obj
