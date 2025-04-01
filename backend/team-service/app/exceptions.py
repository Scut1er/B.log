from typing import Optional

from fastapi import HTTPException, status

from app.utils.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, MIN_WIDTH_LOGO, MIN_HEIGHT_LOGO, MAX_HEIGHT_LOGO, \
    MAX_WIDTH_LOGO


class CustomException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(status_code=self.status_code,
                         detail=detail if detail is not None else self.detail)


class TeamNotExist(CustomException):
    status_code = status.HTTP_404_NOT_FOUND


class TeamAlreadyExists(CustomException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Team with this name already exists"


class WrongFileFormat(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = f"An unacceptable file format. Allowed: {ALLOWED_EXTENSIONS}"


class WrongFileSize(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = f"File size exceeds {int(MAX_FILE_SIZE / (1024 * 1024))}MB"


class WrongFileResolution(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = f"The image should be from {MIN_WIDTH_LOGO}x{MIN_HEIGHT_LOGO} to {MAX_WIDTH_LOGO}x{MAX_HEIGHT_LOGO} pixels"
