from models import Object, File


class FileFactory:
    __patent_obj: Object
    __file: File | None = None

    def __init__(self, obj: Object):
        self.__patent_obj = obj

    def create(self):
        if self.__file is None:
            self.__file = File(object_id=self.__patent_obj.id)
        return self.__file
