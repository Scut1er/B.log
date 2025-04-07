import imghdr
import uuid
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Optional

from PIL import Image

from app.exceptions import WrongFileFormat, WrongFileSize, WrongFileResolution
from app.minio_db import upload_file, delete_file
from app.schemas import Logo

from app.utils.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, MIN_WIDTH_LOGO, MAX_HEIGHT_LOGO, MIN_HEIGHT_LOGO, \
    MAX_WIDTH_LOGO


async def validate_image(logo) -> BytesIO:
    """Проверяет формат, размер и разрешение загружаемого изображения."""
    # Проверка расширение файла
    file_ext = logo.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise WrongFileFormat

    # Проверка размера файла
    content = await logo.read()
    if len(content) > MAX_FILE_SIZE:
        raise WrongFileSize

    # Проверка MIME-типа
    mime_type = imghdr.what(None, content)
    if mime_type not in ALLOWED_EXTENSIONS:
        raise WrongFileFormat

    # Проверка разрешения изображения
    image = Image.open(BytesIO(content))
    width, height = image.size
    if not (MIN_WIDTH_LOGO <= width <= MAX_WIDTH_LOGO or MIN_HEIGHT_LOGO <= height <= MAX_HEIGHT_LOGO):
        raise WrongFileResolution

    # Создаем поток и сбрасываем указатель в начало
    image_stream = BytesIO(content)
    image_stream.seek(0)

    return image_stream


async def upload_logo(logo) -> Logo:
    # Проверка изображения и получение потока с валидными данными
    validated_logo = await validate_image(logo)

    file_ext = logo.filename.split(".")[-1].lower()
    unique_id = uuid.uuid4()
    filename = f"{unique_id}.{file_ext}"

    logo_url = upload_file("team-logos", validated_logo, filename)
    return Logo(filename=filename, logo_url=logo_url)


