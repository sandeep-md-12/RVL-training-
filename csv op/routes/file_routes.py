from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse as FastAPIFileResponse
from controllers.file_controller import FileController
import os

router = APIRouter(prefix="/files", tags=["Files"])
UPLOAD_DIR = "uploads"


@router.post("/upload")
def upload_files(files: list[UploadFile] = File(...)):
    return FileController().upload(files)


@router.get("")
def list_files():
    return FileController().list_files()


@router.get("/{filename}")
def get_file(filename: str):
    details = FileController().get_file(filename)
    path = os.path.join(UPLOAD_DIR, filename)
    return FastAPIFileResponse(path=path, filename=filename, media_type=details["content_type"])
