from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import io
from controllers.s3_controller import S3Controller

router = APIRouter(prefix="/files", tags=["S3"])


@router.post("/upload-s3")
def upload_to_s3(files: list[UploadFile] = File(...)):
    return S3Controller().upload(files)


@router.get("/s3/presigned")
def get_presigned_url(s3_key: str):
    return S3Controller().get_presigned_url(s3_key)


@router.get("/s3/download")
def download_from_s3(s3_key: str):
    file_bytes, content_type, filename = S3Controller().download(s3_key)
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
