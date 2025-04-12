# OBDII API

## Overview

This API continuously fetches data from registered OBDII commands names.

You can register new commands using the `POST /add` endpoint, and unregister commands using the `DELETE /remove` endpoint. To retrieve the data, simply use the `GET /data` endpoint.

Available commands are listed within `obdii.commands`.

## Setup

Python 3.**9** or higher is required.

A [Virtual Environment](https://docs.python.org/3/library/venv.html) is recommended to install the library.

```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
py -3 -m venv .venv
.venv\Scripts\activate
```

## Install Dependencies

After activating the virtual environment, install the required dependencies by running:

```bash
pip install -r ./requirements.txt
```

## Running the API

You may need to configure additional steps if you are using a Bluetooth OBDII device, depending on your OS, and/or if you're using an emulator.

For more details on configuring the connection, refer to the [official py-obdii repository](https://github.com/PaulMarisOUMary/OBDII).

### Quick Configuration

Change the `SERIAL_PORT` constant value in the [main.py](/api/main.py) file.

### Start the API

```bash
cd api
python -m uvicorn --reload --factory "main:app_factory" --log-level debug
```

## Usage

API Endpoints
- **GET** `/data`: Fetch the current data being monitored.
- **POST** `/add` `{key: command_name}`: Register a new command to be monitored.
- **DELETE** `/remove` `{key: command_name}`: Fetch the current data being monitored.