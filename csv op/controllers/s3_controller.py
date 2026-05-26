from fastapi import UploadFile, HTTPException
from services.s3_service import S3Service
from utils.exceptions import S3UploadError, S3FileNotFoundError, S3DownloadError


class S3Controller:
    def __init__(self):
        self.service = S3Service()

    def upload(self, files: list[UploadFile]) -> list[dict]:
        try:
            return self.service.upload(files)
        except S3UploadError as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_presigned_url(self, s3_key: str) -> dict:
        try:
            return self.service.get_presigned_url(s3_key)
        except S3FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    def download(self, s3_key: str) -> tuple:
        try:
            return self.service.download(s3_key)
        except S3FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except S3DownloadError as e:
            raise HTTPException(status_code=500, detail=str(e))
