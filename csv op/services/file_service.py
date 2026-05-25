from fastapi import UploadFile
from repositories.file_repository import FileRepository
from utils.exceptions import FileNotFoundError, InvalidFileTypeError


class FileService:
    def __init__(self):
        self.repo = FileRepository()

    def upload_files(self, files: list[UploadFile]) -> list[dict]:
        results = []
        for file in files:
            if not file.filename.endswith(".csv") and file.content_type not in (
                "text/csv", "application/octet-stream", "text/plain"
            ):
                raise InvalidFileTypeError(f"{file.filename} is not a supported file type")
            results.append(self.repo.save(file))
        return results

    def list_files(self) -> list[dict]:
        return self.repo.get_all()

    def get_file_details(self, filename: str) -> dict:
        path = self.repo.get_path(filename)
        if not path:
            raise FileNotFoundError(f"{filename} not found")
        import os
        return {
            "filename": filename,
            "size_bytes": os.path.getsize(path),
            "content_type": "text/csv" if filename.endswith(".csv") else "application/octet-stream",
            "path": path,
        }
