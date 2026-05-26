from urllib.parse import unquote
import time
from fastapi import UploadFile
from repositories.s3_repository import S3Repository
from utils.exceptions import S3UploadError, S3FileNotFoundError, S3DownloadError


class S3Service:
    def __init__(self):
        self.repo = S3Repository()

    def _build_unique_key(self, filename: str) -> str:
        timestamp = int(time.time())
        return self.repo.build_s3_key(f"{timestamp}_{filename}")

    def upload(self, files: list[UploadFile]) -> list[dict]:
        results = []
        for file in files:
            try:
                file_bytes = file.file.read()
                s3_key = self._build_unique_key(file.filename)
                self.repo.upload(file_bytes, s3_key, file.content_type or "application/octet-stream")
                results.append({"uploaded": file.filename, "s3_key": s3_key})
            except Exception as e:
                raise S3UploadError(f"Failed to upload {file.filename}: {str(e)}")
        return results

    def get_presigned_url(self, s3_key: str) -> dict:
        s3_key = unquote(s3_key)
        if not self.repo.file_exists(s3_key):
            raise S3FileNotFoundError(f"{s3_key} not found in S3")
        url = self.repo.generate_presigned_url(s3_key)
        return {"s3_key": s3_key, "url": url}

    def download(self, s3_key: str) -> tuple[bytes, str, str]:
        s3_key = unquote(s3_key)
        if not self.repo.file_exists(s3_key):
            raise S3FileNotFoundError(f"{s3_key} not found in S3")
        try:
            file_bytes, content_type = self.repo.download(s3_key)
            filename = s3_key.split("/")[-1]
            return file_bytes, content_type, filename
        except Exception as e:
            raise S3DownloadError(f"Failed to download {s3_key}: {str(e)}")
