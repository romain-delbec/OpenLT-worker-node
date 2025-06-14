import os
import shutil
import pandas as pd
from fastapi import UploadFile, HTTPException
from app.config import DATA_DIR
from .indexing import add_owned_entry, add_child_entry, add_received_entry
from .lookthrough import run_lookthrough

portfolios_dir = os.path.join(DATA_DIR, "portfolios")
received_dir = os.path.join(DATA_DIR, "received_portfolios")

def load_expected_headers_from_csv(file_path: str) -> list:
    df = pd.read_csv(file_path, header=None)

    headers = df.iloc[:, 0].tolist()

    return headers

def save_csv(file: UploadFile) -> str:
    EXPECTED_HEADERS = load_expected_headers_from_csv(os.path.join(DATA_DIR, "expected_headers", "tptv6_headers.csv"))
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    try:
        content = file.file.read().decode('utf-8')
        file.file.seek(0)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error reading file content.")

    try:
        df = pd.read_csv(file.file)
        file.file.seek(0)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error parsing CSV file.")

    if list(df.columns) != EXPECTED_HEADERS:
        raise HTTPException(status_code=400, detail="CSV headers do not match the expected TPT v6 template.")
    
    if df["1_Portfolio_identifying_data"].nunique() == 1:
        portfolio_id = df["1_Portfolio_identifying_data"][1]
    else:
        raise HTTPException(status_code=400, detail="File contains multiple portfolio ids.")
    
    if df["6_Valuation_date"].nunique() == 1:
        navdate = df["6_Valuation_date"][1]
    else:
        raise HTTPException(status_code=400, detail="File contains multiple navdates for portfolio.")
    
    add_owned_entry(filename=file.filename, portfolio_id=portfolio_id, navdate=navdate)
    
    for index, row in df.iterrows():
        if row['15_Type_of_identification_code_for_the_instrument'] == 99:
            print("Found child portfolio")
            add_child_entry(
                parent_id=row['1_Portfolio_identifying_data'],
                child_id=row['14_Identification_code_of_the_instrument'],
                navdate=row['6_Valuation_date']
            )
            
    run_lookthrough(portfolio_id=portfolio_id, navdate=navdate)
    
    os.makedirs(portfolios_dir, exist_ok=True)
    path = os.path.join(portfolios_dir, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file.filename

def save_received_csv(file: UploadFile) -> str:
    EXPECTED_HEADERS = load_expected_headers_from_csv(os.path.join(DATA_DIR, "expected_headers", "tptv6_headers.csv"))
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    try:
        content = file.file.read().decode('utf-8')
        file.file.seek(0)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error reading file content.")

    try:
        df = pd.read_csv(file.file)
        file.file.seek(0)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error parsing CSV file.")

    if list(df.columns) != EXPECTED_HEADERS:
        raise HTTPException(status_code=400, detail="CSV headers do not match the expected TPT v6 template.")
    
    if df["1_Portfolio_identifying_data"].nunique() == 1:
        portfolio_id = df["1_Portfolio_identifying_data"][1]
    else:
        raise HTTPException(status_code=400, detail="File contains multiple portfolio ids.")
    
    if df["6_Valuation_date"].nunique() == 1:
        navdate = df["6_Valuation_date"][1]
    else:
        raise HTTPException(status_code=400, detail="File contains multiple navdates for portfolio.")
    
    add_received_entry(filename=file.filename, portfolio_id=portfolio_id, navdate=navdate)
    
    for index, row in df.iterrows():
        if row['15_Type_of_identification_code_for_the_instrument'] == 99:
            print("Found child portfolio")
            add_child_entry(
                parent_id=row['1_Portfolio_identifying_data'],
                child_id=row['14_Identification_code_of_the_instrument'],
                navdate=row['6_Valuation_date']
            )

    run_lookthrough(portfolio_id=portfolio_id, navdate=navdate)
    
    os.makedirs(received_dir, exist_ok=True)
    path = os.path.join(received_dir, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file.filename

def portfolio_to_html(filename):
    df = pd.read_csv(os.path.join(portfolios_dir, filename))
    return df.to_html(classes="table table-bordered", index=False)

def get_csv_path(portfolio_id, navdate, status):
    if status not in ['owned', 'received']:
        raise ValueError("Status must be either 'owned' or 'received'.")
    elif status == 'owned':
        index_path = os.path.join(DATA_DIR, "index", "owned_index.csv")
    else:
        index_path = os.path.join(DATA_DIR, "index", "received_index.csv")
    
    df = pd.read_csv(index_path)

    match = df[(df['portfolio_id'] == portfolio_id) & (df['navdate'] == navdate)]

    if not match.empty:
        return match.iloc[0]['filename']
    else:
        return None
    
def load_portfolio(filename, status):
    if status not in ['owned', 'received']:
        raise ValueError("Status must be either 'owned' or 'received'.")
    elif status == 'owned':
        filepath = os.path.join(portfolios_dir, filename)
    else:
        filepath = os.path.join(received_dir, filename)
    
    df = pd.read_csv(filepath)
    
    return df
