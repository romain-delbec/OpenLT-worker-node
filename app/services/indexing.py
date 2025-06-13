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
    
def load_owned_index():
    file_path = os.path.join(index_dir, "owned_index.csv")
    df = pd.read_csv(file_path)
    
    files = df.to_dict(orient="records")
    
    return files