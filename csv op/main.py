from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from utils.exceptions import (
    FileNotFoundError, InvalidFileTypeError, CSVNotLoadedError, InvalidColumnError, FilterError
)
from routes.file_routes import router as file_router
from routes.csv_routes import router as csv_router
import os

os.makedirs("uploads", exist_ok=True)


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


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred"})


app.include_router(file_router)
app.include_router(csv_router)


@app.get("/")
def health_check():
    return {"status": "ok"}
