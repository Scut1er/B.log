from typing import Optional

from fastapi import HTTPException, status

from app.utils.constants import (ALLOWED_EXTENSIONS, MAX_FILE_SIZE,
                                 MAX_HEIGHT_LOGO, MAX_WIDTH_LOGO,
                                 MIN_HEIGHT_LOGO, MIN_WIDTH_LOGO)


class CustomException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(status_code=self.status_code,
                         detail=detail if detail is not None else self.detail)


class TeamNotExist(CustomException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Team not found. Please check the team ID and try again."


class PlayerNotExist(CustomException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Player not found. Please check the player ID and try again."


class CoachNotExist(CustomException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Coach not found. Please check the coach ID and try again."


class TeamAlreadyExists(CustomException):
    status_code = status.HTTP_409_CONFLICT
    detail = "A team with this name already exists. Please choose a different team name."


class DeleteTeamError(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Error occurred while deleting the team."


class DeletePlayerError(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Error occurred while deleting the player."


class DeleteCoachError(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Error occurred while deleting the coach."


class UpdateLogoError(CustomException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Error occurred while updating the logo."


class UpdatePhotoError(CustomException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Error occurred while updating the photo."


class WrongFileFormat(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = f"Invalid file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}."


class WrongFileSize(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = f"The file size exceeds the allowed limit of {int(MAX_FILE_SIZE / (1024 * 1024))}MB."


class WrongFileResolution(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = (f"The image resolution is not acceptable. "
              f"The image must be between {MIN_WIDTH_LOGO}x{MIN_HEIGHT_LOGO} and {MAX_WIDTH_LOGO}x{MAX_HEIGHT_LOGO} pixels.")


class LoadFileError(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "An error occurred while uploading the file."


class InvalidBirthDateFormat(CustomException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "The birth date must be in the format YYYY-MM-DD."


class InvalidHeightOrWeight(CustomException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Height and weight must be between 1 and 300."
