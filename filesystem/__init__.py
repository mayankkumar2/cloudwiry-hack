from models import File
import zstandard as zstd


def create_file_fs(f: File, b: bytes) -> str:
    file_name = str(f.id.hex)
    b = zstd.compress(b)
    _path = f"data/{file_name}"
    with open(_path, "wb") as f:
        f.write(b)
        f.close()
    return _path


def read_file_fs(f: File) -> str:
    file_name = str(f.id.hex)
    _path = f"data/{file_name}"
    with open(_path, "rb") as f:
        b = f.read()
        b = zstd.decompress(b)
        return b
