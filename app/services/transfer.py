import httpx
import requests
from app.config import SERVER_ADDRESS
            
async def send_file_request(sender_url: str, portfolio_id: str, navdate: str):
    receiver_webhook = f"{SERVER_ADDRESS}/webhook/receive-file"
    payload = {
        "portfolio_id": portfolio_id,
        "navdate": navdate,
        "receiver_url": receiver_webhook
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Send the request without awaiting the response
            client.post(f"{sender_url}/webhook/send-file", json=payload)
        # Optionally log that the request was sent
        print("Request sent (fire-and-forget)")
    except Exception as e:
        print(f"Exception in send_file_request: {e}")