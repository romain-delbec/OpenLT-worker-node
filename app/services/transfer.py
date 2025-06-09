import httpx

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
