import pandas as pd
import asyncio
import requests
import json
import websockets
from .indexing import load_index
from .transfer import send_file_request

async def run_lookthrough(portfolio_id, navdate):    
    child_ids, navdate = load_portfolio_childs(portfolio_id=portfolio_id, navdate=navdate)
    
    for child in child_ids:
        if check_local_availability(portfolio_id=child, navdate=navdate) == False:
            remote_address = fetch_from_central(portfolio_id=child, navdate=navdate)
            if remote_address and remote_address != "Not found":
                await send_file_request(sender_url=remote_address, portfolio_id=child, navdate=navdate)
                
        

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
    url = "http://localhost:8000/api/lookup"
    payload = {
        "portfolio_id": portfolio_id,
        "navdate": navdate
    }
    response = requests.post(url, json=payload)
    response_data = response.json()
    return response_data['server_address']
    print(f'CENTRAL RESPONSE: {response_data}')
    
def upload_to_central(server_address, portfolio_id, navdate):
    url = "http://localhost:8000/upload/"
    payload = {
        "server_address": server_address,
        "portfolio_id": portfolio_id,
        "navdate": navdate
    }
    response = requests.post(url, json=payload)
    print(f'UPLOAD RESPONSE: {response.json()}')