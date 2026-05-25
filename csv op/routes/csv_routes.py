from fastapi import APIRouter
from controllers.csv_controller import CSVController
from schemas.csv_schema import (
    LoadCSVRequest, FilterRequest, SortRequest,
    SelectColumnsRequest, ExportRequest
)

router = APIRouter(prefix="/csv", tags=["CSV"])


@router.post("/load")
def load_csv(body: LoadCSVRequest):
    return CSVController().load(body.filename)


@router.get("/summary")
def summary():
    return CSVController().summary()


@router.post("/filter")
def filter_rows(body: FilterRequest):
    return CSVController().filter_rows(body.column, body.operator, body.value)


@router.post("/sort")
def sort_rows(body: SortRequest):
    return CSVController().sort_rows(body.columns, body.ascending)


@router.post("/select-columns")
def select_columns(body: SelectColumnsRequest):
    return CSVController().select_columns(body.columns)


@router.post("/drop-null")
def drop_null():
    return CSVController().drop_null()


@router.post("/drop-duplicates")
def drop_duplicates():
    return CSVController().drop_duplicates()


@router.post("/export")
def export(body: ExportRequest):
    return CSVController().export(body.filename)
