from minio import Minio
from app.config import settings
from app.exceptions import LoadFileError, DeleteFileError

client = Minio(
    "minio:9000",
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False
)


def upload_file(bucket_name, file, filename) -> str:
    try:
        client.put_object(
            bucket_name, filename, file, length=-1, part_size=5 * 1024 * 1024
        )
        return f"http://localhost:9000/{bucket_name}/{filename}"
    except Exception as e:
        print(f"Ошибка добавления файла {filename} в бакета {bucket_name}: {e}")
        raise LoadFileError


def delete_file(bucket_name, filename):
    try:
        client.remove_object(bucket_name, filename)
    except Exception as e:
        print(f"Ошибка удаления файла {filename} из бакета {bucket_name}: {e}")
        raise DeleteFileError
