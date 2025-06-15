import httpx
import requests
from app.config import SERVER_ADDRESS
            
async def send_file_request(sender_url: str, portfolio_id: str, navdate: str):
    receiver_webhook = f"{SERVER_ADDRESS}/webhook/receive-file"
    file_name = f"{portfolio_id}_{navdate}.csv"  # Define the file name you want to request

    # Prepare the payload according to the FileRequest model
    payload = {
        "portfolio_id": portfolio_id,
        "navdate": navdate,
        "receiver_url": receiver_webhook
    }

    try:
        response = requests.post(
            f"{sender_url}/webhook/send-file",
            json=payload,
            timeout=10
        )
        print('Got response:', response.json())
        return response
    except Exception as e:
        print(f"Exception: {e}")
        raise
