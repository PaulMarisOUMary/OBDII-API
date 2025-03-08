import asyncio
import logging
import obd
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from typing import Any, Dict, Set

logging.getLogger("obd").setLevel(logging.CRITICAL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(fetch_data())
    try:
        yield
    except Exception as e:
        print(e)
    finally:
        shutdown_event.set()
        await task

router = APIRouter()

def app_factory():
    app = FastAPI(
        title="OBD2 API",
        version="0.1",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app

connection = obd.OBD(portstr="COM5", baudrate=38400, fast=False)

# print(obd.scan_serial())
# connection = obd.OBD()
# if connection.is_connected():
#     print(f"Connected to ELM327 Emulator!")
# else:
#     print("Failed to connect to ELM327 Emulator.")

active_data: Set[str] = set()

active_data.add("SPEED")
active_data.add("RPM")
active_data.add("FUEL_LEVEL")
active_data.add("COOLANT_TEMP")

# List all OBD command names and put them in a set as strings
command_names = {name for name, _ in obd.commands.__dict__.items() if obd.commands.has_name(name)}

active_data.update(command_names)

global_response: Dict[str, Any] = {}

shutdown_event = asyncio.Event()

async def fetch_data():
    global global_response
    while not shutdown_event.is_set():
        responses = {}
        for name in active_data:
            if obd.commands.has_name(name):
                cmd = obd.commands[name]
                response = connection.query(cmd)
                if not response.is_null():
                    responses[name] = str(response.value)
                else:
                    responses[name] = "No response"
            else:
                responses[name] = "Invalid command"
        global_response = responses
        await asyncio.sleep(0.1)

@router.get("/request_data")
async def request_data():
    """Returns the current OBD2 data being monitored."""
    return {"active_data": global_response}

@router.post("/add_data")
async def add_data(data: dict):
    """Adds a data item to the monitoring list."""
    name = data.get("name")
    if name:
        active_data.add(name)
        return {"message": f"Data {name} added."}
    return {"error": "No name provided."}

@router.delete("/remove_data")
async def remove_data(data: dict):
    """Removes a data item from the monitoring list."""
    name = data.get("name")
    if name:
        active_data.discard(name)
        return {"message": f"Data {name} removed."}
    return {"error": "No name provided."}