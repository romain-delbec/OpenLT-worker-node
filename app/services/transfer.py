import httpx
import requests

async def fetch_file_ws(remote_url: str, filename: str) -> bytes:
    ws_url = f"{remote_url}/ws/fetch/{filename}"
    async with httpx.AsyncClient() as client:
        async with client.ws_connect(ws_url) as ws:
            data = await ws.receive_bytes()
            return data

async def send_file_ws(remote_url: str, filename: str, data: bytes):
    ws_url = f"{remote_url}/ws/send/{filename}"
    async with httpx.AsyncClient() as client:
        async with client.ws_connect(ws_url) as ws:
            await ws.send_bytes(data)
            
async def send_file_request(sender_url: str, portfolio_id: str, navdate: str):
    receiver_webhook = "http://localhost:8001/webhook/receive-file"
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
