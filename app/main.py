import uvicorn
from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from wakeonlan import send_magic_packet
from dotenv import load_dotenv
import httpx
import asyncio
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Initialize variables from .env
TARGET_MAC = os.getenv("TARGET_MAC")
TARGET_IP = os.getenv("TARGET_IP")
TARGET_PORT = int(os.getenv("TARGET_PORT"))
WAIT_TIMEOUT = 60  # secondes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def wait_for_port(ip: str, port: int, timeout: int) -> bool:
    """
    Wait for a TCP port to become available.
    
    Args:
        ip: Target IP address
        port: Target port number
        timeout: Maximum seconds to wait
    
    Returns:
        bool: True if port becomes available, False if timeout reached
    """
    start_time = asyncio.get_event_loop().time()
    last_error = None

    while (asyncio.get_event_loop().time() - start_time) < timeout:
        try:
            # Attempt connection with a short timeout
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=1.0
            )
            
            # Clean up the connection
            writer.close()
            await writer.wait_closed()
            
            logging.info(f"Successfully connected to {ip}:{port}")
            return True
            
        except Exception as e:
            logging.error(f"Unexpected error checking {ip}:{port}: {str(e)}")
            return False
            
        # Wait before next attempt
        await asyncio.sleep(1)

    logging.warning(f"Timeout reached waiting for {ip}:{port}. Last error: {last_error}")
    return False

app = FastAPI(title="Wake-on-LAN Proxy")

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/wake", response_class=HTMLResponse)
async def wake_on_lan(request: Request, mac_address: str = Form(...)):
    try:
        # Send the magic packet to wake the computer
        send_magic_packet(mac_address)
        message = f"Wake-on-LAN magic packet sent to {mac_address}"
        status = "success"
    except Exception as e:
        message = f"Error: {str(e)}"
        status = "error"

    return templates.TemplateResponse(
        "index.html", {"request": request, "message": message, "status": status}
    )

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    # 1. Send WoL
    send_magic_packet(TARGET_MAC)

    # 2. Wait for the server to start
    server_ready = await wait_for_port(TARGET_IP, TARGET_PORT, WAIT_TIMEOUT)
    if not server_ready:
        return Response(content="Timeout waiting for target machine", status_code=504)

    # 3. Forward the request
    url = f"http://{TARGET_IP}:{TARGET_PORT}/{path}"
    async with httpx.AsyncClient() as client:
        method = request.method
        headers = dict(request.headers)
        body = await request.body()

        forwarded = await client.request(
            method, url, content=body, headers=headers
        )

    return Response(
        content=forwarded.content,
        status_code=forwarded.status_code,
        headers=dict(forwarded.headers)
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
