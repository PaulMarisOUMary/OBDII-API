from asyncio import Event, Lock, TaskGroup
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from obdii import Connection, commands

from basetypes import API
from routes import router


API_VERSION = "1.1.0"

DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"

DEFAULT_FETCH_COMMANDS = {
    commands.VEHICLE_SPEED.name,
    commands.ENGINE_SPEED.name,
    commands.ENGINE_COOLANT_TEMP.name,
    "INVALID_COMMAND_NAME",
}

@asynccontextmanager
async def lifespan(app: API):
    async with TaskGroup() as tg:
        app.task_group = tg
        app.polling_event = Event()
        app.obd = Connection(DEFAULT_SERIAL_PORT, auto_connect=False)
        app.storage_lock = Lock()
        app.storage = dict.fromkeys(DEFAULT_FETCH_COMMANDS, None)

        yield
        app.polling_event.set()

def app_factory():
    app = API(
        title="OBDII API",
        version=API_VERSION,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
    )
    app.include_router(router)
    return app