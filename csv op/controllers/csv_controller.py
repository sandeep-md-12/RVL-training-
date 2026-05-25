from fastapi import HTTPException
from services.csv_service import CSVService
from utils.exceptions import (
    FileNotFoundError, InvalidFileTypeError, CSVNotLoadedError, InvalidColumnError, FilterError
)


class CSVController:
    def __init__(self):
        self.service = CSVService()

    def _handle(self, fn):
        try:
            return fn()
        except (FileNotFoundError,) as e:
            raise HTTPException(status_code=404, detail=str(e))
        except (InvalidFileTypeError, InvalidColumnError, FilterError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except CSVNotLoadedError as e:
            raise HTTPException(status_code=422, detail=str(e))

    def load(self, filename: str) -> dict:
        return self._handle(lambda: self.service.load(filename))

    def summary(self) -> dict:
        return self._handle(lambda: self.service.summary())

    def filter_rows(self, column: str, operator: str, value) -> list[dict]:
        return self._handle(lambda: self.service.filter_rows(column, operator, value))

    def sort_rows(self, columns: list[str], ascending: list[bool] | None) -> list[dict]:
        return self._handle(lambda: self.service.sort_rows(columns, ascending))

    def select_columns(self, columns: list[str]) -> list[dict]:
        return self._handle(lambda: self.service.select_columns(columns))

    def drop_null(self) -> dict:
        return self._handle(lambda: self.service.drop_null())

    def drop_duplicates(self) -> dict:
        return self._handle(lambda: self.service.drop_duplicates())

    def export(self, filename: str) -> dict:
        return self._handle(lambda: self.service.export(filename))
