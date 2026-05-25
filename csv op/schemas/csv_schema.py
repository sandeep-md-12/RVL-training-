from pydantic import BaseModel, field_validator
from typing import List, Optional, Any


class LoadCSVRequest(BaseModel):
    filename: str


class FilterRequest(BaseModel):
    column: str
    operator: str  # "eq", "ne", "gt", "lt", "gte", "lte", "contains"
    value: Any

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        allowed = {"eq", "ne", "gt", "lt", "gte", "lte", "contains"}
        if v not in allowed:
            raise ValueError(f"operator must be one of {allowed}")
        return v


class SortRequest(BaseModel):
    columns: List[str]
    ascending: Optional[List[bool]] = None


class SelectColumnsRequest(BaseModel):
    columns: List[str]


class ExportRequest(BaseModel):
    filename: str
