import pandas as pd
import os
from utils.csv_session import CSVSession

UPLOAD_DIR = "uploads"


class CSVRepository:
    def load(self, filename: str) -> None:
        path = os.path.join(UPLOAD_DIR, filename)
        CSVSession.load(path)

    def get_df(self) -> pd.DataFrame:
        return CSVSession.get()

    def summary(self) -> dict:
        df = CSVSession.get()
        return {
            "shape": list(df.shape),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "null_counts": df.isnull().sum().to_dict(),
            "describe": df.describe(include="all").fillna("").to_dict(),
        }

    def filter_rows(self, column: str, operator: str, value) -> pd.DataFrame:
        df = CSVSession.get()
        ops = {
            "eq": df[column] == value,
            "ne": df[column] != value,
            "gt": df[column] > value,
            "lt": df[column] < value,
            "gte": df[column] >= value,
            "lte": df[column] <= value,
            "contains": df[column].astype(str).str.contains(str(value), case=False, na=False),
        }
        return df[ops[operator]]
        
    def sort_rows(self, columns: list[str], ascending: list[bool] | None) -> pd.DataFrame:
        df = CSVSession.get()
        asc = ascending if ascending is not None else [True] * len(columns)
        return df.sort_values(by=columns, ascending=asc)

    def select_columns(self, columns: list[str]) -> pd.DataFrame:
        return CSVSession.get()[columns]

    def drop_null(self) -> pd.DataFrame:
        return CSVSession.get().dropna()

    def drop_duplicates(self) -> pd.DataFrame:
        return CSVSession.get().drop_duplicates()

    def export(self, filename: str) -> str:
        df = CSVSession.get()
        path = os.path.join(UPLOAD_DIR, filename)
        df.to_csv(path, index=False)
        return path
