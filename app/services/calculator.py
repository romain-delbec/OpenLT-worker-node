import pandas as pd

def run_lookthrough(csv_path: str) -> dict:
    df = pd.read_csv(csv_path)
    # Fake calculation: sum of values
    result = {
        "rows": len(df),
        "sum": df.select_dtypes(include='number').sum().to_dict()
    }
    return result
