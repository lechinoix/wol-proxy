import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from wakeonlan import send_magic_packet

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


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
