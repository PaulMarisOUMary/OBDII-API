from asyncio import Event, Lock, TaskGroup, to_thread
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict
from fastapi import APIRouter, HTTPException

from basetypes import API, RawRequest

from obdii import Connection, commands


SERIAL_PORT = "COM5"

API_VERSION = "1.0"

DEFAULT_FETCH_COMMANDS = {
    commands.VEHICLE_SPEED.name,
    commands.ENGINE_SPEED.name,
    commands.COOLANT_TEMP.name,
    "INVALID_COMMAND_NAME",
}


class StorageUpdater():
    def __init__(self, app: API):
        self.storage_lock = app.storage_lock
        self.storage = app.storage
        self.task_group = app.task_group

    def update_storage(self, cp_storage: Dict[str, Any]):        
        async def update():
            async with self.storage_lock:
                keys_to_remove = set(cp_storage.keys()) - set(self.storage.keys())

                for key in keys_to_remove:
                    cp_storage.pop(key)

                self.storage.update(cp_storage)

        self.task_group.create_task(update())

def background_fetch(stop: Callable[[], bool], app: API) -> None:
    updater = StorageUpdater(app)

    while not stop():
        conn = app.obd
        cp_storage = app.storage.copy()

        for command_name in cp_storage.keys():
            try:
                response = conn.query(commands[command_name])
                cp_storage[command_name] = response.value
            except KeyError:
                cp_storage[command_name] = f"Error: {command_name} not found"
            except Exception as e:
                cp_storage[command_name] = f"CRITError: {str(e)}"

        updater.update_storage(cp_storage)

@asynccontextmanager
async def lifespan(app: API):
    stop_event = Event()

    async def run_blocking():
        await to_thread(background_fetch, stop_event.is_set, app)

    async with TaskGroup() as tg:
        app.task_group = tg
        app.obd = Connection(SERIAL_PORT)
        app.storage_lock = Lock()
        app.storage = dict.fromkeys(DEFAULT_FETCH_COMMANDS, None)

        tg.create_task(run_blocking())
        yield
        stop_event.set()


router = APIRouter()

def app_factory():
    app = API(
        title="OBDII API",
        version=API_VERSION,
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


@router.get("/data")
async def request_data(raw_request: RawRequest):
    async with raw_request.app.storage_lock:
        return {"data": dict(raw_request.app.storage)}

@router.post("/add")
async def add_key(raw_request: RawRequest, key: str):
    key = key.upper()

    async with raw_request.app.storage_lock:
        raw_request.app.storage[key] = None
        return {"status": f"'{key}' added"}

@router.delete("/remove")
async def remove_key(raw_request: RawRequest, key: str):
    key = key.upper()

    async with raw_request.app.storage_lock:
        if key in raw_request.app.storage:
            del raw_request.app.storage[key]
            return {"status": f"'{key}' removed"}
        else:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")