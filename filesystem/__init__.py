import os
import uuid


def create_file_fs(b: list[bytes]) -> str:
    dir_name = uuid.uuid4().hex
    os.mkdir(dir_name)
    file_name = uuid.uuid4().hex
    _path = f"{dir_name}/{file_name}"
    with open(_path, "b") as f:
        f.write(b)
        f.close()
    return _path
