import os
from repositories.csv_repository import CSVRepository
from utils.csv_session import CSVSession
from utils.exceptions import (
    FileNotFoundError, InvalidFileTypeError, CSVNotLoadedError, InvalidColumnError, FilterError
)

UPLOAD_DIR = "uploads"


class CSVService:
    def __init__(self):
        self.repo = CSVRepository()

    def _require_loaded(self):
        if not CSVSession.is_loaded():
            raise CSVNotLoadedError("No CSV loaded. Call POST /csv/load first.")

    def _validate_columns(self, columns: list[str]):
        df = CSVSession.get()
        bad = [c for c in columns if c not in df.columns]
        if bad:
            raise InvalidColumnError(f"Columns not found: {bad}")

    def _df_to_records(self, df) -> list[dict]:
        return df.where(df.notna(), None).to_dict(orient="records")

    def load(self, filename: str) -> dict:
        path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"{filename} not found in uploads")
        if not filename.endswith(".csv"):
            raise InvalidFileTypeError(f"{filename} is not a CSV file")
        self.repo.load(filename)
        df = CSVSession.get()
        return {"loaded": filename, "rows": len(df), "columns": list(df.columns)}

    def summary(self) -> dict:
        self._require_loaded()
        return self.repo.summary()

    def filter_rows(self, column: str, operator: str, value) -> list[dict]:
        self._require_loaded()
        self._validate_columns([column])
        try:
            result = self.repo.filter_rows(column, operator, value)
        except Exception as e:
            raise FilterError(str(e))
        CSVSession._df = result
        return self._df_to_records(result)

    def sort_rows(self, columns: list[str], ascending: list[bool] | None) -> list[dict]:
        self._require_loaded()
        self._validate_columns(columns)
        result = self.repo.sort_rows(columns, ascending)
        CSVSession._df = result
        return self._df_to_records(result)

    def select_columns(self, columns: list[str]) -> list[dict]:
        self._require_loaded()
        self._validate_columns(columns)
        result = self.repo.select_columns(columns)
        CSVSession._df = result
        return self._df_to_records(result)

    def drop_null(self) -> dict:
        self._require_loaded()
        result = self.repo.drop_null()
        CSVSession._df = result
        return {"rows_remaining": len(result), "data": self._df_to_records(result)}

    def drop_duplicates(self) -> dict:
        self._require_loaded()
        result = self.repo.drop_duplicates()
        CSVSession._df = result
        return {"rows_remaining": len(result), "data": self._df_to_records(result)}

    def export(self, filename: str) -> dict:
        self._require_loaded()
        if not filename.endswith(".csv"):
            filename += ".csv"
        path = self.repo.export(filename)
        return {"exported_to": path, "filename": filename}
