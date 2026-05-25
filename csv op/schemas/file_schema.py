from pydantic import BaseModel


class FileResponse(BaseModel):
    filename: str
    size_bytes: int
    content_type: str
