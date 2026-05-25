import os
import shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class FileRepository:
    def save(self, file: UploadFile) -> dict:
        dest = os.path.join(UPLOAD_DIR, file.filename)
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        size = os.path.getsize(dest)
        return {"filename": file.filename, "size_bytes": size, "content_type": file.content_type}

    def get_all(self) -> list[dict]:
        files = []
        for name in os.listdir(UPLOAD_DIR):
            path = os.path.join(UPLOAD_DIR, name)
            if os.path.isfile(path):
                files.append({
                    "filename": name,
                    "size_bytes": os.path.getsize(path),
                    "content_type": "text/csv" if name.endswith(".csv") else "application/octet-stream"
                })
        return files

    def get_path(self, filename: str) -> str | None:
        path = os.path.join(UPLOAD_DIR, filename)
        return path if os.path.isfile(path) else None
