## Setup

1. `python3 -m venv .venv`
2. Activate venv
    a. Windows: `.venv\Scripts\activate`
    b. Linux: `source .venv/bin/activate`
3. `pip install -r requirements.txt`

## Bluetooth setup

1. Windows

https://github.com/Ircama/ELM327-emulator?tab=readme-ov-file#usage-of-bluetooth-with-windows

## Start emulator

`"C:/Program Files (x86)/com0com/setupg.exe"`

`python -m elm -p COM6 -s car --baudrate 38400`

`python -m uvicorn --factory "main:app_factory"`