import os
import pandas as pd
from app.config import DATA_DIR

index_dir = os.path.join(DATA_DIR, "index")

def add_owned_entry(filename, portfolio_id, navdate):
    file_path = os.path.join(index_dir, "owned_index.csv")
    df = pd.read_csv(file_path)
    
    if ((df['filename'] == filename ) & (df['portfolio_id'] == portfolio_id) & (df['navdate'] == navdate)).any():
        return 
    
    if ((df['portfolio_id'] == portfolio_id) & (df['navdate'] == navdate)).any():
        return False

    new_entry = pd.DataFrame([[filename, portfolio_id, navdate]], columns=['filename', 'portfolio_id', 'navdate'])
    df = pd.concat([df, new_entry], ignore_index=True)
    
    df.to_csv(file_path, index=False)
    
def add_child_entry(parent_id, child_id, navdate):
    file_path = os.path.join(index_dir, "owned_childs_index.csv")
    df = pd.read_csv(file_path)
    
    new_entry = pd.DataFrame([[parent_id, child_id, navdate]], columns=['parent_id', 'child_id', 'navdate'])
    df = pd.concat([df, new_entry], ignore_index=True)
    
    df.to_csv(file_path, index=False)
    
def add_received_entry(filename, portfolio_id, navdate):
    file_path = os.path.join(index_dir, "received_index.csv")
    df = pd.read_csv(file_path)
    
    if ((df['filename'] == filename ) & (df['portfolio_id'] == portfolio_id) & (df['navdate'] == navdate)).any():
        return 
    
    if ((df['portfolio_id'] == portfolio_id) & (df['navdate'] == navdate)).any():
        return False

    new_entry = pd.DataFrame([[filename, portfolio_id, navdate]], columns=['filename', 'portfolio_id', 'navdate'])
    df = pd.concat([df, new_entry], ignore_index=True)
    
    df.to_csv(file_path, index=False)
    
def load_index(index):
    if index not in ['owned', 'received', 'owned_childs']:
        raise ValueError("Status must be either 'owned' or 'received' or 'owned_childs")
    elif index == 'owned':
        index_path = os.path.join(DATA_DIR, "index", "owned_index.csv")
    elif index == 'received':
        index_path = os.path.join(DATA_DIR, "index", "received_index.csv")
    else:
        index_path = os.path.join(DATA_DIR, "index", "owned_childs_index.csv")

    df = pd.read_csv(index_path)
    
    return df

def fetch_remote_address():
    address = 'http://localhost:8000'
    return address