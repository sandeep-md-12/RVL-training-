from fastapi import UploadFile, HTTPException
from services.file_service import FileService
from utils.exceptions import FileNotFoundError, InvalidFileTypeError


class FileController:
    def __init__(self):
        self.service = FileService()

    def upload(self, files: list[UploadFile]) -> list[dict]:
        try:
            return self.service.upload_files(files)
        except InvalidFileTypeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def list_files(self) -> list[dict]:
        return self.service.list_files()

    def get_file(self, filename: str) -> dict:
        try:
            return self.service.get_file_details(filename)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
