import pandas as pd
from .indexing import load_index
from .file_handler import get_csv_path, load_portfolio

def run_lookthrough(portfolio_id, navdate):    
    child_ids, navdate = load_portfolio_childs(portfolio_id=portfolio_id, navdate=navdate)
    
    for child in child_ids:
        if check_local_availability(portfolio_id=child, navdate=navdate) == False:
            print(f'{child} not available')
            fetch_from_central(portfolio_id=child, navdate=navdate)
        

def load_portfolio_childs(portfolio_id, navdate):
    df_owned = load_index(index='owned_childs')
    
    filtered_df = df_owned[(df_owned['parent_id'] == portfolio_id) & (df_owned['navdate'] == navdate)]

    child_ids = filtered_df['child_id'].tolist()
    
    return child_ids, navdate

def check_local_availability(portfolio_id, navdate):
    df_owned_index = load_index(index='owned')
    df_received_index = load_index(index='received')
    
    match = df_owned_index[(df_owned_index['portfolio_id'] == portfolio_id) & (df_owned_index['navdate'] == navdate)]
    
    if not match.empty: return 'owned'
    else:
        match = df_received_index[(df_received_index['portfolio_id'] == portfolio_id) & (df_received_index['navdate'] == navdate)]
        if not match.empty: return 'received'
        else: return False
    
def fetch_from_central(portfolio_id, navdate):
    print("Not available locally.")