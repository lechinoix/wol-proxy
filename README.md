# Wake-on-LAN Proxy

A simple FastAPI web application that allows you to remotely wake up computers on your network using Wake-on-LAN (WOL) technology.

## Features

- Simple web interface to send Wake-on-LAN magic packets
- Input validation for MAC addresses
- Success/error feedback

## Prerequisites

- Python 3.8+
- uv (Python package manager)
- A computer with Wake-on-LAN enabled in its BIOS/UEFI settings

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/wol-proxy.git
cd wol-proxy
```

2. Create a virtual environment and install dependencies using uv:

```bash
uv venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Usage

1. Start the application:

```bash
python -m app.main
```

2. Open your browser and navigate to [http://localhost:8000](http://localhost:8000)

3. Enter the MAC address of the computer you want to wake up and click "Wake Computer"

## Note

- Make sure the target computer has Wake-on-LAN enabled in its BIOS/UEFI settings
- Both computers should be on the same network
- Some networks may block WOL packets; check your router settings if having issues
