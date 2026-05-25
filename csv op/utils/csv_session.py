import pandas as pd
from typing import Optional


class CSVSession:
    _df: Optional[pd.DataFrame] = None
    _loaded_file: Optional[str] = None

    @classmethod
    def load(cls, path: str) -> None:
        cls._df = pd.read_csv(path)
        cls._loaded_file = path

    @classmethod
    def get(cls) -> Optional[pd.DataFrame]:
        return cls._df

    @classmethod
    def loaded_file(cls) -> Optional[str]:
        return cls._loaded_file

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._df is not None
