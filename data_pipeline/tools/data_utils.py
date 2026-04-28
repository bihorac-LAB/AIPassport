import pandas as pd

def find_case_insensitive_column(df: pd.DataFrame, expected: str) -> str | None:
    expected_lower = expected.strip().lower()
    for col in df.columns:
        if str(col).strip().lower() == expected_lower:
            return col
    return None

