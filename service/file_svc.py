from models import FileMetadata


async def get_file_metadata(_id):
    files = FileMetadata.objects(file_id=_id)
    return files[0].to_mongo().to_dict()
