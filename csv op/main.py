from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from utils.exceptions import (
    FileNotFoundError, InvalidFileTypeError, CSVNotLoadedError, InvalidColumnError, FilterError,
    S3UploadError, S3FileNotFoundError, S3DownloadError
)
from routes.file_routes import router as file_router
from routes.csv_routes import router as csv_router
from routes.s3_routes import router as s3_router
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="CSV Operations API", version="1.0.0", lifespan=lifespan)


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidFileTypeError)
async def invalid_file_type_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(CSVNotLoadedError)
async def csv_not_loaded_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(InvalidColumnError)
async def invalid_column_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(FilterError)
async def filter_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(S3UploadError)
async def s3_upload_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(S3FileNotFoundError)
async def s3_file_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(S3DownloadError)
async def s3_download_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred"})


app.include_router(file_router)
app.include_router(csv_router)
app.include_router(s3_router)


@app.get("/")
def health_check():
    return {"status": "ok"}
