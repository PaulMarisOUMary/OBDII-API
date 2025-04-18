# OBDII API

## Overview

This API continuously fetches data from registered OBDII commands names.

Available commands to register are listed within `obdii.commands`.

## Setup

Python 3.**9** or higher is required.

A [Virtual Environment](https://docs.python.org/3/library/venv.html) is recommended to use the project.

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

- Change the `SERIAL_PORT` constant value in the [main.py](/api/main.py) file.
- Edit the `DEFAULT_FETCH_COMMANDS` constant to change default registered commands names.

### Start the API

```bash
python -m uvicorn --app-dir api --factory main:app_factory --host 0.0.0.0 --port 8000 --log-level debug --reload
```

## Usage

API Endpoints
- **POST** `connect` `{**kwargs}`: Initialize the connection and start background polling task.
- **POST** `disconnect`: Stop the background polling task and close the connection.
- **GET** `/status`: Check the connection status.
- **GET** `/data`: Fetch the current data being monitored.
- **POST** `/add` `{key: command_name}`: Register a new command to be monitored.
- **DELETE** `/remove` `{key: command_name}`: Unregister a command from being monitored.
